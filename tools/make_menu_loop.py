#!/usr/bin/env python3
"""
Rebuild assets/menu_loop.wav (the seamless menu-music loop) from assets/source/medieval_td_loop.ogg.

Why: the source track is exactly 16 bars at 132 BPM, so its length is a perfect loop, but the last
~45 ms were faded to near-silence. Looping it as-is gives an audible dropout at every repeat.

How:
  1. Find a "donor" bar line inside the track whose lead-in sounds like our ending (spectral
     similarity of the last beat) and whose next bar sounds like bar 1.
  2. Tail: crossfade (30 ms, equal-power) from the original ending into the donor's lead-in, which
     replaces the faded 45 ms with music that naturally flows into a downbeat.
  3. Head: crossfade (25 ms) from the donor's continuation into the real opening, so the very last
     sample flows into the very first one with no discontinuity.
  The loop length is unchanged, so the beat never stumbles.

Needs: python3, numpy, ffmpeg (only for decoding the OGG). The game itself needs none of these.
Usage: python3 tools/make_menu_loop.py [source.ogg] [output.wav]
(with the default settings it reproduces assets/menu_loop.wav byte for byte)
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "source", "medieval_td_loop.ogg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "assets", "menu_loop.wav")
BARS = 16            # the track is 16 bars of 4/4 at 132 BPM
FADE_MS, TAIL_XF_MS, HEAD_XF_MS = 45, 30, 25
DONOR_BAR = 11       # verified by ear-level analysis: the lead-in to bar 11 matches the seam best.
                     # Set to None to search automatically (useful if the source track changes).


def decode(path):
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-acodec", "pcm_s16le", tmp], check=True)
    with wave.open(tmp) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    os.remove(tmp)
    return (x.reshape(-1, ch).mean(axis=1) if ch > 1 else x), sr


def logspec(seg, n=1024, hop=256):
    frames = [seg[i:i + n] * np.hanning(n) for i in range(0, len(seg) - n, hop)]
    return np.log1p(np.abs(np.fft.rfft(np.array(frames), axis=1)))


def similarity(a, b):
    A, B = logspec(a), logspec(b)
    m = min(len(A), len(B))
    A, B = A[:m].ravel() - A[:m].mean(), B[:m].ravel() - B[:m].mean()
    return float(np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B) + 1e-12))


def ramps(k):
    th = np.linspace(0, np.pi / 2, k)
    return np.cos(th), np.sin(th)


def main():
    x, sr = decode(SRC)
    n = len(x)
    bar = n / BARS
    fade, xf, head = (int(ms / 1000 * sr) for ms in (FADE_MS, TAIL_XF_MS, HEAD_XF_MS))
    p = fade + xf
    beat = int(bar / 4)

    # 1) pick the donor bar line
    end_ctx = x[n - fade - beat: n - fade]
    candidates = []
    for k in range(1, BARS):
        t = int(round(k * bar))
        score = similarity(end_ctx, x[t - fade - beat: t - fade]) * similarity(x[:int(bar)], x[t:t + int(bar)])
        candidates.append((score, t, k + 1))
    score, t, bar_no = max(candidates)
    if DONOR_BAR:
        score, t, bar_no = next(c for c in candidates if c[2] == DONOR_BAR)
    # fine-align the donor (+-4 ms) so the tail crossfade overlaps similar waveforms
    a = x[n - p: n - p + xf]
    def overlap(l):
        seg = x[t - p + l: t - p + l + xf]
        return float(np.dot(a, seg) / (np.linalg.norm(a) * np.linalg.norm(seg) + 1e-12))
    lag = max(range(-int(0.004 * sr), int(0.004 * sr) + 1), key=overlap)
    td = t + lag
    print(f"donor: lead-in to bar {bar_no} at {td / sr:.3f}s (score {score:.3f})")

    # 2) tail and 3) head
    y = x.copy()
    out_r, in_r = ramps(xf)
    donor = x[td - p: td]
    y[n - p: n - p + xf] = x[n - p: n - p + xf] * out_r + donor[:xf] * in_r
    y[n - p + xf:] = donor[xf:]
    out_r, in_r = ramps(head)
    y[:head] = x[td: td + head] * out_r + x[:head] * in_r

    peak = np.abs(y).max()
    if peak > 0.98:
        y *= 0.98 / peak
    pcm = np.clip(np.round(y * 32767), -32768, 32767).astype(np.int16)
    with wave.open(OUT, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    print(f"wrote {OUT}: {n / sr:.4f}s, {sr} Hz mono")


if __name__ == "__main__":
    main()
