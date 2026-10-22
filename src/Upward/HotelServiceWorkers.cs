using System;
using System.Collections.Generic;
using Game.Session.Entities.Config;
using Game.Session.Sim;
using HarmonyLib;
using GameMain = Game.Game;

namespace Upward
{
    // Mais funcionarios nos servicos de hotel (camareira, room service, carregador de malas). A demanda
    // deles depende dos quartos ocupados, entao em vez de cortar pedidos aumentamos a equipe.
    // O WorkplaceComponent compara o total com GetWorkerCount() a cada segundo e contrata/demite sozinho,
    // entao a mudanca vale tambem para servicos ja construidos em saves antigos.
    [HarmonyPatch(typeof(WorkplaceConfig), nameof(WorkplaceConfig.GetWorkerCount))]
    internal static class HotelServiceWorkersPatch
    {
        private static readonly SupportTaskType[] HOTEL_TASKS =
        {
            SupportTaskType.ServiceHotelHousekeeping,
            SupportTaskType.ServiceHotelRoomService,
            SupportTaskType.ServiceHotelLuggage,
        };

        // WorkplaceConfig dos servicos de hotel, montado uma vez por partida (GetWorkerCount roda a cada
        // segundo para cada unidade com funcionarios, entao a busca aqui tem que ser so um lookup)
        private static readonly HashSet<WorkplaceConfig> _hotelServices = new HashSet<WorkplaceConfig>();
        private static object _builtForCtx;

        private static void Postfix(WorkplaceConfig __instance, ref uint __result)
        {
            float multiplier = Plugin.HotelServiceWorkersMultiplier.Value;
            if (multiplier == 1f || __result == 0)
            {
                return;
            }
            if (_builtForCtx != GameMain.ctx && !Rebuild())
            {
                return;
            }
            if (_hotelServices.Contains(__instance))
            {
                __result = (uint)Math.Max(1, Math.Ceiling(__result * multiplier));
            }
        }

        private static bool Rebuild()
        {
            var ctx = GameMain.ctx;
            if (ctx == null || ctx.entityman == null || ctx.sim == null || ctx.sim.support == null)
            {
                return false;
            }
            _hotelServices.Clear();
            _builtForCtx = ctx;
            foreach (EntityTemplate tmpl in ctx.entityman.FindTemplatesWithConfig<ServiceConfig>())
            {
                if (tmpl.workplace == null)
                {
                    continue;
                }
                List<SupportTaskType> tasks = ctx.sim.support.FindAllProvidedSupportTasksUnsafe(tmpl);
                if (tasks != null && tasks.Exists(t => Array.IndexOf(HOTEL_TASKS, t) >= 0))
                {
                    _hotelServices.Add(tmpl.workplace);
                    Plugin.Log.LogInfo("Hotel: " + tmpl.template + " tem " + tmpl.workplace.workers
                        + " funcionarios no jogo, x" + Plugin.HotelServiceWorkersMultiplier.Value);
                }
            }
            return true;
        }
    }
}
