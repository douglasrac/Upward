using System;
using System.Collections;
using System.Collections.Generic;
using Assets.Code.Music;
using Game.Services;
using Game.Services.Filesystem;
using Game.Services.Input;
using Game.Session;
using Game.Session.Board;
using Game.Session.Input;
using Game.Session.Sim;
using Game.UI.Session;
using HarmonyLib;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Piso antirruido: o jogador paga por casa de piso, pintando com clique e arrasto como quando
    // constroi andares, e o mapa de ruido dessas casas fica sempre zerado. Como a casa zerada tambem
    // bloqueia o espalhamento, o ruido nao atravessa para os andares vizinhos naquele trecho.
    // Assim da para tratar so uma das torres do mapa. As casas compradas ficam no save.
    internal static class Soundproof
    {
        private const string SAVE_KEY_TILES = "upward_soundproof_tiles";
        private const string SAVE_KEY_FLOORS = "upward_soundproof"; // versao antiga: andares inteiros

        internal static readonly HashSet<GridPos> Tiles = new HashSet<GridPos>();

        // Andares inteiros vindos de save antigo: viram casas quando a grade ja existe
        private static readonly List<int> _pendingFloors = new List<int>();

        // ---- Regra ----

        // Zera as casas tratadas depois de cada atualizacao do mapa de ruido
        internal static void Apply(Heatmaps maps)
        {
            MigrateOldFloors();
            if (Tiles.Count == 0)
            {
                return;
            }
            var grid = GameMain.ctx.board.grid;
            float[] values = maps.GetHeatmap(HeatmapType.noiseHeatmap).data.values;
            foreach (GridPos pos in Tiles)
            {
                if (grid.IsGridPosValid(pos))
                {
                    values[grid.GridPosToGridIndex(pos)] = 0f;
                }
            }
        }

        internal static int CostPerTile
        {
            get { return Mathf.Max(1, Mathf.RoundToInt(Plugin.SoundproofCostPerCell.Value)); }
        }

        internal static void MigrateOldFloors()
        {
            if (_pendingFloors.Count == 0)
            {
                return;
            }
            var grid = GameMain.ctx.board.grid;
            foreach (int floor in _pendingFloors)
            {
                if (!grid.IsFloorValid(floor))
                {
                    continue;
                }
                for (int x = grid.mapleft; x < grid.mapright; x++)
                {
                    var pos = new GridPos(x, floor);
                    if (grid.FindGridCell(pos).hasFloor)
                    {
                        Tiles.Add(pos);
                    }
                }
            }
            Plugin.Log.LogInfo("Piso antirruido: " + _pendingFloors.Count + " andares do save antigo viraram "
                + Tiles.Count + " casas");
            _pendingFloors.Clear();
        }

        // ---- Save ----

        internal static void WriteTo(Hashtable data)
        {
            MigrateOldFloors();
            var list = new ArrayList();
            foreach (GridPos pos in Tiles)
            {
                list.Add(pos.x);
                list.Add(pos.y);
            }
            data[SAVE_KEY_TILES] = list;
        }

        internal static void ReadFrom(Hashtable data)
        {
            Tiles.Clear();
            _pendingFloors.Clear();
            if (data == null)
            {
                return;
            }
            var tiles = data.ContainsKey(SAVE_KEY_TILES) ? data[SAVE_KEY_TILES] as IList : null;
            if (tiles != null)
            {
                for (int i = 0; i + 1 < tiles.Count; i += 2)
                {
                    try { Tiles.Add(new GridPos(Convert.ToInt32(tiles[i]), Convert.ToInt32(tiles[i + 1]))); }
                    catch (Exception) { }
                }
                Plugin.Log.LogInfo("Piso antirruido: " + Tiles.Count + " casas carregadas do save");
                return;
            }
            var floors = data.ContainsKey(SAVE_KEY_FLOORS) ? data[SAVE_KEY_FLOORS] as IList : null;
            if (floors != null)
            {
                foreach (object o in floors)
                {
                    try { _pendingFloors.Add(Convert.ToInt32(o)); } catch (Exception) { }
                }
            }
        }
    }

    // Modo de pintura igual ao de construir andar (mesmo cursor, mesma caixa de informacao com
    // Cancelar, clique e arrasto casa a casa). Com Shift, o arrasto remove em vez de comprar.
    internal class SoundproofInputMode : AddFloorInputMode
    {
        private int _dragTiles;
        private int _dragSpent;

        internal static bool Active
        {
            get { return GameMain.serv != null && GameMain.serv.input != null && GameMain.serv.input.Peek() is SoundproofInputMode; }
        }

        private static bool Removing
        {
            get { return Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift); }
        }

        internal static void Toggle()
        {
            if (GameMain.ctx == null || !GameMain.ctx.Initialized || GameMain.serv == null || GameMain.serv.input == null)
            {
                return;
            }
            if (Active)
            {
                DefaultInputMode.Start();
            }
            else
            {
                GameMain.serv.audio.PlayUISFX(UIEffectType.ButtonClick);
                GameMain.serv.input.Replace(new SoundproofInputMode());
            }
        }

        public override void OnHandlerActivated()
        {
            base.OnHandlerActivated();
            Soundproof.MigrateOldFloors();
            SoundproofButtonPatch.ShowOpen(true);
        }

        public override void OnHandlerDeactivated()
        {
            SoundproofButtonPatch.ShowOpen(false);
            base.OnHandlerDeactivated();
        }

        // Sem substituicao especial: abrir o construir andar a partir daqui troca de modo normalmente
        public override ReplacementType GetReplacement()
        {
            return ReplacementType.None;
        }

        public override void GetInfoText(out string title, out string body, out bool delete)
        {
            title = "Soundproof floor";
            delete = Removing;
            if (delete)
            {
                body = "Drag over soundproof tiles to remove them (no refund).\n";
            }
            else
            {
                body = "Drag over floor tiles to soundproof them.\nCost: " + Loc.Money(CostPerTileMoney) + " per tile\n"
                    + "Hold Shift and drag to remove.\n";
            }
            if (_dragTiles > 0)
            {
                body += delete ? "Removed: " + _dragTiles + " tiles\n"
                    : "This drag: " + _dragTiles + " tiles, " + Loc.Money(_dragSpent) + "\n";
            }
            body += "Soundproof tiles: " + Soundproof.Tiles.Count + "\n";
        }

        private static Money CostPerTileMoney
        {
            get { return Soundproof.CostPerTile; }
        }

        protected override void DoMouseDown(Vector2 pos)
        {
            base.DoMouseDown(pos);
            _dragTiles = 0;
            _dragSpent = 0;
        }

        private GridPos CursorTile
        {
            get { return _cursor.data.placement.gridpos; }
        }

        protected override bool CanPaint()
        {
            GridCell cell = _grid.FindGridCellOrNull(CursorTile);
            if (cell == null || !cell.hasFloor)
            {
                return false;
            }
            bool owned = Soundproof.Tiles.Contains(CursorTile);
            return Removing ? owned : !owned;
        }

        protected override bool CanPay()
        {
            return Removing || GameMain.ctx.sim.player.CanSpend(-Soundproof.CostPerTile);
        }

        protected override void PayAndPaint()
        {
            GridPos pos = CursorTile;
            if (Removing)
            {
                Soundproof.Tiles.Remove(pos);
            }
            else
            {
                int cost = Soundproof.CostPerTile;
                GameMain.ctx.sim.player.DoAdd(-cost, Reason.OtherOneTimeExpense, (GridPosF)pos);
                Soundproof.Tiles.Add(pos);
                _dragSpent += cost;
                // Aplica ja, sem esperar o proximo ciclo do mapa de ruido
                Soundproof.Apply(GameMain.ctx.board.heatmaps);
            }
            _dragTiles++;
            PlayPaintSound(success: true);
            _lastPlacementPos = pos;
            _thisMovementSucceeded = true;
        }

        protected override void OnFailedPaint(bool dragging)
        {
            // Arrastando por cima de casas ja tratadas ou sem piso: silencioso, como no construir andar
            if (dragging || _thisMovementSucceeded)
            {
                return;
            }
            GridPos pos = CursorTile;
            if (_lastPlacementPos.HasValue && _lastPlacementPos.Value.Equals(pos))
            {
                return;
            }
            GridCell cell = _grid.FindGridCellOrNull(pos);
            if (cell == null || !cell.hasFloor)
            {
                TryShowMouseover("No floor here");
            }
            else if (Removing)
            {
                TryShowMouseover("This tile is not soundproof");
            }
            else if (Soundproof.Tiles.Contains(pos))
            {
                TryShowMouseover("Already soundproof");
            }
            else
            {
                TryShowMouseover("Not enough money\n" + Loc.Money(CostPerTileMoney));
            }
            GameMain.serv.audio.PlayUISFX(UIEffectType.CantBuildHere);
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
        // savefile e nulo em partida nova: comeca sem casas tratadas
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
                SoundproofInputMode.Toggle);
        }

        // Modo ativo: fica com a borda acesa
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
            __result = "Soundproof floor: click and drag to soundproof floor tiles, paying per tile ("
                + Plugin.SoundproofKey.Value + ")";
            return false;
        }
    }

    // Tecla (padrao F8) e o destaque azul das casas ja tratadas enquanto o modo esta ativo.
    // Framed tambem e usado pelos outros paineis do mod.
    internal class SoundproofPanel
    {
        private static readonly Color TILE_COLOR = new Color(0.2f, 0.55f, 1f, 0.3f);
        private readonly List<int> _row = new List<int>();

        public void OnGUI()
        {
            var ctx = GameMain.ctx;
            if (ctx == null || !ctx.Initialized || ctx.board == null || GameMain.serv == null || GameMain.serv.camera == null
                || !Plugin.SoundproofEnabled.Value)
            {
                return;
            }

            Event e = Event.current;
            if (e.type == EventType.KeyDown && e.keyCode == Plugin.SoundproofKey.Value)
            {
                SoundproofInputMode.Toggle();
                e.Use();
            }
            if (e.type == EventType.Repaint && SoundproofInputMode.Active)
            {
                DrawTiles();
            }
        }

        // Junta casas vizinhas do mesmo andar num retangulo so
        private void DrawTiles()
        {
            var byFloor = new Dictionary<int, List<int>>();
            foreach (GridPos pos in Soundproof.Tiles)
            {
                List<int> xs;
                if (!byFloor.TryGetValue(pos.y, out xs))
                {
                    xs = new List<int>();
                    byFloor[pos.y] = xs;
                }
                xs.Add(pos.x);
            }
            var old = GUI.color;
            GUI.color = TILE_COLOR;
            foreach (KeyValuePair<int, List<int>> floor in byFloor)
            {
                List<int> xs = floor.Value;
                xs.Sort();
                int start = xs[0], prev = xs[0];
                for (int i = 1; i <= xs.Count; i++)
                {
                    if (i < xs.Count && xs[i] == prev + 1)
                    {
                        prev = xs[i];
                        continue;
                    }
                    DrawRun(floor.Key, start, prev);
                    if (i < xs.Count)
                    {
                        start = prev = xs[i];
                    }
                }
            }
            GUI.color = old;
        }

        private static void DrawRun(int floor, int fromX, int toX)
        {
            var cam = GameMain.serv.camera;
            Vector2 a = cam.WorldToScreenPos(new WorldPos(fromX * Grid.CELLSIZE.x, floor * Grid.CELLSIZE.y));
            Vector2 b = cam.WorldToScreenPos(new WorldPos((toX + 1) * Grid.CELLSIZE.x, (floor + 1) * Grid.CELLSIZE.y));
            // Coordenada de tela do Unity tem origem embaixo; a do IMGUI, em cima
            var rect = Rect.MinMaxRect(a.x, Screen.height - b.y, b.x, Screen.height - a.y);
            if (rect.xMax < 0 || rect.xMin > Screen.width || rect.yMax < 0 || rect.yMin > Screen.height)
            {
                return;
            }
            GUI.DrawTexture(rect, Texture2D.whiteTexture);
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
