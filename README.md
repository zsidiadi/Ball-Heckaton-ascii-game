# cool tower defense game.exe

> A roguelike tower defense game that runs in your terminal. It was made for the **B.A.L.L.S hackathon**.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
![Version](https://img.shields.io/badge/version-0.4.0-orange)

Enemies march down randomly generated paths toward your castle. Build structures, mount weapons on
them, and survive as many levels as you can. Every level ends with a **big boss** and the next one
opens **one more path** to your castle.
When the castle falls you keep your **gems** and spend them on permanent upgrades for the next run.

```
 cool tower defense game.exe   level 1   wave 5/5   kills 67   gem bank 0
+--------------------------------------------------------------------+  LEVEL 1  wave 5/5
|    .      '   .    .      '   .    .      '   .    ,*     '   .    |  WAVE ACTIVE - 3 left
|     '   *  *, *     '   .    .      '   .    .      '/\ .    .     |  CASTLE ########## 40/40
|   .  /\.      '   .    .      '   .    .      '/\/\/\   &  *, '   .|  GOLD 110    GEMS 8
|  /\& /\ '::::B:::::::::::::::::::::::   '   .    .   /\ '/\ .     *|  GOBLIN KING
|   '& /\  B..     *,   .    . *    ':: .    .     /\/\ & &  .      '|  BOSS   #######--- 236
| .  /\. /\:: '   ./\  .      '   .  ::.      '*, ./\  . /\/\/\ & .  |  Gun lv 2
|.     /\/\::    .      '   .    .   :: '   .    .      '  *,   *.   |   dmg 1.4  rng 3.3  6.0/s
| '   .    ::     '   .    .      '  ::    .   *, '   .    .     /^^\|    weapon cost  dmg rng  /s
|    .     ::   .*  *.      ' \^^/.G2::::::::::::::::::::::::::::|[]||  B struct  10g
|,*   '   .:::::::::::::::::::(oo):::A2,* .    .      '   .    . |__||  1 Bow     25g  3.0 3.5 1.4
|   .    .      '   .  *,*, . . . .:: .  . *    '   .    .      '   .|  2 Gun     40g  1.0 3.0 5.6
|  .      '   &    .      . . .G2 .:: .   '   .*   .      '   .    . |  3 Cannon  60g  7.0 4.0 0.6
|   '   *  &  &  &  '   . . . .[],*:: . .    .      '   .    .      '|  4 Frost   45g  0.6 3.0 2.0
|>>    .      '   &    . *  . . . .::  .      '   .    .      '   .  |  5 Flamer  50g  0.9 2.0 4.0
|::::::::::::::::::::::::::::::::::::   '   .    .      '   .  /\.   |  6 Poison locked
| '   .    .      '   .,*  .      '  /\    .      '   .    .      '  |  7 Sniper  70g 22.0 7.0 0.4
|*   .      '   .    .   *  '   .    .      '   .    . *    '   .    |  8 Tesla   65g  4.0 3.5 1.0
|     '   .    . /\   '   .    .  &   '*,/\    .      '   .    .     |  U upgrade 60g
|   .    &      '  ,*    . *    '   .    .      '   .    .      '   .|  X sell   +40g
|  .      '   .    .      '   .    .      '   .    *,     '   .    . |
|   '   .    .      '& *,    .      '   .    .      '   .    . *    '|  N wave   F speed   P pause
| .    .      '/\ .    .   ,* '   .    .      '   *    .      '   .  |  K boom (cash out)   Q quit
+--------------------------------------------------------------------+  move: arrows/wasd/mouse
 GOBLIN KING summons goblins!
```

## Table of contents

- [Features](#features)
- [Getting started](#getting-started)
- [How to play](#how-to-play)
- [Controls](#controls)
- [Game reference](#game-reference)
- [Tuning the game](#tuning-the-game)
- [Project structure](#project-structure)
- [How the code works](#how-the-code-works)
- [Project history](#project-history)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Authors](#authors)
- [License](#license)

## Features

- **Roguelike runs.** Every run has a new random map, and after every wave you choose 1 of 3 random blessings.
- **Levels that grow.** A level is 5 waves, and each new level adds another enemy path to your castle.
- **5 big bosses.** One of them ends every level: Goblin King, Iron Golem, Swamp Hydra, Shadow Wraith
  and Bone Dragon, each with its own ability. After the 5th they come back stronger (II, III, …).
- **8 weapons.** First build a structure, then mount a weapon on it: Bow, Gun, Cannon, Frost, Flamer,
  Poison, Sniper or Tesla. Weapons upgrade up to level 5, and their stats are shown live in the side panel.
- **Meta progression.** Gems survive death and buy permanent upgrades and weapon unlocks.
- **Cash out on purpose.** Blow up your own castle to keep your gems and turn leftover gold into bonus gems.
- **Cute map.** Little forests `/\` `&` and flowers `*,` grow on the grass. You can build right
  over them.
- **Full-screen layout.** The map scales to your terminal size, with all the info and build options
  in a panel on the right. You can use the mouse or the keyboard.
- **Retro menu.** A window-style main menu with START GAME, UPGRADES and QUIT buttons.
- **Zero dependencies.** It's a single Python file that uses only the standard library.

## Getting started

### Requirements

- Python **3.8+**
- A terminal of at least **70×22** characters. Bigger is better, because the map fills the window
  next to the side panel.
- Windows only: `pip install windows-curses`

### Install and run

```bash
git clone https://github.com/zsidiadi/Ball-Heckaton-ascii-game.git
cd Ball-Heckaton-ascii-game
python3 keep.py
```

> **Tip:** maximise or full-screen the terminal **before** starting a run. The map size is fixed
> when the run begins.

## How to play

1. **Build.** Move the cursor onto a grass tile and press **B** to build a structure `[]` (10 gold).
2. **Arm it.** Press **1–8** to mount a weapon on that structure. The side panel shows each weapon's
   cost, damage, range and shots per second.
3. **Fight.** Press **N** to send the next wave. Kills give gold.
4. **Choose a blessing.** After each wave, pick 1 of 3 random bonuses.
5. **Beat the boss.** Wave 5 of every level ends with a big boss. Its name and HP bar appear in
   the side panel.
6. **Level up.** Clear all 5 waves of a level and you get a reward. The next level opens a new path,
   which blinks red. If the new path runs over a tower, you get that tower's full cost back.
7. **Lose well.** When the castle falls you keep the run's gems. Press **K** at any time to blow up the
   castle yourself; every 25 leftover gold becomes 1 extra gem. Quitting with **Q** forfeits the run's gems.
8. **Upgrade.** Open **UPGRADES** in the main menu, spend your gems, then start a stronger run.

## Controls

### Menus

| Key | Action |
| --- | --- |
| Up / Down (or `w` / `s`) | Move between buttons / upgrades |
| `Enter` / `Space` | Press the selected button / buy the selected upgrade |
| `U` | Open the Upgrades screen from the main menu |
| `1`–`9`, `0` | Quick-buy an upgrade (Upgrades screen) |
| `Esc` / `Backspace` / `B` | Back to the main menu |
| `Q` | Quit (main menu) |
| Mouse click | Click any button, upgrade row or `[ BUY ]`. `[X]` in the title bar closes the screen |

### In game

| Key | Action |
| --- | --- |
| Arrow keys / `w` `a` `s` `d` | Move cursor |
| `W` `A` `S` `D` (Shift) | Move cursor 5 tiles |
| Mouse click | Move cursor to the clicked tile |
| `B` | Build structure |
| `1`–`8` | Mount Bow / Gun / Cannon / Frost / Flamer / Poison / Sniper / Tesla |
| `U` | Upgrade weapon |
| `X` | Sell (50% refund) |
| `N` | Start next wave |
| `F` | Game speed x1 / x2 / x3 |
| `P` | Pause |
| `K` | Destroy your own castle (cash out) |
| `Q` | Quit run (gems lost) |
| `Enter` | Continue (level complete, game over) |

## Game reference

### Weapons

| Key | Weapon | Map | Cost | Damage | Range | Shots/s | Special | Unlock |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Bow | `A` | 25g | 3.0 | 3.5 | 1.4 | steady single target | free |
| 2 | Gun | `G` | 40g | 1.0 | 3.0 | 5.6 | very high fire rate | free |
| 3 | Cannon | `C` | 60g | 7.0 | 4.0 | 0.6 | splash radius 1.3 | 8 gems |
| 4 | Frost | `F` | 45g | 0.6 | 3.0 | 2.0 | halves enemy speed for 1.2 s | 10 gems |
| 5 | Flamer | `L` | 50g | 0.9 | 2.0 | 4.0 | burns **every** enemy in range | 6 gems |
| 6 | Poison | `P` | 50g | 0.5 | 3.5 | 1.1 | poison: 2 dmg/s for 3 s, **ignores armor** | 10 gems |
| 7 | Sniper | `S` | 70g | 22.0 | 7.0 | 0.4 | huge range, shoots the enemy with the **most HP** | 12 gems |
| 8 | Tesla | `T` | 65g | 4.0 | 3.5 | 1.0 | lightning jumps to 4 enemies (−20% per jump, +1 jump every 2 levels) | 15 gems |

Locked weapons are unlocked permanently with gems on the Upgrades screen, or for one run with the
**Armory** blessing.

Each upgrade level gives +40% damage, +0.3 range and fires 8% faster, up to level 5.
An upgrade costs 75% of the weapon's base price × its current level.
The number on a tower (`A2`, `G3`, …) is its level.

### Enemies

| Map | Enemy | Base HP | Speed | Castle damage | Gold | Appears |
| --- | --- | --- | --- | --- | --- | --- |
| `o` | Grunt | 8 | 1.5 | 1 | 3 | always |
| `r` | Runner | 5 | 2.8 | 1 | 3 | from wave 2 |
| `B` | Brute | 32 | 0.85 | 3 | 8 | from wave 4 (10% chance to drop a gem) |

Enemy HP grows ×1.25 every wave. The mark after an enemy's letter shows its health:
`:` means healthy, `.` means hurt, and nothing means almost dead. A slowed enemy turns blue,
and a poisoned one turns magenta.

### Bosses

One big boss closes every level: it's the last enemy of wave 5, 10, 15, … Bosses are drawn 2 rows tall,
and their HP bar appears in the side panel.

| Level | Boss | Sprite | Base HP | Speed | Castle damage | Reward | Ability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Goblin King | `\^^/` `(oo)` | 140 | 0.60 | 10 | 40g, 3 gems | summons 2 goblins every 5 s |
| 2 | Iron Golem | `[##]` `/\|\|\` | 150 | 0.45 | 12 | 50g, 4 gems | armor: every hit loses 3 + 0.2×wave damage (min 20% gets through). Poison ignores it |
| 3 | Swamp Hydra | `~@@~` `\HH/` | 170 | 0.55 | 14 | 60g, 5 gems | regenerates 1.5% of max HP per second |
| 4 | Shadow Wraith | `(..)` `/~~\` | 130 | 0.70 | 16 | 70g, 6 gems | can't be slowed, teleports 4 tiles forward every 4 s |
| 5 | Bone Dragon | `/\/\` `<DD>` | 220 | 0.55 | 20 | 100g, 8 gems | enrages below 50% HP: double speed |
| 6+ | the same five again | | | | | | named *II*, *III*, … with HP for that wave |

### Levels

| Level | Waves | Open paths | New path starts at |
| --- | --- | --- | --- |
| 1 | 1–5 | 1 | west `>>` |
| 2 | 6–10 | 2 | north `vv` |
| 3 | 11–15 | 3 | south `^^` |
| 4+ | … | +1 per level | west, north, south, … |

| Reward | Amount |
| --- | --- |
| Wave cleared | 8 + 2×wave gold, 1 gem (+1 more for every 10 waves) |
| Level complete | 40 + 20×level gold, 2×level gems, castle repaired by up to 25% of max HP |

### Blessings (pick 1 of 3 after each wave)

Gold Rush, Mason, Fletcher, Gunsmith, Black Powder, Deep Freeze, Pyromaniac, Toxicology, Deadeye,
Overcharge, Armory (unlocks a random locked weapon for this run), Eagle Eye, Tar Pits, Bounty,
Cheap Bricks, Gem Shard, Whetstone. Blessings for weapons you haven't unlocked never show up.

### Upgrades (permanent, bought with gems)

All upgrades live behind the **UPGRADES** button in the main menu.

| Upgrade | Effect per level | Max | Cost |
| --- | --- | --- | --- |
| Thick Walls | +10 castle HP (base 20) | 10 | 3 × next level |
| War Chest | +20 starting gold (base 60) | 10 | 3 × next level |
| Sharpened Steel | +10% weapon damage | 10 | 4 × next level |
| Gem Magnet | +25% gems earned | 5 | 5 × next level |
| Unlock Flamer | Flamer can be built | 1 | 6 |
| Unlock Cannon | Cannon can be built | 1 | 8 |
| Unlock Frost | Frost can be built | 1 | 10 |
| Unlock Poison | Poison can be built | 1 | 10 |
| Unlock Sniper | Sniper can be built | 1 | 12 |
| Unlock Tesla | Tesla can be built | 1 | 15 |

Progress is saved in `keep_save.json` next to `keep.py`. Delete that file to reset.

## Tuning the game

All balance numbers live at the top of `keep.py`:

| Constant | What it controls |
| --- | --- |
| `WEAPONS` | cost, damage, range, cooldown, specials and gem unlock price of each weapon |
| `ENEMIES` | HP, speed, castle damage and gold of each normal enemy |
| `BOSSES` | name, sprite, HP, speed, damage, rewards and ability of the 5 bosses |
| `TREES`, `FLOWERS`, `FLOWER_COLORS` | the decorations scattered on the grass |
| `HP_GROWTH` | how fast enemies get tougher each wave (default `1.25`) |
| `WAVES_PER_LEVEL` | waves per level (default `5`) |
| `STRUCT_COST`, `MAX_LEVEL` | structure price, max weapon level |
| `META_UPGRADES` | items and prices on the Upgrades screen |
| `PERKS` | the blessing pool |
| `EDGES` | the order in which new paths enter the map |
| `GAME_NAME`, `VERSION` | the name and version shown in the menu and title bar |
| `MIN_W`, `MIN_H`, `PANEL_W` | minimum terminal size and width of the side panel |
| `MAX_MAP_W`, `MAX_MAP_H` | largest map size in tiles (default 120×70) |

## Project structure

```
.
├── keep.py          # the whole game: a single file, standard library only
├── README.md        # this file
├── CHANGELOG.md     # version history: what changed and when
├── .gitignore       # ignores __pycache__ and the save file
└── keep_save.json   # created on first run (git-ignored)
```

## How the code works

`keep.py` is organised top to bottom as follows:

| Section | Responsibility |
| --- | --- |
| Constants | balance data (`WEAPONS`, `ENEMIES`, `BOSSES`, `META_UPGRADES`, `PERKS`, …) |
| `load_meta` / `save_meta` | read and write the JSON save file |
| `Enemy` | an enemy walking along **its own path** (`pos` = how many cells it has walked). Bosses carry their ability state (armor, timer, enraged) |
| `Tower` | a structure on a tile, with an optional weapon (`kind`, `level`, `invested`) |
| `Run` | one playthrough: map, paths, towers, enemies, waves, levels and the run state machine |
| `App` | main menu, Upgrades screen, clickable buttons, input routing, mouse, and **all drawing** (map, decorations, boss sprites, side panel, overlays) |
| `main()` | curses setup, colours, then a fixed **30 FPS** loop: input → update → draw |

**Run state machine**

```
build ──N──▶ wave ──all enemies gone──▶ perk ──1/2/3──▶ build
                │                         │
                │ castle HP = 0           └─ after wave 5, 10, 15… ──▶ levelup ──Enter──▶ build (+1 path)
                ▼
              over ◀──Y── confirm ◀──K/Q── (any playing state)
```

**Path generation** (`place_castle`, `gen_path`, `score_path`, `add_path`): the castle sits on the
right edge with several entry tiles around it. Each new path starts on the next map edge (west, then
north, then south). It is built from random waypoints joined by straight segments, and any loops are cut out.
The generator makes 250 candidate paths and scores each one. It avoids paths that run over towers,
overlap other paths, touch themselves or run alongside other paths, and it prefers paths of a good length.
The best-scoring candidate wins.

**Combat** (`update`, `fire`, `hit`, `boss_ability`): every frame, each weapon whose cooldown is ready
looks at the enemies in range. Most weapons target the enemy with the fewest tiles left to the castle,
the Sniper targets the one with the most HP, and the Flamer hits all of them. Cannons damage everything
in their splash radius, Frost slows, Poison applies damage over time, and Tesla chains to nearby enemies.
All direct hits go through `hit()`, which applies boss armor. Poison damage skips it.

**Decorations** (`make_deco`): a few random "forest centers" are picked. Trees are likely near them,
and flowers are scattered everywhere else. New paths and new structures clear what's in their way.

## Project history

Full details are in [CHANGELOG.md](CHANGELOG.md). Each version is tagged in Git, so
`git diff v0.1.0 v0.2.0` shows exactly what changed.

| Version | Date | Commit | Highlights | `keep.py` size |
| --- | --- | --- | --- | --- |
| 0.0.0 | 2026-10-12 | `f9ef6a2` | Repository created | — |
| [0.1.0](CHANGELOG.md#010---2026-10-12) | 2026-10-12 | `d2ddb55` | First playable tower defense: weapons, waves, blessings, gems, gem shop | 834 lines |
| [0.2.0](CHANGELOG.md#020---2026-10-12) | 2026-10-12 | `cc20d54` | Full-screen map, 5-wave levels, +1 enemy path per level, mouse support | 1037 lines |
| [0.3.0](CHANGELOG.md#030---2026-10-12) | 2026-10-12 | `e973e43` | Renamed to *cool tower defense game.exe*, full-width map with HUD below, menu buttons + Upgrades screen, standard README and CHANGELOG | 1218 lines |
| [0.4.0](CHANGELOG.md#040---2026-10-12) | 2026-10-12 | tag `v0.4.0` | Side panel back on the right, 8 weapons with live stats, 5 big bosses, trees and flowers | 1425 lines |

## Contributing

- **Branches:** `main` is the stable, playable version. Try new things on `test` (or a feature
  branch) and merge into `main` once it works.
- **Changelog:** every change that players or developers would notice gets a line under
  `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md), grouped as *Added*, *Changed*, *Fixed* or *Removed*.
- **Releases:** when you release, rename `Unreleased` to the new version and date, bump the version
  badge in this README, and tag the commit:
  ```bash
  git tag -a v0.3.0 -m "v0.3.0"
  git push origin v0.3.0
  ```
  Versions follow [SemVer](https://semver.org/): new features bump the minor version (0.**3**.0),
  and fixes bump the patch version (0.3.**1**).
- **Commits:** use short imperative summaries, e.g. `Add flying enemies` or `Fix cursor on small terminals`.
- **Before pushing:** run `python3 -m py_compile keep.py`, then play at least one wave.

## Roadmap

These are ideas, not promises:

- [ ] Flying enemies that ignore the path
- [ ] Sound effects (terminal bell)
- [ ] Local high-score table
- [ ] Automated smoke tests in CI

## Authors

- **Ádám Zsidákovits**
- **Cristian-Mihai Radu**

Built for the B.A.L.L.S hackathon, with AI pair-programming help from Claude.

## License

No license has been chosen yet, so all rights are reserved by the authors.
To let others reuse the code, add a `LICENSE` file (for example MIT).
