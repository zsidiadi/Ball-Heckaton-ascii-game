# Changelog

All notable changes to **cool tower defense game.exe** (formerly *ASCII KEEP*) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Every version links to its Git tag, so you can see exactly how the code changed between versions.

## [Unreleased]

## [0.17.0] - 2026-10-13

`cool tower defense game.exe.py`: 2406 lines

### Changed
- **Balance: Gold Mines get more expensive the more you have.** Each Gold Mine you own makes the next one
  **50% dearer**: 60, 90, 135, 203, 304, … gold (new `cost_growth` value in `BUILDINGS["goldmine"]`, worked out
  by `Run.building_cost`).
  - Gold per wave is unchanged: +12, +8 per upgrade level.
  - Upgrade costs are unchanged and the same for every mine, whatever it cost: 45, 90, … gold.
  - Selling a Gold Mine refunds half of what you paid for it (plus half of its upgrades), and the next one
    gets cheaper again.
  - The side panel shows the price of your next Gold Mine. Prices of 3 or more digits push the income text
    to the right instead of running into it. The "Not enough gold" message shows the real price too.
- Upgrades screen: Unlock Gold Mine shows "60g, +50% each". The line also fits a 70-column window now.
- README: Gold Mine row, features list, tuning table and in-game screenshot updated.

## [0.16.0] - 2026-10-13

Commit [`626a1c8`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/626a1c882119eca5d2d32f2a64eb3de58b9131f9)
· `cool tower defense game.exe.py`: 2394 lines

### Changed
- **Balance: the Mine was too strong.**
  - **Price doubled:** 50 gold (was 25). Selling one still refunds half, now 25.
  - **Damage scaling halved:** the blast still does 24 on wave 1 but grows **+12.5% per wave** (was +25%,
    the same rate as enemy HP), set by the new `dmg_growth` value in `BUILDINGS["mine"]`. Blast damage at
    wave 5 / 10 / 15 / 20 is now 38 / 69 / 125 / 225 (was 59 / 179 / 546 / 1665). A mine still clears small
    enemies early on, but late in a run it's a chunk of damage instead of an instant kill.
  - The Sharpened Steel upgrade still raises mine damage too, as before.
- README: Mine row in the buildings table, the tuning table and the in-game screenshot show the new numbers.

## [0.15.1] - 2026-10-13

Commit [`f7c08a8`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/f7c08a85e3d819bdf0b6d6d2b31d3637488f78e8)
· `cool tower defense game.exe.py`: 2393 lines

### Changed
- **The menu title is centred again**, lined up with the buttons below it. The castle on its hill sits right
  next to the title on the left (3 columns away), on the same rows. This needs a window 138 columns wide or
  more. In narrower windows the title moves right just enough to make room for the castle. Below 105 columns
  there's no castle, and the title is centred as before.
- Removed `ART_SHIFT` (the "5 columns left of centre" nudge from 0.14.1); the layout above replaces it.
- `docs/menu.png` shows the new layout (taken in a 140-column window).

## [0.15.0] - 2026-10-13

Commit [`8e1e4ae`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/8e1e4ae2e9bc48c99e63c742226bbfe9ffb3c476)
· `cool tower defense game.exe.py`: 2392 lines

### Added
- **Real buttons in the side panel during a run.** Upgrade, sell, next wave, speed, pause, cash out and quit are
  now coloured buttons, each with a white key cap showing its key: `U` UP (with the price), `X` SELL (with the
  refund), `N` NEXT WAVE, `F` speed (`x1`/`x2`/`x3`), `P` pause (`||`, `>` while paused), `K` CASH OUT and
  `Q` QUIT. Weapons and buildings stay in the list above them.
- **Click them with the mouse.** A click does the same as pressing the key. Clicking the map still moves the
  cursor.
- A button lights up for a moment when it's pressed, by key or by click. It's greyed out when it can't be
  used right now: nothing to upgrade or sell under the cursor, not enough gold, a wave already running, or
  the game paused (only pause works then).
- `docs/game.png`: an in-game screenshot, used in the README.

### Changed
- The side panel's bottom rows (`U up` / `X sell`, `N wave F speed P pause`, `K cash out Q quit`) became the
  three rows of buttons. With room to spare there's a blank line between button rows. On short terminals
  those gaps go first. The upgrade/sell and next wave/speed/pause rows always stay, even at the minimum
  70x22 during a boss fight. Before, the next-wave hint was the first thing to disappear.
- Buttons work on 256-, 16- and 8-colour terminals, and as reverse video on terminals with no colour. Black
  button text is never bold, because many terminals show bold black as grey.
- README: the in-game screenshot is now an image, so the button colours show. The controls table names each
  button, and there are notes on the new constants and on how the buttons work.

### Fixed
- The game no longer crashes at start-up on terminals that can't hide the cursor (for example `vt100`).

## [0.14.1] - 2026-10-13

Commit [`ab53c85`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/ab53c85027fb382a902437763957c5855ef5a807)
· `cool tower defense game.exe.py`: 2279 lines

### Changed
- **The castle and the title sit a bit further left on the main menu.** They still move as one group, centred
  and then shifted 5 columns left (`ART_SHIFT`), so the title lines up better over the menu buttons. They never
  get closer than 2 columns to the window edge.
- `docs/menu.png` shows the new position.

## [0.14.0] - 2026-10-13

Commit [`a773bc8`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/a773bc827dceb3284b0a9438f0f0d44b692cfd60)
· `cool tower defense game.exe.py`: 2277 lines

### Added
- **A castle on a hill next to the title on the main menu.** It's pixel art drawn with terminal block
  characters (`▀` `▄` `█`): a grey stone castle with a red banner, blue flags, a lit window and a wooden gate,
  on a green hill with the yellow enemy path winding up to the gate. The castle and the title are centred
  together.
- The castle is shown when the window is at least 105 columns wide and the terminal can display block
  characters (any UTF-8 terminal, including Windows Terminal). Otherwise the menu shows only the title, as
  before. On 8-colour terminals the bright colours come from bold; with no colours it's drawn as a silhouette.
- `docs/menu.png`: a screenshot of the new main menu, used at the top of the README.

### Changed
- The game sets the terminal's character encoding from your system language settings at start-up, so curses
  can draw the block characters.
- README: the main-menu screenshot is now an image (block art needs colour to read well), plus notes on the
  window size the castle needs, the new `MENU_CASTLE` / `ART_COLORS` constants, and how the menu art is drawn.

## [0.13.1] - 2026-10-13

Commit [`26f9e2f`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/26f9e2f306a49ad1063e63f20cc933ac0ce03059)
· `cool tower defense game.exe.py`: 2149 lines

### Fixed
- **The game file is `cool tower defense game.exe.py`.** It has the game's name and keeps the `.py` format. 0.13.0
  had misread the request and turned it into a fake `.exe`. Python launches it like `keep.py` before it:
  `python3 "cool tower defense game.exe.py"`, `py "cool tower defense game.exe.py"`, or double-click on Windows
  when Python is installed.
- Removed the `.gitattributes` from 0.13.0. A `.py` file is recognised as Python by GitHub on its own.
- Docstring and README (run commands, tuning, project tree, code overview, contributing) use the new file name.
  The game's title, *cool tower defense game.exe*, is unchanged. The save file is still `keep_save.json`.

## [0.13.0] - 2026-10-13

Commit [`80fc4ec`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/80fc4ec226c2f21c667ed6ff3b91d2f03d8b2c59)
· `cool tower defense game.exe` (was `keep.py`): 2150 lines

### Changed
- **The game file is now called `cool tower defense game.exe`** (renamed from `keep.py` with `git mv`, so its
  history is kept). It is still a Python script, so start it with Python:
  - macOS / Linux: `python3 "cool tower defense game.exe"` (or `./"cool tower defense game.exe"`; it stays executable)
  - Windows: `py "cool tower defense game.exe"`

  Double-clicking it on Windows doesn't work, because Windows would try to run it as a native program.
  The quotes are needed because of the spaces.
- The run instructions in the file's docstring, and the README (install, tuning, project tree, code overview,
  history table, contributing), now use the new name. Older changelog entries still say `keep.py`, because that
  was the file's name then.
- The save file keeps its name, `keep_save.json`, so existing progress isn't lost.
- New `.gitattributes` tells GitHub the `.exe` is Python, so it gets syntax highlighting and counts in the
  repository's language bar.

## [0.12.0] - 2026-10-13

Commit [`8d963d9`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/8d963d9bed2456102f89c6864d59a65f1434ac31)
· `keep.py` 1980 → 2148 lines

### Added
- **VOLUME screen** (new main-menu button, hotkey `V`) with three sliders from 0 to 100%:
  **Music** (menu and level themes), **Death sounds** (grunt / runner / brute), and **Announcer**
  (level complete lines and the special thanks).
  - Keyboard: up/down to pick, left/right (or `a` / `d`, `-` / `+`) to change. Mouse: click a bar segment,
    `[-]` / `[+]`, or the bar's left edge to mute. `M` still switches all sound off or on.
  - Music changes live while the menu theme plays. Changing Death sounds plays a grunt, and changing
    Announcer plays the level 1 line, so you hear the new level right away.
  - Volumes are saved in `keep_save.json` (`"volume": {"music": 0-10, "effects": 0-10, "voice": 0-10}`)
    and applied at start-up.
- `Music.set_volume(group, gain)` for `"music"`, `"effects"` and `"voice"`, with a perceptual curve
  (`volume_gain(step) = (step/10)^2`).
  - pygame: `Sound.set_volume`.
  - Linux players: the music stream is scaled 100 ms at a time, so it changes without a restart.
  - Windows `winsound` / MCI and macOS `afplay`: quieter copies of the WAVs are made on demand (`scale_pcm`,
    standard-library `array`) in a temp folder that `close()` deletes. The music restarts with the new copy.
  - Volume 0 skips playing that sound entirely.

### Changed
- Main menu has 5 buttons. The hint line mentions `V volume`.
- **README refreshed** to match the game as of 0.11.0: new main-menu and in-run screenshots (a boss fight with
  every kind of tower, building and trap), a blessings table with every effect, a merged "Music and sound"
  section (music, death sounds, voice lines, and how each OS plays them), Premium store quick keys, sound cues
  in "How the code works", an audio workflow in Contributing, an updated roadmap (sound effects are done),
  and the commit hash for 0.11.0 in the history table.

### Technical notes
- Tested: the scaler (exact sample values), the live stream volume change (the bytes after the change are
  exactly 25%), scaled effect copies (peak ratio exactly 0.36), the Windows restart sequence with a stand-in
  `winsound`, pygame volumes (SDL dummy driver), the Volume screen with keyboard and mouse at 70×22 and 80×24,
  saving and restoring, and full bot games.

## [0.11.0] - 2026-10-13

Commit [`f23ef8f`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/f23ef8fa6db0a3874ae37584763f288609d84f69)
· `keep.py` 1920 → 1980 lines

### Added
- **Level complete voice lines.** When the LEVEL N COMPLETE screen appears (levels 1-5), that level's
  recording plays (`assets/voice/levelN_complete.wav`). The level music pauses for it, and the next level's
  music starts when the player continues. Levels 6+ have no line, so their music keeps playing.
- **Special thanks from the creator** (`assets/special/special_thanks_from_the_creator.wav`, its own asset and
  constant `SPECIAL_THANKS`). It plays when a player starts level 6, the first level past the five, once per run.
  Level 6's music waits until it has finished (4.6 s).
- Quitting to the menu stops any voice line that is still playing (`Music.stop_effects()`).
- `tools/make_sfx.py` also builds the voice lines. Each keeps the whole recording from the first to the last
  spoken word: breaths and clicks before or after are skipped (level 4 had 0.36 s of breath noise and
  level 2 a stray click before the words). Lines are de-clicked and levelled to -14 dBFS (loudest 100 ms),
  a bit louder than the death sounds. The limiter may lower a voice peak by at most 3 dB, so level 1
  (one hard consonant) ends up ~3 dB quieter instead of squashed.

### Changed
- `Run.events` now carries typed cues: `("death", kind)`, `("level_complete", n)`, `("level_start", n)`.
  `App.play_cues()` turns them into sounds, and `App.sync_music()` picks the track (or silence).
- `Music.effect()` takes a path inside `assets/` (`"sfx/grunt_death.wav"`, `"voice/level1_complete.wav"`, …).
  New: `Music.stop_effects()` and `Music.duration()`.
- `make_sfx.py`: the `TAKES` table became `SOUNDS` (output path, take or `None` for a whole recording,
  target loudness). The death sounds come out byte-identical to 0.10.0.

## [0.10.0] - 2026-10-13

Commit [`45fc505`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/45fc505055a18bde0fa44d605d8c0ecc49ea7d7a)
· `keep.py` 1847 → 1920 lines

### Added
- **Death sounds** for the small enemies. When a grunt, runner or brute dies, its own voiced sound plays
  once, mixed on top of the level music. Bosses and enemies that reach the castle make no death sound.
- The sounds were cut from the team's recordings (`assets/source/Grunt.m4a`, `Runner.m4a`, `Brute.m4a`;
  three takes each). The take used: Grunt 2 (clearly the strongest), Runner 2 (most energy of three
  short ones), Brute 3 (longest and strongest; take 1 sounded cut short at 180 ms). Each was trimmed,
  high-passed at 70 Hz, given 3 ms / 25 ms fades (they start and end at exact zero, so no clicks), and
  levelled so its loudest 100 ms sits at -16 dBFS (all three within 0.3 dB of each other), with a gentle
  peak limiter at -1 dBFS.
- `tools/make_sfx.py` reproduces them (numpy + ffmpeg). Change `TAKES` to pick another take.
- `Music.effect(name)` plays one-shot effects over the music: pygame on spare channels; Windows through
  MCI (winsound can only play one sound at a time, and it's busy with the music); Linux and macOS with a
  short-lived `paplay` / `aplay` / `sox` / `afplay` process. At most 4 at once (`SFX_MAX_AT_ONCE`), and the same
  sound never restarts within 60 ms (`SFX_MIN_GAP`).
- `Run.events` lists the enemy kinds that died each frame. The App plays each kind's sound once per frame,
  so a cannon blast killing 5 grunts gives one grunt shout, not five stacked copies.

### Changed
- `M` / `[M] sound` and `--mute` now cover music **and** sound effects.

## [0.9.0] - 2026-10-13

Commit [`5d878c2`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/5d878c205cf345d8f9566233e9de7953fcad2d97)
· `keep.py` 1798 → 1847 lines

### Added
- **Level music.** Five new tracks, one per level: Level 1 plays `level1_loop.wav`, Level 2 plays
  `level2_loop.wav`, and so on up to Level 5. From level 6 the tracks repeat (6 → 1, 7 → 2, …), like the bosses.
  The track switches when the next level starts. Back in the menu, the menu theme returns.
- **Seamless loops for all five.** Each source track (`assets/source/Level_N.ogg`) is exactly 16 bars at
  132 BPM, but none was cut to loop. Levels 1 and 3 faded out at the end (a dropout), and levels 3, 4 and 5
  ended far from their first sample (a click at every repeat; level 4's jump was 0.47 of full scale).
  Each one got the same treatment as the menu theme: the end is rebuilt from its own lead-in to a bar that
  sounds like bar 1 (donor bar 5 for levels 1-4, bar 11 for level 5), and the start is blended in.

### Changed
- `tools/make_menu_loop.py` became **`tools/make_loops.py`**, which rebuilds all six loops from a `TRACKS` table.
- Crossfades are now **loudness-preserving** (the gain is normalised by the two signals' correlation).
  The old equal-power blend made the downbeat up to ~30% louder when the two pieces were similar, as they
  are in the level tracks. The menu loop was regenerated with the new blend. Every loop point now stays
  within 2.4 dB of the track's natural bar transition (the unfixed files were off by up to 12 dB).
- `Music` plays any track by name and switches between them (`Music(folder).play("level3_loop.wav")`).
  Each playback has its own stop signal and kills its own player when it ends, so rapid switching never
  leaves a player running (tested: 60 switches, 0 leftovers).
- `M` / `--mute` now silence all music, not just the menu.
- Constants: `MUSIC_FILE` was replaced by `MUSIC_DIR`, `MENU_TRACK` and `LEVEL_TRACKS`.

## [0.8.0] - 2026-10-13

Commit [`aef90c3`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/aef90c37e87d31126ac0e7c2022620e49d43097a)
· `keep.py` 1617 → 1798 lines

### Added
- **Menu music.** The medieval theme plays on the main menu, Upgrades and Premium screens only. It keeps
  playing while you move between them, stops when a run starts, and comes back on returning to the menu.
- **Seamless loop.** The source track is exactly 16 bars at 132 BPM, but its last ~45 ms were faded out.
  `assets/menu_loop.wav` replaces that fade with the lead-in to bar 11 (30 ms equal-power crossfade)
  and blends the first 25 ms (donor continuation → real opening), so the end flows straight into the start.
  The length is unchanged. Measured at the seam, the volume now matches the music's natural bar transitions
  (quietest 5 ms: 0.034, where it was 0.009 before).
- `tools/make_menu_loop.py` rebuilds the loop from `assets/source/medieval_td_loop.ogg` (numpy + ffmpeg)
  and reproduces the shipped WAV byte for byte.
- `Music` class with no required dependencies: pygame → winsound (Windows) → paplay / aplay / sox
  (raw audio streamed into the player for gapless looping) → afplay (macOS, multi-loop file, tiny gap
  every ~5 min). If no player exists, the game stays silent. A player that keeps crashing is retried
  3 times, then left alone.
- `M` on the menu (or clicking `[M] music` in the bottom-left corner) toggles music. The choice is saved
  as `"music"` in `keep_save.json`.
- `--mute` command-line flag.

### Technical notes
- `App` now takes the music player (`App(scr, music)`) and syncs it every frame against `MENU_STATES`.
  The player is created before curses starts and closed in a `finally` block on exit.
- Tested with stand-in players: the streamed bytes are the loop repeated exactly (no gap or padding at the
  wrap), `stop()` kills the player, the afplay fallback restarts and backs off correctly, and the pygame
  backend plays and stops (SDL dummy audio driver).

## [0.7.0] - 2026-10-12

Commit [`d3e9b48`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/d3e9b4896813809d8e80a4f62bcef8b37e2f542c)
· `keep.py` 1505 → 1617 lines

### Added
- **PREMIUM button** in the main menu (hotkey `P`) that opens a real-money store titled
  "PREMIUM GEAR", with prices in euros:
  Nuke (EUR 5.00, kills every enemy on the field), 10 Gems (EUR 5.00), Second Chance (EUR 3.00),
  Gem Doubler (EUR 8.00), Unlock All (EUR 10.00), Golden Castle skin (EUR 2.00).
- The purchase flow: pick an item (keyboard, `1`–`6`, or click `[ BUY ]`), then a confirm dialog with
  `[ YES ]` / `[ NO ]` (keyboard `Y` / `N` / Enter / Esc, or click).
- `PREMIUM` table, `PAYMENTS_ENABLED` switch, `eur()` price formatter and `App.purchase()`.

### Not yet working (on purpose)
- **Payments are not connected.** Confirming a purchase only shows
  "Payments aren't connected yet - nothing was charged", so **no money is taken and nothing is granted**.
  The premium items have no in-game effect yet. The store screen says so, and the confirm dialog repeats it.
  Real sales need a payment provider before `PAYMENTS_ENABLED` can be turned on.

### Changed
- Main menu has 4 buttons, and the hint line mentions `P premium`.
- `App.box()` now returns its position so dialogs can place buttons inside it.

## [0.6.0] - 2026-10-12

Commit [`4468936`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/4468936802bf8b1fe608422c936beae257da8378)
· `keep.py` 1390 → 1505 lines

### Added
- **Gold Mine** `$` (key `G`, 60g, unlock 8 gems): placed on any empty grass tile without a structure.
  It deals no damage but pays +12 gold after every wave, +8 more per upgrade level (`U`, max level 5).
  The wave-cleared screen shows how much came from mines.
- **Mine** `**` (key `M`, 25g, unlock 6 gems): placed on the enemy path. The first enemy that steps on it
  sets it off, dealing a one-time blast to every enemy within 1.5 tiles. Damage starts at 24 and grows
  with the wave like enemy HP. Boss armor applies.
- **Tar** `~~` (key `T`, 30g, unlock 5 gems): placed on the enemy path. Enemies on it move at half speed.
  It deals no damage and is permanent. The Shadow Wraith ignores it, like every other slow.
- Mines and Tar can be removed with `X` for half their price; only one fits on each path tile.
- Side panel rows for `G` / `M` / `T` with cost and effect (income, current mine damage, slow). Hovering
  them shows their details.
- Upgrades screen: unlocks for Tar, Mine and Gold Mine (13 items now; `1`–`9`, `0` quick-buy the first ten).

### Changed
- **Tesla became the Lightning tower** `Z` (key `8`, 15 gems). It chains to 4 enemies, and each jump deals
  **75%** of the previous hit. Before, it was 80% and the percentage wasn't shown. The falloff is a
  stat (`falloff`) shown on the tower as `4x 75%`.
  Save files that unlocked Tesla automatically get Lightning.
- Blessing "Overcharge" now boosts Lightning. The "Tar Pits" blessing was renamed **Heavy Mud** to avoid
  confusion with the new Tar trap. Armory can now also unlock a building.
- Side panel: upgrade and sell share one row, and low-priority rows (next boss, second info line, column
  header, help) hide automatically on short terminals so the build menu always fits at 70×22.
- The Upgrades screen packs tighter on short terminals.

### Technical notes
- New `BUILDINGS` table and `ITEMS = {**WEAPONS, **BUILDINGS}`. Gold Mines are `Tower` objects with
  `kind="goldmine"`, and Mines and Tar live in the new `Run.traps` map (path tile → kind).
- New methods: `Run.place_building()`, `Run.explode()`, `Run.income()` and `Run.mine_damage()`.
- `load_meta()` migrates the `tesla` unlock to `lightning`.
- Tested: placement rules, selling, upgrading, income, the mine blast, the tar slowdown, lightning falloff,
  save migration, and that the layout fits at 70×22 with a boss on screen, plus full bot games.

## [0.5.0] - 2026-10-12

Commit [`60add35`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/60add3596f06ee9d9b72d16cc2dbd5febcd74231)
· `keep.py` 1425 → 1390 lines

### Changed
- **The map is as wide as it can be while keeping the side panel.** The panel was redesigned to fit in
  24 columns instead of 28, so the map and panel now use every column of the terminal:
  80 columns gives a 26-tile-wide map (was 24), and 200 columns gives 86 (was 84). The max map width went from 120 to 150 tiles.
- Compact side panel: weapon costs are shown in their own `$` column, the castle and boss HP bars are
  8 characters wide, special labels are shorter (`hits all`, `toughest`), and the help text is shorter.

### Removed
- **Trees and flowers.** They didn't work out, so the grass is plain again. `TREES`, `FLOWERS`,
  `FLOWER_COLORS`, `Run.make_deco()` and `Run.deco` were removed.

## [0.4.0] - 2026-10-12

Commit [`b3344c7`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/b3344c7b000e5c928796183c6b3b8b1c1e2df600)
· `keep.py` 1218 → 1425 lines

### Added
- **4 new weapons** (8 total), each with its own mechanic:
  - **Flamer** `L` (key 5, 50g): burns *every* enemy in a short range. Unlock: 6 gems.
  - **Poison** `P` (key 6, 50g): poison damage over time that ignores armor. Unlock: 10 gems.
  - **Sniper** `S` (key 7, 70g): 22 damage, range 7, shoots the enemy with the most HP. Unlock: 12 gems.
  - **Tesla** `T` (key 8, 65g): lightning that jumps between up to 4 enemies, gaining a jump every
    2 levels. Unlock: 15 gems.
- **Live weapon stats** in the side panel: cost, damage, range and shots per second for every weapon,
  including your run's upgrades and blessings. Hovering a tower also shows its special (splash, slow,
  chain, poison, …).
- **5 big bosses.** One ends every level as the last enemy of wave 5, 10, 15, …:
  Goblin King (summons goblins), Iron Golem (armor), Swamp Hydra (regenerates),
  Shadow Wraith (can't be slowed, teleports), Bone Dragon (enrages at half HP).
  They are drawn 2 rows tall, get a name and HP bar in the side panel, and are announced when they appear.
  After level 5 they return as *II*, *III*, ….
- The level-complete screen names the next level's boss and its ability.
- **Trees and flowers.** Little forests (`/\`, `&`) and colorful flowers (`*,`) are scattered on
  the grass. They are cosmetic: building on a tile clears it, and new paths cut through them.
- New blessings: Pyromaniac, Toxicology, Deadeye, Overcharge, and **Armory** (unlocks a random
  locked weapon for the current run).
- Upgrades screen: 6 weapon unlocks (sorted by price) and quick-buy keys `1`–`9`, `0`.

### Changed
- **The in-game info and build options are back in a panel on the right**, where they were before 0.3.0.
  The header and the 3-row HUD under the map were removed, and the message line is below the map again.
- The map is again sized to the terminal minus the 28-column side panel (max 120×70 tiles).
- Bosses are now part of each level's identity instead of one generic boss `M`.
- The Goblin King was tuned to be beatable by a fresh player (140 base HP, summons every 5 s).

### Technical notes
- `WEAPONS` entries gained `unlock` (gem price; 0 = free) and optional `aoe`, `poison`, `strong` and
  `chain` fields. `META_UPGRADES` builds its unlock items from `WEAPONS` automatically.
- `Run.stats_for(kind, level)` computes stats for any weapon (used by the panel), and `stats(tower)` wraps it.
- Tower firing now collects the enemies in range first, then chooses a target by weapon type: first in line,
  most HP, or everyone for the Flamer.
- New `Run.hit()` applies armor to every direct hit, and `Run.boss_ability()` runs the boss abilities.
  `Enemy` gained `boss`, `name`, `armor`, `no_slow`, `timer`, `enraged`, `poison_t` and `poison_dps`.
- New `Run.make_deco()` and the `Run.deco` map; the drawing code renders it under towers and enemies.
- `draw_header`, `draw_hud` and `fit` (0.3.0) were replaced by a row-based `draw_panel`.
- Tested with a fake terminal: every weapon fires and kills, every boss ability works, and full bot games
  run at 70×22, 80×24 and 160×45. Fresh players (bot) reach level 3 most of the time.

## [0.3.0] - 2026-10-12

Commit [`e973e43`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/e973e43305e6c7a6e11cc4902758ea29629d6f06)
· `keep.py` 1037 → 1218 lines

### Added
- **Main menu buttons:** START GAME, UPGRADES and QUIT. You can use them with up/down + Enter,
  hotkeys (`U`, `Q`) or a mouse click.
- **Upgrades screen:** every permanent gem upgrade now lives behind the UPGRADES button. You can
  select with up/down, buy with Enter, quick-buy with `1`–`6`, click `[ BUY ]`, and go back with Esc,
  Backspace, `B` or `[ BACK ]`.
- A retro desktop-window frame on the menus, with a title bar `cool tower defense game.exe   [_] [#] [X]`.
  Clicking `[X]` quits from the main menu or goes back from Upgrades.
- The version number (`v0.3.0`) is shown in the menu frame.
- README rewritten in a standard open-source layout: features, install, full gameplay
  reference, architecture overview, tuning guide, contributing rules and project history.
- `CHANGELOG.md` (this file), covering the project's history from the first commit.

### Changed
- **Renamed the game from "ASCII KEEP" to "cool tower defense game.exe"** in the game (new big
  title art, title bar, header) and in the README title.
- **The map now uses the full terminal width.** The side panel was removed, and its information moved to:
  - a header row: level, wave, phase, castle HP bar, gold, gems, paths, speed;
  - a 3-row HUD under the map: build bar with prices, selected-tile info with controls, and messages.
  At 80 columns the map is 38 tiles wide (was 24); at 150 columns it is 73 (was 59).
  The max map size went from 120×70 to 150×70 tiles.
- The castle is unchanged: same 3-row art, still on the right edge.
- Header and build bar automatically switch to shorter layouts on narrow terminals.
- The game-over screen now says "THE CASTLE HAS FALLEN" (was "THE KEEP HAS FALLEN").
- `Esc` reacts instantly (`ESCDELAY` set to 25 ms).

### Removed
- The gem shop list from the main menu (moved to the Upgrades screen).
- The right-hand side panel during a run (replaced by the header and HUD).

### Technical notes
- New constants `GAME_NAME`, `VERSION`, `HUD_H`, `MAX_MAP_W`, `MAX_MAP_H`; `PANEL_W` was removed.
- `TITLE` is now a list of art blocks, each centered on its own.
- `App` has a third state, `upgrades`, next to `menu` and `run`. Buttons register clickable zones
  (`App.zones`) while they are drawn, and mouse clicks are matched against them.
- `draw_panel` was replaced by `draw_header` and `draw_hud`. A small `fit()` helper drops the
  lowest-priority header items until the line fits the terminal width.
- `Run` (game logic) is unchanged. A bot balance check still shows players with no upgrades reaching level 3–4
  on an 80-column terminal.

## [0.2.0] - 2026-10-12

Commit [`cc20d54`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/cc20d54749cfd4369f51c37e43c1dc60f57e949a)
· `keep.py` +283 / −80 lines (834 → 1037)

### Added
- **Levels.** A run is now split into levels of 5 waves. The 5th wave of each level is a boss wave.
- **Level-complete screen** with a reward (+40 + 20×level gold, +2×level gems, castle repaired
  by up to 25% of max HP). From there the player can start the next level or blow up the castle to cash out.
- **One more enemy path per level.** Level 1 has one path (from the west), level 2 adds one from
  the north, level 3 one from the south, and so on. Enemies are split evenly across all open paths.
- A newly opened path blinks red for 6 seconds. If it runs over a tower, that tower is removed and its
  full cost is refunded.
- Mouse support: click a tile to move the cursor there.
- Shift+WASD moves the cursor 5 tiles at a time.
- Game speed now cycles x1 / x2 / x3 (was x1 / x2).
- Best level reached is saved and shown in the main menu.

### Changed
- **The map fills the whole terminal** (up to 120×70 tiles). It used to be capped at 36×20 tiles.
- Enemies walk up to 1.6× faster on large maps, so waves don't drag on big screens.
- Spawn interval gets 10% shorter for each extra path.
- Header, side panel and wave messages show `level N` and `wave X/5`.
- The side panel's help text was shortened so it fits on 70×22 terminals.

### Technical notes
- `Run.path` (one list of cells) became `Run.paths` (a list of paths) plus a shared `path_set`.
  Each `Enemy` now keeps a reference to its own path, and towers target the enemy with the
  fewest cells left to walk, so targeting works across paths of different lengths.
- The old `make_path()` was replaced by:
  - `place_castle()` picks the castle row and a list of entry cells around the castle;
  - `gen_path()` builds a wiggly path from random waypoints joined by straight segments,
    then cuts out loops;
  - `score_path()` rates a candidate path. It penalises crossing towers, overlapping other
    paths, touching itself and running alongside other paths, and prefers a target length;
  - `add_path()` tries 250 candidates from the next map edge and keeps the best one.
- New `levelup` state in the run state machine (`build → wave → perk → levelup → build`).
- Balance was tuned with automated bot playtests. A player with no upgrades clears levels 1–2
  and usually falls in level 3.

## [0.1.0] - 2026-10-12

Commit [`d2ddb55`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/d2ddb55b216c16210331c3ea5c5d68363a114f7e)
· first playable version (`keep.py`, 834 lines)

### Added
- Roguelike tower defense in a single Python file using only the standard library (`curses`).
- A randomly generated enemy path from the left edge to a castle on the right.
- Two-step building: put a **structure** on grass (10 gold), then mount a **weapon** on it.
- Four weapons: Bow, Gun, Cannon (splash damage) and Frost (slows enemies). Each upgrades
  to level 5, and selling refunds 50% of what was spent.
- Four enemy types: grunt, runner, brute, and a boss every 5th wave. Enemy HP grows 25% per wave.
- After every wave, the player picks 1 of 3 random **blessings** (12 in total).
- **Gems** are the meta currency, earned from waves, bosses and brutes. They are kept when
  the castle falls.
- Players can **destroy their own castle (K)** to cash out early; every 25 leftover gold becomes 1 bonus gem.
- A permanent **gem shop** in the main menu: castle HP, starting gold, damage and gem gain,
  plus unlocks for Cannon and Frost.
- Progress is saved to `keep_save.json`, which is ignored by Git.
- Range preview, hit effects, enemy health indicators, pause, and x2 speed.

## [0.0.0] - 2026-10-12

Commit [`f9ef6a2`](https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/f9ef6a228a87bdbaf17ee5fcb89c06409e78d5bc)

### Added
- Repository created for the B.A.L.L.S hackathon, with a README stub.

[Unreleased]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.17.0...HEAD
[0.17.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.15.1...v0.16.0
[0.15.1]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.15.0...v0.15.1
[0.15.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.14.1...v0.15.0
[0.14.1]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.13.1...v0.14.0
[0.13.1]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/f9ef6a2...v0.1.0
[0.0.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/f9ef6a228a87bdbaf17ee5fcb89c06409e78d5bc
