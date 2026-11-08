#!/usr/bin/env python3
"""Tema de sonidos "AxolOS", sintetizado (nada que licenciar).

Uso: sonidos_axolos.py SALIDA_DIR   (necesita ffmpeg para pasar a .oga)

Timbre de "cristal": senoidal + armónicos suaves con caída exponencial y una
reverberación corta. Todo en La mayor (A–C#–E), para que suene a un mismo sistema.
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
A3, CS4, E4, A4, CS5, E5, A5 = 220.0, 277.18, 329.63, 440.0, 554.37, 659.26, 880.0


def bell(f, dur, amp=1.0, decay=5.0):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-decay * t) * (1 - np.exp(-t * 900))          # ataque suave, sin clic
    tone = (np.sin(2 * np.pi * f * t) + 0.32 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-3 * t)
            + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-6 * t))
    return amp * env * tone


def seq(notes, gap, dur, decay=5.0, amps=None):
    total = int(SR * (gap * (len(notes) - 1) + dur))
    out = np.zeros(total)
    for i, f in enumerate(notes):
        s = bell(f, dur, (amps[i] if amps else 1.0), decay)
        a = int(SR * gap * i)
        out[a:a + len(s)] += s
    return out


def glide(f0, f1, dur, decay=7.0):
    t = np.arange(int(SR * dur)) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.exp(-decay * t) * (1 - np.exp(-t * 900)) * (np.sin(ph) + 0.2 * np.sin(2 * ph))


def room(x, mix=0.22):
    out = np.copy(x)
    for d, g in ((0.031, 0.5), (0.047, 0.4), (0.071, 0.3), (0.109, 0.2)):
        n = int(SR * d)
        y = np.zeros(len(x) + n * 6)
        y[:len(x)] += x
        for k in range(1, 6):
            y[n * k:n * k + len(x)] += x * (g ** k)
        out = np.pad(out, (0, len(y) - len(out))) + mix * (y - np.pad(x, (0, len(y) - len(x))))
    return out


def master(x, peak_db=-3.0):
    x = room(x)
    fade = int(SR * 0.03)
    x[-fade:] *= np.linspace(1, 0, fade)
    return x / np.max(np.abs(x)) * 10 ** (peak_db / 20)


SOUNDS = {
    "desktop-login":        lambda: master(seq([A3, E4, A4, CS5], 0.16, 1.6, 3.2, [0.8, 0.8, 0.9, 1.0]), -4),
    "desktop-logout":       lambda: master(seq([CS5, A4, E4, A3], 0.15, 1.3, 3.6, [0.9, 0.85, 0.8, 0.8]), -5),
    "message-new-instant":  lambda: master(seq([E5, A5], 0.09, 0.45, 9), -8),
    "message":              lambda: master(seq([E5, A5], 0.09, 0.45, 9), -8),
    "dialog-information":   lambda: master(bell(A5, 0.5, 1, 8), -10),
    "bell":                 lambda: master(bell(A5, 0.5, 1, 8), -10),
    "dialog-warning":       lambda: master(seq([E4, E4], 0.14, 0.5, 8), -8),
    "dialog-error":         lambda: master(seq([CS4, A3], 0.13, 0.6, 7), -7),
    "complete":             lambda: master(seq([A4, CS5, E5], 0.07, 0.6, 7), -9),
    "device-added":         lambda: master(glide(440, 880, 0.35), -9),
    "device-removed":       lambda: master(glide(880, 440, 0.35), -9),
    "audio-volume-change":  lambda: master(bell(E5, 0.12, 1, 30), -14),
    "trash-empty":          lambda: master(glide(660, 220, 0.4, 6), -10),
}


def main():
    out = Path(sys.argv[1]); st = out / "stereo"; st.mkdir(parents=True, exist_ok=True)
    report = []
    for name, make in SOUNDS.items():
        x = make()
        pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
        tmp = st / f"{name}.wav"
        with wave.open(str(tmp), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-c:a", "libvorbis",
                        "-q:a", "5", str(st / f"{name}.oga")], check=True)
        tmp.unlink()
        rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
        win = int(SR * 0.1)
        loud = max(20 * np.log10(np.sqrt(np.mean(x[i:i + win] ** 2)) + 1e-9) for i in range(0, max(1, len(x) - win), win))
        report.append(f"  {name:22s} {len(x)/SR:4.2f} s   pico {20*np.log10(np.max(np.abs(x))):6.1f} dBFS   RMS {rms:6.1f}   máx 100 ms {loud:6.1f}")
    (out / "index.theme").write_text(
        "[Sound Theme]\nName=AxolOS\nComment=Sonidos de cristal de AxolOS\nInherits=ocean,freedesktop\n"
        "Directories=stereo\n\n[stereo]\nOutputProfile=stereo\n", encoding="utf-8")
    print("Tema de sonidos AxolOS:"); print("\n".join(report))


if __name__ == "__main__":
    main()
