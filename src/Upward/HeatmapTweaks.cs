using Game.Services.Settings;
using Game.Session.Board;
using UnityEngine;
using GameMain = Game.Game;

namespace Upward
{
    // Ajusta o espalhamento dos indicadores do jogo (cheiro, barulho...).
    // Cada andar e uma linha da grade; a cada atualizacao o valor de uma casa passa para a de cima e a
    // de baixo como valor * muly + addy. Com muly = 0 e addy = -1 isso nunca vence o valor da propria
    // casa, entao o cheiro so se espalha para os lados (mulx/addx continuam os do jogo).
    internal class HeatmapTweaks
    {
        private const float CHECK_INTERVAL = 1f;

        private float _nextCheck;
        private bool _saved;
        private float _origMuly, _origAddy;

        public void Update()
        {
            if (Time.unscaledTime < _nextCheck)
            {
                return;
            }
            _nextCheck = Time.unscaledTime + CHECK_INTERVAL;

            HeatmapSettingsEntry smell = FindSmell();
            if (smell == null)
            {
                return;
            }
            if (!_saved)
            {
                _origMuly = smell.muly;
                _origAddy = smell.addy;
                _saved = true;
                Plugin.Log.LogInfo("Cheiro: espalhamento vertical original muly=" + _origMuly + " addy=" + _origAddy);
            }

            float muly = Plugin.SmellStaysOnFloor.Value ? 0f : _origMuly;
            float addy = Plugin.SmellStaysOnFloor.Value ? -1f : _origAddy;
            if (smell.muly != muly || smell.addy != addy)
            {
                smell.muly = muly;
                smell.addy = addy;
                Plugin.Log.LogInfo(Plugin.SmellStaysOnFloor.Value
                    ? "Cheiro: agora so se espalha no mesmo andar"
                    : "Cheiro: espalhamento entre andares restaurado");
            }
        }

        private static HeatmapSettingsEntry FindSmell()
        {
            var serv = GameMain.serv;
            if (serv == null || serv.globals == null || serv.globals.settings == null || serv.globals.settings.heatmaps == null)
            {
                return null;
            }
            return serv.globals.settings.heatmaps.FindByType(HeatmapType.smellHeatmap);
        }
    }
}
