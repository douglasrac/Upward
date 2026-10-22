using System;
using Game.Session.Board;
using Game.Session.Entities;
using Game.Session.Input;
using HarmonyLib;
using UnityEngine;

namespace Upward
{
    // Construir salas arrastando: o jogo so "pinta" arrastando pisos e lobby. Aqui, com uma sala
    // multiplace (quarto de hotel, escritorio, loja, apartamento...) clicar e arrastar vai
    // construindo uma ao lado da outra no mesmo andar onde o arrasto comecou.
    internal static class DragBuild
    {
        private static readonly Func<AbstractPaintInputMode, Vector2, bool> UpdateCursorPosition =
            AccessTools.MethodDelegate<Func<AbstractPaintInputMode, Vector2, bool>>(
                AccessTools.Method(typeof(AbstractPaintInputMode), "UpdateCursorPosition"));

        private static readonly Action<AbstractPaintInputMode, bool> TryPaint =
            AccessTools.MethodDelegate<Action<AbstractPaintInputMode, bool>>(
                AccessTools.Method(typeof(AbstractPaintInputMode), "TryPaint"));

        private static readonly AccessTools.FieldRef<AbstractPaintInputMode, Entity> Cursor =
            AccessTools.FieldRefAccess<AbstractPaintInputMode, Entity>("_cursor");

        private static readonly AccessTools.FieldRef<AbstractPaintInputMode, GridPos> CursorPos =
            AccessTools.FieldRefAccess<AbstractPaintInputMode, GridPos>("_cursorpos");

        private static readonly AccessTools.FieldRef<AbstractPaintInputMode, bool> Successful =
            AccessTools.FieldRefAccess<AbstractPaintInputMode, bool>("_successful");

        private static readonly AccessTools.FieldRef<BaseInputMode, bool> MouseoverStarted =
            AccessTools.FieldRefAccess<BaseInputMode, bool>("_mouseoverStarted");

        private static AbstractPaintInputMode _active;
        private static int _row;
        private static int _placed;

        // Durante o arrasto as tentativas que nao cabem sao silenciosas (sem som de erro nem aviso)
        internal static bool Silent => _active != null;

        // So a compra normal de salas (nao elevador, closet, mudanca de inquilino) que continua
        // no modo de construcao depois de cada uma
        private static bool Applies(BaseInputMode mode)
        {
            if (!Plugin.DragBuildEnabled.Value || mode == null || mode.GetType() != typeof(BuyEntityInputMode))
            {
                return false;
            }
            Entity cursor = Cursor((AbstractPaintInputMode)mode);
            return cursor != null && cursor.config.placement.multiplace && !cursor.config.placement.paint;
        }

        private static void PaintHere(AbstractPaintInputMode mode)
        {
            if (CursorPos(mode).y != _row)
            {
                return;
            }
            TryPaint(mode, true);
            if (Successful(mode))
            {
                _placed++;
            }
        }

        // O jogo move o cursor no maximo uma casa por chamada durante o arrasto; repete ate
        // alcancar o mouse, tentando construir em cada casa, para nao pular vaga com mouse rapido
        private static void FollowMouse(AbstractPaintInputMode mode, Vector2 scrpos)
        {
            for (int i = 0; i < 300 && UpdateCursorPosition(mode, scrpos); i++)
            {
                PaintHere(mode);
            }
        }

        internal static void OnDragStart(BaseInputMode mode)
        {
            _active = null;
            if (!Applies(mode))
            {
                return;
            }
            var paint = (AbstractPaintInputMode)mode;
            _active = paint;
            _row = CursorPos(paint).y;
            _placed = 0;
            // A casa onde o botao foi apertado tambem recebe uma sala
            PaintHere(paint);
        }

        internal static bool OnDragMove(AbstractPaintInputMode mode, Vector2 scrpos)
        {
            if (mode != _active)
            {
                return true;
            }
            FollowMouse(mode, scrpos);
            return false;
        }

        internal static bool OnMouseUp(AbstractPaintInputMode mode, Vector2 scrpos)
        {
            if (mode != _active)
            {
                return true;
            }
            FollowMouse(mode, scrpos);
            _active = null;
            MouseoverStarted(mode) = false;
            // Arrasto que nao construiu nada: deixa o jogo tentar de novo e mostrar o motivo
            return _placed == 0 && CursorPos(mode).y == _row;
        }

        internal static void Reset()
        {
            _active = null;
        }
    }

    [HarmonyPatch(typeof(BaseInputMode), "DoDragStart")]
    internal static class DragBuildStartPatch
    {
        private static void Postfix(BaseInputMode __instance)
        {
            DragBuild.OnDragStart(__instance);
        }
    }

    [HarmonyPatch(typeof(AbstractPaintInputMode), "DoDragMove")]
    internal static class DragBuildMovePatch
    {
        private static bool Prefix(AbstractPaintInputMode __instance, Vector2 scrpos)
        {
            return DragBuild.OnDragMove(__instance, scrpos);
        }
    }

    [HarmonyPatch(typeof(AbstractPaintInputMode), "DoMouseUp")]
    internal static class DragBuildMouseUpPatch
    {
        private static bool Prefix(AbstractPaintInputMode __instance, Vector2 scrpos)
        {
            return DragBuild.OnMouseUp(__instance, scrpos);
        }
    }

    [HarmonyPatch(typeof(BuyEntityInputMode), "OnFailedPaint")]
    internal static class DragBuildFailPatch
    {
        private static bool Prefix()
        {
            return !DragBuild.Silent;
        }
    }

    [HarmonyPatch(typeof(AbstractPaintInputMode), nameof(AbstractPaintInputMode.OnHandlerDeactivated))]
    internal static class DragBuildDeactivatePatch
    {
        private static void Prefix()
        {
            DragBuild.Reset();
        }
    }
}
