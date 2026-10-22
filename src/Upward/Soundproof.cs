using System;
using System.Collections;
using System.Collections.Generic;
using Game.Services;
using Game.Services.Filesystem;
using Game.UI.MouseOvers;
using Game.UI.Session;
using Game.Session;
using Game.Session.Board;
using Game.Session.Sim;
using HarmonyLib;
using UnityEngine;
using UnityEngine.UI;
using GameMain = Game.Game;

namespace Upward
{
    // Laje antirruido: o jogador paga por andar e o mapa de ruido daquela laje fica sempre zerado
    // (e, como a linha zerada tambem bloqueia o espalhamento, o ruido nao atravessa para os andares
    // vizinhos). Cada andar e uma linha da grade do Heatmap; as lajes compradas ficam no save.
    internal static class Soundproof
    {
        private const string SAVE_KEY = "upward_soundproof";
        private const int FLOOR_HEIGHT = 150; // Grid.CELLSIZE.y

        internal static readonly HashSet<int> Floors = new HashSet<int>();

        // ---- Regra ----

        // Zera a linha de cada laje tratada depois de cada atualizacao do mapa de ruido
        internal static void Apply(Heatmaps maps)
        {
            if (Floors.Count == 0)
            {
                return;
            }
            var grid = GameMain.ctx.board.grid;
            float[] values = maps.GetHeatmap(HeatmapType.noiseHeatmap).data.values;
            foreach (int floor in Floors)
            {
                if (!grid.IsFloorValid(floor))
                {
                    continue;
                }
                for (int x = grid.mapleft; x < grid.mapright; x++)
                {
                    values[grid.GridPosToGridIndex(x, floor)] = 0f;
                }
            }
        }

        // Preco proporcional ao tamanho da laje (casas com piso construido no andar)
        internal static int CellCount(int floor)
        {
            var grid = GameMain.ctx.board.grid;
            if (!grid.IsFloorValid(floor))
            {
                return 0;
            }
            int n = 0;
            for (int x = grid.mapleft; x < grid.mapright; x++)
            {
                if (grid.FindGridCell(new GridPos(x, floor)).hasFloor)
                {
                    n++;
                }
            }
            return n;
        }

        internal static int Cost(int floor)
        {
            return Mathf.Max(1, Mathf.RoundToInt(CellCount(floor) * Plugin.SoundproofCostPerCell.Value));
        }

        internal static bool TryBuy(int floor)
        {
            if (Floors.Contains(floor) || CellCount(floor) == 0)
            {
                return false;
            }
            var player = GameMain.ctx.sim.player;
            int cost = Cost(floor);
            if (!player.CanSpend(-cost))
            {
                return false;
            }
            player.DoAdd(-cost, Reason.OtherOneTimeExpense);
            Floors.Add(floor);
            Plugin.Log.LogInfo("Laje antirruido comprada: andar " + floor + " por " + cost);
            // Aplica ja, sem esperar o proximo ciclo do jogo
            Apply(GameMain.ctx.board.heatmaps);
            return true;
        }

        internal static void Remove(int floor)
        {
            Floors.Remove(floor);
        }

        // ---- Save ----

        internal static void WriteTo(Hashtable data)
        {
            var list = new ArrayList();
            foreach (int f in Floors)
            {
                list.Add(f);
            }
            data[SAVE_KEY] = list;
        }

        internal static void ReadFrom(Hashtable data)
        {
            Floors.Clear();
            var list = data != null && data.ContainsKey(SAVE_KEY) ? data[SAVE_KEY] as IList : null;
            if (list == null)
            {
                return;
            }
            foreach (object o in list)
            {
                try { Floors.Add(Convert.ToInt32(o)); } catch (Exception) { }
            }
            Plugin.Log.LogInfo("Lajes antirruido carregadas do save: " + Floors.Count);
        }
    }

    [HarmonyPatch(typeof(Heatmaps), nameof(Heatmaps.UpdateHeatmap))]
    internal static class SoundproofHeatmapPatch
    {
        private static void Postfix(Heatmaps __instance, HeatmapType type)
        {
            if (type == HeatmapType.noiseHeatmap)
            {
                Soundproof.Apply(__instance);
            }
        }
    }

    [HarmonyPatch(typeof(SessionContext), nameof(SessionContext.CreateSaveFile))]
    internal static class SoundproofSavePatch
    {
        private static void Postfix(SaveFile __result)
        {
            if (__result != null && __result.data != null)
            {
                Soundproof.WriteTo(__result.data);
            }
        }
    }

    [HarmonyPatch(typeof(SessionContext), nameof(SessionContext.StartInitializeManagers))]
    internal static class SoundproofLoadPatch
    {
        // savefile e nulo em partida nova: comeca sem lajes tratadas
        private static void Prefix(SaveFile savefile)
        {
            Soundproof.ReadFrom(savefile != null ? savefile.data : null);
        }
    }

    // Botao na barra do canto superior esquerdo (clone do Grid Button, veja HudButton)
    [HarmonyPatch(typeof(HUDLayers), "InitializeGameObject")]
    internal static class SoundproofButtonPatch
    {
        internal const string TOOLTIP_KEY = "upward.soundproof.tooltip";
        internal static HudButton Button;

        private static void Postfix(HUDLayers __instance)
        {
            if (!Plugin.SoundproofEnabled.Value)
            {
                return;
            }
            Button = HudButton.Create(__instance, "Soundproof Button", "textures/soundproof_icon.png", TOOLTIP_KEY,
                SoundproofPanel.Toggle);
        }

        // Painel aberto: fica com a borda acesa
        internal static void ShowOpen(bool open)
        {
            if (Button != null)
            {
                Button.ShowLit(open);
            }
        }
    }

    // Texto da caixa de descricao do botao (o jogo busca pelo lockey)
    [HarmonyPatch(typeof(Loc), nameof(Loc.Get), new[] { typeof(string) })]
    internal static class SoundproofTooltipPatch
    {
        private static bool Prefix(string key, ref string __result)
        {
            if (key != SoundproofButtonPatch.TOOLTIP_KEY)
            {
                return true;
            }
            __result = "Soundproof floor: pay per floor to keep that floor isolated from noise ("
                + Plugin.SoundproofKey.Value + ")";
            return false;
        }
    }

    // Painel (tecla configuravel, padrao F8): escolhe o andar com as setas, mostra o preco e compra.
    // Os andares tratados aparecem em azul sobre o predio; o escolhido, em amarelo.
    internal class SoundproofPanel
    {
        private static SoundproofPanel _instance;
        private bool _open;
        private bool _toggleRequested;
        private int _floor;
        private string _message = "";
        private float _messageUntil;
        private Texture2D _white;
        private GUIStyle _label, _title, _box, _button;

        public SoundproofPanel()
        {
            _instance = this;
        }

        // Chamado pelo botao da barra (UI do Unity); quem abre de fato e o OnGUI
        internal static void Toggle()
        {
            if (_instance != null)
            {
                _instance._toggleRequested = true;
            }
        }

        public void OnGUI()
        {
            var ctx = GameMain.ctx;
            if (ctx == null || !ctx.Initialized || ctx.board == null || GameMain.serv == null || GameMain.serv.camera == null)
            {
                _open = false;
                _toggleRequested = false;
                return;
            }
            if (!Plugin.SoundproofEnabled.Value)
            {
                return;
            }

            Event e = Event.current;
            if (e.type == EventType.KeyDown && e.keyCode == Plugin.SoundproofKey.Value)
            {
                _toggleRequested = true;
                e.Use();
            }
            if (_toggleRequested)
            {
                _toggleRequested = false;
                Toggle(ctx);
            }
            if (!_open)
            {
                return;
            }

            EnsureStyles();
            DrawBands(ctx);
            DrawWindow(ctx);
        }

        private void Toggle(SessionContext ctx)
        {
            _open = !_open;
            SoundproofButtonPatch.ShowOpen(_open);
            if (_open)
            {
                // Comeca no andar que esta no centro da tela
                var center = new Vector2(Screen.width / 2f, Screen.height / 2f);
                _floor = ctx.board.grid.WorldPosToGridPos(GameMain.serv.camera.ScreenToWorldPos(center)).y;
                _floor = Mathf.Max(_floor, 0);
            }
        }

        private void DrawBands(SessionContext ctx)
        {
            foreach (int f in Soundproof.Floors)
            {
                DrawBand(f, new Color(0.2f, 0.55f, 1f, 0.28f));
            }
            DrawBand(_floor, new Color(1f, 0.85f, 0.2f, 0.28f));
        }

        private void DrawBand(int floor, Color color)
        {
            var cam = GameMain.serv.camera;
            Vector2 bottom = cam.WorldToScreenPos(new WorldPos(0f, floor * FLOOR_H));
            Vector2 top = cam.WorldToScreenPos(new WorldPos(0f, (floor + 1) * FLOOR_H));
            // Coordenada de tela do Unity tem origem embaixo; a do IMGUI, em cima
            float y1 = Screen.height - top.y;
            float y2 = Screen.height - bottom.y;
            var old = GUI.color;
            GUI.color = color;
            GUI.DrawTexture(new Rect(0, y1, Screen.width, y2 - y1), _white);
            GUI.color = old;
        }

        private const int FLOOR_H = 150;

        private void DrawWindow(SessionContext ctx)
        {
            var rect = new Rect(WindowPosition(), new Vector2(270, 210));
            GuiInputBlock.Add(rect);
            GUI.Box(rect, GUIContent.none, _box);
            GUILayout.BeginArea(new Rect(rect.x + 12, rect.y + 10, rect.width - 24, rect.height - 20));

            GUILayout.Label("Soundproof floor", _title);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("-", _button, GUILayout.Width(32))) { _floor--; }
            GUILayout.Label("Floor " + _floor, _title, GUILayout.ExpandWidth(true));
            if (GUILayout.Button("+", _button, GUILayout.Width(32))) { _floor++; }
            GUILayout.EndHorizontal();

            var grid = ctx.board.grid;
            if (!grid.IsFloorValid(_floor))
            {
                _floor = Mathf.Clamp(_floor, grid.mapbottom, grid.maptop - 1);
            }

            int cells = Soundproof.CellCount(_floor);
            bool owned = Soundproof.Floors.Contains(_floor);
            if (owned)
            {
                GUILayout.Label("This floor is already soundproof.", _label);
                if (GUILayout.Button("Remove (no refund)", _button))
                {
                    Soundproof.Remove(_floor);
                }
            }
            else if (cells == 0)
            {
                GUILayout.Label("No floor tiles built on this floor.", _label);
            }
            else
            {
                int cost = Soundproof.Cost(_floor);
                GUILayout.Label("Price: $" + cost + "  (" + cells + " tiles)", _label);
                bool can = ctx.sim.player.CanSpend(-cost);
                GUI.enabled = can;
                if (GUILayout.Button(can ? "Soundproof this floor" : "Not enough money", _button))
                {
                    if (Soundproof.TryBuy(_floor))
                    {
                        Say("Floor " + _floor + " is now soundproof.");
                    }
                }
                GUI.enabled = true;
            }

            GUILayout.Label("Soundproof floors: " + Soundproof.Floors.Count, _label);
            if (Time.unscaledTime < _messageUntil)
            {
                GUILayout.Label(_message, _label);
            }
            if (GUILayout.Button("Close", _button))
            {
                _open = false;
                SoundproofButtonPatch.ShowOpen(false);
            }
            GUILayout.EndArea();
        }

        // Logo abaixo do botao da barra
        private static Vector2 WindowPosition()
        {
            var button = SoundproofButtonPatch.Button;
            return button == null || button.Rect == null ? new Vector2(170, 54) : button.BelowLeft();
        }

        private void Say(string text)
        {
            _message = text;
            _messageUntil = Time.unscaledTime + 3f;
        }

        private void EnsureStyles()
        {
            if (_white == null)
            {
                _white = Texture2D.whiteTexture;
            }
            if (_label == null)
            {
                // Cores das caixas do jogo: fundo cinza-chumbo opaco, borda um pouco mais clara
                var text = new Color(0.93f, 0.93f, 0.95f);
                _label = new GUIStyle(GUI.skin.label) { wordWrap = true, fontSize = 13 };
                _label.normal.textColor = text;
                _title = new GUIStyle(_label) { fontStyle = FontStyle.Bold, fontSize = 15 };
                _box = new GUIStyle(GUI.skin.box) { border = new RectOffset(2, 2, 2, 2) };
                _box.normal.background = Framed(new Color32(30, 31, 36, 255), new Color32(78, 80, 90, 255));
                _button = new GUIStyle(GUI.skin.button) { fontSize = 13, border = new RectOffset(2, 2, 2, 2) };
                _button.normal.background = Framed(new Color32(52, 54, 62, 255), new Color32(90, 93, 104, 255));
                _button.hover.background = Framed(new Color32(70, 73, 84, 255), new Color32(220, 220, 225, 255));
                _button.active.background = Framed(new Color32(40, 41, 47, 255), new Color32(220, 220, 225, 255));
                _button.normal.textColor = _button.hover.textColor = _button.active.textColor = text;
            }
        }

        // Textura 8x8 com 2px de borda, esticada pelo GUIStyle.border
        internal static Texture2D Framed(Color32 fill, Color32 edge)
        {
            var tex = new Texture2D(8, 8, TextureFormat.RGBA32, false);
            var px = new Color32[64];
            for (int i = 0; i < 64; i++)
            {
                int x = i % 8, y = i / 8;
                px[i] = (x < 2 || y < 2 || x > 5 || y > 5) ? edge : fill;
            }
            tex.SetPixels32(px);
            tex.Apply();
            tex.hideFlags = HideFlags.HideAndDontSave;
            return tex;
        }
    }
}
