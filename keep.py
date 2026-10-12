#!/usr/bin/env python3
"""
cool tower defense game.exe - a roguelike tower defense for the terminal.

Protect your castle from waves of enemies walking down random paths.
  1. Build a STRUCTURE on a grass tile           (B)
  2. Mount one of 8 WEAPONS on it                (1-8)
  3. Upgrade or sell it                          (U / X)
The game is split into LEVELS of 5 waves. Wave 5 of every level ends with one
of 5 big BOSSES. Beat a level and the next one opens ONE MORE enemy path.
After every wave you pick one of three random blessings.
When the castle falls you KEEP the gems you earned. You can also blow up
your own castle (K) to cash out early: leftover gold turns into bonus gems.
Spend gems in the UPGRADES menu on permanent upgrades and new weapons.

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
GAME_NAME = "cool tower defense game.exe"
VERSION = "0.5.0"

MIN_W, MIN_H = 70, 22
MAP_X, MAP_Y = 1, 2          # screen position of the top-left map cell
PANEL_W = 24                 # width of the info panel on the right (kept as narrow as possible)
MAX_MAP_W, MAX_MAP_H = 150, 70

# colour pair ids
GRASS, PATH, STRUCT, C_BOW, C_GUN, C_CANNON, C_FROST, RED, CASTLE, GOLD, GEM, CURSOR, MAG = range(1, 14)

STRUCT_COST = 10
MAX_LEVEL = 5
WAVES_PER_LEVEL = 5

EDGES = ["left", "top", "bottom"]          # where new paths start, in this order
EDGE_NAMES = {"left": "WEST", "top": "NORTH", "bottom": "SOUTH"}

# unlock = gems needed to unlock it permanently in the Upgrades menu (0 = available from the start)
WEAPONS = {
    "bow":    dict(key="1", name="Bow",    ch="A", cost=25, dmg=3.0,  rng=3.5, cd=0.70, color=C_BOW,    unlock=0,
                   info="steady single-target"),
    "gun":    dict(key="2", name="Gun",    ch="G", cost=40, dmg=1.0,  rng=3.0, cd=0.18, color=C_GUN,    unlock=0,
                   info="very fast, short range"),
    "cannon": dict(key="3", name="Cannon", ch="C", cost=60, dmg=7.0,  rng=4.0, cd=1.80, color=C_CANNON, unlock=8,
                   splash=1.3, info="slow, splash damage"),
    "frost":  dict(key="4", name="Frost",  ch="F", cost=45, dmg=0.6,  rng=3.0, cd=0.50, color=C_FROST,  unlock=10,
                   slow=1.2, info="slows enemies"),
    "flame":  dict(key="5", name="Flamer", ch="L", cost=50, dmg=0.9,  rng=2.0, cd=0.25, color=GOLD,     unlock=6,
                   aoe=True, info="burns ALL enemies in range"),
    "poison": dict(key="6", name="Poison", ch="P", cost=50, dmg=0.5,  rng=3.5, cd=0.90, color=MAG,      unlock=10,
                   poison=(2.0, 3.0), info="poison cloud, ignores armor"),
    "sniper": dict(key="7", name="Sniper", ch="S", cost=70, dmg=22.0, rng=7.0, cd=2.60, color=STRUCT,   unlock=12,
                   strong=True, info="huge range, hits the toughest"),
    "tesla":  dict(key="8", name="Tesla",  ch="T", cost=65, dmg=4.0,  rng=3.5, cd=1.00, color=C_GUN,    unlock=15,
                   chain=4, info="lightning jumps between enemies"),
}
WEAPON_ORDER = ["bow", "gun", "cannon", "frost", "flame", "poison", "sniper", "tesla"]

ENEMIES = {
    "grunt":  dict(ch="o", hp=8,   spd=1.5,  dmg=1,  gold=3,  color=RED),
    "runner": dict(ch="r", hp=5,   spd=2.8,  dmg=1,  gold=3,  color=MAG),
    "brute":  dict(ch="B", hp=32,  spd=0.85, dmg=3,  gold=8,  color=RED),
}
HP_GROWTH = 1.25             # enemy HP multiplier per wave

# one big boss closes every level (wave 5, 10, 15, ...). After the 5th they come back stronger.
BOSSES = [
    dict(name="GOBLIN KING",   sprite=("\\^^/", "(oo)"),  hp=140, spd=0.60, dmg=10, gold=40,  gems=3,
         ability="summon", info="summons goblins every 5s"),
    dict(name="IRON GOLEM",    sprite=("[##]", "/||\\"),  hp=150, spd=0.45, dmg=12, gold=50,  gems=4,
         ability="armor",  info="armor blocks weak hits"),
    dict(name="SWAMP HYDRA",   sprite=("~@@~", "\\HH/"),  hp=170, spd=0.55, dmg=14, gold=60,  gems=5,
         ability="regen",  info="regenerates 1.5% HP/s"),
    dict(name="SHADOW WRAITH", sprite=("(..)", "/~~\\"),  hp=130, spd=0.70, dmg=16, gold=70,  gems=6,
         ability="blink",  info="can't be slowed, teleports"),
    dict(name="BONE DRAGON",   sprite=("/\\/\\", "<DD>"), hp=220, spd=0.55, dmg=20, gold=100, gems=8,
         ability="enrage", info="enrages at half health"),
]
ROMAN = ["", "", " II", " III", " IV", " V"]

# permanent upgrades bought with gems: id, name, description, base cost, max level
META_UPGRADES = [
    ("walls",  "Thick Walls",     "+10 castle HP",            3, 10),
    ("chest",  "War Chest",       "+20 starting gold",        3, 10),
    ("sharp",  "Sharpened Steel", "+10% weapon damage",       4, 10),
    ("magnet", "Gem Magnet",      "+25% gems earned",         5, 5),
] + sorted([(k, f"Unlock {w['name']}", w["info"], w["unlock"], 1) for k, w in WEAPONS.items() if w["unlock"]],
           key=lambda u: u[3])
QUICK_KEYS = "1234567890"

# two blocks of big letters: "cool tower" / "defense game.exe"
TITLE = [
    [
        '             _   _',
        ' __ ___  ___| | | |_ _____ __ _____ _ _',
        "/ _/ _ \\/ _ \\ | |  _/ _ \\ V  V / -_) '_|",
        '\\__\\___/\\___/_|  \\__\\___/\\_/\\_/\\___|_|',
    ],
    [
        '    _      __',
        ' __| |___ / _|___ _ _  ___ ___   __ _ __ _ _ __  ___   _____ _____',
        "/ _` / -_)  _/ -_) ' \\(_-</ -_) / _` / _` | '  \\/ -_)_/ -_) \\ / -_)",
        '\\__,_\\___|_| \\___|_||_/__/\\___| \\__, \\__,_|_|_|_\\___(_)___/_\\_\\___|',
        '                                |___/',
    ],
]


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def num(v, width):
    """Format a stat so it fits in `width` characters."""
    s = f"{v:.1f}"
    if len(s) > width:
        s = f"{v:.0f}"
    return s.rjust(width)


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
def p_flame(r): r.mods["wdmg"]["flame"] *= 1.4
def p_poison(r): r.mods["wdmg"]["poison"] *= 1.5
def p_sniper(r): r.mods["wdmg"]["sniper"] *= 1.35
def p_tesla(r): r.mods["chain"] += 2
def p_range(r): r.mods["range"] += 0.5
def p_tar(r): r.mods["enemy_speed"] *= 0.9
def p_bounty(r): r.mods["bounty"] += 1
def p_bricks(r): r.mods["struct_cost"] = max(2, r.mods["struct_cost"] // 2)
def p_gems(r): r.gems_raw += 2


def p_steel(r):
    for k in r.mods["wdmg"]:
        r.mods["wdmg"][k] *= 1.1


def p_armory(r):
    locked = [k for k in WEAPON_ORDER if k not in r.unlocked]
    k = random.choice(locked)
    r.unlocked.add(k)
    w = WEAPONS[k]
    return f"Blessing: Armory - the {w['name']} ({w['key']}) is unlocked for this run!"


# name, description, function, requirement (None = always, weapon id = must be unlocked,
# "locked" = at least one weapon still locked)
PERKS = [
    ("Gold Rush",    "+40 gold right now",              p_gold,   None),
    ("Mason",        "repair castle +15, max HP +5",    p_repair, None),
    ("Fletcher",     "Bows deal +30% damage",           p_bow,    "bow"),
    ("Gunsmith",     "Guns fire 25% faster",            p_gun,    "gun"),
    ("Black Powder", "Cannons +30% dmg, bigger blast",  p_cannon, "cannon"),
    ("Deep Freeze",  "Frost +50% dmg, slows longer",    p_frost,  "frost"),
    ("Pyromaniac",   "Flamers +40% damage",             p_flame,  "flame"),
    ("Toxicology",   "Poison +50% damage",              p_poison, "poison"),
    ("Deadeye",      "Snipers +35% damage",             p_sniper, "sniper"),
    ("Overcharge",   "Tesla lightning +2 jumps",        p_tesla,  "tesla"),
    ("Armory",       "unlock a random weapon this run", p_armory, "locked"),
    ("Eagle Eye",    "all weapons +0.5 range",          p_range,  None),
    ("Tar Pits",     "new enemies move 10% slower",     p_tar,    None),
    ("Bounty",       "+1 gold per kill",                p_bounty, None),
    ("Cheap Bricks", "structures cost half",            p_bricks, None),
    ("Gem Shard",    "+2 gems right now",               p_gems,   None),
    ("Whetstone",    "all weapons +10% damage",         p_steel,  None),
]


def special_text(kind, s):
    w = WEAPONS[kind]
    if "splash" in w:
        return f"splash {s['splash']:.1f}"
    if "slow" in w:
        return f"slow {s['slow']:.1f}s"
    if w.get("aoe"):
        return "hits all"
    if "poison" in w:
        return f"poison {s['poison']:.1f}/s"
    if w.get("strong"):
        return "toughest"
    if "chain" in w:
        return f"chain x{s['chain']}"
    return ""


# ------------------------------------------------------------------ entities
class Enemy:
    def __init__(self, kind, wave, speed_mult, path, boss=None, cycle=1):
        t = boss if boss else ENEMIES[kind]
        scale = HP_GROWTH ** (wave - 1)
        self.kind = kind
        self.boss = boss
        self.name = (boss["name"] + ROMAN[min(cycle, 5)] if cycle <= 5 else f"{boss['name']} {cycle}") if boss else kind
        self.ch = t.get("ch", "M")
        self.color = t.get("color", MAG)
        self.hp = self.maxhp = t["hp"] * scale
        self.spd = t["spd"] * speed_mult
        self.dmg = t["dmg"]
        self.gold = t["gold"]
        self.path = path
        self.pos = 0.0
        self.slow_t = 0.0
        self.poison_t = 0.0
        self.poison_dps = 0.0
        self.leaked = False
        ability = boss["ability"] if boss else None
        self.armor = 3 + 0.2 * wave if ability == "armor" else 0.0
        self.no_slow = ability == "blink"
        self.timer = 0.0
        self.enraged = False

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
        self.unlocked = {k for k, w in WEAPONS.items() if not w["unlock"] or up.get(k)}
        self.mods = dict(enemy_speed=1.0, range=0.0, struct_cost=STRUCT_COST, bounty=0,
                         splash=0.0, slow=0.0, chain=0,
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
        self.msg = "Build a structure (B), mount a weapon (1-8), then press N to start."

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
    def stats_for(self, kind, level=1):
        w = WEAPONS[kind]
        lv = level - 1
        f = (1.4 ** lv) * self.dmg_mult * self.mods["wdmg"][kind]
        s = dict(
            dmg=w["dmg"] * f,
            rng=w["rng"] + 0.3 * lv + self.mods["range"],
            cd=w["cd"] * (0.92 ** lv) * self.mods["wcd"][kind],
        )
        if "splash" in w:
            s["splash"] = w["splash"] + self.mods["splash"]
        if "slow" in w:
            s["slow"] = w["slow"] + self.mods["slow"]
        if "poison" in w:
            s["poison"], s["poison_t"] = w["poison"][0] * f, w["poison"][1]
        if "chain" in w:
            s["chain"] = w["chain"] + self.mods["chain"] + lv // 2
        return s

    def stats(self, t):
        return self.stats_for(t.kind, t.level)

    def upgrade_cost(self, t):
        return int(WEAPONS[t.kind]["cost"] * 0.75 * t.level)

    def wave_in_level(self):
        return (self.wave - 1) % WAVES_PER_LEVEL + 1 if self.wave else 0

    def level_boss(self, level=None):
        level = level or self.level
        return BOSSES[(level - 1) % len(BOSSES)], (level - 1) // len(BOSSES) + 1

    def boss_alive(self):
        for e in self.enemies:
            if e.boss and e.hp > 0:
                return e
        return None

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
            q.append("boss")      # the boss always comes last
        self.spawn_queue = q
        self.spawn_gap = max(0.3, 0.9 - 0.04 * n) / (1 + 0.1 * (len(self.paths) - 1))
        self.spawn_t = 0.0
        self.state = "wave"
        self.msg = (f"Level {self.level}, wave {self.wave_in_level()}/{WAVES_PER_LEVEL} incoming! "
                    f"({len(q)} enemies{', BOSS: ' + self.level_boss()[0]['name'] if boss else ''})")

    def spawn(self, kind):
        path = self.paths[self.spawn_i % len(self.paths)]
        self.spawn_i += 1
        speed = self.mods["enemy_speed"] * self.map_speed
        if kind == "boss":
            b, cycle = self.level_boss()
            e = Enemy("boss", self.wave, speed, path, boss=b, cycle=cycle)
            self.msg = f"!!! {e.name} APPEARS - {b['info']} !!!"
        else:
            e = Enemy(kind, self.wave, speed, path)
        self.enemies.append(e)

    def wave_cleared(self):
        bonus = 8 + 2 * self.wave
        self.gold += bonus
        g = (1 + self.wave // 10) * self.gem_mult
        self.gems_raw += g
        self.cleared = self.wave
        has_locked = any(k not in self.unlocked for k in WEAPONS)
        pool = [p for p in PERKS if p[3] is None or p[3] in self.unlocked or (p[3] == "locked" and has_locked)]
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
        b, cycle = self.level_boss(lv + 1)
        self.level_info = [
            f"*** LEVEL {lv} COMPLETE! ***", "",
            (f"castle repaired +{heal}" if heal else "castle at full health") +
            f"    +{gold} gold    +{gems:.1f} gems", "",
            f"LEVEL {lv + 1}: a new path opens from the {EDGE_NAMES[nxt]}!",
            f"Enemies will attack from {len(self.paths) + 1} directions.",
            f"Boss of this level: {b['name']}{ROMAN[min(cycle, 5)]} ({b['info']})", "",
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
            self.spawn(self.spawn_queue.pop(0))
            self.spawn_t = self.spawn_gap

        summoned = []
        for e in self.enemies:
            slowed = e.slow_t > 0 and not e.no_slow
            e.slow_t = max(0.0, e.slow_t - dt)
            if e.poison_t > 0:
                e.hp -= e.poison_dps * dt
                e.poison_t -= dt
            if e.boss:
                summoned += self.boss_ability(e, dt)
            e.pos += e.spd * (0.5 if slowed else 1.0) * dt
            last = len(e.path) - 1
            if e.pos >= last:
                e.pos = last
                e.hp = 0
                e.leaked = True
                self.hp -= e.dmg
                self.msg = f"The castle was hit for {e.dmg}!"
                for c in self.castle_cells:
                    self.effects.append([c[0], c[1], "!", RED, 0.3])
        self.enemies += summoned

        for (x, y), t in self.towers.items():
            if not t.kind:
                continue
            t.cd -= dt
            if t.cd > 0:
                continue
            w = WEAPONS[t.kind]
            s = self.stats(t)
            r2 = s["rng"] ** 2
            in_range = [e for e in self.enemies if e.hp > 0 and dist2(e.cell(), (x, y)) <= r2]
            if not in_range:
                continue
            t.cd = s["cd"]
            if w.get("aoe"):
                target = None
            elif w.get("strong"):
                target = max(in_range, key=lambda e: e.hp)
            else:
                target = min(in_range, key=lambda e: e.left())
            self.fire(x, y, t.kind, s, target, in_range)

        alive = []
        for e in self.enemies:
            if e.hp > 0:
                alive.append(e)
            elif not e.leaked:
                self.kills += 1
                self.gold += e.gold + self.mods["bounty"]
                if e.boss:
                    g = e.boss["gems"]
                    self.gems_raw += g * self.gem_mult
                    self.msg = f"{e.name} DEFEATED! +{e.gold} gold, +{g} gems"
                elif e.kind == "brute" and random.random() < 0.1:
                    self.gems_raw += 1 * self.gem_mult
                    self.msg = "The brute dropped a gem!"
        self.enemies = alive

        if self.hp <= 0:
            self.hp = 0
            self.end(manual=False)
        elif not self.spawn_queue and not self.enemies:
            self.wave_cleared()

    def boss_ability(self, e, dt):
        ab = e.boss["ability"]
        e.timer += dt
        new = []
        if ab == "regen":
            e.hp = min(e.maxhp, e.hp + 0.015 * e.maxhp * dt)
        elif ab == "summon" and e.timer >= 5.0:
            e.timer = 0.0
            for i in range(2):
                g = Enemy("grunt", self.wave, self.mods["enemy_speed"] * self.map_speed, e.path)
                g.pos = max(0.0, e.pos - 0.4 - 0.6 * i)
                new.append(g)
            self.msg = f"{e.name} summons goblins!"
        elif ab == "blink" and e.timer >= 4.0:
            e.timer = 0.0
            x, y = e.cell()
            self.effects.append([x, y, "~", MAG, 0.4])
            e.pos = min(len(e.path) - 1.01, e.pos + 4)
        elif ab == "enrage" and not e.enraged and e.hp < e.maxhp / 2:
            e.enraged = True
            e.spd *= 2.0
            self.msg = f"{e.name} IS ENRAGED!"
        return new

    def hit(self, e, dmg):
        if e.armor:
            dmg = max(dmg * 0.2, dmg - e.armor)
        e.hp -= dmg

    def fire(self, x, y, kind, s, target, in_range):
        w = WEAPONS[kind]
        col = w["color"]
        if w.get("aoe"):
            for e in in_range:
                self.hit(e, s["dmg"])
                ex, ey = e.cell()
                self.effects.append([ex, ey, "^", col, 0.12])
            return
        tx, ty = target.cell()
        if "splash" in w:
            r2 = s["splash"] ** 2
            for e in self.enemies:
                if e.hp > 0 and dist2(e.cell(), (tx, ty)) <= r2:
                    self.hit(e, s["dmg"])
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                self.effects.append([tx + dx, ty + dy, "*", col, 0.25])
        elif "chain" in w:
            done, cur, dmg = [], target, s["dmg"]
            for _ in range(s["chain"]):
                self.hit(cur, dmg)
                done.append(cur)
                cx, cy = cur.cell()
                self.effects.append([cx, cy, "z", col, 0.15])
                nxt = [e for e in self.enemies if e.hp > 0 and e not in done and dist2(e.cell(), (cx, cy)) <= 6.25]
                if not nxt:
                    break
                cur = min(nxt, key=lambda e: dist2(e.cell(), (cx, cy)))
                dmg *= 0.8
        else:
            self.hit(target, s["dmg"])
            mark = "x"
            if "slow" in w:
                mark = "~"
                if not target.no_slow:
                    target.slow_t = max(target.slow_t, s["slow"])
            if "poison" in w:
                mark = "%"
                target.poison_dps = max(target.poison_dps, s["poison"]) if target.poison_t > 0 else s["poison"]
                target.poison_t = s["poison_t"]
            steps = 3 if w.get("strong") else 1
            for i in range(1, steps + 1):
                f = i / (steps + 1)
                self.effects.append([round(x + (tx - x) * f), round(y + (ty - y) * f),
                                     "-" if kind == "gun" else ("." if steps > 1 else "'"), col, 0.08])
            self.effects.append([tx, ty, "X" if w.get("strong") else mark, col, 0.12])

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
                extra = fn(self)
                self.msg = (extra or f"Blessing: {name} - {desc}.") + " Press N for the next wave."
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
            self.msg = "There's already a structure here. Add a weapon with 1-8."
        elif self.gold < cost:
            self.msg = f"Not enough gold (need {cost})."
        else:
            self.gold -= cost
            self.towers[c] = Tower(cost)
            self.msg = "Structure built! Now mount a weapon with 1-8."

    def add_weapon(self, kind):
        c = tuple(self.cursor)
        w = WEAPONS[kind]
        t = self.towers.get(c)
        if kind not in self.unlocked:
            self.msg = f"{w['name']} is locked. Unlock it with gems in the UPGRADES menu."
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
ENTER_KEYS = (10, 13, curses.KEY_ENTER, ord(" "))
BACK_KEYS = (27, curses.KEY_BACKSPACE, 127, 8, ord("q"), ord("Q"), ord("b"), ord("B"))
UP_KEYS = (curses.KEY_UP, ord("w"), ord("W"))
DOWN_KEYS = (curses.KEY_DOWN, ord("s"), ord("S"))

MENU_ITEMS = [("START GAME", "start"), ("UPGRADES", "upgrades"), ("QUIT", "quit")]


class App:
    def __init__(self, scr):
        self.scr = scr
        self.meta = load_meta()
        self.state = "menu"        # menu, upgrades, run
        self.run = None
        self.running = True
        self.menu_sel = 0
        self.shop_sel = 0
        self.shop_msg = ""
        self.zones = []            # clickable areas: (y, x0, x1, action)
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
        x = max(0, (w - len(s)) // 2)
        self.put(y, x, s, attr)
        return x

    def button(self, y, label, action, selected=False, width=20):
        """Draw a clickable [ BUTTON ] centered on row y."""
        text = f"[ {label.center(width - 4)} ]"
        attr = curses.A_REVERSE | curses.A_BOLD if selected else curses.A_BOLD
        x = self.center(y, text, self.color(CASTLE) | attr if selected else attr)
        if selected:
            self.put(y, x - 3, ">", self.color(CASTLE) | curses.A_BOLD)
            self.put(y, x + len(text) + 2, "<", self.color(CASTLE) | curses.A_BOLD)
        self.zones.append((y, x, x + len(text), action))

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
            if self.state == "run":
                if mx >= MAP_X:
                    self.run.click((mx - MAP_X) // 2, my - MAP_Y)
            else:
                for y, x0, x1, action in self.zones:
                    if my == y and x0 <= mx < x1:
                        self.do(action)
                        break
            return
        if self.state == "menu":
            n = len(MENU_ITEMS)
            if k in UP_KEYS:
                self.menu_sel = (self.menu_sel - 1) % n
            elif k in DOWN_KEYS:
                self.menu_sel = (self.menu_sel + 1) % n
            elif k in ENTER_KEYS:
                self.do(MENU_ITEMS[self.menu_sel][1])
            elif k in (ord("u"), ord("U")):
                self.do("upgrades")
            elif k in (ord("q"), ord("Q"), 27):
                self.do("quit")
        elif self.state == "upgrades":
            n = len(META_UPGRADES)
            if k in UP_KEYS:
                self.shop_sel = (self.shop_sel - 1) % n
            elif k in DOWN_KEYS:
                self.shop_sel = (self.shop_sel + 1) % n
            elif k in ENTER_KEYS:
                self.buy(self.shop_sel)
            elif 0 <= k < 256 and chr(k) in QUICK_KEYS[:n]:
                self.shop_sel = QUICK_KEYS.index(chr(k))
                self.buy(self.shop_sel)
            elif k in BACK_KEYS:
                self.do("back")
        else:
            self.run.key(k)
            if self.run.done:
                self.state = "menu"
                self.run = None

    def do(self, action):
        if action == "start":
            self.new_run()
        elif action == "upgrades":
            self.state, self.shop_msg = "upgrades", ""
        elif action == "quit":
            self.running = False
        elif action == "back":
            self.state = "menu"
        elif action[0] == "sel":
            self.shop_sel = action[1]
        elif action[0] == "buy":
            self.shop_sel = action[1]
            self.buy(action[1])

    def buy(self, i):
        uid, name, desc, base, mx = META_UPGRADES[i]
        lv = self.meta["up"].get(uid, 0)
        if lv >= mx:
            self.shop_msg = f"{name} is already maxed."
            return
        cost = meta_cost(base, lv)
        if self.meta["gems"] < cost:
            self.shop_msg = f"{name} costs {cost} gems - you have {self.meta['gems']}."
            return
        self.meta["gems"] -= cost
        self.meta["up"][uid] = lv + 1
        save_meta(self.meta)
        self.shop_msg = f"Bought {name}!" + (f" Now level {lv + 1}." if mx > 1 else "")

    def new_run(self):
        # the map fills the terminal, minus the info panel on the right
        h, w = self.scr.getmaxyx()
        W = max(19, min(MAX_MAP_W, (w - 4 - PANEL_W) // 2))   # frame + 1 space gap + panel
        H = max(12, min(MAX_MAP_H, h - MAP_Y - 2))
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
        self.zones = []
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "upgrades":
            self.draw_upgrades()
        else:
            self.draw_run()
        self.scr.refresh()

    def window(self, subtitle=""):
        """Retro desktop-window frame around the whole screen."""
        h, w = self.scr.getmaxyx()
        bar = curses.A_REVERSE | curses.A_BOLD
        self.put(0, 0, " " * (w - 1), bar)
        self.put(0, 1, f" {GAME_NAME}" + (f" - {subtitle}" if subtitle else ""), bar)
        btns = "[_] [#] [X]"
        bx = w - 2 - len(btns)
        self.put(0, bx, btns, bar)
        self.zones.append((0, bx + 8, bx + 11, "quit" if self.state == "menu" else "back"))
        for y in range(1, h - 1):
            self.put(y, 0, "|", curses.A_DIM)
            self.put(y, w - 2, "|", curses.A_DIM)
        self.put(h - 1, 0, "+" + "-" * (w - 3) + "+", curses.A_DIM)
        self.put(h - 1, w - 4 - len(VERSION) - 2, f" v{VERSION} ", curses.A_DIM)

    def draw_menu(self):
        m = self.meta
        h, w = self.scr.getmaxyx()
        self.window()
        roomy = h >= 30
        step = 2 if roomy else 1
        total = sum(len(b) + 1 for b in TITLE) + (2 if roomy else 0) + 2 + len(MENU_ITEMS) * step + 2
        y = max(1, 1 + (h - 2 - total) // 2)
        for block in TITLE:
            bw = max(len(l) for l in block)
            x = max(1, (w - bw) // 2)
            for line in block:
                self.put(y, x, line, self.color(CASTLE) | curses.A_BOLD)
                y += 1
            y += 1
        if roomy:
            self.center(y, "a roguelike tower defense  -  protect the castle, keep the gems", curses.A_DIM)
            y += 2
        self.center(y, f"GEMS {m['gems']}    best: level {m.get('best_level', 0)}, wave {m.get('best', 0)}"
                       f"    runs {m.get('runs', 0)}", self.color(GEM) | curses.A_BOLD)
        y += 2
        for i, (label, action) in enumerate(MENU_ITEMS):
            self.button(y, label, action, selected=(i == self.menu_sel))
            y += step
        y += 1
        self.center(y, "up/down + ENTER   or click   (U upgrades, Q quit)", curses.A_DIM)

    def draw_upgrades(self):
        m = self.meta
        h, w = self.scr.getmaxyx()
        self.window("Upgrades")
        n = len(META_UPGRADES)
        gap = 2 if h >= n + 15 else 1
        total = 3 + n + 1 + 3 * gap + 1
        y = max(1, 1 + (h - 2 - total) // 2)
        self.center(y, "-=  U P G R A D E S  =-", self.color(CASTLE) | curses.A_BOLD)
        y += 1
        self.center(y, f"GEMS {m['gems']}", self.color(GEM) | curses.A_BOLD)
        y += 2
        row_w = 52
        left = max(2, (w - row_w) // 2)
        for i, (uid, name, desc, base, mx) in enumerate(META_UPGRADES):
            lv = m["up"].get(uid, 0)
            maxed = lv >= mx
            cost = meta_cost(base, lv)
            price = ("MAXED" if mx > 1 else "OWNED") if maxed else f"{cost} gems"
            lvl = f"lv {lv}/{mx}" if mx > 1 else ""
            sel = i == self.shop_sel
            can = not maxed and m["gems"] >= cost
            attr = curses.A_REVERSE | curses.A_BOLD if sel else (curses.A_DIM if maxed else 0)
            text = f" {QUICK_KEYS[i]}) {name:<16} {lvl:<8} {price:<10} "
            self.put(y, left, ">" if sel else " ", self.color(CASTLE) | curses.A_BOLD)
            self.put(y, left + 2, text, attr)
            self.zones.append((y, left, left + 2 + len(text), ("sel", i)))
            if not maxed:
                bx = left + 3 + len(text)
                self.put(y, bx, "[ BUY ]", self.color(GEM) | curses.A_BOLD if can else curses.A_DIM)
                self.zones.append((y, bx, bx + 7, ("buy", i)))
            y += 1
        y += 1
        uid, name, desc, base, mx = META_UPGRADES[self.shop_sel]
        lv = m["up"].get(uid, 0)
        detail = f"{name}: {desc}" + (" per level" if mx > 1 else "")
        if uid in WEAPONS:
            wd = WEAPONS[uid]
            detail += f" ({wd['cost']}g  dmg {wd['dmg']:g}  rng {wd['rng']:g}  {1 / wd['cd']:.1f}/s)"
        elif lv < mx:
            detail += f"  -  next costs {meta_cost(base, lv)} gems"
        self.center(y, detail)
        y += gap
        self.center(y, self.shop_msg, self.color(GOLD) | curses.A_BOLD)
        y += gap
        self.button(y, "BACK", "back", selected=False, width=12)
        y += gap
        self.center(y, f"up/down select   ENTER buy   {QUICK_KEYS[0]}-{QUICK_KEYS[n - 1]} quick buy   ESC back",
                    curses.A_DIM)

    def draw_run(self):
        r = self.run
        mx, my = MAP_X, MAP_Y
        W, H = r.W, r.H

        # header
        self.put(0, 0, f" {GAME_NAME} ", curses.A_REVERSE | curses.A_BOLD)
        hdr = f"  level {r.level}   wave {r.wave_in_level()}/{WAVES_PER_LEVEL}   kills {r.kills}   "
        self.put(0, len(GAME_NAME) + 2, hdr, curses.A_BOLD)
        self.put(0, len(GAME_NAME) + 2 + len(hdr), f"gem bank {self.meta['gems']}", self.color(GEM))

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
                elif rng2 >= 0 and dist2(c, cur) <= rng2:
                    s, a = (" .", self.color(WEAPONS[ct.kind]["color"]))
                else:
                    s, a = grass[(x * 7 + y * 13) % len(grass)], self.color(GRASS) | curses.A_DIM
                self.put(my + y, mx + 2 * x, s, a)

        # castle (right edge, 3 rows tall)
        cy = r.castle_y
        cx = mx + 2 * (W - 2)
        hp_frac = r.hp / max(1, r.max_hp)
        ca = self.color(RED if hp_frac < 0.3 else CASTLE) | curses.A_BOLD
        for i, row in enumerate(("/^^\\", "|[]|", "|__|")):
            self.put(my + cy - 1 + i, cx, row, ca)

        # enemies (bosses last so they are drawn on top)
        for e in sorted(r.enemies, key=lambda e: e.boss is not None):
            x, y = e.cell()
            slowed = e.slow_t > 0 and not e.no_slow
            if e.boss:
                a = self.color(RED if e.enraged else MAG) | curses.A_BOLD
                if slowed:
                    a = self.color(C_FROST) | curses.A_BOLD
                top, bottom = e.boss["sprite"]
                sx = min(max(mx, mx + 2 * x - 1), mx + 2 * W - 4)
                ty, by = (y - 1, y) if y > 0 else (y, y + 1)
                self.put(my + ty, sx, top, a)
                self.put(my + by, sx, bottom, a)
                continue
            a = self.color(e.color) | curses.A_BOLD
            if slowed:
                a = self.color(C_FROST) | curses.A_BOLD
            elif e.poison_t > 0:
                a = self.color(MAG) | curses.A_BOLD
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

        self.draw_panel(mx + 2 * W + 2, my - 1)
        self.put(my + H + 1, 0, " " + r.msg, self.color(GOLD))
        self.draw_overlay()

    def draw_panel(self, px, py):
        """Info + build menu on the right. Everything fits in PANEL_W (24) columns."""
        r = self.run
        bottom = py + r.H + 1                  # don't run into the message line
        rows = []                              # list of lists of (text, attr, x offset)
        bold, dim = curses.A_BOLD, curses.A_DIM

        phase = {"build": "BUILD PHASE", "wave": "WAVE ACTIVE", "perk": "WAVE CLEARED",
                 "levelup": "LEVEL CLEARED", "paused": "PAUSED", "confirm": "...", "over": "GAME OVER"}[r.state]
        if r.state == "wave":
            phase += f" - {len(r.spawn_queue) + len(r.enemies)} left"
        bar_w = 8
        filled = max(0, int(bar_w * r.hp / max(1, r.max_hp)))

        rows.append([(f"LEVEL {r.level}", self.color(CASTLE) | bold, 0),
                     (f"wave {r.wave_in_level()}/{WAVES_PER_LEVEL}", bold, 9)])
        rows.append([(phase, bold, 0)])
        rows.append([("CASTLE", bold, 0), ("#" * filled, self.color(RED if filled < 3 else C_BOW) | bold, 7),
                     ("-" * (bar_w - filled), dim, 7 + filled), (f"{r.hp}/{r.max_hp}", 0, 8 + bar_w)])
        rows.append([(f"GOLD {r.gold}", self.color(GOLD) | bold, 0),
                     (f"GEMS {int(r.gems_raw)}", self.color(GEM) | bold, 12)])
        boss = r.boss_alive()
        if boss:
            bf = max(0, min(bar_w, int(bar_w * boss.hp / boss.maxhp + 0.99)))
            rows.append([(boss.name, self.color(RED if boss.enraged else MAG) | bold, 0)])
            rows.append([("BOSS", bold, 0), ("#" * bf, self.color(MAG) | bold, 7),
                         ("-" * (bar_w - bf), dim, 7 + bf), (f"{int(boss.hp)}", 0, 8 + bar_w)])
        else:
            b, cycle = r.level_boss()
            rows.append([(f"paths {len(r.paths)}  speed x{r.speed}", dim, 0)])
            rows.append([(f"boss: {b['name']}{ROMAN[min(cycle, 5)]}", dim, 0)])

        # what's under the cursor
        cur = tuple(r.cursor)
        t = r.towers.get(cur)
        if t and t.kind:
            s = r.stats(t)
            w = WEAPONS[t.kind]
            rows.append([(f"{w['name']} lv {t.level}", self.color(w["color"]) | bold, 0),
                         (special_text(t.kind, s), dim, len(w["name"]) + 6)])
            rows.append([(f"dmg {s['dmg']:.1f} rng {s['rng']:.1f} {1 / s['cd']:.1f}/s", dim, 0)])
        else:
            if t:
                label = "Structure: pick 1-8"
            elif cur in r.path_set:
                label = "Enemy path"
            elif cur in r.castle_cells:
                label = "Your castle!"
            else:
                label = "Grass: buildable"
            rows.append([(label, bold if t else dim, 0)])
            rows.append([])

        # build menu with weapon stats:  "3 Cannon 60  7.0 4.0 0.6"
        gold_c = self.color(GOLD)
        rows.append([("  weapon  $  dmg rng  /s", dim, 0)])
        sc = r.mods["struct_cost"]
        ok = r.gold >= sc and r.free(cur)
        rows.append([("B struct", 0 if ok else dim, 0), (str(sc).rjust(2), gold_c if ok else dim, 9)])
        for kind in WEAPON_ORDER:
            w = WEAPONS[kind]
            locked = kind not in r.unlocked
            line = f"{w['key']} {w['name']:<6}"
            if locked:
                rows.append([(line, dim, 0), ("locked", dim, 9)])
                continue
            s = r.stats_for(kind)
            ok = bool(t) and not t.kind and r.gold >= w["cost"]
            here = bool(t) and t.kind == kind
            attr = self.color(w["color"]) | bold if (ok or here) else 0
            rows.append([(line, attr, 0), (str(w["cost"]).rjust(2), gold_c if ok else dim, 9),
                         (f"{num(s['dmg'], 4)} {num(s['rng'], 3)} {num(1 / s['cd'], 3)}", 0 if ok else dim, 12)])
        if t and t.kind and t.level < MAX_LEVEL:
            uc = r.upgrade_cost(t)
            ok = r.gold >= uc
            rows.append([("U upgrade", 0 if ok else dim, 0), (f"{uc}g", gold_c if ok else dim, 10)])
        else:
            rows.append([("U upgrade", dim, 0), ("-", dim, 10)])
        rows.append([("X sell", 0 if t else dim, 0), (f"+{t.invested // 2}g" if t else "-", dim, 10)])
        rows.append([])
        for line in ("N wave F speed P pause", "K cash out    Q quit",
                     "move: arrows/wasd/mouse", "Shift+WASD = 5 tiles"):
            rows.append([(line, dim, 0)])

        for i, row in enumerate(rows):
            y = py + i
            if y > bottom:
                break
            for text, attr, dx in row:
                self.put(y, px + dx, text, attr)

    def draw_overlay(self):
        r = self.run
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
            title = "*** KABOOM! You destroyed your own castle ***" if f["manual"] else "*** THE CASTLE HAS FALLEN ***"
            lines = [title, "", f"reached level:  {f['level']}", f"waves survived: {f['waves']}",
                     f"enemies slain:  {f['kills']}",
                     f"gems kept:      {f['gems']}" + (f"  (incl. {f['bonus']} from gold)" if f["bonus"] else ""),
                     f"gem bank now:   {self.meta['gems']}", "", "ENTER - back to the menu"]
            self.box(lines, self.color(RED if not f["manual"] else GOLD) | curses.A_BOLD)


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
    os.environ.setdefault("ESCDELAY", "25")   # make ESC react instantly
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
