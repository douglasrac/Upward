# Upward

**The ultimate mod for Project Highrise.** Upward is a [BepInEx 5](https://github.com/BepInEx/BepInEx) plugin that makes your tower feel alive at night and removes a lot of the tedious clicking from building — without replacing the original game.

> Version 1.2.0 · Project Highrise (Steam, Windows) · BepInEx 5.4.23 **x86**

---

## Features

### A tower that sleeps at night
- **Shops and restaurants close for real.** Outside their working hours, every store and restaurant pulls down a steel shutter with an animation, its lights go off and a **CLOSED** sign appears. 69 of the 71 storefronts have their own hand-made "closed" facade; the rest fall back to a generic shutter.
- **Shutter sounds.** Real public-domain garage-door recordings play when a shop opens or closes. Sounds are positional (only heard when on screen, louder when zoomed in, panned left/right) and follow the game's effects volume.
- **Rooftop restaurants** (terraces) are dimmed to a night-blue tint instead of being covered, so the sky behind them stays visible.
- **Offices turn their lights off** gradually after work hours.
- **Services** (stands, gallery, spa, room service, florist, etc.) only dim their lights when closed.
- **Vacant hotel rooms stay dark.**
- **Apartments follow their residents:** the lights are on only while someone is awake at home, and go off when everyone leaves or goes to bed (with a short delay so they don't flicker). Optionally, you can use a fixed schedule instead (dark from 0:00 to 6:00 by default).

### Less busywork when building
- **Drag to build rooms.** With a room selected (hotel room, office, shop, apartment...), click and drag to build several side by side on the floor where the drag started. A single click works as before.
- **Furnish all at once.** In the *Pick furnishings* dialog for hotel rooms and apartments, **Shift+click** an option to furnish every other vacant space of the same type and size in the building (each one is charged, until you run out of money).
- **Pipette.** A new button on the top-left HUD bar (or press **V**) arms the pipette: click anything already built and you go straight into building that same item, without hunting for it in the build menu. Occupied rooms (offices, shops, apartments, furnished hotel rooms) pick the empty space of the same type and size; services such as the Communal Bathroom, vending machines and mod items work too. Esc or V again cancels.
- **Automatic utility lines.** A finished electrical or plumbing closet automatically lays its lines (power, phone, cable TV / water, gas, HVAC) across the whole floor, for free — you only pay for the closet. New floor built later on a floor with a closet also gets the lines. Old saves are completed when loaded.
- **Bigger utility meters.** Power, water, cable, gas and phone hookups supply 25 / 100 / 300 instead of 10 / 50 / 150. HVAC is unchanged.

### Noise, smell and services
- **Soundproof floors.** A new button on the top-left HUD bar (next to the Grid button, or press **F8**) opens a panel where you can soundproof a floor. You pay per floor (200 per built floor tile by default); that floor's noise is cleared and no longer spreads to the floors above and below. Soundproofed floors are stored in your save.
- **Auto booking for events.** In *Performer Booking*, the new **Auto booking** button (or press **F9**) lists every event space. Check the ones you want on autopilot and set each one's ticket price: whenever a checked space is free (cleaned and with nothing booked), it books the cheapest available performer or corporate event, just like doing it by hand. It only books when a performer suite is free for that day, so events are not cancelled for lack of a room. Choices are stored in your save.
- **Restaurant smell stays on its floor.** Smell spreads sideways only, never up or down.
- **Fewer service requests.** Apartments and offices ask for services (plumber, florist, IT, water...) 40% less often. Hotel rooms are not affected.
- **More hotel staff.** Housekeeping, Room Service Kitchen and Luggage Service get 1.5× the workers, which also applies to services already built in old saves.

Every feature can be switched off or tuned in the config file (see [Configuration](#configuration)).

---

## Installation

The download already includes **BepInEx 5.4.23.2 (x86)**, the mod loader Upward runs on. You just extract one zip into the game folder.

1. Download **`Upward-1.2.0.zip`** from the [Releases page](https://github.com/douglasrac/Upward/releases).
2. Find your game folder: in Steam, right-click **Project Highrise → Manage → Browse local files**. It looks like
   `...\steamapps\common\Project Highrise\` and contains `Game.exe`.
3. Extract the zip **into that folder** (allow it to merge folders). You should end up with:
   ```
   Project Highrise\
   ├─ Game.exe
   ├─ winhttp.dll            (BepInEx)
   ├─ doorstop_config.ini    (BepInEx)
   └─ BepInEx\
      ├─ core\               (BepInEx)
      └─ plugins\
         └─ Upward\
            ├─ Upward.dll
            ├─ sounds\
            └─ textures\
   ```
4. Start the game from Steam as usual. To check that it loaded, open `BepInEx\LogOutput.log` and look for a line like `Upward 1.2.0 carregado`.

### Already have BepInEx?
If you already use BepInEx 5 **x86** for other Project Highrise mods, download **`Upward-1.2.0-plugin-only.zip`** instead and extract it into `Project Highrise\BepInEx\plugins\`. Don't use the x64 build of BepInEx: Project Highrise is a 32-bit game, so it will not load.

### Uninstall
Delete the `BepInEx\plugins\Upward` folder (and optionally `BepInEx\config\upward.projecthighrise.cfg`). To remove BepInEx entirely, also delete `winhttp.dll`, `doorstop_config.ini` and the `BepInEx` folder.

> **Saves:** Upward only adds its own data (soundproofed floors) to the save. Utility lines it laid and furniture it bought are normal game objects and stay if you remove the mod.

---

## Configuration

After the first launch with Upward, edit `BepInEx\config\upward.projecthighrise.cfg` with any text editor (with the game closed). Section and key names are in Portuguese; here is what they mean:

| Section | Key | Default | What it does |
|---|---|---|---|
| `Lojas` | `ArteDeFechada` | `true` | Shops/restaurants show the shutter, lights off and CLOSED sign after hours |
| `Lojas` | `EscritoriosApagamLuzes` | `true` | Offices turn their lights off after hours |
| `Lojas` | `ServicosApagamLuzes` | `true` | Services only dim their lights after hours |
| `Lojas` | `DuracaoAnimacaoPorta` | `0.6` | Shutter animation length (real seconds) |
| `Hotel` | `QuartosVagosApagados` | `true` | Vacant hotel rooms are dark |
| `Apartamentos` | `ApagarDeMadrugada` | `true` | Apartments turn their lights off |
| `Apartamentos` | `SeguirMoradores` | `true` | Lights follow residents; `false` uses the fixed hours below |
| `Apartamentos` | `DuracaoLuz` | `0.2` | Light fade time (real seconds) |
| `Apartamentos` | `AtrasoApagarMinutos` | `3` | Game minutes to wait before turning lights off |
| `Apartamentos` | `HoraApagar` | `0` | Lights-off hour when `SeguirMoradores = false` (23.5 = 23:30) |
| `Apartamentos` | `HoraAcender` | `6` | Lights-on hour when `SeguirMoradores = false` |
| `Cheiro` | `NaoPassaEntreAndares` | `true` | Smell does not spread between floors |
| `Sons` | `Ativado` | `true` | Enable Upward's sounds |
| `Sons` | `Volume` | `0.8` | Volume of Upward's sounds (0–1) |
| `Utilidades` | `LinhasAutomaticas` | `true` | Closets lay their lines across the floor for free |
| `Utilidades` | `CompletarSavesAntigos` | `true` | Complete utility lines on floors with closets when loading a save |
| `Utilidades` | `LigacoesMaiores` | `true` | Bigger utility meter capacities |
| `Ruido` | `LajeAntirruido` | `true` | Enable the soundproof floor panel |
| `Ruido` | `PrecoPorCasa` | `200` | Soundproofing price per built floor tile |
| `Ruido` | `Tecla` | `F8` | Key that opens/closes the soundproof panel |
| `Construcao` | `ArrastarSalas` | `true` | Drag to build rooms |
| `Construcao` | `MobiliarTodos` | `true` | Shift+click to furnish all vacant spaces |
| `Construcao` | `ContaGotas` | `true` | Pipette button |
| `Construcao` | `TeclaContaGotas` | `V` | Key that arms the pipette |
| `Eventos` | `BookingAutomatico` | `true` | Auto booking panel for event spaces |
| `Eventos` | `Tecla` | `F9` | Key that opens/closes the auto booking panel |
| `Servicos` | `FrequenciaPedidos` | `0.6` | Service request frequency multiplier (1 = original game) |
| `Servicos` | `FuncionariosHotel` | `1.5` | Hotel service staff multiplier (1 = original game) |

### Custom closed-store art
Each store's closed facade is a PNG in `plugins\Upward\textures\closed\<template>.png` (the template is the game's internal name, e.g. `retail-level-one-a`). Replace a file with your own image of the same size to change it; `textures\closed\TAMANHOS.txt` lists the expected sizes.

### Extra ambient sounds
Put `.wav` files in `plugins\Upward\sounds\emitters\<EmitterName>\` (for example `AMB_DeliveryService`) and they are added to that ambient emitter's random pool. The emitter names are written to the log when a game starts.

---

## Building from source

Requirements: Windows, the [.NET SDK](https://dotnet.microsoft.com/download) (6 or newer), and the game with BepInEx installed (the project references the game's DLLs; they are not included in this repository).

```bash
dotnet build src/Upward/Upward.csproj -c Release
```

The build copies `Upward.dll` and the `assets` folder to `<GameDir>\BepInEx\plugins\Upward`. Close the game first (it locks the DLL), or add `-p:SkipInstall=true` to only compile. If your game is not in the default location, pass it explicitly:

```bash
dotnet build src/Upward/Upward.csproj -c Release -p:GameDir="C:\Program Files (x86)\Steam\steamapps\common\Project Highrise"
```

### Repository layout
```
src/Upward/        C# plugin (Harmony patches + per-frame logic)
assets/sounds/     Shutter sounds (see sounds/CREDITOS.txt) and ambient emitter sounds
assets/textures/   closed/         facades used in game
                   closed_custom/  source art for the facades
tools/             Python scripts used to generate, fit and import the art and sounds
```

---

## Compatibility and known limitations
- Tested on the Steam version of Project Highrise (Unity 2017.4, 32-bit) on Windows with BepInEx 5.4.23.2.
- Steam Workshop cannot host it (Workshop only supports data mods), so it is distributed here.
- Utility lines and bigger meters make the early game cheaper; economy rebalancing may come later.
- Other BepInEx mods that patch the same systems (build tools, heatmaps, utilities) may conflict.

## Credits
- Shutter sounds: "Garage door closing/opening" by ezwa (PDSounds), Wikimedia Commons, public domain.
- Built with [BepInEx](https://github.com/BepInEx/BepInEx) and [Harmony](https://github.com/pardeike/Harmony). The release zip includes BepInEx 5.4.23.2 unmodified (MIT license, see `BepInEx\LICENSE.txt`) and its Unity Doorstop loader `winhttp.dll` (LGPL-2.1, see `BepInEx\DOORSTOP_LICENSE.txt`; source at [NeighTools/UnityDoorstop](https://github.com/NeighTools/UnityDoorstop)).
- Project Highrise is © SomaSim. This is an unofficial fan mod, not affiliated with or endorsed by SomaSim or Kasedo Games.
