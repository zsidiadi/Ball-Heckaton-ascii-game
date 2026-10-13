"""Sound: every sound the game asks for exists and is a valid WAV, and the run's sound cues turn into the right
sounds at the right time (without a real audio player)."""
import os
import subprocess
import sys
import tempfile
import time
import types
import unittest
import wave

from helpers import game, make_app


def wav_seconds(rel):
    with wave.open(os.path.join(game.MUSIC_DIR, rel)) as w:
        return w.getnframes() / w.getframerate()


class Assets(unittest.TestCase):
    def test_every_sound_file_exists_and_plays(self):
        files = ([game.MENU_TRACK] + list(game.LEVEL_TRACKS) + list(game.DEATH_SOUNDS.values())
                 + list(game.BOSS_DEATH_SOUNDS.values()) + list(game.LEVEL_COMPLETE_SOUNDS) + [game.SPECIAL_THANKS])
        for rel in files:
            self.assertGreater(wav_seconds(rel), 0.1, rel)

    def test_every_boss_has_a_death_sound(self):
        self.assertEqual(set(game.BOSS_DEATH_SOUNDS), {b["name"] for b in game.BOSSES})

    def test_effects_follow_the_death_sounds_slider(self):
        music = game.Music.__new__(game.Music)
        self.assertEqual(music.group("sfx/boss_bone_dragon.wav"), "effects")
        self.assertEqual(music.group("voice/level1_complete.wav"), "voice")

    def test_scale_pcm(self):
        pcm = (1000).to_bytes(2, "little", signed=True) + (-2000).to_bytes(2, "little", signed=True)
        half = game.scale_pcm(pcm, 2, 0.5)
        self.assertEqual([int.from_bytes(half[i:i + 2], "little", signed=True) for i in (0, 2)], [500, -1000])


class FakeMusic:
    backend = "fake"

    def __init__(self, clock):
        self.clock, self.played = clock, []

    def effect(self, name, priority=False):
        self.played.append((round(self.clock[0], 2), name, priority))

    def duration(self, name):
        return wav_seconds(name)

    def play(self, name):
        pass

    def stop(self):
        pass

    def stop_effects(self):
        pass

    def set_volume(self, group, gain):
        pass

    def pause(self):
        self.played.append((round(self.clock[0], 2), "PAUSE", False))

    def resume(self):
        self.played.append((round(self.clock[0], 2), "RESUME", False))


class Cues(unittest.TestCase):
    def setUp(self):
        self.clock = [0.0]
        self.real_time = game.time.time
        game.time.time = lambda: self.clock[0]

    def tearDown(self):
        game.time.time = self.real_time

    def test_level_line_waits_for_the_boss_roar(self):
        music = FakeMusic(self.clock)
        scr, app = make_app(music=True)
        app.music = music
        app.key(10)
        app.run.events = [("death", "grunt"), ("boss_death", "BONE DRAGON")]
        app.play_cues()
        self.clock[0] = 0.3
        app.run.events = [("level_complete", 5)]
        app.play_cues()
        for _ in range(60):
            self.clock[0] += 0.05
            app.play_cues()
        roar = wav_seconds("sfx/boss_bone_dragon.wav")
        (t1, s1, p1), (t2, s2, p2), (t3, s3, p3) = music.played
        self.assertEqual((s1, p1), ("sfx/grunt_death.wav", False))
        self.assertEqual((s2, p2), ("sfx/boss_bone_dragon.wav", True))
        self.assertEqual((s3, p3), ("voice/level5_complete.wav", True))
        self.assertGreaterEqual(t3, roar)

    def test_sound_off_plays_nothing(self):
        music = FakeMusic(self.clock)
        scr, app = make_app(music=False)
        app.music = music
        app.key(10)
        app.run.events = [("boss_death", "IRON GOLEM"), ("level_complete", 2), ("death", "brute")]
        app.play_cues()
        self.assertEqual(music.played, [])


    def test_music_pauses_with_the_game(self):
        music = FakeMusic(self.clock)
        scr, app = make_app(music=True)
        app.music = music
        app.key(10)
        app.sync_music()
        app.key(ord("p"))
        app.sync_music()
        self.assertEqual(music.played[-1][1], "PAUSE")
        app.key(ord("p"))
        app.sync_music()
        self.assertEqual(music.played[-1][1], "RESUME")


PLAYER = """#!{python}
# stand-in audio player: appends everything it is fed to {out}, at about 20x real speed
import sys, time
with open({out!r}, "ab") as f:
    while True:
        b = sys.stdin.buffer.read(8820)
        if not b:
            break
        f.write(b)
        f.flush()
        time.sleep(0.005)
"""


def state(pid):
    """'T' when the process is stopped (frozen), from ps (Linux and macOS)."""
    return subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()[:1]


@unittest.skipIf(os.name == "nt", "Linux/macOS players only")
class PauseOnLinuxAndMac(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ctd_player_")
        self.out = os.path.join(self.dir, "stream.raw")
        script = os.path.join(self.dir, "paplay")
        with open(script, "w") as f:
            f.write(PLAYER.format(python=sys.executable, out=self.out))
        os.chmod(script, 0o755)
        self.path = os.environ["PATH"]
        os.environ["PATH"] = self.dir + os.pathsep + self.path
        self.music = game.Music.__new__(game.Music)
        game.Music.__init__(self.music, game.MUSIC_DIR)
        self.music.backend, self.music.player = "pipe", "paplay"

    def tearDown(self):
        self.music.close()
        os.environ["PATH"] = self.path

    def size(self):
        return os.path.getsize(self.out) if os.path.exists(self.out) else 0

    def test_pause_freezes_the_stream_and_resume_carries_on(self):
        m = self.music
        m.play("level1_loop.wav")
        time.sleep(0.6)
        m.pause()
        time.sleep(0.3)
        self.assertEqual(state(m.proc.pid), "T", "the player is frozen")
        frozen = self.size()
        time.sleep(0.5)
        self.assertEqual(self.size(), frozen, "no music while paused")
        m.resume()
        time.sleep(0.6)
        self.assertNotEqual(state(m.proc.pid), "T")
        self.assertGreater(self.size(), frozen)
        started = time.time()
        m.stop()                                         # also fine while paused: see the next test
        self.assertLess(time.time() - started, 2.0)
        pcm = m._load("level1_loop.wav")[3]
        with open(self.out, "rb") as f:
            got = f.read()
        self.assertGreater(len(got), 0)
        self.assertEqual(got, (pcm * (len(got) // len(pcm) + 1))[:len(got)],
                         "the music goes on from where it was, it doesn't restart")

    def test_stop_while_paused_does_not_hang(self):
        m = self.music
        m.play("level2_loop.wav")
        time.sleep(0.4)
        m.pause()
        time.sleep(0.4)                                  # the feeding thread is now stuck on a full pipe
        started = time.time()
        m.stop()
        self.assertLess(time.time() - started, 2.0)
        self.assertFalse(m.paused)
        self.assertIsNone(m.thread)


class PauseOnWindows(unittest.TestCase):
    """winsound can't pause: resume() plays the loop from the paused moment (checked with a fake winsound)."""

    def test_resume_starts_the_loop_where_it_was_paused(self):
        calls = []
        fake = types.SimpleNamespace(PlaySound=lambda path, flags: calls.append(path), SND_FILENAME=1,
                                     SND_ASYNC=2, SND_LOOP=4, SND_NODEFAULT=8)
        real = sys.modules.get("winsound")
        sys.modules["winsound"] = fake
        clock = [100.0]
        real_time = game.time.time
        game.time.time = lambda: clock[0]
        m = game.Music.__new__(game.Music)
        game.Music.__init__(m, game.MUSIC_DIR)
        m.backend = "winsound"
        try:
            m.play("menu_loop.wav")
            clock[0] += 7.25                             # 7.25 s into the track...
            m.pause()
            self.assertIsNone(calls[-1])                 # ...the music stops
            clock[0] += 30                               # paused for 30 s
            m.resume()
            rate, ch, width, pcm = m._load("menu_loop.wav")
            cut = int(7.25 * rate) * ch * width
            with wave.open(calls[-1]) as w:
                data = w.readframes(w.getnframes())
            self.assertEqual(data, pcm[cut:] + pcm[:cut], "the loop restarts at 7.25 s and wraps around")
            clock[0] += 1.0                              # pausing again later lands at 8.25 s
            m.pause()
            m.resume()
            cut = int(8.25 * rate) * ch * width
            with wave.open(calls[-1]) as w:
                self.assertEqual(w.readframes(w.getnframes()), pcm[cut:] + pcm[:cut])
        finally:
            game.time.time = real_time
            m.close()
            if real is None:
                del sys.modules["winsound"]
            else:
                sys.modules["winsound"] = real


class PauseOnPygame(unittest.TestCase):
    def test_the_music_channel_is_paused_and_unpaused(self):
        calls = []
        m = game.Music.__new__(game.Music)
        game.Music.__init__(m, game.MUSIC_DIR)
        m.backend, m.playing, m.current = "pygame", True, "menu_loop.wav"
        m.channel = types.SimpleNamespace(pause=lambda: calls.append("pause"), unpause=lambda: calls.append("unpause"))
        m.pause()
        m.pause()                                        # twice is the same as once
        m.resume()
        self.assertEqual(calls, ["pause", "unpause"])


if __name__ == "__main__":
    unittest.main()
