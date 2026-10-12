#!/usr/bin/env python3
"""
Cut the enemy death sounds out of the voice recordings in assets/source/ and write them to assets/sfx/.

Each recording (Grunt.m4a, Runner.m4a, Brute.m4a) has three takes separated by silence. For every
recording this script:
  1. finds the takes (10 ms energy envelope, gaps of silence between them),
  2. keeps the take listed in TAKES (picked by level, length and no clipping: see the table below),
  3. trims it tightly (from 5 ms before the sound starts to 20 ms after it ends),
  4. removes rumble below ~70 Hz, adds a 3 ms fade-in and a 25 ms fade-out so it never clicks,
  5. levels it so its loudest 100 ms hits -16 dBFS like the others (a gentle peak limiter keeps
     every sample under -1 dBFS),
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
OUT_DIR = os.path.join(ROOT, "assets", "sfx")
RATE = 44100
TARGET_DB, PEAK_DB = -16.0, -1.0       # loudness of the loudest 100 ms, and the sample ceiling

# recording -> (output file, which take to use, 1-based)
TAKES = {
    "Grunt.m4a":  ("grunt_death.wav", 2),    # clearly the loudest / fullest take (others 4-5 dB quieter)
    "Runner.m4a": ("runner_death.wav", 2),   # all three are short and strong; take 2 has the most energy
    "Brute.m4a":  ("brute_death.wav", 3),    # longest, strongest take; take 1 sounds cut short (180 ms)
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


def highpass(x, cutoff=70.0):
    a = 1.0 / (1.0 + 2 * np.pi * cutoff / RATE)          # first-order high-pass
    y = np.zeros_like(x)
    prev_x = prev_y = 0.0
    for i, v in enumerate(x):
        prev_y = a * (prev_y + v - prev_x)
        prev_x = v
        y[i] = prev_y
    return y


def process(x):
    x = highpass(x)
    fi, fo = int(0.003 * RATE), int(0.025 * RATE)
    x[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi)) ** 2
    x[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
    win = int(0.100 * RATE)
    loudest = max(np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, max(1, len(x) - win), win // 4))
    x *= 10 ** (TARGET_DB / 20) / loudest
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
    os.makedirs(OUT_DIR, exist_ok=True)
    for src, (out, take) in TAKES.items():
        x = decode(os.path.join(SRC_DIR, src))
        takes = find_takes(x)
        for k, (a, b) in enumerate(takes, 1):
            seg = x[a:b]
            print(f"{src} take {k}: {a / RATE:5.2f}-{b / RATE:5.2f}s  peak {20 * np.log10(np.abs(seg).max()):6.1f} dBFS"
                  f"  rms {20 * np.log10(np.sqrt(np.mean(seg ** 2))):6.1f} dBFS{'   <- used' if k == take else ''}")
        s, e = tighten(x, *takes[take - 1])
        y = process(x[s:e].copy())
        pcm = np.clip(np.round(y * 32767), -32768, 32767).astype(np.int16)
        with wave.open(os.path.join(OUT_DIR, out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        print(f"  -> assets/sfx/{out}: {len(pcm) / RATE * 1000:.0f} ms, peak {20 * np.log10(np.abs(y).max()):.1f} dBFS\n")


if __name__ == "__main__":
    main()
