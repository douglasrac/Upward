using System.Collections.Generic;
using Game.Session.Entities.Config;
using Game.Systems.Requirements;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Deixa construir no subsolo o que o jogo so aceita acima do chao:
    // - Ice Cream Stand e Smoothie Bar (andar 0 a 5 -> qualquer subsolo ate o 5)
    // - Art Consultant, Art Dealer, Art Gallery e Art Museum (belowground #false -> #true)
    // - Obras de arte de dentro do predio: quadros, esculturas, murais e fontes internas (idem)
    // Muda os requisitos do template, entao a descricao da loja de construcao tambem mostra a regra nova.
    internal class UndergroundShops
    {
        private const float CHECK_INTERVAL = 1f;
        private const int LOWEST_FLOOR = -50;

        private static readonly HashSet<string> FLOOR_RANGE_TEMPLATES = new HashSet<string>
        {
            "restaurant-level-one-g", // Ice Cream Stand
            "restaurant-level-one-h", // Smoothie Bar
        };

        // Vale para o template e para todos que herdam dele (cada obra de arte tem a sua base)
        private static readonly HashSet<string> BELOWGROUND_TEMPLATES = new HashSet<string>
        {
            "consultant-aesthetics",
            "consultant-aesthetics-dealer",
            "consultant-aesthetics-gallery",
            "consultant-aesthetics-cp4",
            "painting-small-base",
            "sculpture-small-base",
            "painting-medium-base",
            "sculpture-medium-base",
            "painting-mural",
            "sculpture-large-inside",
            "fountain-indoor-base",
        };

        private float _nextCheck;
        private object _appliedForCtx;
        // Valor original de cada requisito alterado, para voltar ao jogo original se desligar a opcao
        private readonly Dictionary<FloorNumberRequirement, int> _originalFrom = new Dictionary<FloorNumberRequirement, int>();
        private readonly List<FloorRequirement> _changedFloorReqs = new List<FloorRequirement>();

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
            bool enabled = Plugin.ShopsUnderground.Value;
            if (enabled && _appliedForCtx != ctx)
            {
                Apply();
                _appliedForCtx = ctx;
            }
            else if (!enabled && (_originalFrom.Count > 0 || _changedFloorReqs.Count > 0))
            {
                Restore();
                _appliedForCtx = null;
            }
        }

        private void Apply()
        {
            foreach (string name in FLOOR_RANGE_TEMPLATES)
            {
                PlacementRequirements reqs = FindReqs(name);
                if (reqs == null)
                {
                    continue;
                }
                foreach (IPlacementRequirement req in reqs)
                {
                    var range = req as FloorNumberRequirement;
                    if (range != null && range.range.from >= 0 && !_originalFrom.ContainsKey(range))
                    {
                        _originalFrom[range] = range.range.from;
                        range.range.from = LOWEST_FLOOR;
                        Plugin.Log.LogInfo("Subsolo: " + name + " agora vai do andar " + LOWEST_FLOOR + " ao " + range.range.to);
                    }
                }
            }
            Dictionary<string, EntityTemplate> all = GameMain.ctx.entityman.GetAllTemplatesUnsafe();
            foreach (EntityTemplate tmpl in all.Values)
            {
                if (tmpl.placement == null || tmpl.placement.reqs == null || !InheritsBelowground(tmpl, all))
                {
                    continue;
                }
                foreach (IPlacementRequirement req in tmpl.placement.reqs)
                {
                    var floor = req as FloorRequirement;
                    if (floor != null && !floor.belowground && !_changedFloorReqs.Contains(floor))
                    {
                        floor.belowground = true;
                        _changedFloorReqs.Add(floor);
                        Plugin.Log.LogInfo("Subsolo: " + tmpl.template + " agora pode ficar no subsolo");
                    }
                }
            }
        }

        private static bool InheritsBelowground(EntityTemplate tmpl, Dictionary<string, EntityTemplate> all)
        {
            // Limite de passos so por seguranca contra um ciclo de parents
            for (int i = 0; i < 20 && tmpl != null; i++)
            {
                if (BELOWGROUND_TEMPLATES.Contains(tmpl.template))
                {
                    return true;
                }
                string parent = tmpl.ident.parent;
                if (parent == null || !all.TryGetValue(parent, out tmpl))
                {
                    return false;
                }
            }
            return false;
        }

        private static PlacementRequirements FindReqs(string name)
        {
            EntityTemplate tmpl = GameMain.ctx.entityman.FindTemplate(name);
            return tmpl == null || tmpl.placement == null ? null : tmpl.placement.reqs;
        }

        private void Restore()
        {
            foreach (KeyValuePair<FloorNumberRequirement, int> kv in _originalFrom)
            {
                kv.Key.range.from = kv.Value;
            }
            foreach (FloorRequirement floor in _changedFloorReqs)
            {
                floor.belowground = false;
            }
            _originalFrom.Clear();
            _changedFloorReqs.Clear();
            Plugin.Log.LogInfo("Subsolo: regras originais de andar restauradas");
        }
    }
}
