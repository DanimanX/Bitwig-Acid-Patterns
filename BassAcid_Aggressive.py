#!/usr/bin/env python3
"""
BassAcid_Aggressive.py - Generador de bajo Hard / Aggressive Acid Techno (Marie Vaunt @ Verknipt style).
Intervalos oscuros (D Frigio, Tritono, saltos de octava y doble octava 303 scream),
rolling implacable de semicorcheas y acentos extremos.

Uso:
    python3 BassAcid_Aggressive.py
    python3 BassAcid_Aggressive.py --bpm 155 --root 50 --bars 4 --output ./output/BassAcid_Aggressive.mid
"""

import sys
import random
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from midi_core import (
    MidiSequence,
    TICKS_PER_16TH,
    TICKS_PER_BAR,
    note_name_to_midi,
    build_timestamped_filename,
)

# Nombre canónico de salida (sin timestamp). Un script = un archivo con este nombre.
DEFAULT_OUTPUT_STEM = "BassAcid_Aggressive_Verknipt"


def generate_bass_acid_aggressive(
    bpm: float = 155.0,
    root_note: int = 50,  # D3 (MIDI 50)
    total_bars: int = 4,
    accent_vol: int = 127,
    normal_vol: int = 80,
    ghost_vol: int = 54,
    seed: int = None,
    output_path: str = None
):
    if seed is not None:
        random.seed(seed)

    seq = MidiSequence(name="BassAcid_Aggressive_Verknipt", bpm=bpm)
    track = seq.track

    # Intervalos oscuros y agresivos (D Frigio / Tritono / Screams)
    # -12: Subgrave, 0: Tónica, 1: D# (tensión frigia brutal), 3: F, 5: G, 6: G# (tritono),
    # 7: A, 12: D alta, 13: D# aguda, 24: D scream doble octava
    dark_intervals = [-12, 0, 0, 1, 3, 5, 6, 7, 12, 12, 13, 24]

    # Generar motivo motriz base de 16 semicorcheas
    base_riff = []
    for step in range(1, 17):
        is_kick_beat = ((step - 1) % 4 == 0)  # Pasos 1, 5, 9, 13
        is_offbeat = ((step - 1) % 4 == 2)    # Pasos 3, 7, 11, 15 (contratiempos)

        if is_kick_beat:
            # En el golpe del kick: espacio para el kick o tónica subgrave seca
            if random.random() > 0.35:
                base_riff.append({"type": "off"})
            else:
                base_riff.append({
                    "type": "note",
                    "offset": 0 if (random.random() > 0.5) else -12,
                    "accent": False,
                    "slide": False,
                    "vol": normal_vol,
                    "gate_ratio": 0.45
                })
        elif is_offbeat:
            # Contratiempos: ancla energética, notas acentuadas o saltos de octava
            scream = (random.random() > 0.40)
            base_riff.append({
                "type": "note",
                "offset": 12 if scream else random.choice(dark_intervals),
                "accent": True,
                "slide": scream,
                "vol": accent_vol,
                "gate_ratio": 1.15 if scream else 0.85
            })
        else:
            # Rolling 16ths continuas
            if random.random() > 0.15:
                is_acc = (random.random() > 0.70)
                is_sld = (random.random() > 0.60)
                offset = random.choice(dark_intervals)
                if is_acc:
                    v = accent_vol
                else:
                    v = normal_vol if (random.random() > 0.5) else ghost_vol

                base_riff.append({
                    "type": "note",
                    "offset": offset,
                    "accent": is_acc,
                    "slide": is_sld,
                    "vol": v,
                    "gate_ratio": 1.12 if is_sld else 0.75
                })
            else:
                base_riff.append({"type": "off"})

    notes_placed = 0

    # Renderizado con progresión dramática de ferocidad rave
    for bar in range(total_bars):
        bar_tick = bar * TICKS_PER_BAR

        for step in range(1, 17):
            step_tick = bar_tick + (step - 1) * TICKS_PER_16TH
            item = dict(base_riff[step - 1])

            # Variaciones progresivas según compás:
            if bar == 1:
                # Compás 2: Más slides agudos en contratiempos
                if step in (7, 15):
                    item = {"type": "note", "offset": 12, "accent": True, "slide": True, "vol": accent_vol, "gate_ratio": 1.15}
            elif bar == 2:
                # Compás 3: Tensión con tritono (+6) y semitono frigio (+1)
                if step in (3, 11):
                    item = {"type": "note", "offset": 6 if (random.random() > 0.5) else 1, "accent": True, "slide": True, "vol": accent_vol, "gate_ratio": 1.15}
            elif bar == (total_bars - 1):
                # Compás final: Clímax y fill salvaje ametralladora antes de resolver
                if step >= 9:
                    fill_offsets = [0, 12, 13, 24, 12, 6, 1, 0]
                    fill_idx = step - 9
                    item = {
                        "type": "note",
                        "offset": fill_offsets[fill_idx] if fill_idx < len(fill_offsets) else 12,
                        "accent": True,
                        "slide": (step % 2 == 0),
                        "vol": accent_vol,
                        "gate_ratio": 1.15 if (step % 2 == 0) else 0.85
                    }

            if item["type"] == "note":
                note_num = max(0, min(127, root_note + item["offset"]))
                vel = item.get("vol", normal_vol)
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
        output_path = build_timestamped_filename(DEFAULT_OUTPUT_STEM, directory=output_dir)

    saved = seq.save(output_path, copy_to_bitwig=True)
    return saved, notes_placed


def main():
    parser = argparse.ArgumentParser(description="Generador de BassAcid Aggressive (Marie Vaunt style) para Bitwig")
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

    saved_paths, count = generate_bass_acid_aggressive(
        bpm=args.bpm,
        root_note=root_midi,
        total_bars=args.bars,
        seed=args.seed,
        output_path=args.output
    )

    print(f"\n[OK] BassAcid Aggressive (Marie Vaunt / Verknipt) generado:")
    print(f"  • Notas colocadas: {count}")
    print(f"  • Tempo: {args.bpm} BPM | Compases: {args.bars} | Raíz: {root_midi}")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
