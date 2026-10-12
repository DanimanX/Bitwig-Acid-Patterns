#!/usr/bin/env python3
"""
acid_kick_pattern.py - Generador de Kick estilo Hard Acid / Rolling Rumble para Bitwig Studio.
Basado en acid_kick_pattern.lua (155 BPM, 4 compases, 64 semicorcheas).
Genera bombo 4x4 sólido, ghost kicks / rumble groove en la semicorchea previa al beat, y redoble final.

Uso:
    python3 acid_kick_pattern.py
    python3 acid_kick_pattern.py --bpm 155 --note 36 --output ./output/Acid_Kick_Rumble.mid
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


def generate_acid_kick(
    bpm: float = 155.0,
    note: int = 36,  # MIDI 36 (C1 - Bombo estándar General MIDI / Drum Machine)
    total_bars: int = 4,
    main_vol: int = 127,
    ghost_vol: int = 58,
    enable_ghosts: bool = True,
    enable_fill: bool = True,
    seed: int = None,
    output_path: str = None,
    channel: int = 0,  # Canal 0 (Canal 1 en DAW) para máxima compatibilidad con VSTs y Bitwig
):
    if seed is not None:
        random.seed(seed)

    seq = MidiSequence(name="Acid_Kick_Rumble_4x4", bpm=bpm)
    track = seq.track

    main_hits = 0
    ghost_hits = 0

    # 1. Kicks principales 4-on-the-floor (cada 4 semicorcheas: 1, 5, 9, 13...)
    for bar in range(total_bars):
        bar_tick = bar * TICKS_PER_BAR
        for beat in range(4):
            step_tick = bar_tick + (beat * 4) * TICKS_PER_16TH
            track.add_note(tick=step_tick, duration_ticks=int(TICKS_PER_16TH * 0.8), note=note, velocity=main_vol, channel=channel)
            main_hits += 1

    # 2. Ghost Kicks para crear el empuje "Rolling Rumble" (semicorcheas 4, 8, 12, 16)
    if enable_ghosts:
        for bar in range(total_bars):
            # No saturar el compás final si hay fill
            if not (enable_fill and bar == (total_bars - 1)):
                bar_tick = bar * TICKS_PER_BAR
                rumble_steps = [3, 7, 11, 15]  # 0-indexed (pasos 4, 8, 12, 16)
                for step in rumble_steps:
                    if random.random() > 0.25:
                        step_tick = bar_tick + step * TICKS_PER_16TH
                        v = ghost_vol + random.randint(-6, 8)
                        vol = max(30, min(85, v))
                        track.add_note(tick=step_tick, duration_ticks=int(TICKS_PER_16TH * 0.5), note=note, velocity=vol, channel=channel)
                        ghost_hits += 1

    # 3. Redoble / Fill al final del ciclo (Compás final: pasos 9 a 16)
    if enable_fill:
        final_bar_tick = (total_bars - 1) * TICKS_PER_BAR
        # Pasos del fill: semicorcheas 9, 11, 13, 14, 15, 16 (índices 0-based: 8, 10, 12, 13, 14, 15)
        fill_pattern = [
            (8, 127),
            (10, 95),
            (12, 110),
            (13, 118),
            (14, 125),
            (15, 127),
        ]
        for step_idx, v in fill_pattern:
            step_tick = final_bar_tick + step_idx * TICKS_PER_16TH
            track.add_note(tick=step_tick, duration_ticks=int(TICKS_PER_16TH * 0.6), note=note, velocity=v, channel=channel)
            main_hits += 1

    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename("Acid_Kick_Rumble_4x4.mid", directory=output_dir)

    saved = seq.save(output_path, copy_to_bitwig=True)
    return saved, main_hits, ghost_hits


def main():
    parser = argparse.ArgumentParser(description="Generador de Acid Kick (4x4 + Rumble + Fill) para Bitwig")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--note", type=str, default="36", help="Nota MIDI del Kick (default: 36 / C1)")
    parser.add_argument("--bars", type=int, default=4, help="Cantidad de compases (default: 4)")
    parser.add_argument("--no-ghosts", action="store_true", help="Desactivar ghost kicks rumble")
    parser.add_argument("--no-fill", action="store_true", help="Desactivar redoble final")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        note_midi = int(args.note)
    except ValueError:
        note_midi = note_name_to_midi(args.note)

    saved_paths, mains, ghosts = generate_acid_kick(
        bpm=args.bpm,
        note=note_midi,
        total_bars=args.bars,
        enable_ghosts=not args.no_ghosts,
        enable_fill=not args.no_fill,
        output_path=args.output
    )

    print(f"\n[OK] Acid Kick (4x4 + Rumble) generado:")
    print(f"  • Golpes principales: {mains} | Ghost/Rumble: {ghosts} | Nota: {note_midi}")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
