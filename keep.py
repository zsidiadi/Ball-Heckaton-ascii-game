#!/usr/bin/env python3
"""
ASCII KEEP - a roguelike tower defense for the terminal.

Protect your castle from waves of enemies walking down random paths.
  1. Build a STRUCTURE on a grass tile           (B)
  2. Mount a WEAPON on that structure            (1-4)
  3. Upgrade or sell it                          (U / X)
The game is split into LEVELS of 5 waves (wave 5 has a boss). Beat a level
and the next one opens ONE MORE enemy path to your castle.
After every wave you pick one of three random blessings.
When the castle falls you KEEP the gems you earned. You can also blow up
your own castle (K) to cash out early: leftover gold turns into bonus gems.
Spend gems in the main menu on permanent upgrades and new weapons.

Run:  python3 keep.py          (Windows: pip install windows-curses first)
"""

import curses
import json
import os
import random
import time

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keep_save.json")
FPS = 30
DT = 1.0 / FPS
MIN_W, MIN_H = 70, 22
MAP_X, MAP_Y = 1, 2          # screen position of the top-left map cell
PANEL_W = 28                 # width of the info panel on the right

# colour pair ids
GRASS, PATH, STRUCT, C_BOW, C_GUN, C_CANNON, C_FROST, RED, CASTLE, GOLD, GEM, CURSOR, MAG = range(1, 14)

STRUCT_COST = 10
MAX_LEVEL = 5
WAVES_PER_LEVEL = 5

EDGES = ["left", "top", "bottom"]          # where new paths start, in this order
EDGE_NAMES = {"left": "WEST", "top": "NORTH", "bottom": "SOUTH"}

WEAPONS = {
    "bow":    dict(key="1", name="Bow",    ch="A", cost=25, dmg=3.0, rng=3.5, cd=0.70, color=C_BOW,
                   info="steady single-target"),
    "gun":    dict(key="2", name="Gun",    ch="G", cost=40, dmg=1.0, rng=3.0, cd=0.18, color=C_GUN,
                   info="very fast, short range"),
    "cannon": dict(key="3", name="Cannon", ch="C", cost=60, dmg=7.0, rng=4.0, cd=1.80, color=C_CANNON,
                   splash=1.3, info="slow, splash damage"),
    "frost":  dict(key="4", name="Frost",  ch="F", cost=45, dmg=0.6, rng=3.0, cd=0.50, color=C_FROST,
                   slow=1.2, info="slows enemies"),
}
WEAPON_ORDER = ["bow", "gun", "cannon", "frost"]

ENEMIES = {
    "grunt":  dict(ch="o", hp=8,   spd=1.5,  dmg=1,  gold=3,  color=RED),
    "runner": dict(ch="r", hp=5,   spd=2.8,  dmg=1,  gold=3,  color=MAG),
    "brute":  dict(ch="B", hp=32,  spd=0.85, dmg=3,  gold=8,  color=RED),
    "boss":   dict(ch="M", hp=160, spd=0.6,  dmg=10, gold=40, color=MAG),
}
HP_GROWTH = 1.25             # enemy HP multiplier per wave

# permanent upgrades bought with gems: id, name, description, base cost, max level
META_UPGRADES = [
    ("walls",  "Thick Walls",     "+10 castle HP",            3, 10),
    ("chest",  "War Chest",       "+20 starting gold",        3, 10),
    ("sharp",  "Sharpened Steel", "+10% weapon damage",       4, 10),
    ("magnet", "Gem Magnet",      "+25% gems earned",         5, 5),
    ("cannon", "Unlock Cannon",   "cannons: splash damage",   8, 1),
    ("frost",  "Unlock Frost",    "frost towers slow enemies", 10, 1),
]

TITLE = [
    "    _    ____   ____ ___ ___     _  __ ___ ___ ___ ",
    "   /_\\  / ___| / ___|_ _|_ _|   | |/ /| __| __| _ \\",
    "  / _ \\ \\___ \\| |    | | | |    | ' < | _|| _||  _/",
    " /_/ \\_\\|____/ \\____|___|___|   |_|\\_\\|___|___|_|  ",
]


# ------------------------------------------------------------------ save data
def load_meta():
    data = {"gems": 0, "best": 0, "best_level": 0, "runs": 0, "up": {}}
    try:
        with open(SAVE_FILE) as f:
            data.update(json.load(f))
    except (OSError, ValueError):
        pass
    return data


def save_meta(meta):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(meta, f, indent=1)
    except OSError:
        pass


def meta_cost(base, level):
    return base * (level + 1)


# ------------------------------------------------------------------ blessings
def p_gold(r): r.gold += 40
def p_repair(r): r.max_hp += 5; r.hp = min(r.max_hp, r.hp + 15)
def p_bow(r): r.mods["wdmg"]["bow"] *= 1.3
def p_gun(r): r.mods["wcd"]["gun"] *= 0.8
def p_cannon(r): r.mods["wdmg"]["cannon"] *= 1.3; r.mods["splash"] += 0.5
def p_frost(r): r.mods["wdmg"]["frost"] *= 1.5; r.mods["slow"] += 0.6
def p_range(r): r.mods["range"] += 0.5
def p_tar(r): r.mods["enemy_speed"] *= 0.9
def p_bounty(r): r.mods["bounty"] += 1
def p_bricks(r): r.mods["struct_cost"] = max(2, r.mods["struct_cost"] // 2)
def p_gems(r): r.gems_raw += 2
def p_steel(r):
    for k in r.mods["wdmg"]:
        r.mods["wdmg"][k] *= 1.1


PERKS = [
    ("Gold Rush",    "+40 gold right now",              p_gold,   None),
    ("Mason",        "repair castle +15, max HP +5",    p_repair, None),
    ("Fletcher",     "Bows deal +30% damage",           p_bow,    "bow"),
    ("Gunsmith",     "Guns fire 25% faster",            p_gun,    "gun"),
    ("Black Powder", "Cannons +30% dmg, bigger blast",  p_cannon, "cannon"),
    ("Deep Freeze",  "Frost +50% dmg, slows longer",    p_frost,  "frost"),
    ("Eagle Eye",    "all weapons +0.5 range",          p_range,  None),
    ("Tar Pits",     "new enemies move 10% slower",     p_tar,    None),
    ("Bounty",       "+1 gold per kill",                p_bounty, None),
    ("Cheap Bricks", "structures cost half",            p_bricks, None),
    ("Gem Shard",    "+2 gems right now",               p_gems,   None),
    ("Whetstone",    "all weapons +10% damage",         p_steel,  None),
]


# ------------------------------------------------------------------ entities
class Enemy:
    def __init__(self, kind, wave, speed_mult, path):
        t = ENEMIES[kind]
        scale = HP_GROWTH ** (wave - 1)
        self.kind = kind
        self.ch = t["ch"]
        self.color = t["color"]
        self.hp = self.maxhp = t["hp"] * scale
        self.spd = t["spd"] * speed_mult
        self.dmg = t["dmg"]
        self.gold = t["gold"]
        self.path = path
        self.pos = 0.0
        self.slow_t = 0.0
        self.leaked = False

    def cell(self):
        return self.path[int(self.pos)]

    def left(self):
        return len(self.path) - 1 - self.pos


class Tower:
    def __init__(self, invested):
        self.kind = None      # None = bare structure
        self.level = 0
        self.cd = 0.0
        self.invested = invested


# ------------------------------------------------------------------ one run
class Run:
    def __init__(self, W, H, meta):
        self.W, self.H, self.meta = W, H, meta
        up = meta["up"]
        self.max_hp = 20 + 10 * up.get("walls", 0)
        self.hp = self.max_hp
        self.gold = 60 + 20 * up.get("chest", 0)
        self.dmg_mult = 1 + 0.10 * up.get("sharp", 0)
        self.gem_mult = 1 + 0.25 * up.get("magnet", 0)
        self.unlocked = {"bow", "gun"} | {k for k in ("cannon", "frost") if up.get(k)}
        self.mods = dict(enemy_speed=1.0, range=0.0, struct_cost=STRUCT_COST, bounty=0,
                         splash=0.0, slow=0.0,
                         wdmg={k: 1.0 for k in WEAPONS}, wcd={k: 1.0 for k in WEAPONS})
        # bigger maps have longer paths, so enemies walk a bit faster there
        self.map_speed = min(1.6, max(1.0, ((W + H) / 44.0) ** 0.5))
        self.level = 1
        self.wave = 0
        self.cleared = 0
        self.kills = 0
        self.gems_raw = 0.0
        self.towers = {}
        self.enemies = []
        self.spawn_queue = []
        self.spawn_t = 0.0
        self.spawn_gap = 1.0
        self.spawn_i = 0
        self.effects = []
        self.speed = 1
        self.state = "build"   # build, wave, perk, levelup, paused, confirm, over
        self.prev_state = "build"
        self.confirm = None
        self.offer = []
        self.wave_msg = ""
        self.level_info = []
        self.done = False
        self.final = None
        self.paths = []
        self.path_set = set()
        self.newest = set()
        self.new_path_t = 0.0
        self.place_castle()
        self.add_path()
        self.cursor = list(self.near_free(self.paths[0][len(self.paths[0]) // 2]))
        self.msg = "Build a structure (B), mount a weapon (1-4), then press N to start."

    # -------------------------------------------------------------- map
    def place_castle(self):
        W, H = self.W, self.H
        cy = random.randint(max(3, H // 4), min(H - 4, 3 * H // 4))
        self.castle_y = cy
        self.castle_cells = {(cx, y) for cx in (W - 2, W - 1) for y in (cy - 1, cy, cy + 1)}
        # grass cells touching the castle where a path can end, in order of use
        self.entries = [(W - 3, cy), (W - 2, cy - 2), (W - 2, cy + 2),
                        (W - 3, cy - 1), (W - 3, cy + 1), (W - 1, cy - 2), (W - 1, cy + 2)]

    def gen_path(self, start, end):
        """Random wiggly path made of straight segments between waypoints."""
        W, H = self.W, self.H
        (sx, sy), (ex, ey) = start, end
        k = random.randint(2, 3) + (W + H) // 40
        pts = []
        for i in range(1, k + 1):
            t = i / (k + 1)
            px = sx + (ex - sx) * t + random.uniform(-0.3, 0.3) * W
            py = sy + (ey - sy) * t + random.uniform(-0.45, 0.45) * H
            pts.append((int(min(max(px, 1), W - 5)), int(min(max(py, 1), H - 2))))
        pts.append(end)
        cells = [start]
        for bx, by in pts:
            x, y = cells[-1]
            if random.random() < 0.5:
                while x != bx:
                    x += 1 if bx > x else -1
                    cells.append((x, y))
                while y != by:
                    y += 1 if by > y else -1
                    cells.append((x, y))
            else:
                while y != by:
                    y += 1 if by > y else -1
                    cells.append((x, y))
                while x != bx:
                    x += 1 if bx > x else -1
                    cells.append((x, y))
        # cut out loops so the path never visits a cell twice
        out, index = [], {}
        for c in cells:
            if c in index:
                cut = index[c]
                for d in out[cut + 1:]:
                    del index[d]
                del out[cut + 1:]
            else:
                index[c] = len(out)
                out.append(c)
        if any(c in self.castle_cells for c in out):
            return None
        return out

    def score_path(self, cells):
        idx = {c: i for i, c in enumerate(cells)}
        towers = overlap = touch = beside = 0
        for i, (x, y) in enumerate(cells):
            if (x, y) in self.towers:
                towers += 1
            if (x, y) in self.path_set:
                overlap += 1
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                j = idx.get(n)
                if j is not None and abs(j - i) > 1:
                    touch += 1
                if n in self.path_set and (x, y) not in self.path_set:
                    beside += 1
        target = 1.3 * (self.W + self.H)
        return towers * 1000 + overlap * 4 + touch * 3 + beside + abs(len(cells) - target) * 0.5

    def add_path(self):
        """Open one more enemy path to the castle. Returns (edge, towers crushed, refund)."""
        W, H = self.W, self.H
        edge = EDGES[len(self.paths) % len(EDGES)]
        used = {p[-1] for p in self.paths}
        free_entries = [e for e in self.entries if e not in used]
        end = free_entries[0] if free_entries else random.choice(self.entries)
        starts = [p[0] for p in self.paths]
        best = None
        for attempt in range(250):
            if edge == "left":
                start = (0, random.randint(1, H - 2))
            elif edge == "top":
                start = (random.randint(0, max(1, W - 8)), 0)
            else:
                start = (random.randint(0, max(1, W - 8)), H - 1)
            if start in self.path_set or start in self.towers:
                continue
            if attempt < 200 and any(abs(start[0] - s[0]) + abs(start[1] - s[1]) < 6 for s in starts):
                continue
            cells = self.gen_path(start, end)
            if not cells:
                continue
            sc = self.score_path(cells)
            if best is None or sc < best[0]:
                best = (sc, cells)
        if best is None:   # practically impossible, but never leave the map without a path
            cy = self.castle_y
            best = (0, [(x, cy) for x in range(0, W - 2)])
        cells = best[1]
        crushed = [c for c in cells if c in self.towers]
        refund = sum(self.towers[c].invested for c in crushed)
        for c in crushed:
            del self.towers[c]
        self.gold += refund
        self.paths.append(cells)
        self.path_set |= set(cells)
        self.newest = set(cells)
        self.new_path_t = 6.0
        return edge, len(crushed), refund

    def near_free(self, c):
        for r in range(1, 4):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    n = (c[0] + dx, c[1] + dy)
                    if 0 <= n[0] < self.W and 0 <= n[1] < self.H and self.free(n):
                        return n
        return c

    def free(self, c):
        return c not in self.path_set and c not in self.castle_cells and c not in self.towers

    # -------------------------------------------------------------- stats
    def stats(self, t):
        w = WEAPONS[t.kind]
        lv = t.level - 1
        s = dict(
            dmg=w["dmg"] * (1.4 ** lv) * self.dmg_mult * self.mods["wdmg"][t.kind],
            rng=w["rng"] + 0.3 * lv + self.mods["range"],
            cd=w["cd"] * (0.92 ** lv) * self.mods["wcd"][t.kind],
        )
        if "splash" in w:
            s["splash"] = w["splash"] + self.mods["splash"]
        if "slow" in w:
            s["slow"] = w["slow"] + self.mods["slow"]
        return s

    def upgrade_cost(self, t):
        return int(WEAPONS[t.kind]["cost"] * 0.75 * t.level)

    def wave_in_level(self):
        return (self.wave - 1) % WAVES_PER_LEVEL + 1 if self.wave else 0

    # -------------------------------------------------------------- waves & levels
    def start_wave(self):
        self.wave += 1
        n = self.wave
        boss = self.wave_in_level() == WAVES_PER_LEVEL
        q = []
        for _ in range(5 + 2 * n):
            r = random.random()
            if n >= 4 and r < min(0.25, 0.04 * n):
                q.append("brute")
            elif n >= 2 and r < 0.45:
                q.append("runner")
            else:
                q.append("grunt")
        if boss:
            q.append("boss")
        self.spawn_queue = q
        self.spawn_gap = max(0.3, 0.9 - 0.04 * n) / (1 + 0.1 * (len(self.paths) - 1))
        self.spawn_t = 0.0
        self.state = "wave"
        self.msg = (f"Level {self.level}, wave {self.wave_in_level()}/{WAVES_PER_LEVEL} incoming! "
                    f"({len(q)} enemies{', BOSS!' if boss else ''})")

    def wave_cleared(self):
        bonus = 8 + 2 * self.wave
        self.gold += bonus
        g = (1 + self.wave // 10) * self.gem_mult
        self.gems_raw += g
        self.cleared = self.wave
        pool = [p for p in PERKS if p[3] is None or p[3] in self.unlocked]
        self.offer = random.sample(pool, 3)
        self.wave_msg = (f"LEVEL {self.level} - WAVE {self.wave_in_level()}/{WAVES_PER_LEVEL} CLEARED!"
                         f"   +{bonus} gold   +{g:.1f} gems")
        self.state = "perk"

    def level_complete(self):
        lv = self.level
        gold = 40 + 20 * lv
        gems = 2 * lv * self.gem_mult
        heal = min(self.max_hp - self.hp, self.max_hp // 4)
        self.gold += gold
        self.gems_raw += gems
        self.hp += heal
        nxt = EDGES[len(self.paths) % len(EDGES)]
        self.level_info = [
            f"*** LEVEL {lv} COMPLETE! ***", "",
            (f"castle repaired +{heal}" if heal else "castle at full health") +
            f"    +{gold} gold    +{gems:.1f} gems", "",
            f"LEVEL {lv + 1}: a new path opens from the {EDGE_NAMES[nxt]}!",
            f"Enemies will attack from {len(self.paths) + 1} directions.", "",
            "ENTER  start next level",
            "K      blow up the castle and cash out",
        ]
        self.meta["best_level"] = max(self.meta.get("best_level", 0), lv)
        save_meta(self.meta)
        self.state = "levelup"

    def next_level(self):
        self.level += 1
        edge, crushed, refund = self.add_path()
        self.msg = f"LEVEL {self.level}! A new path opened from the {EDGE_NAMES[edge]} (blinking red)."
        if crushed:
            self.msg += f" It crushed {crushed} tower(s): +{refund} gold refunded."
        self.state = "build"

    def end(self, manual):
        bonus = self.gold // 25 if manual else 0
        gems = int(self.gems_raw) + bonus
        self.final = dict(manual=manual, gems=gems, bonus=bonus, waves=self.cleared,
                          kills=self.kills, level=self.level)
        self.meta["gems"] += gems
        self.meta["best"] = max(self.meta.get("best", 0), self.cleared)
        self.meta["best_level"] = max(self.meta.get("best_level", 0), self.level)
        self.meta["runs"] = self.meta.get("runs", 0) + 1
        save_meta(self.meta)
        self.state = "over"

    # -------------------------------------------------------------- simulation
    def update(self, dt):
        self.effects = [[x, y, ch, col, t - dt] for x, y, ch, col, t in self.effects if t - dt > 0]
        self.new_path_t = max(0.0, self.new_path_t - dt)
        if self.state != "wave":
            return
        self.spawn_t -= dt
        if self.spawn_queue and self.spawn_t <= 0:
            path = self.paths[self.spawn_i % len(self.paths)]
            self.spawn_i += 1
            speed = self.mods["enemy_speed"] * self.map_speed
            self.enemies.append(Enemy(self.spawn_queue.pop(0), self.wave, speed, path))
            self.spawn_t = self.spawn_gap

        for e in self.enemies:
            spd = e.spd * (0.5 if e.slow_t > 0 else 1.0)
            e.slow_t = max(0.0, e.slow_t - dt)
            e.pos += spd * dt
            last = len(e.path) - 1
            if e.pos >= last:
                e.pos = last
                e.hp = 0
                e.leaked = True
                self.hp -= e.dmg
                self.msg = f"The castle was hit for {e.dmg}!"
                for c in self.castle_cells:
                    self.effects.append([c[0], c[1], "!", RED, 0.3])

        for (x, y), t in self.towers.items():
            if not t.kind:
                continue
            t.cd -= dt
            if t.cd > 0:
                continue
            s = self.stats(t)
            r2 = s["rng"] ** 2
            target = None
            for e in self.enemies:
                if e.hp <= 0:
                    continue
                ex, ey = e.cell()
                if (ex - x) ** 2 + (ey - y) ** 2 <= r2 and (target is None or e.left() < target.left()):
                    target = e
            if target:
                t.cd = s["cd"]
                self.fire(x, y, t, s, target)

        alive = []
        for e in self.enemies:
            if e.hp > 0:
                alive.append(e)
            elif not e.leaked:
                self.kills += 1
                self.gold += e.gold + self.mods["bounty"]
                if e.kind == "boss":
                    self.gems_raw += 3 * self.gem_mult
                    self.msg = "BOSS SLAIN! +3 gems"
                elif e.kind == "brute" and random.random() < 0.1:
                    self.gems_raw += 1 * self.gem_mult
                    self.msg = "The brute dropped a gem!"
        self.enemies = alive

        if self.hp <= 0:
            self.hp = 0
            self.end(manual=False)
        elif not self.spawn_queue and not self.enemies:
            self.wave_cleared()

    def fire(self, x, y, t, s, target):
        tx, ty = target.cell()
        if t.kind == "cannon":
            for e in self.enemies:
                if e.hp <= 0:
                    continue
                ex, ey = e.cell()
                if (ex - tx) ** 2 + (ey - ty) ** 2 <= s["splash"] ** 2:
                    e.hp -= s["dmg"]
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                self.effects.append([tx + dx, ty + dy, "*", C_CANNON, 0.25])
        elif t.kind == "frost":
            target.hp -= s["dmg"]
            target.slow_t = max(target.slow_t, s["slow"])
            self.effects.append([tx, ty, "~", C_FROST, 0.2])
        else:
            target.hp -= s["dmg"]
            mx, my = round((x + tx) / 2), round((y + ty) / 2)
            self.effects.append([mx, my, "-" if t.kind == "gun" else "'", WEAPONS[t.kind]["color"], 0.08])
            self.effects.append([tx, ty, "x", WEAPONS[t.kind]["color"], 0.1])

    # -------------------------------------------------------------- input
    def click(self, x, y):
        if self.state in ("build", "wave") and 0 <= x < self.W and 0 <= y < self.H:
            self.cursor = [x, y]

    def key(self, k):
        st = self.state
        if st == "over":
            if k in (10, 13, curses.KEY_ENTER, ord(" ")):
                self.done = True
            return
        if st == "confirm":
            if k in (ord("y"), ord("Y")):
                if self.confirm == "destroy":
                    self.end(manual=True)
                else:
                    self.meta["best"] = max(self.meta.get("best", 0), self.cleared)
                    save_meta(self.meta)
                    self.done = True
            elif k in (ord("n"), ord("N"), 27):
                self.state = self.prev_state
            return
        if st == "perk":
            if k in (ord("1"), ord("2"), ord("3")):
                name, desc, fn, _ = self.offer[k - ord("1")]
                fn(self)
                self.msg = f"Blessing: {name} - {desc}. Press N for the next wave."
                self.state = "build"
                if self.wave % WAVES_PER_LEVEL == 0:
                    self.level_complete()
            return
        if k in (ord("q"), ord("Q"), ord("k"), ord("K")) and st != "paused":
            self.prev_state = st
            self.confirm = "destroy" if k in (ord("k"), ord("K")) else "quit"
            self.state = "confirm"
            return
        if st == "levelup":
            if k in (10, 13, curses.KEY_ENTER, ord(" ")):
                self.next_level()
            return
        if k in (ord("p"), ord("P")):
            if st == "paused":
                self.state = self.prev_state
            else:
                self.prev_state, self.state = st, "paused"
            return
        if st == "paused":
            return

        cx, cy = self.cursor
        moves = {curses.KEY_LEFT: (-1, 0), ord("a"): (-1, 0), ord("A"): (-5, 0),
                 curses.KEY_RIGHT: (1, 0), ord("d"): (1, 0), ord("D"): (5, 0),
                 curses.KEY_UP: (0, -1), ord("w"): (0, -1), ord("W"): (0, -5),
                 curses.KEY_DOWN: (0, 1), ord("s"): (0, 1), ord("S"): (0, 5)}
        if k in moves:
            dx, dy = moves[k]
            self.cursor = [min(self.W - 1, max(0, cx + dx)), min(self.H - 1, max(0, cy + dy))]
        elif k in (ord("f"), ord("F")):
            self.speed = self.speed % 3 + 1
            self.msg = f"Game speed x{self.speed}"
        elif k in (ord("n"), ord("N")):
            if st == "build":
                self.start_wave()
            else:
                self.msg = "A wave is already in progress!"
        elif k in (ord("b"), ord("B")):
            self.build_structure()
        elif k in (ord("u"), ord("U")):
            self.upgrade()
        elif k in (ord("x"), ord("X")):
            self.sell()
        else:
            for kind in WEAPON_ORDER:
                if k == ord(WEAPONS[kind]["key"]):
                    self.add_weapon(kind)

    def build_structure(self):
        c = tuple(self.cursor)
        cost = self.mods["struct_cost"]
        if c in self.path_set or c in self.castle_cells:
            self.msg = "You can't build on the path or the castle."
        elif c in self.towers:
            self.msg = "There's already a structure here. Add a weapon with 1-4."
        elif self.gold < cost:
            self.msg = f"Not enough gold (need {cost})."
        else:
            self.gold -= cost
            self.towers[c] = Tower(cost)
            self.msg = "Structure built! Now mount a weapon: 1 Bow, 2 Gun, 3 Cannon, 4 Frost."

    def add_weapon(self, kind):
        c = tuple(self.cursor)
        w = WEAPONS[kind]
        t = self.towers.get(c)
        if kind not in self.unlocked:
            self.msg = f"{w['name']} is locked. Unlock it with gems in the main menu."
        elif t is None:
            self.msg = f"Build a structure first (B, {self.mods['struct_cost']}g), then add the {w['name']}."
        elif t.kind:
            self.msg = "This structure already has a weapon. U to upgrade, X to sell."
        elif self.gold < w["cost"]:
            self.msg = f"Not enough gold for a {w['name']} (need {w['cost']})."
        else:
            self.gold -= w["cost"]
            t.kind, t.level, t.cd = kind, 1, 0.0
            t.invested += w["cost"]
            self.msg = f"{w['name']} mounted - {w['info']}."

    def upgrade(self):
        t = self.towers.get(tuple(self.cursor))
        if not t or not t.kind:
            self.msg = "Nothing to upgrade here."
            return
        if t.level >= MAX_LEVEL:
            self.msg = "Already max level."
            return
        cost = self.upgrade_cost(t)
        if self.gold < cost:
            self.msg = f"Upgrade costs {cost} gold."
            return
        self.gold -= cost
        t.level += 1
        t.invested += cost
        self.msg = f"{WEAPONS[t.kind]['name']} upgraded to level {t.level}!"

    def sell(self):
        c = tuple(self.cursor)
        t = self.towers.get(c)
        if not t:
            self.msg = "Nothing to sell here."
            return
        refund = t.invested // 2
        self.gold += refund
        del self.towers[c]
        self.msg = f"Sold for {refund} gold."


# ------------------------------------------------------------------ app / drawing
class App:
    def __init__(self, scr):
        self.scr = scr
        self.meta = load_meta()
        self.state = "menu"
        self.run = None
        self.running = True
        self.menu_msg = ""
        self.anim = 0.0

    def color(self, n):
        return curses.color_pair(n) if curses.has_colors() else 0

    def put(self, y, x, s, attr=0):
        h, w = self.scr.getmaxyx()
        if y < 0 or y >= h or x >= w - 1:
            return
        if x < 0:
            s, x = s[-x:], 0
        try:
            self.scr.addstr(y, x, s[: w - 1 - x], attr)
        except curses.error:
            pass

    def center(self, y, s, attr=0):
        w = self.scr.getmaxyx()[1]
        self.put(y, max(0, (w - len(s)) // 2), s, attr)

    def box(self, lines, attr=0):
        h, w = self.scr.getmaxyx()
        bw = max(len(s) for s in lines) + 4
        top = max(0, (h - len(lines)) // 2 - 1)
        left = max(0, (w - bw) // 2)
        self.put(top, left, "+" + "-" * (bw - 2) + "+", attr)
        for i, s in enumerate(lines):
            self.put(top + 1 + i, left, "| " + s.ljust(bw - 4) + " |", attr)
        self.put(top + 1 + len(lines), left, "+" + "-" * (bw - 2) + "+", attr)

    # -------------------------------------------------------------- input
    def key(self, k):
        if k == curses.KEY_MOUSE:
            try:
                _, mx, my, _, _ = curses.getmouse()
            except curses.error:
                return
            if self.state == "run" and mx >= MAP_X:
                self.run.click((mx - MAP_X) // 2, my - MAP_Y)
            return
        if self.state == "menu":
            if k in (ord("q"), ord("Q")):
                self.running = False
            elif k in (10, 13, curses.KEY_ENTER, ord(" ")):
                self.new_run()
            elif ord("1") <= k <= ord(str(len(META_UPGRADES))):
                self.buy(k - ord("1"))
        else:
            self.run.key(k)
            if self.run.done:
                self.state = "menu"
                self.run = None

    def buy(self, i):
        uid, name, desc, base, mx = META_UPGRADES[i]
        lv = self.meta["up"].get(uid, 0)
        if lv >= mx:
            self.menu_msg = f"{name} is already maxed."
            return
        cost = meta_cost(base, lv)
        if self.meta["gems"] < cost:
            self.menu_msg = f"{name} costs {cost} gems - you have {self.meta['gems']}."
            return
        self.meta["gems"] -= cost
        self.meta["up"][uid] = lv + 1
        save_meta(self.meta)
        self.menu_msg = f"Bought {name}!"

    def new_run(self):
        # the map fills the whole terminal, minus the info panel on the right
        h, w = self.scr.getmaxyx()
        W = max(19, min(120, (w - MAP_X - 3 - PANEL_W) // 2))
        H = max(14, min(70, h - MAP_Y - 2))
        self.run = Run(W, H, self.meta)
        self.state = "run"

    def update(self, dt):
        self.anim += dt
        if self.state == "run":
            for _ in range(self.run.speed):
                self.run.update(dt)

    # -------------------------------------------------------------- draw
    def draw(self):
        self.scr.erase()
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_run()
        self.scr.refresh()

    def draw_menu(self):
        m = self.meta
        h = self.scr.getmaxyx()[0]
        y = max(1, (h - 24) // 2)
        for line in TITLE:
            self.center(y, line, self.color(CASTLE) | curses.A_BOLD)
            y += 1
        y += 1
        self.center(y, "a roguelike tower defense  -  protect the keep, keep the gems", curses.A_DIM)
        y += 2
        self.center(y, f"GEMS: {m['gems']}    best: level {m.get('best_level', 0)}, wave {m.get('best', 0)}"
                       f"    runs: {m.get('runs', 0)}", self.color(GEM) | curses.A_BOLD)
        y += 2
        self.center(y, "-- GEM SHOP (permanent) --", curses.A_BOLD)
        y += 1
        w = self.scr.getmaxyx()[1]
        left = max(0, (w - 62) // 2)
        for i, (uid, name, desc, base, mx) in enumerate(META_UPGRADES):
            lv = m["up"].get(uid, 0)
            if lv >= mx:
                price = "MAXED" if mx > 1 else "OWNED"
            else:
                price = f"{meta_cost(base, lv)} gems"
            lvl = f"lv {lv}/{mx}" if mx > 1 else ""
            can = lv < mx and m["gems"] >= meta_cost(base, lv)
            attr = self.color(GEM) | curses.A_BOLD if can else (curses.A_DIM if lv >= mx else 0)
            self.put(y, left, f" {i + 1}) {name:<16} {desc:<26} {lvl:<8} {price}", attr)
            y += 1
        y += 1
        if self.menu_msg:
            self.center(y, self.menu_msg, self.color(GOLD))
        y += 2
        self.center(y, f"each level = {WAVES_PER_LEVEL} waves, every new level opens one more path to your castle",
                    curses.A_DIM)
        y += 2
        blink = curses.A_BOLD if int(self.anim * 2) % 2 else 0
        self.center(y, "ENTER  start a new run        1-6  buy upgrade        Q  quit", blink)

    def draw_run(self):
        r = self.run
        mx, my = MAP_X, MAP_Y
        W, H = r.W, r.H

        # header
        hdr = f" ASCII KEEP   level {r.level}   wave {r.wave_in_level()}/{WAVES_PER_LEVEL}   kills {r.kills}"
        self.put(0, 0, hdr, curses.A_BOLD)
        self.put(0, len(hdr) + 3, f"gem bank {self.meta['gems']}", self.color(GEM))

        # frame
        self.put(my - 1, mx - 1, "+" + "-" * (2 * W) + "+")
        self.put(my + H, mx - 1, "+" + "-" * (2 * W) + "+")
        for y in range(H):
            self.put(my + y, mx - 1, "|")
            self.put(my + y, mx + 2 * W, "|")

        # range preview of the tower under the cursor
        cur = tuple(r.cursor)
        ct = r.towers.get(cur)
        rng2 = r.stats(ct)["rng"] ** 2 if ct and ct.kind else -1

        starts = {}
        for p in r.paths:
            sx, sy = p[0]
            starts[p[0]] = ">>" if sx == 0 else ("vv" if sy == 0 else "^^")
        blink_new = r.new_path_t > 0 and int(self.anim * 4) % 2 == 0

        grass = ["  ", " .", "  ", " '", "  ", "  ", ". ", "  "]
        for y in range(H):
            for x in range(W):
                c = (x, y)
                if c in r.castle_cells:
                    continue
                if c in r.path_set:
                    s, a = ("::", self.color(PATH))
                    if c in starts:
                        s, a = (starts[c], self.color(RED) | curses.A_BOLD)
                    elif blink_new and c in r.newest:
                        a = self.color(RED) | curses.A_BOLD | curses.A_REVERSE
                elif c in r.towers:
                    t = r.towers[c]
                    if t.kind:
                        w = WEAPONS[t.kind]
                        s, a = (w["ch"] + str(t.level), self.color(w["color"]) | curses.A_REVERSE | curses.A_BOLD)
                    else:
                        s, a = ("[]", self.color(STRUCT) | curses.A_BOLD)
                else:
                    s = grass[(x * 7 + y * 13) % len(grass)]
                    a = self.color(GRASS) | curses.A_DIM
                    if rng2 >= 0 and (x - cur[0]) ** 2 + (y - cur[1]) ** 2 <= rng2:
                        s, a = (" .", self.color(WEAPONS[ct.kind]["color"]))
                self.put(my + y, mx + 2 * x, s, a)

        # castle
        cy = r.castle_y
        cx = mx + 2 * (W - 2)
        hp_frac = r.hp / max(1, r.max_hp)
        ca = self.color(RED if hp_frac < 0.3 else CASTLE) | curses.A_BOLD
        for i, row in enumerate(("/^^\\", "|[]|", "|__|")):
            self.put(my + cy - 1 + i, cx, row, ca)

        # enemies
        for e in r.enemies:
            x, y = e.cell()
            a = self.color(e.color) | curses.A_BOLD
            if e.slow_t > 0:
                a = self.color(C_FROST) | curses.A_BOLD
            frac = e.hp / e.maxhp
            tail = ":" if frac > 0.66 else ("." if frac > 0.33 else " ")
            self.put(my + y, mx + 2 * x, e.ch + tail, a)

        # effects
        for x, y, ch, col, _ in r.effects:
            if 0 <= x < W and 0 <= y < H:
                self.put(my + y, mx + 2 * x, ch, self.color(col) | curses.A_BOLD)

        # cursor
        x, y = r.cursor
        if int(self.anim * 4) % 2 == 0 or r.state != "wave":
            if r.free(cur):
                self.put(my + y, mx + 2 * x, "<>", self.color(CURSOR) | curses.A_REVERSE)
            else:
                self.put(my + y, mx + 2 * x - 1, "{", self.color(CURSOR) | curses.A_BOLD)
                self.put(my + y, mx + 2 * x + 2, "}", self.color(CURSOR) | curses.A_BOLD)

        self.draw_panel(mx + 2 * W + 3, my - 1)
        self.put(my + H + 1, 0, " " + r.msg, self.color(GOLD))

        # overlays
        if r.state == "perk":
            lines = [r.wave_msg, "", "Choose a blessing:", ""]
            for i, (name, desc, _, _) in enumerate(r.offer):
                lines.append(f" {i + 1}) {name:<13} {desc}")
            lines += ["", "press 1, 2 or 3"]
            self.box(lines, self.color(GOLD) | curses.A_BOLD)
        elif r.state == "levelup":
            self.box(r.level_info, self.color(C_BOW) | curses.A_BOLD)
        elif r.state == "paused":
            self.box(["      PAUSED      ", "", "  P to continue  "], curses.A_BOLD)
        elif r.state == "confirm":
            if r.confirm == "destroy":
                bonus = r.gold // 25
                lines = ["BLOW UP YOUR OWN CASTLE?", "",
                         f"You keep {int(r.gems_raw)} gems + {bonus} bonus gems",
                         "(every 25 leftover gold = 1 gem)", "", "Y = KABOOM      N = cancel"]
            else:
                lines = ["ABANDON THIS RUN?", "", "Gems from this run will be LOST.",
                         "(use K to blow up the castle and keep them)", "", "Y = abandon     N = cancel"]
            self.box(lines, self.color(RED) | curses.A_BOLD)
        elif r.state == "over":
            f = r.final
            title = "*** KABOOM! You destroyed your own keep ***" if f["manual"] else "*** THE KEEP HAS FALLEN ***"
            lines = [title, "", f"reached level:  {f['level']}", f"waves survived: {f['waves']}",
                     f"enemies slain:  {f['kills']}",
                     f"gems kept:      {f['gems']}" + (f"  (incl. {f['bonus']} from gold)" if f["bonus"] else ""),
                     f"gem bank now:   {self.meta['gems']}", "", "ENTER - back to the gem shop"]
            self.box(lines, self.color(RED if not f["manual"] else GOLD) | curses.A_BOLD)

    def draw_panel(self, px, py):
        r = self.run
        y = py
        bar_w = 10
        filled = int(bar_w * r.hp / max(1, r.max_hp))
        phase = {"build": "BUILD PHASE", "wave": "WAVE ACTIVE", "perk": "WAVE CLEARED",
                 "levelup": "LEVEL CLEARED", "paused": "PAUSED", "confirm": "...", "over": "GAME OVER"}[r.state]
        self.put(y, px, f"LEVEL {r.level}", self.color(CASTLE) | curses.A_BOLD)
        self.put(y, px + 9, f"wave {r.wave_in_level()}/{WAVES_PER_LEVEL}", curses.A_BOLD); y += 1
        self.put(y, px, phase, curses.A_BOLD); y += 1
        info = f"paths {len(r.paths)}   speed x{r.speed}"
        if r.state == "wave":
            info += f"   left {len(r.spawn_queue) + len(r.enemies)}"
        self.put(y, px, info, curses.A_DIM); y += 1
        self.put(y, px, "CASTLE ", curses.A_BOLD)
        self.put(y, px + 7, "#" * filled, self.color(RED if filled < 4 else C_BOW) | curses.A_BOLD)
        self.put(y, px + 7 + filled, "-" * (bar_w - filled), curses.A_DIM)
        self.put(y, px + 8 + bar_w, f"{r.hp}/{r.max_hp}"); y += 1
        self.put(y, px, f"GOLD   {r.gold}", self.color(GOLD) | curses.A_BOLD); y += 1
        self.put(y, px, f"GEMS   {int(r.gems_raw)} this run", self.color(GEM) | curses.A_BOLD); y += 2

        cur = tuple(r.cursor)
        t = r.towers.get(cur)
        if t and t.kind:
            s = r.stats(t)
            w = WEAPONS[t.kind]
            self.put(y, px, f"{w['name']} lv {t.level}", self.color(w["color"]) | curses.A_BOLD); y += 1
            self.put(y, px, f" dmg {s['dmg']:.1f} rng {s['rng']:.1f} {1 / s['cd']:.1f}/s", curses.A_DIM); y += 1
        elif t:
            self.put(y, px, "Structure (no weapon)", curses.A_BOLD); y += 2
        elif cur in r.path_set:
            self.put(y, px, "Enemy path", curses.A_DIM); y += 2
        elif cur in r.castle_cells:
            self.put(y, px, "Your castle!", curses.A_DIM); y += 2
        else:
            self.put(y, px, "Grass - buildable", curses.A_DIM); y += 2
        y += 1

        def row(key, label, cost, ok, locked=False):
            nonlocal y
            attr = curses.A_DIM if (locked or not ok) else 0
            self.put(y, px, f"{key:<2} {label:<12}", attr | curses.A_BOLD if not attr else attr)
            self.put(y, px + 16, "locked" if locked else cost,
                     curses.A_DIM if (locked or not ok) else self.color(GOLD))
            y += 1

        sc = r.mods["struct_cost"]
        row("B", "structure", f"{sc}g", r.gold >= sc and r.free(cur))
        for kind in WEAPON_ORDER:
            w = WEAPONS[kind]
            row(w["key"], w["name"], f"{w['cost']}g",
                bool(t) and not t.kind and r.gold >= w["cost"], kind not in r.unlocked)
        if t and t.kind and t.level < MAX_LEVEL:
            row("U", "upgrade", f"{r.upgrade_cost(t)}g", r.gold >= r.upgrade_cost(t))
        else:
            row("U", "upgrade", "-", False)
        row("X", "sell", f"+{t.invested // 2}g" if t else "-", bool(t))
        y += 1
        bottom = py + r.H + 1          # don't run into the message line
        for line in ("N next wave   F speed x1-3", "P pause  K boom  Q quit",
                     "move: arrows/wasd/mouse", "shift+WASD jumps 5 tiles"):
            if y <= bottom:
                self.put(y, px, line, curses.A_DIM)
            y += 1


def main(scr):
    curses.curs_set(0)
    scr.nodelay(True)
    scr.keypad(True)
    try:
        curses.mousemask(curses.BUTTON1_PRESSED | curses.BUTTON1_CLICKED)
        curses.mouseinterval(0)
    except (curses.error, AttributeError):
        pass
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        pairs = {
            GRASS: curses.COLOR_GREEN, PATH: curses.COLOR_YELLOW, STRUCT: curses.COLOR_WHITE,
            C_BOW: curses.COLOR_GREEN, C_GUN: curses.COLOR_CYAN, C_CANNON: curses.COLOR_RED,
            C_FROST: curses.COLOR_BLUE, RED: curses.COLOR_RED, CASTLE: curses.COLOR_YELLOW,
            GOLD: curses.COLOR_YELLOW, GEM: curses.COLOR_MAGENTA, CURSOR: curses.COLOR_YELLOW,
            MAG: curses.COLOR_MAGENTA,
        }
        for pid, col in pairs.items():
            curses.init_pair(pid, col, bg)

    h, w = scr.getmaxyx()
    if h < MIN_H or w < MIN_W:
        scr.nodelay(False)
        scr.addstr(0, 0, f"Terminal is {w}x{h}, need at least {MIN_W}x{MIN_H}. Resize and retry.")
        scr.getch()
        return

    app = App(scr)
    while app.running:
        start = time.time()
        while True:
            k = scr.getch()
            if k == -1:
                break
            app.key(k)
        app.update(DT)
        app.draw()
        spare = DT - (time.time() - start)
        if spare > 0:
            time.sleep(spare)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
