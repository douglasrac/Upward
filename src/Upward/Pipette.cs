using System;
using System.Collections.Generic;
using Assets.Code.Music;
using Game.Services;
using Game.Services.Input;
using Game.Services.Settings;
using Game.Session.Board;
using Game.Session.Entities;
using Game.Session.Entities.Config;
using Game.Session.Input;
using Game.UI.Session;
using Game.UI.Session.HUD;
using Game.Util;
using HarmonyLib;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Conta-gotas: em vez de procurar no menu de construcao, o jogador aponta para algo ja construido
    // e o jogo entra no modo de construir aquele mesmo item, como se o botao do menu fosse clicado.
    // O botao da barra ou a tecla (padrao V) arma a ferramenta e o proximo clique no predio escolhe.
    // Salas ocupadas viram o espaco vazio do mesmo tipo e tamanho.
    internal static class Pipette
    {
        internal static bool Armed { get; private set; }
        internal static HudButton Button;

        private static string _message = "";
        private static float _messageUntil;
        private static GUIStyle _style;

        // Template colocado -> botao do menu que o coloca (refeito quando as configuracoes mudam)
        private static UISettings _indexedFor;
        private static readonly Dictionary<string, UIBuildElementDef> _index = new Dictionary<string, UIBuildElementDef>();

        // Chave do estado do botao (BuildRibbonUtils e internal)
        private static readonly Func<UIBuildElementDef, string> GetLocString =
            AccessTools.MethodDelegate<Func<UIBuildElementDef, string>>(
                AccessTools.Method(AccessTools.TypeByName("Game.UI.Session.HUD.BuildRibbonUtils"), "GetLocString"));

        internal static void ToggleArmed()
        {
            SetArmed(!Armed);
            if (Armed)
            {
                // O clique tem que chegar ao modo padrao, nao a um modo de construcao aberto
                DefaultInputMode.Start();
            }
        }

        private static void SetArmed(bool armed)
        {
            Armed = armed;
            if (Button != null)
            {
                Button.ShowLit(armed);
            }
        }

        // Clique com a ferramenta armada (vem do modo padrao)
        internal static void OnClick(Vector2 scrpos)
        {
            if (Pick(scrpos))
            {
                SetArmed(false);
            }
        }

        internal static void Update()
        {
            if (!Armed)
            {
                return;
            }
            // Esc, ou o jogador abriu outro modo pelo menu: desarma
            if (Input.GetKeyDown(KeyCode.Escape) || GameMain.serv == null || GameMain.serv.input == null
                || !DefaultInputMode.IsDefaultActive)
            {
                SetArmed(false);
            }
        }

        private static bool Pick(Vector2 scrpos)
        {
            var ctx = GameMain.ctx;
            if (ctx == null || !ctx.Initialized || ctx.board == null)
            {
                return false;
            }
            WorldPos world = GameMain.serv.camera.ScreenToWorldPos(scrpos);
            GridCell cell = ctx.board.grid.PickCellUnderCursor(world);
            if (cell == null || (!cell.hasUnit && !cell.hasFloor))
            {
                return Fail("Nothing here to copy");
            }

            if (!cell.hasUnit)
            {
                if (cell.hasLobby)
                {
                    return Fail("Lobbies can't be copied");
                }
                GameMain.serv.audio.PlayUISFX(UIEffectType.ButtonClick);
                GameMain.serv.input.Replace(new AddFloorInputMode());
                return true;
            }

            Entity entity = ctx.entityman.Find(cell.unitId);
            if (entity == null)
            {
                return Fail("Nothing here to copy");
            }
            EntityTemplate template = entity.config;
            string name = Loc.Get(template.unit != null ? template.unit.locname : template.template);

            UIBuildElementDef def = FindMenuButton(template);
            if (def != null)
            {
                // Mesma regra que deixa o botao cinza no menu (bloqueado ou sem lugar valido)
                BuildButtonState button;
                bool locked = BuildButtonState.allconfigs != null
                    && BuildButtonState.allconfigs.TryGetValue(GetLocString(def) ?? "", out button)
                    && button.RefreshState(def, false) == BuildButtonState.States.Disabled;
                if (locked || !def.visreqs.AllSatisfied())
                {
                    return Fail(name + " can't be built right now");
                }
                GameMain.serv.audio.PlayUISFX(def.sfx);
                Run(def);
                return true;
            }

            // Fora do menu: servicos (janela de servicos), maquinas de venda (popup proprio) e itens de mods
            foreach (ServicesDefinition services in GameMain.serv.globals.settings.economy.services)
            {
                foreach (ServicesDefinitionDetail service in services.entries)
                {
                    if (service.template == template.template)
                    {
                        if (!service.visreqs.AllSatisfied() || !service.reqs.AllSatisfied())
                        {
                            return Fail(name + " can't be built right now");
                        }
                        // O mesmo que clicar no servico na janela de servicos
                        GameMain.serv.audio.PlayUISFX(UIEffectType.ButtonClick);
                        ctx.sim.moveins.StartMovingInService(template);
                        return true;
                    }
                }
            }
            foreach (VendingDefinition vending in GameMain.serv.globals.settings.economy.vending)
            {
                if (vending.template == template.template)
                {
                    if (!vending.IsRunnable())
                    {
                        return Fail(name + " can't be built right now");
                    }
                    return Place(template.template);
                }
            }
            if (template.ident.IsModTemplate && template.unit != null)
            {
                return Place(template.template);
            }
            return Fail(name + " is not in the build menu");
        }

        private static bool Place(string template)
        {
            GameMain.serv.audio.PlayUISFX(UIEffectType.ButtonClick);
            GameMain.serv.input.Replace(new BuyEntityInputMode(template));
            return true;
        }

        // Faz o mesmo que o clique no botao do menu (BuildSubController.OnRibbonButtonClick)
        private static void Run(UIBuildElementDef def)
        {
            if (def.action == UIBuildElementAction.PlaceTemplate)
            {
                GameMain.serv.input.Replace(new BuyEntityInputMode(def.GetActionArg(0)));
            }
            else
            {
                BuildRibbonCallbacks.callbacks[def.GetActionArg(0)](def);
            }
        }

        private static UIBuildElementDef FindMenuButton(EntityTemplate template)
        {
            BuildIndex();
            UIBuildElementDef def;
            if (_index.TryGetValue(template.template, out def))
            {
                return def;
            }
            // Sala ocupada (escritorio, loja, apartamento, quarto mobiliado): o menu so tem o espaco vazio
            if (template.emptyspace == null && template.unit != null)
            {
                return FindEmptySpaceButton(template);
            }
            return null;
        }

        private static void BuildIndex()
        {
            UISettings ui = GameMain.serv.globals.settings.ui;
            if (_indexedFor == ui)
            {
                return;
            }
            _indexedFor = ui;
            _index.Clear();
            foreach (UIBuildGroup group in ui.mainribbon)
            {
                AddToIndex(group.group);
            }
            foreach (UIBuildCategory category in ui.subribbons)
            {
                foreach (UIBuildCategoryTab tab in category.tabs)
                {
                    AddToIndex(tab.elements);
                }
            }
            Plugin.Log.LogInfo("Conta-gotas: " + _index.Count + " itens do menu de construcao indexados");
        }

        private static void AddToIndex(List<UIBuildElementDef> defs)
        {
            if (defs == null)
            {
                return;
            }
            foreach (UIBuildElementDef def in defs)
            {
                if (def == null || !def.IsButton)
                {
                    continue;
                }
                string template = null;
                if (def.action == UIBuildElementAction.PlaceTemplate)
                {
                    template = def.GetActionArg(0);
                }
                else if (def.action == UIBuildElementAction.Callback)
                {
                    switch (def.GetActionArg(0))
                    {
                        case BuildRibbonCallbacks.BUYUTIL:
                            template = def.GetActionArg(2);
                            break;
                        case BuildRibbonCallbacks.BUILDELEVATOR:
                            template = def.GetActionArg(1);
                            break;
                    }
                }
                // O mesmo closet aparece em varias abas de utilidade; vale o primeiro
                if (template != null && !_index.ContainsKey(template))
                {
                    _index.Add(template, def);
                }
            }
        }

        // Acha o tipo de espaco vazio cujos anuncios trazem esse inquilino (mesma regra do jogo:
        // tags dos anuncios e mesmo tamanho) e o botao do menu desse espaco vazio
        private static UIBuildElementDef FindEmptySpaceButton(EntityTemplate tenant)
        {
            EntityManager entityman = GameMain.ctx.entityman;
            foreach (MoveInsDefinition moveins in GameMain.serv.globals.settings.economy.moveins)
            {
                if (!moveins.size.Equals(tenant.placement.size) || !Offers(moveins, tenant, entityman))
                {
                    continue;
                }
                foreach (KeyValuePair<string, UIBuildElementDef> pair in _index)
                {
                    EntityTemplate space = entityman.FindTemplate(pair.Key);
                    if (space != null && space.emptyspace != null && space.emptyspace.type == moveins.type
                        && space.placement.size.Equals(moveins.size))
                    {
                        return pair.Value;
                    }
                }
            }
            return null;
        }

        private static bool Offers(MoveInsDefinition moveins, EntityTemplate tenant, EntityManager entityman)
        {
            if (moveins.instant != null && HasTag(moveins.instant.tags, tenant, entityman))
            {
                return true;
            }
            if (moveins.entries != null)
            {
                foreach (MoveInsEntry entry in moveins.entries)
                {
                    if (HasTag(entry.tags, tenant, entityman))
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        private static bool HasTag(IEnumerable<string> tags, EntityTemplate tenant, EntityManager entityman)
        {
            if (tags == null)
            {
                return false;
            }
            foreach (string tag in tags)
            {
                HashSet<EntityTemplate> templates = entityman.GetCachedTemplatesByTagUnsafe(tag);
                if (templates != null && templates.Contains(tenant))
                {
                    return true;
                }
            }
            return false;
        }

        private static bool Fail(string text)
        {
            GameMain.serv.audio.PlayUISFX(UIEffectType.CantBuildHere);
            _message = text;
            _messageUntil = Time.unscaledTime + 2.5f;
            return false;
        }

        // Aviso perto do mouse: ferramenta armada, ou por que nao deu para copiar
        internal static void OnGUI()
        {
            bool showMessage = Time.unscaledTime < _messageUntil;
            if (!Armed && !showMessage)
            {
                return;
            }
            if (_style == null)
            {
                _style = new GUIStyle(GUI.skin.box) { fontSize = 13, wordWrap = false, border = new RectOffset(2, 2, 2, 2) };
                _style.normal.background = SoundproofPanel.Framed(new Color32(30, 31, 36, 235), new Color32(78, 80, 90, 255));
                _style.normal.textColor = new Color(0.93f, 0.93f, 0.95f);
                _style.padding = new RectOffset(8, 8, 4, 4);
            }
            string text = showMessage ? _message : "Pick something to build (Esc cancels)";
            var content = new GUIContent(text);
            Vector2 size = _style.CalcSize(content);
            Vector2 mouse = Event.current.mousePosition;
            GUI.Box(new Rect(mouse.x + 18f, mouse.y + 18f, size.x, size.y), content, _style);
        }
    }

    // Clique no modo padrao com a ferramenta armada: escolhe em vez de selecionar
    [HarmonyPatch(typeof(DefaultInputMode), "ProcessClickOnEntity")]
    internal static class PipetteClickPatch
    {
        private static bool Prefix(Vector2 pos)
        {
            if (!Pipette.Armed)
            {
                return true;
            }
            Pipette.OnClick(pos);
            return false;
        }
    }

    // A tecla entra na lista de atalhos do jogo, que ja fica muda quando ha texto sendo digitado
    [HarmonyPatch(typeof(KeyboardShortcutManager), nameof(KeyboardShortcutManager.Initialize))]
    internal static class PipetteKeyPatch
    {
        private static readonly AccessTools.FieldRef<KeyboardShortcutManager, List<KeyInput>> Inhibitable =
            AccessTools.FieldRefAccess<KeyboardShortcutManager, List<KeyInput>>("_inhibitable");

        private static void Prefix(KeyboardShortcutManager __instance)
        {
            List<KeyInput> keys = Inhibitable(__instance);
            if (Plugin.PipetteEnabled.Value && !keys.Exists(k => k.onSuccess == (Action)Pipette.ToggleArmed))
            {
                keys.Add(new KeyInput(Plugin.PipetteKey.Value, Pipette.ToggleArmed));
            }
        }
    }

    [HarmonyPatch(typeof(HUDLayers), "InitializeGameObject")]
    [HarmonyPriority(Priority.Low)]
    internal static class PipetteButtonPatch
    {
        internal const string TOOLTIP_KEY = "upward.pipette.tooltip";

        private static void Postfix(HUDLayers __instance)
        {
            Pipette.Button = Plugin.PipetteEnabled.Value
                ? HudButton.Create(__instance, "Pipette Button", "textures/pipette_icon.png", TOOLTIP_KEY, Pipette.ToggleArmed)
                : null;
        }
    }

    [HarmonyPatch(typeof(Loc), nameof(Loc.Get), new[] { typeof(string) })]
    internal static class PipetteTooltipPatch
    {
        private static bool Prefix(string key, ref string __result)
        {
            if (key != PipetteButtonPatch.TOOLTIP_KEY)
            {
                return true;
            }
            __result = "Pipette: click something already built to build more of it ("
                + Plugin.PipetteKey.Value + ")";
            return false;
        }
    }
}
