# Ball-Heckaton-ascii-game
This is an Ascii game made by Ádám Zsidákovits and Cristian-Mihai Radu for the B.A.L.L.S heckaton

## ASCII KEEP — a roguelike tower defense

Enemies march down randomly generated paths toward your castle. Build structures,
mount weapons on them, and survive as many levels as you can. When the castle falls
you **keep your gems** and spend them on permanent upgrades for the next run.

The map fills your whole terminal, so make the window big (or full screen) before starting.

```
+--------------------------------------------------+  WAVE 1  WAVE ACTIVE
|>>::::::     '  ::  ::.      '   .    .      '   .|  CASTLE ########## 30/30
|.     ::   .    ::  :: '   .    .      '   .    . |  GOLD   10
|   .  o:.      ':: .::  .   :: '  ::    .      '  |
|  .   :: '   .  o:. ::   .  ::    ::     '   .    |  B  structure    10g
|   '  o:o:o:o:::o: ':: . A2 .::   ::   .    .     |  1  Bow          25g
| .    .      '   .  :: . G1 .::   .::  .     /^^\ |  2  Gun          40g
|    .      '   .    :::::::::: .  ::::::::::::|[]||  3  Cannon       locked
+--------------------------------------------------+
```

### Run it

```
python3 keep.py
```

Needs Python 3 and a terminal of at least 70x22 (bigger = bigger map). Works out of the box on macOS and Linux.
On Windows run `pip install windows-curses` first.

### How to play

1. Move the cursor onto a grass tile and press **B** to build a structure `[]`.
2. Press **1-4** to mount a weapon on it:

   | Key | Weapon | Cost | |
   | --- | --- | --- | --- |
   | 1 | Bow `A` | 25g | steady single-target damage |
   | 2 | Gun `G` | 40g | very fast, short range |
   | 3 | Cannon `C` | 60g | slow, splash damage (unlock with gems) |
   | 4 | Frost `F` | 45g | slows enemies (unlock with gems) |

3. Press **N** to send the next wave. Kills give gold; clearing waves gives gold and gems.
4. After every wave pick **1 of 3 random blessings** (more gold, castle repair, faster guns...).

### Levels

Each **level is 5 waves**, and wave 5 is a boss `M`. Beat all 5 and you get a level reward
(gold, gems, castle repair), then you can start the next level, which **opens one more path**
to your castle:

| Level | Paths | Enemies come from |
| --- | --- | --- |
| 1 | 1 | west `>>` |
| 2 | 2 | west + north `vv` |
| 3 | 3 | west + north + south `^^` |
| 4+ | +1 each level | ... |

The new path blinks red for a few seconds. If it runs over one of your towers, that tower
is removed and you get its full cost back.

**Losing is part of the game.** When the castle is destroyed you keep the gems from that run.
You can also **blow up your own castle (K)** to cash out early; every 25 leftover gold becomes
an extra gem. Quitting with Q forfeits the run's gems.

Spend gems in the main menu: more castle HP, more starting gold, more damage, more gems,
and unlocking the Cannon and Frost tower. Progress is saved in `keep_save.json`.

### Controls

| Key | Action |
| --- | --- |
| Arrows / wasd | move cursor (Shift+WASD jumps 5 tiles, or click with the mouse) |
| B | build structure |
| 1-4 | mount weapon |
| U | upgrade weapon (max level 5) |
| X | sell (50% refund) |
| N | start next wave |
| F | game speed x1 / x2 / x3 |
| P | pause |
| K | destroy your own castle (cash out) |
| Q | quit run |

Enemies: `o` grunt, `r` runner (fast), `B` brute (tanky), `M` boss. An enemy turns blue
while slowed, and the dot after its letter shows how much health it has left.
