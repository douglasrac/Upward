using System;
using System.Collections;
using System.Collections.Generic;
using Game.Services;
using Game.Services.Filesystem;
using Game.Services.Settings;
using Game.Session;
using Game.Session.Entities;
using Game.Session.Entities.Components;
using Game.Session.Sim;
using Game.UI.Popups;
using Game.UI.Session.Hotels;
using Game.UI.Session.HUD;
using HarmonyLib;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Booking automatico: o jogador marca quais salas de evento ficam no automatico e o preco do
    // ingresso de cada uma. Toda hora do jogo, sala marcada que ficou livre (limpa e sem evento)
    // recebe o artista/evento corporativo disponivel mais barato, como se fosse escolhido na mao
    // no Performer Booking. As salas marcadas ficam no save.
    internal static class AutoBooking
    {
        private const string SAVE_KEY = "upward_autobooking";
        internal const int DEFAULT_PERCENT = 100;

        // id da sala de evento -> preco do ingresso em % (0 a 200, igual ao slider do jogo)
        internal static readonly Dictionary<int, int> Rooms = new Dictionary<int, int>();

        // O mesmo que o botao de confirmar do jogo chama (e internal no jogo)
        private static readonly Action<EventSpaceManager, PerformerRecord, Entity, bool> Book =
            AccessTools.MethodDelegate<Action<EventSpaceManager, PerformerRecord, Entity, bool>>(
                AccessTools.Method(typeof(EventSpaceManager), "BookPerformerAndAssignToRoom"));

        internal static readonly AccessTools.FieldRef<BasePopup, GameObject> PopupGo =
            AccessTools.FieldRefAccess<BasePopup, GameObject>("_go");

        // ---- Regra ----

        internal static void TryBookAll()
        {
            if (!Plugin.AutoBookingEnabled.Value || Rooms.Count == 0)
            {
                return;
            }
            var eventspaces = GameMain.ctx.sim.eventspaces;
            var gone = new List<int>();
            foreach (KeyValuePair<int, int> kv in Rooms)
            {
                Entity room = GameMain.ctx.entityman.Find(kv.Key);
                if (room == null || room.components.eventspace == null)
                {
                    gone.Add(kv.Key);
                    continue;
                }
                if (!eventspaces.IsEventSpaceReadyToAssign(room))
                {
                    continue;
                }
                PerformerRecord rec = FindCandidate(room);
                if (rec == null)
                {
                    continue;
                }
                rec.ticketpricemultiplier = kv.Value / 100f;
                Book(eventspaces, rec, room, false);
                string text = "Auto booking: " + rec.name + " at " + RoomName(room)
                    + " (tickets " + kv.Value + "%)";
                GameMain.ctx.hud.tickers.Add(new TickerEntryText(text, 30f));
                Plugin.Log.LogInfo(text + ", custo " + rec.cashcost);
            }
            foreach (int id in gone)
            {
                Rooms.Remove(id);
            }
        }

        // O mais barato entre os que o jogo deixaria reservar na mao para esse tipo de sala
        internal static PerformerRecord FindCandidate(Entity room)
        {
            string template = room.config.template;
            PerformerRecord best = null;
            foreach (PerformerRecord rec in GameMain.ctx.sim.eventspaces.data.performers)
            {
                if (!rec.isWaiting || rec.def == null || !rec.def.eventspaces.Contains(template)
                    || rec.GetBookingState() != PerformerRecord.UIState.Available || !HasPerformerRoom(rec.def))
                {
                    continue;
                }
                if (best == null || Math.Abs(rec.cashcost) < Math.Abs(best.cashcost))
                {
                    best = rec;
                }
            }
            return best;
        }

        // O jogo so reserva o quarto de hotel do artista no dia do evento: se varios eventos caem no
        // mesmo dia, o segundo fica sem suite e e cancelado (sem devolver o dinheiro). Reservando
        // sozinho isso aconteceria muito, entao so marca se sobra suite preferida naquele dia.
        private static bool HasPerformerRoom(PerformerDef def)
        {
            int suites = 0;
            foreach (string template in def.roomtemplates)
            {
                HashSet<Entity> rooms = GameMain.ctx.entityman.GetCachedEntitiesByTemplateUnsafe(template);
                suites += rooms != null ? rooms.Count : 0;
            }
            int day = GameMain.ctx.clock.currentDayNumber + def.daysinadvance;
            int sameDay = 0;
            foreach (PerformerRecord other in GameMain.ctx.sim.eventspaces.data.performers)
            {
                if (other.isBooked && other.eventday == day && other.def != null
                    && Overlaps(other.def.roomtemplates, def.roomtemplates))
                {
                    sameDay++;
                }
            }
            return sameDay < suites;
        }

        private static bool Overlaps(List<string> a, List<string> b)
        {
            foreach (string s in a)
            {
                if (b.Contains(s))
                {
                    return true;
                }
            }
            return false;
        }

        // Primeiro tipo de evento que usa essa sala (cada sala de evento tem um so na pratica)
        internal static PerformerDef DefFor(Entity room)
        {
            foreach (PerformerDef def in GameMain.serv.globals.settings.hotels.eventperformers)
            {
                if (def.eventspaces.Contains(room.config.template))
                {
                    return def;
                }
            }
            return null;
        }

        internal static string RoomName(Entity room)
        {
            return room.components.unit.GetInstanceOrCategoryName() + " (floor " + room.data.placement.gridpos.y + ")";
        }

        // ---- Save ----

        // Lista plana: id, %, id, %... (o serializador do save ja aceita listas de inteiros)
        internal static void WriteTo(Hashtable data)
        {
            var list = new ArrayList();
            foreach (KeyValuePair<int, int> kv in Rooms)
            {
                list.Add(kv.Key);
                list.Add(kv.Value);
            }
            data[SAVE_KEY] = list;
        }

        internal static void ReadFrom(Hashtable data)
        {
            Rooms.Clear();
            var list = data != null && data.ContainsKey(SAVE_KEY) ? data[SAVE_KEY] as IList : null;
            if (list == null)
            {
                return;
            }
            for (int i = 0; i + 1 < list.Count; i += 2)
            {
                try { Rooms[Convert.ToInt32(list[i])] = Convert.ToInt32(list[i + 1]); } catch (Exception) { }
            }
            Plugin.Log.LogInfo("Booking automatico carregado do save: " + Rooms.Count + " sala(s)");
        }
    }

    // Logo depois da rotina de cada hora do jogo (que e quando a limpeza termina e a sala fica pronta)
    [HarmonyPatch(typeof(EventSpaceManager), "DoHourlyUpdate")]
    internal static class AutoBookingHourlyPatch
    {
        private static void Postfix()
        {
            AutoBooking.TryBookAll();
        }
    }

    [HarmonyPatch(typeof(SessionContext), nameof(SessionContext.CreateSaveFile))]
    internal static class AutoBookingSavePatch
    {
        private static void Postfix(SaveFile __result)
        {
            if (__result != null && __result.data != null)
            {
                AutoBooking.WriteTo(__result.data);
            }
        }
    }

    [HarmonyPatch(typeof(SessionContext), nameof(SessionContext.StartInitializeManagers))]
    internal static class AutoBookingLoadPatch
    {
        private static void Prefix(SaveFile savefile)
        {
            AutoBooking.ReadFrom(savefile != null ? savefile.data : null);
        }
    }

    // Sabe quando a lista do Performer Booking esta na frente, para mostrar o botao "Auto booking"
    [HarmonyPatch(typeof(BasePopup))]
    internal static class AutoBookingListPatch
    {
        internal static PerformerListPopup ListOnTop;

        [HarmonyPostfix, HarmonyPatch(nameof(BasePopup.OnActivated))]
        private static void Activated(BasePopup __instance)
        {
            ListOnTop = __instance as PerformerListPopup;
        }

        [HarmonyPostfix, HarmonyPatch(nameof(BasePopup.OnDeactivated))]
        private static void Deactivated(BasePopup __instance)
        {
            if (__instance == ListOnTop)
            {
                ListOnTop = null;
            }
        }

        [HarmonyPostfix, HarmonyPatch(nameof(BasePopup.OnPopped))]
        private static void Popped(BasePopup __instance)
        {
            if (__instance == ListOnTop)
            {
                ListOnTop = null;
            }
        }
    }

    // Painel (tecla configuravel, padrao F9, ou o botao "Auto booking" embaixo da lista do Performer
    // Booking): uma linha por sala de evento, com liga/desliga e o preco do ingresso.
    internal class AutoBookingPanel
    {
        private const float WIDTH = 440f;
        private const float ROW_H = 92f;

        private bool _open;
        private bool _toggleRequested;
        private Vector2 _scroll;
        private GUIStyle _label, _small, _title, _box, _button, _toggle;

        public void OnGUI()
        {
            var ctx = GameMain.ctx;
            if (ctx == null || !ctx.Initialized || ctx.sim == null || ctx.sim.eventspaces == null)
            {
                _open = false;
                _toggleRequested = false;
                return;
            }
            if (!Plugin.AutoBookingEnabled.Value)
            {
                return;
            }
            EnsureStyles();

            Event e = Event.current;
            if (e.type == EventType.KeyDown && e.keyCode == Plugin.AutoBookingKey.Value)
            {
                _toggleRequested = true;
                e.Use();
            }
            DrawListButton();
            if (_toggleRequested)
            {
                _toggleRequested = false;
                _open = !_open;
            }
            if (_open)
            {
                DrawWindow(ctx);
            }
        }

        // Botao logo abaixo do quadro da lista do Performer Booking: fecha a lista e abre o painel
        private void DrawListButton()
        {
            PerformerListPopup list = AutoBookingListPatch.ListOnTop;
            GameObject go = list != null ? AutoBooking.PopupGo(list) : null;
            if (go == null || _open)
            {
                return;
            }
            Transform panel = go.transform.Find("Panel");
            var rt = panel != null ? panel as RectTransform : null;
            if (rt == null)
            {
                return;
            }
            var corners = new Vector3[4];
            rt.GetWorldCorners(corners); // 0 = baixo-esquerda, 3 = baixo-direita
            var rect = new Rect(corners[3].x - 170f, Screen.height - corners[0].y + 6f, 170f, 30f);
            if (GUI.Button(rect, "Auto booking (" + Plugin.AutoBookingKey.Value + ")", _button))
            {
                list.Close();
                _toggleRequested = true;
            }
        }

        private void DrawWindow(SessionContext ctx)
        {
            List<Entity> rooms = AllEventSpaces(ctx);
            float listH = Mathf.Min(Mathf.Max(rooms.Count, 1) * ROW_H, Screen.height * 0.6f);
            var rect = new Rect((Screen.width - WIDTH) / 2f, 90f, WIDTH, listH + 150f);
            GuiInputBlock.Add(rect);
            GUI.Box(rect, GUIContent.none, _box);
            GUILayout.BeginArea(new Rect(rect.x + 12, rect.y + 10, rect.width - 24, rect.height - 20));

            GUILayout.Label("Auto booking", _title);
            GUILayout.Label("Checked event spaces book the cheapest available performer or corporate event "
                + "as soon as they are free, at the ticket price set here.", _small);

            _scroll = GUILayout.BeginScrollView(_scroll, GUILayout.Height(listH));
            if (rooms.Count == 0)
            {
                GUILayout.Label("No event spaces built yet.", _label);
            }
            foreach (Entity room in rooms)
            {
                DrawRoom(ctx, room);
            }
            GUILayout.EndScrollView();

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Book now", _button))
            {
                AutoBooking.TryBookAll();
            }
            if (GUILayout.Button("Close", _button))
            {
                _open = false;
            }
            GUILayout.EndHorizontal();
            GUILayout.EndArea();
        }

        private void DrawRoom(SessionContext ctx, Entity room)
        {
            int percent;
            bool on = AutoBooking.Rooms.TryGetValue(room.id, out percent);
            if (!on)
            {
                percent = AutoBooking.DEFAULT_PERCENT;
            }
            PerformerDef def = AutoBooking.DefFor(room);

            GUILayout.BeginVertical(GUILayout.Height(ROW_H - 6f));
            string kind = def == null ? "" : def.IsEntertainer() ? "  -  Entertainment" : "  -  Corporate";
            bool newOn = GUILayout.Toggle(on, " " + AutoBooking.RoomName(room) + kind, _toggle);
            GUILayout.Label(Status(ctx, room, newOn), _small);

            GUI.enabled = newOn;
            GUILayout.BeginHorizontal();
            GUILayout.Label("Tickets " + percent + "%", _label, GUILayout.Width(100));
            float slider = GUILayout.HorizontalSlider(percent, 0f, 200f, GUILayout.ExpandWidth(true));
            GUILayout.EndHorizontal();
            if (def != null)
            {
                float mult = percent / 100f;
                float conv = def.pricetopeepconversion.Eval(mult);
                GUILayout.Label("$" + Mathf.RoundToInt(def.ticketprice.Evaluate() * mult) + " per ticket, "
                    + Mathf.RoundToInt(def.minpeeps.Evaluate() * conv) + "-"
                    + Mathf.RoundToInt(def.maxpeeps.Evaluate() * conv) + " attendees", _small);
            }
            GUI.enabled = true;
            GUILayout.EndVertical();

            // Passos de 5%, como o jogo arredonda o slider dele na tela
            int newPercent = Mathf.Clamp(Mathf.RoundToInt(slider / 5f) * 5, 0, 200);
            if (newOn)
            {
                AutoBooking.Rooms[room.id] = newPercent;
                if (!on)
                {
                    AutoBooking.TryBookAll();
                }
            }
            else if (on)
            {
                AutoBooking.Rooms.Remove(room.id);
            }
        }

        private static string Status(SessionContext ctx, Entity room, bool auto)
        {
            PerformerRecord rec = ctx.sim.eventspaces.FindRecordForEventSpace(room);
            if (rec != null)
            {
                int days = Math.Max(0, rec.eventday - ctx.clock.currentDayNumber);
                return "Booked: " + rec.name + (days == 0 ? " (today)" : " (in " + days + " day" + (days > 1 ? "s" : "") + ")");
            }
            if (room.components.placement.NeedsToBeBuilt())
            {
                return "Under construction";
            }
            if (room.components.eventspace.GetCurrentState() != EventSpaceComponent.State.Ready)
            {
                return "Being cleaned and set up";
            }
            if (auto && AutoBooking.FindCandidate(room) == null)
            {
                return "Free - waiting for an available performer (money, requirements or hotel suite)";
            }
            return "Free";
        }

        private static List<Entity> AllEventSpaces(SessionContext ctx)
        {
            var list = new List<Entity>();
            foreach (int id in ctx.sim.eventspaces.GetAllEventSpacesUnsafe())
            {
                Entity e = ctx.entityman.Find(id);
                if (e != null && e.components.eventspace != null)
                {
                    list.Add(e);
                }
            }
            list.Sort((a, b) => a.data.placement.gridpos.y != b.data.placement.gridpos.y
                ? a.data.placement.gridpos.y - b.data.placement.gridpos.y
                : string.Compare(a.config.template, b.config.template, StringComparison.Ordinal));
            return list;
        }

        // Mesmo visual do painel de laje antirruido
        private void EnsureStyles()
        {
            if (_label != null)
            {
                return;
            }
            var text = new Color(0.93f, 0.93f, 0.95f);
            _label = new GUIStyle(GUI.skin.label) { wordWrap = true, fontSize = 13 };
            _label.normal.textColor = text;
            _small = new GUIStyle(_label) { fontSize = 12 };
            _small.normal.textColor = new Color(0.72f, 0.73f, 0.78f);
            _title = new GUIStyle(_label) { fontStyle = FontStyle.Bold, fontSize = 15 };
            _toggle = new GUIStyle(GUI.skin.toggle) { fontSize = 13, fontStyle = FontStyle.Bold };
            _toggle.normal.textColor = _toggle.hover.textColor = _toggle.onNormal.textColor = _toggle.onHover.textColor = text;
            _box = new GUIStyle(GUI.skin.box) { border = new RectOffset(2, 2, 2, 2) };
            _box.normal.background = SoundproofPanel.Framed(new Color32(30, 31, 36, 255), new Color32(78, 80, 90, 255));
            _button = new GUIStyle(GUI.skin.button) { fontSize = 13, border = new RectOffset(2, 2, 2, 2) };
            _button.normal.background = SoundproofPanel.Framed(new Color32(52, 54, 62, 255), new Color32(90, 93, 104, 255));
            _button.hover.background = SoundproofPanel.Framed(new Color32(70, 73, 84, 255), new Color32(220, 220, 225, 255));
            _button.active.background = SoundproofPanel.Framed(new Color32(40, 41, 47, 255), new Color32(220, 220, 225, 255));
            _button.normal.textColor = _button.hover.textColor = _button.active.textColor = text;
        }
    }
}
