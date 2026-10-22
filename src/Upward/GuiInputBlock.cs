using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;

namespace Upward
{
    // Os paineis do mod sao IMGUI, que o jogo nao enxerga: sem isto a roda do mouse sobre o painel
    // tambem dava zoom e arrastar a barra de rolagem movia a camera. Cada painel aberto registra o
    // proprio retangulo a cada frame; com o mouse em cima, o jogo nao le o mouse naquele frame.
    internal static class GuiInputBlock
    {
        private static readonly List<Rect> _rects = new List<Rect>();
        private static readonly List<int> _frames = new List<int>();

        // rect em coordenadas do IMGUI (origem em cima)
        internal static void Add(Rect rect)
        {
            _rects.Add(rect);
            _frames.Add(Time.frameCount);
        }

        internal static bool IsMouseOver()
        {
            Vector2 m = Input.mousePosition;
            var p = new Vector2(m.x, Screen.height - m.y);
            bool over = false;
            for (int i = _rects.Count - 1; i >= 0; i--)
            {
                // Painel que nao desenhou no ultimo frame foi fechado
                if (Time.frameCount - _frames[i] > 1)
                {
                    _rects.RemoveAt(i);
                    _frames.RemoveAt(i);
                }
                else if (_rects[i].Contains(p))
                {
                    over = true;
                }
            }
            return over;
        }
    }

    [HarmonyPatch]
    internal static class GuiInputBlockPatch
    {
        private static readonly AccessTools.FieldRef<object, bool> MouseDown =
            AccessTools.FieldRefAccess<bool>(AccessTools.TypeByName("Game.Services.Input.MouseInputSource"), "_mouseDown");

        private static MethodBase TargetMethod()
        {
            return AccessTools.Method("Game.Services.Input.MouseInputSource:Update");
        }

        // Arraste que comecou fora do painel continua normal, para o jogo receber o soltar do botao
        private static bool Prefix(object __instance, ref bool __result)
        {
            if (MouseDown(__instance) || !GuiInputBlock.IsMouseOver())
            {
                return true;
            }
            __result = false;
            return false;
        }
    }
}
