# Changelog

All notable changes to **cool tower defense game.exe** (formerly *ASCII KEEP*) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Every version links to its Git tag, so you can see exactly how the code changed between versions.

## [Unreleased]

## [0.7.0] - 2026-10-12

`keep.py` 1505 → 1617 lines

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

[Unreleased]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/f9ef6a2...v0.1.0
[0.0.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/f9ef6a228a87bdbaf17ee5fcb89c06409e78d5bc
