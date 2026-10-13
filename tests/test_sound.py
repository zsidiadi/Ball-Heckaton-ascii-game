"""Sound: every sound the game asks for exists and is a valid WAV, and the run's sound cues turn into the right
sounds at the right time (without a real audio player)."""
import os
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


if __name__ == "__main__":
    unittest.main()
