using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Upward
{
    // Carrega as texturas (.png) e sons (.wav) da pasta assets do plugin.
    // Qualquer arquivo pode ser trocado por outro com o mesmo nome.
    internal static class UpwardAssets
    {
        public static Texture2D Shutter;
        public static Texture2D Sign;
        public static Texture2D LightsOff;

        public static AudioClip ShutterClose;
        public static AudioClip ShutterOpen;

        private static string _root;
        private static readonly Dictionary<string, Texture2D> _closedImages = new Dictionary<string, Texture2D>();

        // Imagem de "fechado" propria do tipo de loja: textures/closed/<template>.png (ou null)
        public static Texture2D GetClosedImage(string template)
        {
            Texture2D tex;
            if (!_closedImages.TryGetValue(template, out tex))
            {
                string relative = "textures/closed/" + template + ".png";
                tex = File.Exists(Path.Combine(_root, relative)) ? LoadTexture(relative, TextureWrapMode.Clamp) : null;
                _closedImages[template] = tex;
            }
            return tex;
        }

        public static void Load(string root)
        {
            _root = root;
            Shutter = LoadTexture("textures/closed_shutter.png", TextureWrapMode.Repeat);
            Sign = LoadTexture("textures/closed_sign.png", TextureWrapMode.Clamp);
            LightsOff = LoadTexture("textures/lights_off.png", TextureWrapMode.Clamp);

            ShutterClose = LoadWav("sounds/shutter_close.wav");
            ShutterOpen = LoadWav("sounds/shutter_open.wav");
        }

        public static Texture2D LoadTexture(string relative, TextureWrapMode wrap)
        {
            string path = Path.Combine(_root, relative);
            if (!File.Exists(path))
            {
                Plugin.Log.LogWarning("Textura nao encontrada: " + path);
                return null;
            }
            var tex = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            tex.LoadImage(File.ReadAllBytes(path));
            tex.wrapMode = wrap;
            tex.filterMode = FilterMode.Bilinear;
            tex.name = Path.GetFileNameWithoutExtension(path);
            return tex;
        }

        public static AudioClip LoadWav(string relative)
        {
            string path = Path.Combine(_root, relative);
            if (!File.Exists(path))
            {
                Plugin.Log.LogWarning("Som nao encontrado: " + path);
                return null;
            }
            try
            {
                return WavLoader.Load(path);
            }
            catch (Exception ex)
            {
                Plugin.Log.LogError("Falha ao ler " + path + ": " + ex.Message);
                return null;
            }
        }

        // Todos os .wav de uma pasta (usado para ampliar os sons ambiente das lojas)
        public static List<AudioClip> LoadWavFolder(string relative)
        {
            var clips = new List<AudioClip>();
            string dir = Path.Combine(_root, relative);
            if (!Directory.Exists(dir))
            {
                return clips;
            }
            foreach (string file in Directory.GetFiles(dir, "*.wav"))
            {
                AudioClip clip = LoadWav(file.Substring(_root.Length + 1));
                if (clip != null)
                {
                    clips.Add(clip);
                }
            }
            return clips;
        }
    }

    // Leitor de WAV PCM (8/16/24/32 bits) sem depender do WWW do Unity
    internal static class WavLoader
    {
        public static AudioClip Load(string path)
        {
            byte[] bytes = File.ReadAllBytes(path);
            if (bytes.Length < 44 || ReadTag(bytes, 0) != "RIFF" || ReadTag(bytes, 8) != "WAVE")
            {
                throw new FormatException("nao e um arquivo WAV");
            }

            int channels = 0, sampleRate = 0, bits = 0, format = 0;
            int pos = 12;
            while (pos + 8 <= bytes.Length)
            {
                string id = ReadTag(bytes, pos);
                int size = BitConverter.ToInt32(bytes, pos + 4);
                int body = pos + 8;
                if (id == "fmt ")
                {
                    format = BitConverter.ToInt16(bytes, body);
                    channels = BitConverter.ToInt16(bytes, body + 2);
                    sampleRate = BitConverter.ToInt32(bytes, body + 4);
                    bits = BitConverter.ToInt16(bytes, body + 14);
                }
                else if (id == "data")
                {
                    if (format != 1 && format != 3 && format != -2)
                    {
                        throw new FormatException("WAV precisa ser PCM (formato " + format + ")");
                    }
                    size = Math.Min(size, bytes.Length - body);
                    float[] samples = Decode(bytes, body, size, bits, format == 3);
                    var clip = AudioClip.Create(Path.GetFileNameWithoutExtension(path),
                        samples.Length / channels, channels, sampleRate, false);
                    clip.SetData(samples, 0);
                    return clip;
                }
                pos = body + size + (size & 1);
            }
            throw new FormatException("WAV sem bloco de dados");
        }

        private static float[] Decode(byte[] b, int start, int size, int bits, bool isFloat)
        {
            int step = bits / 8;
            var output = new float[size / step];
            for (int i = 0; i < output.Length; i++)
            {
                int p = start + i * step;
                switch (bits)
                {
                    case 8: output[i] = (b[p] - 128) / 128f; break;
                    case 16: output[i] = BitConverter.ToInt16(b, p) / 32768f; break;
                    case 24: output[i] = ((b[p] << 8 | b[p + 1] << 16 | b[p + 2] << 24) >> 8) / 8388608f; break;
                    case 32: output[i] = isFloat ? BitConverter.ToSingle(b, p) : BitConverter.ToInt32(b, p) / 2147483648f; break;
                    default: throw new FormatException(bits + " bits nao suportado");
                }
            }
            return output;
        }

        private static string ReadTag(byte[] b, int pos)
        {
            return System.Text.Encoding.ASCII.GetString(b, pos, 4);
        }
    }
}
