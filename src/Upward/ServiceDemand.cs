using System.Collections.Generic;
using Game.Session.Entities;
using Game.Session.Entities.Config;
using Game.Session.Sim;
using HarmonyLib;

namespace Upward
{
    // Frequencia dos pedidos de servico (encanador, florista, TI, agua...). A cada sorteio a unidade
    // abre um pedido se rng <= probability; aqui devolvemos uma copia da lista needservices com a
    // probability multiplicada. So o UnitComponent le a probability, entao o resto do jogo (telas de
    // mudanca, relatorio da Ada) continua igual. Quartos de hotel ficam de fora: a camareira e quem
    // limpa o quarto.
    [HarmonyPatch(typeof(SupportTaskManager), nameof(SupportTaskManager.GetNeededServices))]
    internal static class ServiceDemandPatch
    {
        private static readonly Dictionary<List<ServiceRequestConfig>, List<ServiceRequestConfig>> _cache =
            new Dictionary<List<ServiceRequestConfig>, List<ServiceRequestConfig>>();
        private static float _cachedMultiplier = -1f;

        private static void Postfix(EntityTemplate config, ref List<ServiceRequestConfig> __result)
        {
            float multiplier = Plugin.ServiceDemandMultiplier.Value;
            if (__result == null || config.hotelroom != null || multiplier == 1f)
            {
                return;
            }
            if (multiplier != _cachedMultiplier)
            {
                _cache.Clear();
                _cachedMultiplier = multiplier;
                Plugin.Log.LogInfo("Servicos: frequencia dos pedidos x" + multiplier);
            }
            List<ServiceRequestConfig> scaled;
            if (!_cache.TryGetValue(__result, out scaled))
            {
                scaled = new List<ServiceRequestConfig>(__result.Count);
                foreach (ServiceRequestConfig req in __result)
                {
                    ServiceRequestConfig copy = req;
                    copy.probability = req.probability * multiplier;
                    scaled.Add(copy);
                }
                _cache[__result] = scaled;
            }
            __result = scaled;
        }
    }
}
