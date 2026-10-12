#!/usr/bin/env python3
"""
Rebuild the seamless music loops in assets/ (menu + levels 1-5) from the originals in assets/source/.

Why: every source track is exactly 16 bars at 132 BPM, so its length is a perfect loop, but the ends
were not made to loop: some fade to near-silence in the last ~45 ms (a dropout at every repeat), others
end on a sample far from the first one (a click at every repeat).

How:
  1. Find a "donor" bar line inside the track whose lead-in sounds like our ending (spectral
     similarity of the last beat) and whose next bar sounds like bar 1.
  2. Tail: crossfade (30 ms, loudness-preserving) from the original ending into the donor's lead-in, which
     replaces the faded 45 ms with music that naturally flows into a downbeat.
  3. Head: crossfade (25 ms) from the donor's continuation into the real opening, so the very last
     sample flows into the very first one with no discontinuity.
  The loop length is unchanged, so the beat never stumbles.

Needs: python3, numpy, ffmpeg (only for decoding the OGG). The game itself needs none of these.
Usage: python3 tools/make_loops.py                 # rebuild every track in TRACKS
       python3 tools/make_loops.py src.ogg out.wav [donor_bar]   # one custom track
(with the default settings it reproduces the shipped WAVs byte for byte)
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = 16            # every track is 16 bars of 4/4 at 132 BPM
FADE_MS, TAIL_XF_MS, HEAD_XF_MS = 45, 30, 25
# source, output, donor bar. The donor bars were picked by spectral analysis (lead-in sounds like the
# track's ending AND the following bar sounds like bar 1) and checked at the seam. None = search automatically.
TRACKS = [
    ("medieval_td_loop.ogg", "menu_loop.wav",   11),
    ("Level_1.ogg",          "level1_loop.wav",  5),
    ("Level_2.ogg",          "level2_loop.wav",  5),
    ("Level_3.ogg",          "level3_loop.wav",  5),
    ("Level_4.ogg",          "level4_loop.wav",  5),
    ("Level_5.ogg",          "level5_loop.wav", 11),
]


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


def xfade(a, b):
    """Crossfade a -> b that keeps the loudness constant whatever the two signals are:
    gains (1-f, f) normalised by the expected power (1-f)^2 + f^2 + 2*rho*f*(1-f), where rho is their
    correlation. Unrelated audio (rho=0) gets an equal-power fade, near-identical audio (rho=1) a linear one,
    so similar downbeats don't add up into a volume bump."""
    rho = min(1.0, max(0.0, float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))))
    f = np.linspace(0.0, 1.0, len(a))
    return (a * (1 - f) + b * f) / np.sqrt((1 - f) ** 2 + f ** 2 + 2 * rho * f * (1 - f))


def make_loop(src, out, donor_bar=None):
    x, sr = decode(src)
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
    if donor_bar:
        score, t, bar_no = next(c for c in candidates if c[2] == donor_bar)
    # fine-align the donor (+-4 ms) so the tail crossfade overlaps similar waveforms
    a = x[n - p: n - p + xf]
    def overlap(l):
        seg = x[t - p + l: t - p + l + xf]
        return float(np.dot(a, seg) / (np.linalg.norm(a) * np.linalg.norm(seg) + 1e-12))
    lag = max(range(-int(0.004 * sr), int(0.004 * sr) + 1), key=overlap)
    td = t + lag
    print(f"{os.path.basename(src)}: donor = lead-in to bar {bar_no} at {td / sr:.3f}s (score {score:.3f})")

    # 2) tail and 3) head
    y = x.copy()
    donor = x[td - p: td]
    y[n - p: n - p + xf] = xfade(x[n - p: n - p + xf], donor[:xf])
    y[n - p + xf:] = donor[xf:]
    y[:head] = xfade(x[td: td + head], x[:head])

    peak = np.abs(y).max()
    if peak > 0.98:
        y *= 0.98 / peak
    pcm = np.clip(np.round(y * 32767), -32768, 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    print(f"  wrote {out}: {n / sr:.4f}s, {sr} Hz mono")


def main():
    if len(sys.argv) >= 3:
        make_loop(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
        return
    for src, out, donor in TRACKS:
        make_loop(os.path.join(ROOT, "assets", "source", src), os.path.join(ROOT, "assets", out), donor)


if __name__ == "__main__":
    main()
