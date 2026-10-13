"""Shared test helpers: load the game file (its name has spaces), a fake curses screen and a simple bot.

The game is loaded once as the module `game`. Its save file is redirected to a temporary folder, so running
the tests never touches your real progress, and colours are switched off so no real terminal is needed.
"""
import curses
import importlib.machinery
import importlib.util
import os
import random
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_FILE = os.path.join(ROOT, "cool tower defense game.exe.py")

_loader = importlib.machinery.SourceFileLoader("game", GAME_FILE)
_spec = importlib.util.spec_from_loader("game", _loader)
game = importlib.util.module_from_spec(_spec)
_loader.exec_module(game)

TMP = tempfile.mkdtemp(prefix="ctd_tests_")
game.SAVE_FILE = os.path.join(TMP, "save.json")
curses.has_colors = lambda: False

ALL_UNLOCKED = {k: 1 for k, item in game.ITEMS.items() if item["unlock"]}


def fresh_meta(up=None, **extra):
    meta = {"gems": 0, "best": 0, "best_level": 0, "runs": 0, "up": dict(up or {})}
    meta.update(extra)
    return meta


class FakeScreen:
    """Just enough of a curses window: remembers every character drawn and fails on drawing off-screen."""
    encoding = "utf-8"

    def __init__(self, h, w):
        self.h, self.w = h, w
        self.erase()

    def getmaxyx(self):
        return self.h, self.w

    def erase(self):
        self.buf = [[" "] * self.w for _ in range(self.h)]

    def addstr(self, y, x, text, attr=0):
        assert 0 <= y < self.h and 0 <= x and x + len(text) <= self.w, (y, x, text)
        for i, ch in enumerate(text):
            self.buf[y][x + i] = ch

    def refresh(self):
        pass

    def text(self):
        return "\n".join("".join(row).rstrip() for row in self.buf)

    def find(self, s):
        """(row, column) of the first place `s` is drawn."""
        for y, row in enumerate(self.buf):
            x = "".join(row).find(s)
            if x >= 0:
                return y, x
        raise AssertionError(f"{s!r} is not on the screen")


def make_app(h=30, w=120, up=None, **meta):
    scr = FakeScreen(h, w)
    app = game.App(scr)
    app.meta = fresh_meta(up, **meta)
    return scr, app


def click(app, y, x, bstate=None):
    """One mouse event at row y, column x (a press of the left button unless `bstate` says otherwise)."""
    bstate = curses.BUTTON1_PRESSED if bstate is None else bstate
    curses.getmouse = lambda: (0, x, y, 0, bstate)
    app.key(curses.KEY_MOUSE)


def bot_build(app):
    """Build towers next to the path and upgrade them while there is gold, like a simple player would."""
    r = app.run
    path = {p for pth in r.paths for p in pth}
    spots = sorted((c for c in ((x, y) for x in range(r.W) for y in range(r.H)) if r.free(c)),
                   key=lambda c: -sum(1 for p in path if (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 <= 9))[:40]
    kinds = [k for k in game.WEAPON_ORDER if k in r.unlocked]
    for _ in range(12):
        weapons = [c for c, t in r.towers.items() if t.kind in game.WEAPONS and t.level < game.MAX_LEVEL]
        affordable = [k for k in kinds if r.price(k) + r.mods["struct_cost"] <= r.gold]
        if affordable and spots and len(r.towers) < 16:
            r.cursor = list(spots.pop(0))
            app.key(ord("b"))
            app.key(ord(game.WEAPONS[random.choice(affordable)]["key"]))
        elif weapons:
            c = min(weapons, key=lambda c: r.towers[c].level)
            if r.gold < r.upgrade_cost(r.towers[c]):
                break
            r.cursor = list(c)
            app.key(ord("u"))
        else:
            break


def play_until_over(app, draw_every=0, max_frames=400000):
    """Start a run from the menu and let the bot play it to the end. Returns the number of frames played."""
    app.key(10)
    r, frames = app.run, 0
    while app.state == "run" and frames < max_frames:
        frames += 1
        if r.state == "build":
            bot_build(app)
            app.key(ord("n"))
        elif r.state == "perk":
            app.key(ord(random.choice("123")))
        elif r.state in ("levelup", "over"):
            if draw_every:
                app.draw()
            app.key(10)
        else:
            app.update(game.DT)
            if draw_every and frames % draw_every == 0:
                app.draw()
    return frames
