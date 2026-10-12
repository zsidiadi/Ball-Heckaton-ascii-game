#!/usr/bin/env python3
"""
Make the game's sound effects and voice lines from the recordings in assets/source/.

  - enemy death sounds (Grunt.m4a, Runner.m4a, Brute.m4a: three takes each)  -> assets/sfx/
  - "level complete" voice lines (Level_N_complete.m4a: one take each)        -> assets/voice/
  - the creator's special thanks (special_thanks_from_the_creator.m4a)        -> assets/special/

For every recording this script:
  1. finds the takes (10 ms energy envelope, gaps of silence between them),
  2. keeps the take listed in SOUNDS (picked by level, length and no clipping), or, for voice lines
     (take None), the whole recording from the first to the last spoken word (breaths/clicks around it skipped),
  3. trims it tightly (from 5 ms before the sound starts to 20 ms after it ends),
  4. removes rumble below ~70 Hz, adds a 3 ms fade-in and a 25 ms fade-out so it never clicks,
  5. levels it so its loudest 100 ms hits the target in SOUNDS (death sounds -16 dBFS, voice lines
     -14 dBFS so they come through clearly); a gentle peak limiter keeps every sample under -1 dBFS,
  6. writes a 44.1 kHz mono 16-bit WAV.

Needs: python3, numpy, ffmpeg (for decoding the m4a). The game itself needs none of these.
Usage: python3 tools/make_sfx.py            (prints every take it finds, then writes the chosen ones)
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "source")
ASSETS = os.path.join(ROOT, "assets")
RATE = 44100
PEAK_DB = -1.0                          # sample ceiling
VOICE_MAX_CUT_DB = 3.0                  # voice lines: the limiter may lower a peak by at most this much

# recording -> (output path under assets/, take to use (1-based) or None = whole recording,
#               loudness of the loudest 100 ms in dBFS)
SOUNDS = {
    "Grunt.m4a":  ("sfx/grunt_death.wav", 2, -16.0),     # clearly the loudest / fullest take (others 4-5 dB quieter)
    "Runner.m4a": ("sfx/runner_death.wav", 2, -16.0),    # all three are short and strong; take 2 has the most energy
    "Brute.m4a":  ("sfx/brute_death.wav", 3, -16.0),     # longest, strongest take; take 1 sounds cut short (180 ms)
    "Level_1_complete.m4a": ("voice/level1_complete.wav", None, -14.0),
    "Level_2_complete.m4a": ("voice/level2_complete.wav", None, -14.0),
    "Level_3_complete.m4a": ("voice/level3_complete.wav", None, -14.0),
    "Level_4_complete.m4a": ("voice/level4_complete.wav", None, -14.0),
    "Level_5_complete.m4a": ("voice/level5_complete.wav", None, -14.0),
    "special_thanks_from_the_creator.m4a": ("special/special_thanks_from_the_creator.wav", None, -14.0),
}


def decode(path):
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "1", "-ar", str(RATE),
                    "-acodec", "pcm_s16le", tmp], check=True)
    with wave.open(tmp) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    os.remove(tmp)
    return x


def find_takes(x):
    """Return (start, end) sample ranges of the takes."""
    win = int(0.010 * RATE)
    env = np.array([np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, len(x) - win, win)])
    thr = env.max() * 0.08
    active = env > thr
    takes, i = [], 0
    while i < len(active):
        if active[i]:
            j = i
            while j < len(active) and (active[j] or active[j:j + 15].any()):   # bridge gaps < 150 ms
                j += 1
            takes.append((i * win, j * win))
            i = j
        else:
            i += 1
    return takes


def tighten(x, start, end):
    """Grow the take outwards to where the sound really starts / fades (-55 dBFS), plus small margins."""
    quiet = 10 ** (-55 / 20)
    s = start
    while s > 0 and abs(x[s - 1]) > quiet:
        s -= 1
    e = end
    while e < len(x) and np.max(np.abs(x[e:e + 64])) > quiet:
        e += 64
    return max(0, s - int(0.005 * RATE)), min(len(x), e + int(0.020 * RATE))


def speech_span(x):
    """Voice lines: start 30 ms before the first 20 ms window within 25 dB of the loudest one, end 80 ms after
    the last such window. This skips breaths, clicks and room noise before/after the words."""
    win = int(0.020 * RATE)
    env = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + win] ** 2)) + 1e-12) for i in range(0, len(x) - win, win)])
    idx = np.nonzero(env > env.max() - 25)[0]
    return max(0, idx[0] * win - int(0.030 * RATE)), min(len(x), (idx[-1] + 1) * win + int(0.080 * RATE))


def highpass(x, cutoff=70.0):
    a = 1.0 / (1.0 + 2 * np.pi * cutoff / RATE)          # first-order high-pass
    y = np.zeros_like(x)
    prev_x = prev_y = 0.0
    for i, v in enumerate(x):
        prev_y = a * (prev_y + v - prev_x)
        prev_x = v
        y[i] = prev_y
    return y


def process(x, target_db=-16.0, max_cut_db=None):
    x = highpass(x)
    fi, fo = int(0.003 * RATE), int(0.025 * RATE)
    x[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi)) ** 2
    x[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
    win = int(0.100 * RATE)
    loudest = max(np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, max(1, len(x) - win), win // 4))
    gain = 10 ** (target_db / 20) / loudest
    if max_cut_db is not None:          # never let the limiter squash a peak by more than this (voice stays clean)
        gain = min(gain, 10 ** ((PEAK_DB + max_cut_db) / 20) / np.max(np.abs(x)))
    x *= gain
    return limit(x, 10 ** (PEAK_DB / 20))


def limit(x, ceiling):
    """Gentle peak limiter: per-sample gain that keeps |x| <= ceiling, spread over +-2 ms so it doesn't distort."""
    gain = np.minimum(1.0, ceiling / np.maximum(np.abs(x), 1e-9))
    k = int(0.002 * RATE)
    padded = np.pad(gain, k, mode="edge")
    gmin = np.min(np.lib.stride_tricks.sliding_window_view(padded, 2 * k + 1), axis=1)      # look ahead/behind
    smooth = np.convolve(np.pad(gmin, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    return x * np.minimum(smooth, gmin)


def main():
    for src, (out, take, target) in SOUNDS.items():
        x = decode(os.path.join(SRC_DIR, src))
        if take is None:                              # voice line: from the first to the last spoken word
            s, e = speech_span(x)
            print(f"{src}: whole recording, speech {s / RATE:.2f}-{e / RATE:.2f}s")
        else:
            takes = find_takes(x)
            for k, (a, b) in enumerate(takes, 1):
                seg = x[a:b]
                print(f"{src} take {k}: {a / RATE:5.2f}-{b / RATE:5.2f}s  peak {20 * np.log10(np.abs(seg).max()):6.1f} dBFS"
                      f"  rms {20 * np.log10(np.sqrt(np.mean(seg ** 2))):6.1f} dBFS{'   <- used' if k == take else ''}")
            s, e = tighten(x, *takes[take - 1])
        y = process(x[s:e].copy(), target, None if take else VOICE_MAX_CUT_DB)
        pcm = np.clip(np.round(y * 32767), -32768, 32767).astype(np.int16)
        os.makedirs(os.path.dirname(os.path.join(ASSETS, out)), exist_ok=True)
        with wave.open(os.path.join(ASSETS, out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        print(f"  -> assets/{out}: {len(pcm) / RATE * 1000:.0f} ms, peak {20 * np.log10(np.abs(y).max()):.1f} dBFS\n")


if __name__ == "__main__":
    main()
