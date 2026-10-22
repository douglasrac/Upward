using System.Collections.Generic;
using Game.Session.Board;
using Game.Session.Entities.Config;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Aumenta a capacidade das ligacoes (medidores) de energia, agua, cabo, gas e telefone:
    // 10 -> 25, 50 -> 100, 150 -> 300. HVAC fica como no jogo.
    // Muda o valor base do config do template, entao vale para a simulacao, para a descricao da loja de
    // construcao e para medidores ja construidos em saves antigos. Os modificadores do jogo continuam.
    internal class UtilityCapacity
    {
        private const float CHECK_INTERVAL = 1f;

        private static readonly Dictionary<float, float> NEW_VALUES = new Dictionary<float, float>
        {
            { 10f, 25f },
            { 50f, 100f },
            { 150f, 300f },
        };

        private float _nextCheck;
        private object _appliedForCtx;
        // Valor original de cada ligacao alterada, para voltar ao jogo original se desligar a opcao
        private readonly Dictionary<UtilityProvidedPair, float> _originals = new Dictionary<UtilityProvidedPair, float>();

        public void Update()
        {
            if (Time.unscaledTime < _nextCheck)
            {
                return;
            }
            _nextCheck = Time.unscaledTime + CHECK_INTERVAL;

            var ctx = GameMain.ctx;
            if (ctx == null || ctx.entityman == null)
            {
                return;
            }
            bool enabled = Plugin.BiggerUtilityMeters.Value;
            if (enabled && _appliedForCtx != ctx)
            {
                Apply();
                _appliedForCtx = ctx;
            }
            else if (!enabled && _originals.Count > 0)
            {
                Restore();
                _appliedForCtx = null;
            }
        }

        private void Apply()
        {
            foreach (EntityTemplate tmpl in GameMain.ctx.entityman.FindTemplatesWithConfig<ClosetConfig>())
            {
                ClosetConfig closet = tmpl.closet;
                if (closet == null || !closet.IsMeter() || closet.provides == null)
                {
                    continue;
                }
                foreach (UtilityProvidedPair pair in closet.provides)
                {
                    if (pair.type == RangeType.UtilHVAC || pair.provides == null || _originals.ContainsKey(pair))
                    {
                        continue;
                    }
                    float newValue;
                    if (NEW_VALUES.TryGetValue(pair.provides.value, out newValue))
                    {
                        _originals[pair] = pair.provides.value;
                        pair.provides.value = newValue;
                        Plugin.Log.LogInfo("Utilidades: " + tmpl.template + " (" + pair.type + ") "
                            + _originals[pair] + " -> " + newValue);
                    }
                }
            }
        }

        private void Restore()
        {
            foreach (KeyValuePair<UtilityProvidedPair, float> kv in _originals)
            {
                kv.Key.provides.value = kv.Value;
            }
            _originals.Clear();
            Plugin.Log.LogInfo("Utilidades: capacidade original dos medidores restaurada");
        }
    }
}
