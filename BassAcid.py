#!/usr/bin/env python3
"""
BassAcid.py - Generador de línea de bajo estilo Hard Acid / Rolling 303 para Bitwig Studio.
Basado en BassAcid.lua (155 BPM, 4 compases, 64 semicorcheas).
Genera groove hipnótico con slides (legato overlap para emuladores 303 y sintes VST) y acentos de velocidad.

Uso:
    python3 BassAcid.py
    python3 BassAcid.py --bpm 155 --root 50 --bars 4 --output ./output/BassAcid.mid
"""

import os
import sys
import random
import argparse
from pathlib import Path

# Permitir importar midi_core desde el mismo directorio
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from midi_core import (
    MidiSequence,
    TICKS_PER_16TH,
    TICKS_PER_BAR,
    note_name_to_midi,
    build_timestamped_filename,
)


def generate_bass_acid(
    bpm: float = 155.0,
    root_note: int = 50,  # D3 / D-2 en rack (MIDI 50)
    total_bars: int = 4,
    accent_vol: int = 127,
    normal_vol: int = 84,
    seed: int = None,
    output_path: str = None
) -> str:
    if seed is not None:
        random.seed(seed)

    seq = MidiSequence(name="BassAcid_Rolling_303", bpm=bpm)
    track = seq.track

    # Escala: D Minor Pentatonic / Acid Box (D-1, D-2, F-2, G-2, G#-2, A-2, C-3, D-3)
    scale_intervals = [-12, 0, 0, 3, 5, 6, 7, 10, 12, 15]

    # Generar motivo motriz base de 16 semicorcheas (1 compás)
    base_riff = []
    for step in range(1, 17):
        is_kick_beat = ((step - 1) % 4 == 0)  # Pasos 1, 5, 9, 13 (golpe 4x4)

        if is_kick_beat:
            # En el golpe del Kick: 75% silencio para dejar espacio al bombo, o tónica raíz corta
            if random.random() > 0.25:
                base_riff.append({"type": "off"})
            else:
                base_riff.append({
                    "type": "note",
                    "offset": 0,
                    "accent": False,
                    "slide": False,
                    "gate_ratio": 0.50  # Nota corta/staccato
                })
        else:
            # En contratiempos y rolling 16ths: alta actividad
            if random.random() > 0.20:
                note_off = random.choice(scale_intervals)
                is_acc = (random.random() > 0.65)
                is_sld = (random.random() > 0.70)
                base_riff.append({
                    "type": "note",
                    "offset": note_off,
                    "accent": is_acc,
                    "slide": is_sld,
                    "gate_ratio": 1.10 if is_sld else 0.80  # Slide = solapamiento legato (>100%)
                })
            else:
                base_riff.append({"type": "off"})

    notes_placed = 0

    # Renderizar los compases con evolución musical
    for bar in range(total_bars):
        bar_tick = bar * TICKS_PER_BAR

        for step in range(1, 17):
            step_tick = bar_tick + (step - 1) * TICKS_PER_16TH
            item = base_riff[step - 1]

            # Compás final (bar == total_bars - 1): Variación / Fill activo en las últimas semicorcheas
            if bar == (total_bars - 1) and step >= 9:
                if random.random() > 0.25:
                    item = {
                        "type": "note",
                        "offset": 12 if (step % 2 == 0) else random.choice(scale_intervals),
                        "accent": (step >= 13),
                        "slide": (step % 3 == 0),
                        "gate_ratio": 1.12 if (step % 3 == 0) else 0.85
                    }

            if item["type"] == "note":
                note_num = max(0, min(127, root_note + item["offset"]))
                vel = accent_vol if item["accent"] else normal_vol
                gate = item.get("gate_ratio", 0.80)
                duration = int(TICKS_PER_16TH * gate)

                track.add_note(
                    tick=step_tick,
                    duration_ticks=duration,
                    note=note_num,
                    velocity=vel,
                    channel=0
                )
                notes_placed += 1

    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename("BassAcid_Rolling_303.mid", directory=output_dir)

    saved = seq.save(output_path, copy_to_bitwig=True)
    return saved, notes_placed


def main():
    parser = argparse.ArgumentParser(description="Generador de BassAcid (Rolling 303) para Bitwig")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--root", type=str, default="50", help="Nota raíz MIDI o nombre (default: 50 / D3)")
    parser.add_argument("--bars", type=int, default=4, help="Cantidad de compases (default: 4)")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria opcional")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    saved_paths, count = generate_bass_acid(
        bpm=args.bpm,
        root_note=root_midi,
        total_bars=args.bars,
        seed=args.seed,
        output_path=args.output
    )

    print(f"\n[OK] BassAcid (Rolling 303) generado:")
    print(f"  • Notas colocadas: {count}")
    print(f"  • Tempo: {args.bpm} BPM | Compases: {args.bars} | Raíz: {root_midi}")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
