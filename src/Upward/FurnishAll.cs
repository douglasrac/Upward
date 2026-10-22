using System;
using System.Collections.Generic;
using Game.Services.Settings;
using Game.Session.Entities;
using Game.Session.Entities.Data;
using Game.Session.Sim;
using Game.UI.Session.MoveIns;
using HarmonyLib;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Mobiliar todos de uma vez: no "Pick furnishings" de quartos de hotel e apartamentos (os
    // vagos que mobiliam na hora), Shift+clique numa opcao mobilia tambem todos os outros espacos
    // vagos do mesmo tipo e tamanho no predio, cobrando cada um, ate o dinheiro acabar.
    internal static class FurnishAll
    {
        private static readonly AccessTools.FieldRef<MoveInTenantsDialog, bool> Instant =
            AccessTools.FieldRefAccess<MoveInTenantsDialog, bool>("_instant");

        private static readonly AccessTools.FieldRef<MoveInTenantsDialog, string> EntryId =
            AccessTools.FieldRefAccess<MoveInTenantsDialog, string>("_entryid");

        private static readonly Func<MoveInTenantsDialog, Entity> GetEntity =
            AccessTools.MethodDelegate<Func<MoveInTenantsDialog, Entity>>(
                AccessTools.Method(typeof(Game.UI.Session.InfoDialogs.EntityInfoDialog), "GetEntity"));

        // Gera candidatos novos (cada sala precisa da propria UnitInstanceData, o jogo guarda a referencia)
        private static readonly Action<MoveInsManager, MoveInsDefinition> RefreshInstantTenantList =
            AccessTools.MethodDelegate<Action<MoveInsManager, MoveInsDefinition>>(
                AccessTools.Method(typeof(MoveInsManager), "RefreshInstantTenantList"));

        private static bool ShiftHeld => Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);

        private static List<Entity> FindSameEmptySpaces(Entity original)
        {
            var list = new List<Entity>();
            if (original == null)
            {
                return list;
            }
            foreach (Entity e in GameMain.ctx.entityman.GetAllEntities())
            {
                if (e != original && e.initialized && e.components.emptyspace != null
                    && e.config.template == original.config.template)
                {
                    list.Add(e);
                }
            }
            return list;
        }

        // Chamado antes do clique original: guarda o que foi escolhido, porque a sala clicada some
        internal static State Before(MoveInTenantsDialog dialog, MoveInTenantsDialog.TenantEntryContext ctx)
        {
            if (!Plugin.FurnishAllEnabled.Value || !Instant(dialog) || !ShiftHeld || ctx.def == null)
            {
                return null;
            }
            Entity original = GetEntity(dialog);
            if (original == null || !GameMain.ctx.sim.moveins.CanMoveIn(ctx.unitdata, original))
            {
                return null;
            }
            return new State
            {
                def = ctx.def,
                entryid = EntryId(dialog),
                template = ctx.unitdata.template,
                others = FindSameEmptySpaces(original),
            };
        }

        internal static void After(State state)
        {
            if (state == null)
            {
                return;
            }
            MoveInsManager moveins = GameMain.ctx.sim.moveins;
            int done = 0;
            int skipped = 0;
            foreach (Entity space in state.others)
            {
                if (!space.initialized || space.components.emptyspace == null)
                {
                    continue;
                }
                RefreshInstantTenantList(moveins, state.def);
                UnitInstanceData unit = moveins.FindSavedStatus(state.entryid).candidates
                    .Find(c => c.template == state.template);
                if (unit == null || !moveins.CanMoveIn(unit, space))
                {
                    skipped++;
                    continue;
                }
                if (moveins.PerformMoveIn(state.def, state.entryid, unit, space) != null)
                {
                    done++;
                }
            }
            // Deixa a lista do dialogo como o jogo espera para a proxima sala vaga
            RefreshInstantTenantList(moveins, state.def);
            Plugin.Log.LogInfo("Mobiliar todos: " + state.template + " em mais " + done + " sala(s)"
                + (skipped > 0 ? ", " + skipped + " sem dinheiro ou requisito" : ""));
        }

        internal class State
        {
            public MoveInsDefinition def;
            public string entryid;
            public string template;
            public List<Entity> others;
        }
    }

    [HarmonyPatch(typeof(MoveInTenantsDialog), "OnEntryClick")]
    internal static class FurnishAllClickPatch
    {
        private static void Prefix(MoveInTenantsDialog __instance, MoveInTenantsDialog.TenantEntryContext ctx,
            out FurnishAll.State __state)
        {
            __state = FurnishAll.Before(__instance, ctx);
        }

        private static void Postfix(FurnishAll.State __state)
        {
            FurnishAll.After(__state);
        }
    }
}
