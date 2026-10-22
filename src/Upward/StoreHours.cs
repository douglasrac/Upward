using System.Collections.Generic;
using Game.Session.Board;
using Game.Session.Entities;
using Game.Session.Entities.Config;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Mostra a arte de "fechado" nas lojas fora do horario (workhours do jogo).
    // O jogo ja impede clientes fora do horario; aqui so trocamos o visual e tocamos o som.
    internal class StoreHours
    {
        private enum Look
        {
            None,
            Shutter,   // lojas, restaurantes, servicos: porta de aco + placa + luz apagada
            LightsOff, // escritorios: so apaga as luzes
            Image,     // loja com imagem propria em textures/closed/<template>.png: aparece aos poucos
            Tint,      // terracos na cobertura: escurece o proprio desenho (tem partes transparentes,
                       // entao nada pode ser posto por cima sem tampar o ceu)
        }

        // Cor multiplicada no desenho do terraco fechado: luz apagada, puxando para o azul da noite
        private static readonly Color TINT_NIGHT = new Color(0.32f, 0.36f, 0.5f, 1f);

        private class Closable
        {
            public Entity entity;
            public Look look;
            public GameObject root;
            public Transform cover;
            public Mesh coverMesh;
            public GameObject sign;
            public float width;
            public float height;
            public bool closed;
            public float progress; // 0 = aberta, 1 = totalmente fechada
            public float lastLitSim = float.MinValue; // apartamentos: ultimo momento com morador acordado em casa
        }

        private const float SCAN_INTERVAL = 0.25f;
        private const float COVER_DEPTH = 25f; // entre a decoracao (30) e as pessoas andando (20)
        private const float SIGN_DEPTH = 24f;

        private readonly Dictionary<int, Closable> _items = new Dictionary<int, Closable>();
        private readonly List<int> _stale = new List<int>();
        private readonly HashSet<int> _seen = new HashSet<int>();
        private float _nextScan;
        private int _loggedTotal = -1, _loggedClosed = -1;
        private Material _shutterMat, _signMat, _lightsMat;
        private readonly Dictionary<string, Material> _imageMats = new Dictionary<string, Material>();

        public void Update()
        {
            // No menu e durante o carregamento do save a lista de entidades ainda nao existe
            var ctx = GameMain.ctx;
            // (ctx.loading nao serve: fica true a partida inteira quando ela veio de um save)
            if (ctx == null || !ctx.Initialized || ctx.entityman == null || !ctx.entityman.initialized
                || ctx.clock == null || !ctx.clock.initialized)
            {
                Clear();
                return;
            }
            if (Time.unscaledTime >= _nextScan)
            {
                _nextScan = Time.unscaledTime + SCAN_INTERVAL;
                Scan();
            }
            Animate();
        }

        // Unidades com alguem acordado dentro: pessoa visivel cuja tarefa atual tem a unidade como
        // alvo (morador em casa, faz-tudo consertando, camareira...) e que ja esta pisando numa casa
        // dessa unidade. Quem so passa pelo corredor tem outro alvo. Montado uma vez por varredura.
        private static readonly HashSet<int> _occupiedUnits = new HashSet<int>();
        private const string SLEEP_SCRIPT = "script-rest-at-home";

        private static void CollectAwakePeople()
        {
            _occupiedUnits.Clear();
            var grid = GameMain.ctx.board.grid;
            foreach (Entity p in GameMain.ctx.entityman.GetAllEntities())
            {
                if (p == null || !p.attached || p.components == null || p.components.peep == null
                    || p.components.script == null || p.components.sprite == null || !p.components.sprite.IsVisible)
                {
                    continue;
                }
                var queue = p.components.script.queue;
                if (queue == null || queue.context == null || queue.context.targetid == 0)
                {
                    continue;
                }
                // Dormindo (ou indo para a cama): a pessoa vira a arte da cama, mas a luz deve apagar
                if (queue.Head != null && queue.Head.Name == SLEEP_SCRIPT)
                {
                    continue;
                }
                Entity standingOn = grid.FindEntityOrNull(p.data.placement.gridpos);
                if (standingOn != null && standingOn.id == queue.context.targetid)
                {
                    _occupiedUnits.Add(standingOn.id);
                }
            }
        }

        private void Scan()
        {
            _seen.Clear();
            CollectAwakePeople();
            foreach (Entity e in GameMain.ctx.entityman.GetAllEntities())
            {
                // So unidades (lojas, escritorios, apartamentos, quartos); pula pessoas e o resto
                if (e == null || !e.initialized || !e.attached || e.components == null || e.components.unit == null)
                {
                    continue;
                }
                Look look = ChooseLook(e);
                if (look == Look.None)
                {
                    continue;
                }
                _seen.Add(e.id);

                Closable item;
                bool fresh = false;
                if (!_items.TryGetValue(e.id, out item) || item.entity != e || item.root == null || item.look != look)
                {
                    if (item != null)
                    {
                        Destroy(item);
                    }
                    item = Build(e, look);
                    _items[e.id] = item;
                    fresh = true;
                }

                bool closed = ShouldBeClosed(e, item);
                if (fresh)
                {
                    // Ao carregar o save, ja aparece no estado certo, sem animacao nem som
                    item.closed = closed;
                    item.progress = closed ? 1f : 0f;
                    Apply(item);
                }
                else if (closed != item.closed)
                {
                    item.closed = closed;
                    // Som da porta de aco em toda loja/restaurante, com ou sem arte propria
                    if ((look == Look.Shutter || look == Look.Image || look == Look.Tint) && SoundPlayer.Instance != null)
                    {
                        SoundPlayer.Instance.PlayShutter(Center(item), closed);
                    }
                }
                else if (look == Look.Tint && item.progress > 0f)
                {
                    // O jogo recria as pecas do desenho as vezes (com a cor normal): reaplica o escuro
                    Apply(item);
                }

                bool visible = e.components.sprite.IsVisible;
                if (item.root.activeSelf != (visible && item.progress > 0f))
                {
                    item.root.SetActive(visible && item.progress > 0f);
                }
            }

            _stale.Clear();
            foreach (KeyValuePair<int, Closable> pair in _items)
            {
                if (!_seen.Contains(pair.Key))
                {
                    _stale.Add(pair.Key);
                }
            }
            foreach (int id in _stale)
            {
                Destroy(_items[id]);
                _items.Remove(id);
            }

            int closedCount = 0;
            foreach (Closable item in _items.Values)
            {
                if (item.closed)
                {
                    closedCount++;
                }
            }
            if (_items.Count != _loggedTotal || closedCount != _loggedClosed)
            {
                _loggedTotal = _items.Count;
                _loggedClosed = closedCount;
                Plugin.Log.LogInfo("Lojas/escritorios/apartamentos/quartos controlados: " + _loggedTotal + ", apagados agora: " + _loggedClosed
                    + " (hora do jogo " + GameMain.ctx.clock.currentHourOfDayF.ToString("0.0") + ")");
            }
        }

        private static Look ChooseLook(Entity e)
        {
            var c = e.components;
            if (c.unit == null || c.sprite == null || c.placement == null)
            {
                return Look.None;
            }
            if (c.hotelroom != null)
            {
                return Plugin.HotelVacantLightsOff.Value ? Look.LightsOff : Look.None;
            }
            if (c.residence != null)
            {
                return Plugin.ApartmentsLightsOff.Value ? Look.LightsOff : Look.None;
            }
            if (c.workplace == null || !e.config.workplace.workhours.initialized)
            {
                return Look.None;
            }
            if (DescendsFrom(e.config, "restaurant-roof-base"))
            {
                return Plugin.ShopsClose.Value ? Look.Tint : Look.None;
            }
            if (Plugin.ShopsClose.Value && UpwardAssets.GetClosedImage(e.config.template) != null)
            {
                return Look.Image;
            }
            if (c.office != null)
            {
                return Plugin.OfficesLightsOff.Value ? Look.LightsOff : Look.None;
            }
            if (c.eventspace != null)
            {
                return Look.None;
            }
            // Porta de aco so para loja/restaurante sem arte propria (ex.: de um mod);
            // servicos, estandes, galeria, spa etc. so apagam a luz
            // Lojas herdam de retail-base e restaurantes de restaurant-base, inclusive os de mods
            if (DescendsFrom(e.config, "retail-base") || DescendsFrom(e.config, "restaurant-base"))
            {
                return Plugin.ShopsClose.Value ? Look.Shutter : Look.None;
            }
            return Plugin.ServicesLightsOff.Value ? Look.LightsOff : Look.None;
        }

        private static readonly Dictionary<string, bool> _descends = new Dictionary<string, bool>();

        // Sobe a cadeia de heranca do tipo (parent, parent do parent...) procurando baseName
        private static bool DescendsFrom(EntityTemplate config, string baseName)
        {
            string key = config.template + "|" + baseName;
            bool result;
            if (_descends.TryGetValue(key, out result))
            {
                return result;
            }
            EntityTemplate t = config;
            for (int depth = 0; t != null && t.ident != null && depth < 30; depth++)
            {
                if (t.ident.template == baseName)
                {
                    result = true;
                    break;
                }
                t = t.ident.parent != null ? GameMain.ctx.entityman.FindTemplate(t.ident.parent) : null;
            }
            _descends[key] = result;
            return result;
        }

        private static bool ShouldBeClosed(Entity e, Closable item)
        {
            var c = e.components;
            if (c.placement.NeedsToBeBuilt() || c.placement.IsBroken)
            {
                return false;
            }
            if (c.hotelroom != null)
            {
                // Quarto "alugado" = tem hospedes reservados; sem reserva fica escuro,
                // a nao ser que alguem esteja trabalhando la dentro (camareira, manutencao)
                var hotel = GameMain.ctx.sim?.hotel;
                var entry = hotel?.data?.FindEntryForRoom(e);
                bool rented = entry != null && entry.hasReservation;
                return !rented && !SomeoneAwakeInside(e, item);
            }
            if (c.residence != null)
            {
                if (!Plugin.ApartmentsFollowResidents.Value)
                {
                    var night = new DailyInterval { from = Plugin.ApartmentsOffHour.Value, to = Plugin.ApartmentsOnHour.Value };
                    return night.InsideInterval(GameMain.ctx.clock.currentHourOfDayF);
                }
                float now = GameMain.ctx.clock.elapsedSimSeconds;
                if (SomeoneAwakeInside(e, item))
                {
                    item.lastLitSim = now;
                    return false;
                }
                // Espera alguns minutos do jogo antes de apagar: evita piscar quando o morador troca de tarefa
                float delay = Plugin.ApartmentsOffDelayMinutes.Value * Game.Session.Sim.GameClock.SIM_SECONDS_PER_CALENDAR_MINUTE;
                return now - item.lastLitSim >= delay;
            }
            return !c.workplace.IsDuringBusinessHoursNow();
        }

        // Vale para moradores e prestadores de servico (veja CollectAwakePeople). Nao usamos a
        // reserva de lugar: com varios moradores nem todos conseguem uma.
        private static bool SomeoneAwakeInside(Entity unit, Closable item)
        {
            return _occupiedUnits.Contains(unit.id);
        }

        private void Animate()
        {
            float step = Time.unscaledDeltaTime / Mathf.Max(0.05f, Plugin.ShutterSeconds.Value);
            float apartmentStep = Time.unscaledDeltaTime / Mathf.Max(0.01f, Plugin.ApartmentsFadeSeconds.Value);
            foreach (Closable item in _items.Values)
            {
                float target = item.closed ? 1f : 0f;
                if (item.progress == target || item.root == null)
                {
                    continue;
                }
                bool apartment = item.entity.components != null && item.entity.components.residence != null;
                item.progress = Mathf.MoveTowards(item.progress, target, apartment ? apartmentStep : step);
                Apply(item);
            }
        }

        private void Apply(Closable item)
        {
            float p = item.progress;
            bool visible = item.entity.components.sprite != null && item.entity.components.sprite.IsVisible;
            item.root.SetActive(visible && p > 0f);
            if (item.look == Look.Tint)
            {
                var sprite = item.entity.components.sprite;
                if (p <= 0f)
                {
                    sprite.ClearColor();
                }
                else
                {
                    sprite.SetColor(Color.Lerp(Color.white, TINT_NIGHT, p));
                }
                return;
            }
            if (p <= 0f)
            {
                return;
            }

            if (item.look == Look.Shutter)
            {
                // A porta desce do teto: altura cresce ancorada em cima e mostra a parte de baixo
                // da textura (com a barra e o puxador), como uma porta de enrolar de verdade.
                float h = item.height * p;
                item.cover.localPosition = new Vector3(item.width / 2f, item.height - h / 2f, COVER_DEPTH);
                item.cover.localScale = new Vector3(item.width, h, 1f);
                float tilesX = Mathf.Max(1f, Mathf.Round(item.width / 100f));
                SetUVs(item.coverMesh, 0f, tilesX, 0f, p);
                item.sign.SetActive(p >= 1f);
            }
            else
            {
                item.cover.localPosition = new Vector3(item.width / 2f, item.height / 2f, COVER_DEPTH);
                item.cover.localScale = new Vector3(item.width, item.height, 1f);
                var fade = new Color(1f, 1f, 1f, p);
                item.coverMesh.colors = new[] { fade, fade, fade, fade };
            }
        }

        private Closable Build(Entity e, Look look)
        {
            EnsureMaterials();
            GridPos size = e.config.placement.size;
            var item = new Closable
            {
                entity = e,
                look = look,
                width = size.x * Grid.CELLSIZE.x,
                height = size.y * Grid.CELLSIZE.y,
            };

            item.root = new GameObject("UpwardClosed");
            item.root.transform.SetParent(e.components.sprite.transform, false);
            item.root.SetActive(false);
            if (look == Look.Tint)
            {
                return item; // nada por cima: so muda a cor do proprio desenho
            }

            Material coverMat = look == Look.Shutter ? _shutterMat
                : look == Look.Image ? ImageMaterial(e.config.template)
                : _lightsMat;
            item.coverMesh = MakeQuad();
            item.cover = MakeRenderer("cover", item.root.transform, item.coverMesh, coverMat).transform;

            if (look == Look.Shutter && UpwardAssets.Sign != null)
            {
                float sw = UpwardAssets.Sign.width;
                float sh = UpwardAssets.Sign.height;
                item.sign = MakeRenderer("sign", item.root.transform, MakeQuad(), _signMat);
                item.sign.transform.localScale = new Vector3(sw, sh, 1f);
                item.sign.transform.localPosition = new Vector3(item.width / 2f, item.height - 12f - sh / 2f, SIGN_DEPTH);
            }
            else
            {
                item.sign = new GameObject("sign");
                item.sign.transform.SetParent(item.root.transform, false);
            }
            return item;
        }

        private static Vector3 Center(Closable item)
        {
            return item.root.transform.parent.TransformPoint(new Vector3(item.width / 2f, item.height / 2f, 0f));
        }

        private void EnsureMaterials()
        {
            if (_shutterMat != null)
            {
                return;
            }
            Shader shader = Shader.Find("Sprites/Default");
            _shutterMat = new Material(shader) { mainTexture = UpwardAssets.Shutter, name = "UpwardShutter" };
            _signMat = new Material(shader) { mainTexture = UpwardAssets.Sign, name = "UpwardSign" };
            _lightsMat = new Material(shader) { mainTexture = UpwardAssets.LightsOff, name = "UpwardLightsOff" };
        }

        private Material ImageMaterial(string template)
        {
            Material mat;
            if (!_imageMats.TryGetValue(template, out mat))
            {
                mat = new Material(Shader.Find("Sprites/Default"))
                {
                    mainTexture = UpwardAssets.GetClosedImage(template),
                    name = "UpwardClosed_" + template,
                };
                _imageMats[template] = mat;
            }
            return mat;
        }

        private static GameObject MakeRenderer(string name, Transform parent, Mesh mesh, Material mat)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = mat;
            mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            mr.receiveShadows = false;
            return go;
        }

        private static Mesh MakeQuad()
        {
            var mesh = new Mesh();
            mesh.vertices = new[]
            {
                new Vector3(-0.5f, -0.5f, 0f), new Vector3(0.5f, -0.5f, 0f),
                new Vector3(-0.5f, 0.5f, 0f), new Vector3(0.5f, 0.5f, 0f),
            };
            mesh.triangles = new[] { 0, 2, 1, 2, 3, 1 };
            mesh.colors = new[] { Color.white, Color.white, Color.white, Color.white };
            SetUVs(mesh, 0f, 1f, 0f, 1f);
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void SetUVs(Mesh mesh, float u0, float u1, float v0, float v1)
        {
            mesh.uv = new[] { new Vector2(u0, v0), new Vector2(u1, v0), new Vector2(u0, v1), new Vector2(u1, v1) };
        }

        private static void Destroy(Closable item)
        {
            if (item.look == Look.Tint && item.entity != null && !item.entity.destroyed
                && item.entity.components != null && item.entity.components.sprite != null)
            {
                item.entity.components.sprite.ClearColor();
            }
            if (item.root != null)
            {
                Object.Destroy(item.root);
            }
        }

        private void Clear()
        {
            if (_items.Count == 0)
            {
                return;
            }
            foreach (Closable item in _items.Values)
            {
                Destroy(item);
            }
            _items.Clear();
        }
    }
}
