using System.Collections.Generic;
using System.Linq;
using System.Text;
using Game.Session.Assets;
using HarmonyLib;
using UnityEngine;

namespace Upward
{
    // Sons ambiente extras: cada emissor do jogo (ex.: AMB_DeliveryService) e um objeto em
    // "Audio/Effects". Arquivos .wav em sounds/emitters/<NomeDoEmissor>/ entram no sorteio dele.
    [HarmonyPatch(typeof(SfxManager), nameof(SfxManager.Initialize))]
    internal static class SfxManagerPatch
    {
        private static bool _listed;
        private static readonly Dictionary<string, List<AudioClip>> _cache = new Dictionary<string, List<AudioClip>>();

        private static void Postfix()
        {
            GameObject effects = GameObject.Find("Audio/Effects");
            if (effects == null)
            {
                return;
            }
            var names = new StringBuilder();
            foreach (Transform child in effects.transform)
            {
                names.Append(child.name).Append(' ');
                var randomizer = child.GetComponent<TenantRandomizer>();
                if (randomizer == null)
                {
                    continue;
                }
                // Carrega uma vez so: o SfxManager reinicia a cada partida carregada
                List<AudioClip> extra;
                if (!_cache.TryGetValue(child.name, out extra))
                {
                    extra = UpwardAssets.LoadWavFolder("sounds/emitters/" + child.name);
                    _cache[child.name] = extra;
                }
                if (extra.Count == 0 || randomizer.TenantClip1 == null)
                {
                    continue;
                }
                // Os 5 canais sorteiam de listas separadas; os novos sons entram em todas
                randomizer.TenantClip1 = Append(randomizer.TenantClip1, extra);
                randomizer.TenantClip2 = Append(randomizer.TenantClip2, extra);
                randomizer.TenantClip3 = Append(randomizer.TenantClip3, extra);
                randomizer.TenantClip4 = Append(randomizer.TenantClip4, extra);
                randomizer.TenantClip5 = Append(randomizer.TenantClip5, extra);
                Plugin.Log.LogInfo("Emissor " + child.name + ": +" + extra.Count + " sons");
            }
            if (!_listed)
            {
                _listed = true;
                Plugin.Log.LogInfo("Emissores de som disponiveis: " + names);
            }
        }

        private static AudioClip[] Append(AudioClip[] clips, List<AudioClip> extra)
        {
            if (clips == null || clips.Length == 0)
            {
                return clips;
            }
            return clips.Concat(extra.Where(c => !clips.Contains(c))).ToArray();
        }
    }
}
