using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Toca sons "no mundo": so se o ponto estiver na tela, com volume pelo zoom
    // e panorama pela posicao horizontal, igual aos sons ambiente do jogo.
    internal class SoundPlayer : MonoBehaviour
    {
        private const int VOICES = 6;
        // Zoom do jogo (orthographicSize): 150 = mais perto possivel; jogando normal fica ~400-600.
        // Volume cheio ate FULL_ORTHO e cai ate MIN_ZOOM_GAIN em FAR_ORTHO.
        private const float FULL_ORTHO = 550f;
        private const float FAR_ORTHO = 1300f;
        private const float MIN_ZOOM_GAIN = 0.25f;

        public static SoundPlayer Instance;

        private AudioSource[] _voices;
        private int _next;
        private float _lastShutterTime;

        public static void Create(GameObject host)
        {
            Instance = host.AddComponent<SoundPlayer>();
        }

        private void Awake()
        {
            _voices = new AudioSource[VOICES];
            for (int i = 0; i < VOICES; i++)
            {
                _voices[i] = gameObject.AddComponent<AudioSource>();
                _voices[i].playOnAwake = false;
                _voices[i].spatialBlend = 0f;
            }
        }

        public void PlayShutter(Vector3 worldPos, bool closing)
        {
            // Muitas lojas fecham na mesma hora: no maximo uma porta a cada 0,2 s
            if (Time.unscaledTime - _lastShutterTime < 0.2f)
            {
                return;
            }
            if (PlayAt(worldPos, closing ? UpwardAssets.ShutterClose : UpwardAssets.ShutterOpen, 1f))
            {
                _lastShutterTime = Time.unscaledTime;
            }
        }

        public bool PlayAt(Vector3 worldPos, AudioClip clip, float gain)
        {
            if (clip == null || !Plugin.SoundsEnabled.Value || GameMain.serv == null || GameMain.serv.camera == null)
            {
                LogOnce("sem-clip", "Som nao tocou: arquivo nao carregado ou sons desligados");
                return false;
            }
            Camera cam = GameMain.serv.camera.main;
            if (cam == null)
            {
                return false;
            }
            Vector3 vp = cam.WorldToViewportPoint(worldPos);
            if (vp.x < -0.05f || vp.x > 1.05f || vp.y < -0.05f || vp.y > 1.05f)
            {
                return false;
            }
            float zoom = Mathf.Lerp(1f, MIN_ZOOM_GAIN, Mathf.InverseLerp(FULL_ORTHO, FAR_ORTHO, cam.orthographicSize));
            float sfx = GameSfxVolume();
            float volume = zoom * gain * Plugin.SoundsVolume.Value * sfx;
            if (volume <= 0.01f)
            {
                LogOnce("mudo", "Som nao tocou: volume zero (zoom " + cam.orthographicSize.ToString("0")
                    + ", efeitos do jogo " + sfx.ToString("0.00") + ", config " + Plugin.SoundsVolume.Value + ")");
                return false;
            }
            LogOnce("tocou-" + clip.name, "Tocando " + clip.name + " (zoom " + cam.orthographicSize.ToString("0")
                + ", volume " + volume.ToString("0.00") + ")");

            AudioSource voice = _voices[_next];
            _next = (_next + 1) % VOICES;
            voice.panStereo = Mathf.Clamp((vp.x - 0.5f) * 1.2f, -0.8f, 0.8f);
            voice.pitch = Random.Range(0.95f, 1.05f);
            voice.PlayOneShot(clip, volume);
            return true;
        }

        // Diagnostico: cada situacao aparece no log uma vez so por sessao
        private readonly System.Collections.Generic.HashSet<string> _logged = new System.Collections.Generic.HashSet<string>();

        private void LogOnce(string key, string message)
        {
            if (_logged.Add(key))
            {
                Plugin.Log.LogInfo(message);
            }
        }

        private static float GameSfxVolume()
        {
            try
            {
                return GameMain.serv.saveload.player.prefs.game.sfx;
            }
            catch
            {
                return 1f;
            }
        }
    }
}
