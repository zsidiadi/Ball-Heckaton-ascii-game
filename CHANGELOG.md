# Changelog

All notable changes to **ASCII KEEP** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Every version links to its Git tag, so you can see exactly how the code changed between versions.

## [Unreleased]

### Added
- README rewritten in a standard open-source layout: features, install, full gameplay
  reference, architecture overview, tuning guide, contributing rules and project history.
- `CHANGELOG.md` (this file), covering the project's history from the first commit.
- Git tags `v0.1.0` and `v0.2.0` marking the two earlier releases.

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

[Unreleased]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/compare/f9ef6a2...v0.1.0
[0.0.0]: https://github.com/zsidiadi/Ball-Heckaton-ascii-game/commit/f9ef6a228a87bdbaf17ee5fcb89c06409e78d5bc
