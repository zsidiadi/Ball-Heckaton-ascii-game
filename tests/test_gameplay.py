"""Game rules: paths, weapons, buildings, blessings, bosses, saving, and whole runs played by a bot."""
import json
import os
import random
import unittest

from helpers import ALL_UNLOCKED, game, make_app, play_until_over


def new_run(up=None, w=40, h=20, gold=5000):
    r = game.Run(w, h, {"gems": 0, "up": dict(up or {})})
    r.gold = gold
    return r


def grass(r):
    return [c for c in ((x, y) for y in range(r.H) for x in range(r.W)) if r.free(c)]


class Paths(unittest.TestCase):
    def test_paths_are_valid_on_every_map_size(self):
        for h, w in ((14, 19), (18, 24), (46, 84), (66, 120)):
            for seed in range(15):
                random.seed(seed)
                r = game.Run(w, h, {"gems": 0, "up": {}})
                for _ in range(7):                       # 8 paths: deeper than any real run goes
                    r.add_path()
                for p in r.paths:
                    self.assertEqual(len(set(p)), len(p), "a path never crosses itself")
                    self.assertTrue(all(0 <= x < w and 0 <= y < h for x, y in p))
                    self.assertFalse(any(c in r.castle_cells for c in p))
                    for a, b in zip(p, p[1:]):
                        self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1, "steps are one tile")
                    ex, ey = p[-1]
                    self.assertTrue(any(abs(ex - cx) + abs(ey - cy) == 1 for cx, cy in r.castle_cells))

    def test_new_path_refunds_crushed_towers_in_full(self):
        random.seed(3)
        r = new_run()
        for c in grass(r):
            r.cursor = list(c)
            r.build_structure()
        paid = {c: t.invested for c, t in r.towers.items()}
        gold = r.gold
        edge, crushed, refund = r.add_path()
        self.assertGreater(crushed, 0)
        self.assertEqual(r.gold - gold, refund)
        self.assertEqual(refund, sum(v for c, v in paid.items() if c not in r.towers))


class Weapons(unittest.TestCase):
    def test_map_letter_is_first_letter_of_the_name(self):
        letters = [w["ch"] for w in game.WEAPONS.values()]
        self.assertEqual(letters, [w["name"][0].upper() for w in game.WEAPONS.values()])
        self.assertEqual(len(set(letters)), len(letters), "every weapon has its own letter")
        self.assertEqual(game.WEAPONS["frost"]["name"], "Ice")

    def test_mount_upgrade_sell(self):
        r = new_run(ALL_UNLOCKED)
        c = grass(r)[0]
        r.cursor = list(c)
        r.build_structure()
        for kind in game.WEAPON_ORDER:
            w = game.WEAPONS[kind]
            gold = r.gold
            r.add_weapon(kind)
            t = r.towers[c]
            self.assertEqual((t.kind, t.level, gold - r.gold), (kind, 1, w["cost"]))
            self.assertEqual(r.upgrade_cost(t), int(w["cost"] * 0.75))
            r.upgrade()
            self.assertEqual(t.level, 2)
            s1, s2 = r.stats_for(kind, 1), r.stats_for(kind, 2)
            self.assertAlmostEqual(s2["dmg"] / s1["dmg"], 1.4)
            self.assertAlmostEqual(s2["rng"] - s1["rng"], 0.3)
            invested, gold = t.invested, r.gold
            r.sell()
            self.assertEqual(r.gold - gold, invested // 2)
            r.build_structure()

    def test_locked_weapon_cannot_be_mounted(self):
        r = new_run()
        r.cursor = list(grass(r)[0])
        r.build_structure()
        r.add_weapon("sniper")
        self.assertIsNone(r.towers[tuple(r.cursor)].kind)
        self.assertIn("locked", r.msg)


class Buildings(unittest.TestCase):
    def test_gold_mine_gets_50_percent_dearer_per_mine_owned(self):
        r = new_run(ALL_UNLOCKED)
        free = grass(r)
        prices = []
        for c in free[:5]:
            prices.append(r.price("goldmine"))
            r.cursor = list(c)
            r.place_building("goldmine")
        self.assertEqual(prices, [60, 90, 135, 203, 304])
        for c in free[:5]:                                   # same income and upgrade price for every mine
            self.assertEqual(r.income(r.towers[c]), 12)
            self.assertEqual(r.upgrade_cost(r.towers[c]), 45)
        r.cursor = list(free[4])
        r.sell()
        self.assertEqual(r.price("goldmine"), 304, "selling one makes the next one cheaper again")

    def test_mine_costs_50_and_grows_12_5_percent_per_wave(self):
        r = new_run(ALL_UNLOCKED)
        self.assertEqual(r.price("mine"), 50)
        for wave in (1, 5, 10):
            self.assertAlmostEqual(r.mine_damage(wave), 24 * 1.125 ** (wave - 1) * r.dmg_mult)

    def test_mine_explodes_once_and_hits_the_group(self):
        r = new_run(ALL_UNLOCKED)
        c = r.paths[0][6]
        r.cursor = list(c)
        r.place_building("mine")
        r.wave, r.state, r.spawn_queue = 1, "wave", []
        brutes = [game.Enemy("brute", 1, 1.0, r.paths[0]) for _ in range(3)]
        for i, e in enumerate(brutes):
            e.pos = 5.95 - 0.3 * i
        r.enemies = list(brutes)
        for _ in range(10):
            r.update(game.DT)
        self.assertNotIn(c, r.traps)
        for e in brutes:
            self.assertAlmostEqual(32 - e.hp, 24.0)

    def test_traps_go_on_the_path_only_one_per_tile(self):
        r = new_run(ALL_UNLOCKED)
        r.cursor = list(grass(r)[0])
        r.place_building("mine")
        self.assertEqual(r.traps, {})
        c = r.paths[0][4]
        r.cursor = list(c)
        r.place_building("tar")
        r.place_building("mine")
        self.assertEqual(r.traps, {c: "tar"})


class Blessings(unittest.TestCase):
    def perk(self, name):
        return next(p for p in game.PERKS if p[0] == name)[2]

    def test_every_blessing_runs(self):
        for name, desc, fn, req in game.PERKS:
            r = new_run(ALL_UNLOCKED if name != "Armory" else {})
            fn(r)

    def test_haggler_halves_one_weapon_once_never_buildings(self):
        r = new_run(ALL_UNLOCKED)
        for _ in range(len(game.WEAPON_ORDER)):
            self.perk("Haggler")(r)
        self.assertEqual(r.mods["half"], set(game.WEAPON_ORDER))
        for k in game.WEAPON_ORDER:
            self.assertEqual(r.price(k), game.WEAPONS[k]["cost"] // 2, "halved once, never twice")
        self.assertEqual((r.price("goldmine"), r.price("mine"), r.price("tar")), (60, 50, 30))
        for _ in range(100):                     # nothing left to halve: never offered again
            r.wave = 1
            r.wave_cleared()
            self.assertNotIn("Haggler", [p[0] for p in r.offer])

    def test_royal_gift_makes_the_next_one_free(self):
        r = new_run(ALL_UNLOCKED)
        c = grass(r)[0]
        self.perk("Royal Gift")(r)
        r.cursor = list(c)
        r.build_structure()                       # structures don't use the gift up
        self.assertEqual(r.mods["free"], 1)
        gold = r.gold
        r.add_weapon("sniper")
        self.assertEqual((r.gold, r.mods["free"], r.price("sniper")), (gold, 0, 70))


class Bosses(unittest.TestCase):
    def boss_fight(self, level):
        r = new_run()
        r.level, r.wave, r.state, r.spawn_queue = level, 5 * level - 1, "wave", []
        b, cycle = r.level_boss()
        boss = game.Enemy("boss", r.wave, 1.0, r.paths[0], boss=b, cycle=cycle)
        r.enemies = [boss]
        return r, boss

    def test_each_level_brings_its_boss_and_they_come_back(self):
        names = [game.BOSSES[i]["name"] for i in range(5)]
        r = new_run()
        self.assertEqual([r.level_boss(lv)[0]["name"] for lv in range(1, 11)], names * 2)
        self.assertEqual(r.level_boss(6)[1], 2)

    def test_boss_death_sound_only_when_killed(self):
        for level in range(1, 7):
            r, boss = self.boss_fight(level)
            boss.hp = 0
            r.update(game.DT)
            self.assertIn(("boss_death", boss.boss["name"]), r.events)
        r, boss = self.boss_fight(1)
        boss.pos = len(boss.path) - 1.0001
        for _ in range(30):
            r.update(game.DT)
        self.assertTrue(boss.leaked)
        self.assertFalse([e for e in r.events if e[0] == "boss_death"], "no sound when it reaches the castle")

    def test_abilities(self):
        r, king = self.boss_fight(1)
        king.timer = 4.99
        r.update(0.02)
        self.assertEqual(sum(1 for e in r.enemies if e.kind == "grunt"), 2, "Goblin King summons 2 goblins")
        r, golem = self.boss_fight(2)
        hp = golem.hp
        r.hit(golem, 1.0)
        self.assertAlmostEqual(hp - golem.hp, 0.2, msg="armor lets 20% of a weak hit through")
        r, hydra = self.boss_fight(3)
        hydra.hp = hydra.maxhp / 2
        r.update(1.0)
        self.assertAlmostEqual(hydra.hp, hydra.maxhp * 0.515, delta=0.01 * hydra.maxhp)
        r, wraith = self.boss_fight(4)
        self.assertTrue(wraith.no_slow)
        r, dragon = self.boss_fight(5)
        spd = dragon.spd
        dragon.hp = dragon.maxhp * 0.49
        r.update(game.DT)
        self.assertTrue(dragon.enraged)
        self.assertAlmostEqual(dragon.spd, spd * 2)

    def test_poisoned_hydra_stays_dead(self):
        r, hydra = self.boss_fight(3)
        hydra.hp, hydra.poison_t, hydra.poison_dps = 0.01, 1.0, 5.0
        r.update(game.DT)
        self.assertNotIn(hydra, r.enemies)


class Saving(unittest.TestCase):
    def test_missing_or_broken_save_gives_defaults(self):
        if os.path.exists(game.SAVE_FILE):
            os.remove(game.SAVE_FILE)
        self.assertEqual(game.load_meta()["gems"], 0)
        with open(game.SAVE_FILE, "w") as f:
            f.write("{not json")
        self.assertEqual(game.load_meta()["gems"], 0)

    def test_old_tesla_unlock_becomes_lightning(self):
        with open(game.SAVE_FILE, "w") as f:
            json.dump({"gems": 3, "up": {"tesla": 1}}, f)
        meta = game.load_meta()
        self.assertEqual((meta["gems"], meta["up"]), (3, {"lightning": 1}))
        os.remove(game.SAVE_FILE)


class WholeRuns(unittest.TestCase):
    def test_bot_plays_full_runs_and_keeps_gems(self):
        for seed, (h, w), up in ((1, (30, 120), {}), (2, (22, 70), ALL_UNLOCKED), (3, (50, 200), ALL_UNLOCKED)):
            random.seed(seed)
            scr, app = make_app(h, w, up)
            play_until_over(app, draw_every=5)
            self.assertEqual(app.state, "menu")
            self.assertGreaterEqual(app.meta["gems"], 1)
            self.assertEqual(app.meta["runs"], 1)

    def test_cash_out_turns_leftover_gold_into_gems(self):
        random.seed(4)
        scr, app = make_app()
        app.key(10)
        r = app.run
        r.gold = 260
        app.key(ord("k"))
        app.key(ord("y"))
        self.assertEqual(r.final["bonus"], 10)
        app.key(10)
        self.assertEqual(app.state, "menu")


if __name__ == "__main__":
    unittest.main()
