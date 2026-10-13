"""Screens: every menu and the run screen draw at every supported size, buttons work with keys and mouse,
the side panel stays inside its 24 columns, and the Premium store never charges or grants anything."""
import copy
import random
import unittest

from helpers import ALL_UNLOCKED, FakeScreen, click, game, make_app, play_until_over

SIZES = [(22, 70), (24, 80), (30, 104), (30, 105), (30, 120), (30, 140), (50, 200)]


class Menus(unittest.TestCase):
    def test_every_menu_screen_draws_at_every_size(self):
        for h, w in SIZES:
            scr, app = make_app(h, w, gems=7)
            for state in ("menu", "upgrades", "premium", "volume"):
                app.state = state
                app.draw()
                self.assertIn(game.GAME_NAME, scr.text())

    def test_castle_beside_the_title_only_when_it_fits(self):
        for h, w in SIZES:
            scr, app = make_app(h, w)
            app.draw()
            title_x = scr.find("\\__,_\\___|_|")[1]
            self.assertEqual("█" in scr.text(), w >= 105, (h, w))
            if w < 105 or w >= 138:                      # title exactly centred like the buttons
                self.assertEqual(title_x, max(1, (w - 67) // 2), (h, w))

    def test_menu_buttons_by_mouse_and_keys(self):
        scr, app = make_app()
        for label, state in (("UPGRADES", "upgrades"), ("PREMIUM", "premium"), ("VOLUME", "volume")):
            app.state = "menu"
            app.draw()
            y, x = scr.find(label)
            click(app, y, x)
            self.assertEqual(app.state, state)
        app.state = "menu"
        for key, state in (("u", "upgrades"), ("p", "premium"), ("v", "volume")):
            app.state = "menu"
            app.key(ord(key))
            self.assertEqual(app.state, state)
        app.state = "menu"
        app.draw()
        y, x = scr.find("START GAME")
        click(app, y, x)
        self.assertEqual(app.state, "run")

    def test_buying_an_upgrade_spends_gems(self):
        scr, app = make_app(gems=10)
        app.key(ord("u"))
        app.key(ord("1"))                                # Thick Walls level 1 costs 3 gems
        self.assertEqual((app.meta["gems"], app.meta["up"].get("walls")), (7, 1))

    def test_premium_never_charges_or_grants(self):
        scr, app = make_app(gems=5)
        before = copy.deepcopy(app.meta)
        app.key(ord("p"))
        for i in range(len(game.PREMIUM)):
            app.key(ord(str(i + 1)))
            app.key(ord("y"))
            self.assertIn("nothing was charged", app.prem_msg)
        self.assertFalse(game.PAYMENTS_ENABLED)
        self.assertEqual(app.meta, before)

    def test_volume_sliders(self):
        scr, app = make_app()
        app.key(ord("v"))
        app.key(game.curses.KEY_LEFT)
        self.assertEqual(app.meta["volume"]["music"], 9)
        self.assertEqual([game.volume_gain(s) for s in (0, 5, 10)], [0.0, 0.25, 1.0])


class RunScreen(unittest.TestCase):
    def test_panel_never_wider_than_24_columns(self):
        widest = [0]
        original = game.App.draw_panel

        def spy(app, px, py):
            put = app.put

            def measured(y, x, s, attr=0):
                widest[0] = max(widest[0], x - px + len(s))
                put(y, x, s, attr)
            app.put = measured
            try:
                original(app, px, py)
            finally:
                del app.put
        game.App.draw_panel = spy
        try:
            for (h, w), up in (((22, 70), {}), ((50, 200), ALL_UNLOCKED)):
                random.seed(3)
                scr, app = make_app(h, w, up)
                play_until_over(app, draw_every=2)
        finally:
            game.App.draw_panel = original
        self.assertLessEqual(widest[0], game.PANEL_W)

    def test_side_panel_buttons_work_by_mouse(self):
        for h, w in ((22, 70), (30, 120)):
            random.seed(1)
            scr, app = make_app(h, w)
            app.key(10)
            r = app.run
            spot = next((x, y) for y in range(r.H) for x in range(r.W) if r.free((x, y)))
            r.cursor = list(spot)
            app.key(ord("b"))
            app.key(ord("1"))

            def press(letter, dx=1):
                app.draw()
                y, x = next((z[0], z[1]) for z in app.zones if z[3] == ("key", ord(letter)))
                click(app, y, x + dx)

            press("u")
            self.assertEqual(r.towers[spot].level, 2)
            press("f")
            self.assertEqual(r.speed, 2)
            press("n")
            self.assertEqual(r.state, "wave")
            self.assertFalse(app.button_specs()["n"][1], "NEXT WAVE is greyed out during a wave")
            press("p")
            self.assertEqual(r.state, "paused")
            press("p")
            self.assertEqual(r.state, "wave")
            press("x")
            self.assertNotIn(spot, r.towers)
            click(app, game.MAP_Y + 2, game.MAP_X + 2 * 3)
            self.assertEqual(r.cursor, [3, 2], "clicking the map still moves the cursor")

    def test_block_characters_only_where_the_terminal_can_show_them(self):
        scr = FakeScreen(30, 120)
        scr.encoding = "ascii"
        app = game.App(scr)
        app.draw()
        self.assertNotIn("█", scr.text())


if __name__ == "__main__":
    unittest.main()
