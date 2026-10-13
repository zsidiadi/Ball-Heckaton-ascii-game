"""The README and CHANGELOG must match the code: every number in the game reference tables, the version, the
lists of blessings, upgrades and premium items, and every link inside the repository."""
import os
import re
import unittest

from helpers import ROOT, game

README = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
CHANGELOG = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()


def table(header):
    """Rows of the markdown table that starts with `header` (cells split on | but not on an escaped \\|)."""
    lines = README[README.index(header):].split("\n")
    rows = []
    for line in lines[2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])])
    return rows


def numbers(text):
    return re.findall(r"\d+(?:\.\d+)?", text)


class ReadmeMatchesCode(unittest.TestCase):
    def test_version(self):
        self.assertIn(f"version-{game.VERSION}-", README, "README version badge")
        latest = re.search(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d\d-\d\d)", CHANGELOG, re.M).group(1)
        self.assertEqual(latest, game.VERSION, "newest CHANGELOG release")

    def test_weapons_table(self):
        rows = table("| Key | Weapon | Map |")
        self.assertEqual([r[1] for r in rows], [game.WEAPONS[k]["name"] for k in game.WEAPON_ORDER])
        for key, name, letter, cost, dmg, rng, shots, special, unlock in rows:
            w = next(w for w in game.WEAPONS.values() if w["name"] == name)
            self.assertEqual(key, w["key"])
            self.assertEqual(letter, f"`{w['ch']}`")
            self.assertEqual(cost, f"{w['cost']}g")
            self.assertEqual((dmg, rng, shots), (f"{w['dmg']:.1f}", f"{w['rng']:.1f}", f"{1 / w['cd']:.1f}"), name)
            self.assertEqual(unlock, f"{w['unlock']} gems" if w["unlock"] else "free")
            for k in ("splash", "slow"):
                if k in w:
                    self.assertIn(f"{w[k]:g}", numbers(special), name)
            if "poison" in w:
                self.assertEqual(numbers(special)[:2], [f"{v:g}" for v in w["poison"]])
            if "chain" in w:
                self.assertEqual(numbers(special)[:2], [str(w["chain"]), str(round(w["falloff"] * 100))])

    def test_buildings_table(self):
        for key, name, mark, where, cost, effect, unlock in table("| Key | Item | Map |"):
            kind = next(k for k, b in game.BUILDINGS.items() if b["name"] == name)
            b = game.BUILDINGS[kind]
            self.assertEqual(key.lower(), b["key"])
            self.assertTrue(mark.startswith("`" + b["ch"]))
            self.assertEqual(cost.split(",")[0], f"{b['cost']}g")
            self.assertEqual(unlock, f"{b['unlock']} gems")
            self.assertEqual("grass" in where, b["where"] == "grass")
            if kind == "goldmine":
                self.assertIn(f"+{round((b['cost_growth'] - 1) * 100)}%", cost)
                self.assertEqual(numbers(effect)[:2], [str(b["income"]), str(b["income_lv"])])
            if kind == "mine":
                for v in (f"{b['radius']:g}", str(b["dmg"]), f"{(b['dmg_growth'] - 1) * 100:g}"):
                    self.assertIn(v, numbers(effect))

    def test_enemies_table(self):
        for mark, name, hp, spd, dmg, gold, appears in table("| Map | Enemy | Base HP |"):
            e = game.ENEMIES[name.lower()]
            self.assertEqual((mark, hp, spd, dmg, gold),
                             (f"`{e['ch']}`", str(e["hp"]), f"{e['spd']:g}", str(e["dmg"]), str(e["gold"])))
        self.assertIn(f"Enemy HP grows ×{game.HP_GROWTH:g} every wave", README)

    def test_bosses_table(self):
        rows = [r for r in table("| Level | Boss | Sprite |") if r[0].isdigit()]
        self.assertEqual(len(rows), len(game.BOSSES))
        for (level, name, sprite, hp, spd, dmg, reward, ability), b in zip(rows, game.BOSSES):
            self.assertEqual(name.upper(), b["name"])
            self.assertEqual(sprite, " ".join(f"`{s}`" for s in b["sprite"]))
            self.assertEqual((hp, spd, dmg), (str(b["hp"]), f"{b['spd']:.2f}", str(b["dmg"])))
            self.assertEqual(reward, f"{b['gold']}g, {b['gems']} gems")

    def test_upgrades_table(self):
        rows = table("| Upgrade | Effect per level |")
        self.assertEqual(sorted(r[0] for r in rows), sorted(u[1] for u in game.META_UPGRADES))
        for name, effect, most, cost in rows:
            uid, _, _, base, mx = next(u for u in game.META_UPGRADES if u[1] == name)
            self.assertEqual(most, str(mx))
            self.assertEqual(cost, f"{base} × next level" if mx > 1 else str(base))

    def test_blessings_and_premium_lists(self):
        names = set()
        for row in table("| Blessing | Effect | | Blessing | Effect |"):
            names |= {row[0], row[3]} - {""}
        self.assertEqual(names, {p[0] for p in game.PERKS})
        rows = table("| Item | Price | What it will do |")
        self.assertEqual([(r[0], r[1], r[2]) for r in rows], [(p[1], game.eur(p[2]), p[3]) for p in game.PREMIUM])

    def test_limits_and_sizes(self):
        self.assertIn(f"at least **{game.MIN_W}×{game.MIN_H}**", README)
        self.assertIn(f"slim {game.PANEL_W}-column side panel", README)
        self.assertIn(f"default {game.MAX_MAP_W}×{game.MAX_MAP_H}", README)
        self.assertIn(f"structure `[]` ({game.STRUCT_COST} gold)", README)


class Links(unittest.TestCase):
    @staticmethod
    def anchors(text):
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-") for h in re.findall(r"^#+ (.*)$", text, re.M)}

    def test_links_inside_the_repo_work(self):
        docs = {"README.md": README, "CHANGELOG.md": CHANGELOG}
        for doc, text in docs.items():
            for target in re.findall(r"\]\(([^)\s]+)\)", re.sub(r"```.*?```", "", text, flags=re.S)):
                if target.startswith("http"):
                    continue
                path, _, anchor = target.partition("#")
                path = path or doc
                self.assertTrue(os.path.exists(os.path.join(ROOT, path)), f"{doc}: {target}")
                if anchor:
                    self.assertIn(anchor, self.anchors(docs[path]), f"{doc}: {target}")

    def test_changelog_lists_every_release_with_a_link(self):
        versions = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", CHANGELOG, re.M)
        for v in versions:
            self.assertRegex(CHANGELOG, rf"(?m)^\[{re.escape(v)}\]: https://github\.com/\S+$", v)


if __name__ == "__main__":
    unittest.main()
