# Contributing to cool tower defense game.exe

Thanks for helping! The whole game is one Python file using only the standard library, so getting started
takes a minute.

## Setup

```bash
git clone https://github.com/zsidiadi/Ball-Heckaton-ascii-game.git
cd Ball-Heckaton-ascii-game
python3 "cool tower defense game.exe.py"        # Windows: pip install windows-curses, then py "cool tower defense game.exe.py"
```

You need Python 3.8 or newer. Nothing else is required to play or to run the tests.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests need no terminal and no sound card. They draw every screen into a fake screen, let a bot play
whole runs, check the game rules and sounds, and check that the README's tables and version match the code.
They run in under two minutes and never touch your save file. GitHub Actions runs them on every push and pull
request on Linux (Python 3.8 and 3.13), macOS and Windows: see `.github/workflows/tests.yml`.

| File | What it checks |
| --- | --- |
| `tests/test_gameplay.py` | paths, weapons, buildings, blessings, bosses, saving, whole bot-played runs |
| `tests/test_screens.py` | every menu at every size, the menu castle, buttons by mouse and key, side-panel width, the Premium store never charging |
| `tests/test_sound.py` | every sound file exists, sound cues and their timing (with a fake audio player) |
| `tests/test_docs.py` | README numbers, lists and version match the code; every link inside the repo works |
| `tests/helpers.py` | loads the game, the fake screen, the bot |

If you change a number in the game (a weapon's cost, a boss's HP, …), `test_docs.py` fails until the README
says the same. That's on purpose, so the docs never drift from the game.

## Workflow

- **Branches:** `main` is the stable, playable version. Work on `test` (or a feature branch) and merge into
  `main` once the tests pass and you've played at least one wave.
- **Commits:** short imperative summaries, e.g. `Add flying enemies` or `Fix cursor on small terminals`.
- **Changelog:** every change that players or developers would notice gets a line under `## [Unreleased]` in
  [CHANGELOG.md](CHANGELOG.md), grouped as *Added*, *Changed*, *Fixed* or *Removed*
  ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/)).

## Releasing

Versions follow [Semantic Versioning](https://semver.org/): new features bump the minor version
(1.**1**.0), fixes bump the patch version (1.0.**1**).

1. In `CHANGELOG.md`, rename `## [Unreleased]` to the new version and today's date, and add an empty
   `## [Unreleased]` above it.
2. Set `VERSION` near the top of `cool tower defense game.exe.py`.
3. In `README.md`, update the version badge and add a row to the **Project history** table.
4. Run the tests, commit (`Release X.Y.Z: …`) and push.
5. Fill in the release's commit hash in the CHANGELOG's link list and the README history table, and
   optionally tag it:
   ```bash
   git tag -a vX.Y.Z <commit> -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```

Release dates are the authors' local dates (UTC+3).

## Sound and music

The game plays the WAV files in `assets/`. They are made from the original recordings in `assets/source/` by
two scripts, which need `numpy` (`pip install -r tools/requirements.txt`) and `ffmpeg`:

- `tools/make_loops.py`: the seamless music loops (menu and levels 1-5).
- `tools/make_sfx.py`: death sounds, boss death sounds, voice lines and the special thanks. To add a sound,
  put the recording in `assets/source/`, add a line to its `SOUNDS` table, and run the script.

Both scripts rebuild the existing files byte for byte, so you can always check that nothing else changed.
