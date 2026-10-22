using System;
using System.Collections.Generic;
using System.IO;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using UnityEngine;

namespace Upward
{
    [BepInPlugin(Guid, "Upward", Version)]
    public class Plugin : BaseUnityPlugin
    {
        public const string Guid = "upward.projecthighrise";
        public const string Version = "1.0.0";

        internal static Plugin Instance;
        internal static ManualLogSource Log;
        internal static string AssetsDir;

        internal static ConfigEntry<bool> ShopsClose;
        internal static ConfigEntry<bool> OfficesLightsOff;
        internal static ConfigEntry<bool> ServicesLightsOff;
        internal static ConfigEntry<bool> HotelVacantLightsOff;
        internal static ConfigEntry<bool> ApartmentsLightsOff;
        internal static ConfigEntry<bool> ApartmentsFollowResidents;
        internal static ConfigEntry<float> ApartmentsFadeSeconds;
        internal static ConfigEntry<float> ApartmentsOffDelayMinutes;
        internal static ConfigEntry<float> ApartmentsOffHour;
        internal static ConfigEntry<float> ApartmentsOnHour;
        internal static ConfigEntry<float> ShutterSeconds;
        internal static ConfigEntry<bool> SmellStaysOnFloor;
        internal static ConfigEntry<bool> SoundsEnabled;
        internal static ConfigEntry<float> SoundsVolume;

        internal static ConfigEntry<bool> AutoUtilitiesEnabled;
        internal static ConfigEntry<bool> AutoUtilitiesOldSaves;
        internal static ConfigEntry<bool> BiggerUtilityMeters;

        internal static ConfigEntry<bool> SoundproofEnabled;
        internal static ConfigEntry<float> SoundproofCostPerCell;
        internal static ConfigEntry<KeyCode> SoundproofKey;

        internal static ConfigEntry<bool> DragBuildEnabled;
        internal static ConfigEntry<bool> FurnishAllEnabled;

        internal static ConfigEntry<float> ServiceDemandMultiplier;
        internal static ConfigEntry<float> HotelServiceWorkersMultiplier;

        private readonly SoundproofPanel _soundproofPanel = new SoundproofPanel();
        private StoreHours _storeHours;
        private readonly HeatmapTweaks _heatmapTweaks = new HeatmapTweaks();
        private readonly UtilityCapacity _utilityCapacity = new UtilityCapacity();
        private readonly HashSet<string> _loggedErrors = new HashSet<string>();

        private void Awake()
        {
            Instance = this;
            Log = Logger;
            AssetsDir = Path.GetDirectoryName(Info.Location);

            ShopsClose = Config.Bind("Lojas", "ArteDeFechada", true,
                "Fora do horario de funcionamento, a loja mostra a porta de aco fechada, luzes apagadas e a placa CLOSED.");
            OfficesLightsOff = Config.Bind("Lojas", "EscritoriosApagamLuzes", true,
                "Escritorios fora do expediente ficam com as luzes apagadas (sem porta de aco).");
            ServicesLightsOff = Config.Bind("Lojas", "ServicosApagamLuzes", true,
                "Servicos, estandes, galeria, spa, room service etc. fora do horario so apagam as luzes.");
            HotelVacantLightsOff = Config.Bind("Hotel", "QuartosVagosApagados", true,
                "Quartos de hotel sem reserva ficam com as luzes apagadas.");
            ApartmentsLightsOff = Config.Bind("Apartamentos", "ApagarDeMadrugada", true,
                "Apartamentos apagam as luzes (seguindo os moradores ou por horario, veja abaixo).");
            ApartmentsFollowResidents = Config.Bind("Apartamentos", "SeguirMoradores", true,
                "Luz acesa so com morador acordado em casa; apaga quando todos saem ou vao dormir. "
                + "Se false, usa HoraApagar/HoraAcender.");
            ApartmentsFadeSeconds = Config.Bind("Apartamentos", "DuracaoLuz", 0.2f,
                "Segundos (tempo real) que a luz do apartamento leva para acender ou apagar.");
            ApartmentsOffDelayMinutes = Config.Bind("Apartamentos", "AtrasoApagarMinutos", 3f,
                "Minutos do jogo que a luz espera depois que todos saem ou dormem antes de apagar "
                + "(evita piscar quando o morador troca de tarefa).");
            ApartmentsOffHour = Config.Bind("Apartamentos", "HoraApagar", 0f,
                "So com SeguirMoradores = false: hora em que apagam a luz (0 = meia-noite; aceita 23.5 = 23h30).");
            ApartmentsOnHour = Config.Bind("Apartamentos", "HoraAcender", 6f,
                "So com SeguirMoradores = false: hora em que acendem a luz de novo.");
            ShutterSeconds = Config.Bind("Lojas", "DuracaoAnimacaoPorta", 0.6f,
                "Segundos (tempo real) que a porta de aco leva para descer ou subir.");
            SmellStaysOnFloor = Config.Bind("Cheiro", "NaoPassaEntreAndares", true,
                "O cheiro dos restaurantes so se espalha para os lados, nunca para o andar de cima ou de baixo.");
            SoundsEnabled = Config.Bind("Sons", "Ativado", true, "Liga os sons novos do Upward.");
            SoundsVolume = Config.Bind("Sons", "Volume", 0.8f,
                "Volume dos sons novos (0 a 1). Tambem segue o volume de efeitos do jogo.");

            AutoUtilitiesEnabled = Config.Bind("Utilidades", "LinhasAutomaticas", true,
                "Closet eletrico/hidraulico pronto ja passa as linhas dele por todo o piso do andar, sem custo "
                + "(so o closet e cobrado). Piso novo num andar com closet tambem recebe as linhas.");
            AutoUtilitiesOldSaves = Config.Bind("Utilidades", "CompletarSavesAntigos", true,
                "Ao carregar um save, completa as linhas de todos os andares que ja tem closet.");
            BiggerUtilityMeters = Config.Bind("Utilidades", "LigacoesMaiores", true,
                "Ligacoes de energia, agua, cabo, gas e telefone fornecem 25/100/300 em vez de 10/50/150. "
                + "HVAC nao muda.");

            SoundproofEnabled = Config.Bind("Ruido", "LajeAntirruido", true,
                "Liga o painel de laje antirruido: paga-se por andar e o ruido daquela laje some.");
            SoundproofCostPerCell = Config.Bind("Ruido", "PrecoPorCasa", 200f,
                "Preco da laje antirruido por casa de piso construida no andar.");
            SoundproofKey = Config.Bind("Ruido", "Tecla", KeyCode.F8,
                "Tecla que abre e fecha o painel de laje antirruido.");

            DragBuildEnabled = Config.Bind("Construcao", "ArrastarSalas", true,
                "Clicar e arrastar com uma sala selecionada (quarto, escritorio, loja, apartamento...) constroi "
                + "varias lado a lado no andar onde o arrasto comecou. Clique simples continua igual.");
            FurnishAllEnabled = Config.Bind("Construcao", "MobiliarTodos", true,
                "No Pick furnishings de quartos de hotel e apartamentos, Shift+clique numa opcao "
                + "aplica a escolha a todos os espacos vagos do mesmo tipo no predio.");

            ServiceDemandMultiplier = Config.Bind("Servicos", "FrequenciaPedidos", 0.6f,
                "Multiplica a chance de apartamentos e escritorios pedirem servicos (encanador, florista, TI, "
                + "agua etc.). 1 = jogo original, 0.6 = 40% menos pedidos. Quartos de hotel nao mudam.");
            HotelServiceWorkersMultiplier = Config.Bind("Servicos", "FuncionariosHotel", 1.5f,
                "Multiplica os funcionarios de Housekeeping, Room Service Kitchen e Luggage Service "
                + "(arredonda para cima). 1 = jogo original.");

            UpwardAssets.Load(AssetsDir);
            SoundPlayer.Create(gameObject);
            _storeHours = new StoreHours();

            new Harmony(Guid).PatchAll(typeof(Plugin).Assembly);
            Log.LogInfo("Upward " + Version + " carregado. Assets em " + AssetsDir);
        }

        private void OnGUI()
        {
            try
            {
                _soundproofPanel.OnGUI();
            }
            catch (Exception ex)
            {
                if (_loggedErrors.Add("gui" + ex.GetType().Name + ex.StackTrace))
                {
                    Log.LogError("Erro no painel de laje antirruido: " + ex);
                }
            }
        }

        private void Update()
        {
            try
            {
                _heatmapTweaks.Update();
                _utilityCapacity.Update();
                _storeHours.Update();
            }
            catch (Exception ex)
            {
                // Loga cada erro diferente uma vez so, para nao inundar o log a cada frame
                string key = ex.GetType().Name + ex.StackTrace;
                if (_loggedErrors.Add(key))
                {
                    Log.LogError("Erro no StoreHours: " + ex);
                }
            }
        }
    }
}
