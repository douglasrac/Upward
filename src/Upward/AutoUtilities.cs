using System;
using System.Collections.Generic;
using Game.Session.Board;
using Game.Session.Entities;
using Game.Session.Entities.Config;
using Game.Session.Sim;
using Game.Systems.Events;
using HarmonyLib;
using GameMain = Game.Game;

namespace Upward
{
    // Linhas automaticas: um closet eletrico ou hidraulico pronto ja leva as linhas dele (energia,
    // telefone, TV a cabo / agua, gas, HVAC) para todo o trecho de piso do andar, de graca. So o
    // closet e cobrado. Piso novo construido depois num andar com closet tambem ganha as linhas.
    internal static class AutoUtilities
    {
        private const int PIPE_FLOOR = -1; // InfrastructureManager.PIPE_FLOOR: andar da rua, sempre ligado

        private static readonly Action<InfrastructureManager, RangeType, GridPos, bool> UpdateClosetOnPipeChange =
            AccessTools.MethodDelegate<Action<InfrastructureManager, RangeType, GridPos, bool>>(
                AccessTools.Method(typeof(InfrastructureManager), "UpdateClosetOnPipeChange",
                    new[] { typeof(RangeType), typeof(GridPos), typeof(bool) }));

        private static readonly Action<InfrastructureManager, RangeType> UpdateActivation =
            AccessTools.MethodDelegate<Action<InfrastructureManager, RangeType>>(
                AccessTools.Method(typeof(InfrastructureManager), "UpdateActivation"));

        private static readonly AccessTools.FieldRef<InfrastructureManager, bool> NeedToRecomputeClaims =
            AccessTools.FieldRefAccess<InfrastructureManager, bool>("_needToRecomputeUtilityClaims");

        // Closets comuns (nao medidores nem o compressor), ja construidos
        private static bool IsAutoCloset(Entity e)
        {
            return e != null && e.components.closet != null && e.config.closet.type == ClosetType.Closet
                && e.config.closet.provides != null && !e.components.placement.NeedsToBeBuilt();
        }

        // HVAC so existe depois do compressor, que cria a linha de HVAC no andar da rua
        private static bool HvacAvailable()
        {
            return GameMain.ctx.board.ranges.GetFloor(PIPE_FLOOR).GetRangesUnsafe(RangeType.UtilHVAC).Count > 0;
        }

        private static void AddClosetTypes(Entity closet, HashSet<RangeType> types, bool hvac)
        {
            foreach (UtilityProvidedPair provide in closet.config.closet.provides)
            {
                if (provide.type != RangeType.UtilHVAC || hvac)
                {
                    types.Add(provide.type);
                }
            }
        }

        private static bool HasFloor(int x, int y)
        {
            GridCell cell = GameMain.ctx.board.grid.FindGridCellOrNull(new GridPos(x, y));
            return cell != null && cell.hasFloor;
        }

        private static int SegmentLeft(int x, int y)
        {
            while (HasFloor(x - 1, y))
            {
                x--;
            }
            return x;
        }

        // Poe a linha em toda casa de piso continua do trecho que comeca em x (sem cobrar)
        private static bool FillSegment(RangeType type, int left, int y)
        {
            var infra = GameMain.ctx.sim.infra;
            var ranges = GameMain.ctx.board.ranges;
            bool changed = false;
            for (int x = left; HasFloor(x, y); x++)
            {
                var pos = new GridPos(x, y);
                if (ranges.FindRangeThatContains(type, pos) == null)
                {
                    ranges.EnsureInARange(type, pos);
                    UpdateClosetOnPipeChange(infra, type, pos, true);
                    changed = true;
                }
            }
            return changed;
        }

        // Igual ao fim do DoPlacePipe do jogo, mas uma vez por tipo em vez de uma vez por casa
        private static void Apply(HashSet<RangeType> changed)
        {
            if (changed.Count == 0)
            {
                return;
            }
            var infra = GameMain.ctx.sim.infra;
            foreach (RangeType type in changed)
            {
                UpdateActivation(infra, type);
            }
            NeedToRecomputeClaims(infra) = true;
        }

        internal static void FillForCloset(Entity closet)
        {
            var types = new HashSet<RangeType>();
            AddClosetTypes(closet, types, HvacAvailable());
            GridPos pos = closet.data.placement.gridpos;
            int left = SegmentLeft(pos.x, pos.y);
            var changed = new HashSet<RangeType>();
            foreach (RangeType type in types)
            {
                if (FillSegment(type, left, pos.y))
                {
                    changed.Add(type);
                }
            }
            Apply(changed);
        }

        // Piso novo: se o trecho do andar onde ele entrou tem closet, as linhas do closet chegam ate ele
        internal static void FillAroundNewFloor(GridPos pos)
        {
            var grid = GameMain.ctx.board.grid;
            bool hvac = HvacAvailable();
            int left = SegmentLeft(pos.x, pos.y);
            var types = new HashSet<RangeType>();
            for (int x = left; HasFloor(x, pos.y); x++)
            {
                Entity e = grid.FindEntityOrNull(new GridPos(x, pos.y));
                if (IsAutoCloset(e))
                {
                    AddClosetTypes(e, types, hvac);
                }
            }
            var changed = new HashSet<RangeType>();
            foreach (RangeType type in types)
            {
                if (FillSegment(type, left, pos.y))
                {
                    changed.Add(type);
                }
            }
            Apply(changed);
        }

        // Completa todos os andares com closet (saves antigos, e o HVAC quando o compressor fica pronto)
        internal static void FillAll()
        {
            var grid = GameMain.ctx.board.grid;
            bool hvac = HvacAvailable();
            var changed = new HashSet<RangeType>();
            int closets = 0;
            for (int y = grid.mapbottom; y < grid.maptop; y++)
            {
                for (int x = grid.mapleft; x < grid.mapright; x++)
                {
                    var pos = new GridPos(x, y);
                    Entity e = grid.FindEntityOrNull(pos);
                    if (!IsAutoCloset(e) || e.data.placement.gridpos != pos)
                    {
                        continue;
                    }
                    closets++;
                    var types = new HashSet<RangeType>();
                    AddClosetTypes(e, types, hvac);
                    int left = SegmentLeft(x, y);
                    foreach (RangeType type in types)
                    {
                        if (FillSegment(type, left, y))
                        {
                            changed.Add(type);
                        }
                    }
                }
            }
            Apply(changed);
            Plugin.Log.LogInfo("Linhas automaticas: " + closets + " closets verificados, tipos completados: "
                + string.Join(", ", new List<RangeType>(changed).ConvertAll(t => t.ToString()).ToArray()));
        }
    }

    // Closet (ou compressor) terminou de ser construido: o jogo ja ligou o closet, agora espalhamos as linhas
    [HarmonyPatch(typeof(InfrastructureManager), "OnAfterConstructionFinished")]
    internal static class ClosetFinishedPatch
    {
        private static void Postfix(GameEvent gev)
        {
            if (!Plugin.AutoUtilitiesEnabled.Value)
            {
                return;
            }
            Entity e = GameMain.ctx.entityman.Find(gev.eid);
            if (e == null || e.components.closet == null || e.config.closet.provides == null)
            {
                return;
            }
            if (e.config.closet.special == ClosetConfig.SpecialAction.Compressor)
            {
                AutoUtilities.FillAll();
            }
            else if (e.config.closet.type == ClosetType.Closet)
            {
                AutoUtilities.FillForCloset(e);
            }
        }
    }

    [HarmonyPatch(typeof(Grid), nameof(Grid.AddFloor))]
    internal static class AddFloorPatch
    {
        private static void Postfix(GridPos gridpos)
        {
            var infra = GameMain.ctx.sim?.infra;
            if (!Plugin.AutoUtilitiesEnabled.Value || infra == null || !infra.IsInfrastructureInitialized)
            {
                return;
            }
            AutoUtilities.FillAroundNewFloor(gridpos);
        }
    }

    [HarmonyPatch(typeof(InfrastructureManager), "OnLoadedGameStarted")]
    internal static class LoadedGamePatch
    {
        private static void Postfix()
        {
            if (Plugin.AutoUtilitiesEnabled.Value && Plugin.AutoUtilitiesOldSaves.Value)
            {
                AutoUtilities.FillAll();
            }
        }
    }
}
