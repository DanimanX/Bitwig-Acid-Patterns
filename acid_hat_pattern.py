#!/usr/bin/env python3
"""
acid_hat_pattern.py - Generador de Hi-Hats estilo Hard Acid Techno / Rave para Bitwig Studio.
Basado en acid_hat_pattern.lua (155 BPM, 4 compases, 64 semicorcheas).
Genera contratiempos marcados (offbeats), rolling galopante de semicorcheas con dinámica y swing/micro-delay,
más redobles de fill en los compases 2 y 4.

Uso:
    python3 acid_hat_pattern.py
    python3 acid_hat_pattern.py --bpm 155 --note 42 --output ./output/Acid_HiHat_Rave.mid
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


def generate_acid_hat(
    bpm: float = 155.0,
    note: int = 42,  # MIDI 42 (F#1 - Closed Hi-Hat estándar General MIDI / Drum Machine)
    total_bars: int = 4,
    offbeat_vol: int = 127,
    rolling_vol: int = 76,
    ghost_vol: int = 52,
    enable_rolling: bool = True,
    enable_fills: bool = True,
    seed: int = None,
    output_path: str = None,
    channel: int = 0,  # Canal 0 (Canal 1 en DAW) para máxima compatibilidad con VSTs y Bitwig
):
    if seed is not None:
        random.seed(seed)

    seq = MidiSequence(name="Acid_HiHat_Rave_16ths", bpm=bpm)
    track = seq.track

    hits_count = 0

    for bar in range(total_bars):
        bar_tick = bar * TICKS_PER_BAR

        for step in range(1, 17):
            step_tick = bar_tick + (step - 1) * TICKS_PER_16TH
            is_kick_beat = ((step - 1) % 4 == 0)  # Pasos 1, 5, 9, 13
            is_offbeat = ((step - 1) % 4 == 2)    # Pasos 3, 7, 11, 15 (contratiempo clásico)

            if is_offbeat:
                # CONTRATIEMPO (Offbeat Hat): Pulso principal bailable
                vol = max(90, min(127, offbeat_vol - random.randint(0, 8)))
                duration = int(TICKS_PER_16TH * 0.75)
                track.add_note(tick=step_tick, duration_ticks=duration, note=note, velocity=vol, channel=channel)
                hits_count += 1

            elif enable_rolling:
                if is_kick_beat:
                    # En el golpe del Kick: a 155 BPM suele dejarse libre o ghost muy sutil
                    if random.random() > 0.65:
                        vol = max(30, min(80, ghost_vol + random.randint(-6, 6)))
                        duration = int(TICKS_PER_16TH * 0.40)
                        track.add_note(tick=step_tick, duration_ticks=duration, note=note, velocity=vol, channel=channel)
                        hits_count += 1
                else:
                    # Semicorcheas intermedias (2, 4, 6, 8, 10, 12, 14, 16): rolling drive continuo
                    if random.random() > 0.15:
                        vol = max(40, min(105, rolling_vol + random.randint(-8, 10)))
                        # Micro-delay sutil (swing analógico entre 0 y 8 ticks)
                        micro_delay = random.randint(0, 8)
                        duration = int(TICKS_PER_16TH * 0.50)
                        track.add_note(tick=step_tick + micro_delay, duration_ticks=duration, note=note, velocity=vol, channel=channel)
                        hits_count += 1

        # Redobles / Fills especiales:
        if enable_fills:
            if bar == 1:
                # Final del compás 2 (pasos 15 y 16): mini redoble rápido
                t15 = bar_tick + 14 * TICKS_PER_16TH
                t16 = bar_tick + 15 * TICKS_PER_16TH
                track.add_note(tick=t15, duration_ticks=int(TICKS_PER_16TH * 0.5), note=note, velocity=110, channel=channel)
                track.add_note(tick=t16, duration_ticks=int(TICKS_PER_16TH * 0.5), note=note, velocity=125, channel=channel)
                hits_count += 2
            elif bar == (total_bars - 1):
                # Final del compás final (pasos 13 a 16): ametralladora creciente
                fill_hits = [(12, 95), (13, 108), (14, 120), (15, 127)]
                for step_idx, v in fill_hits:
                    t = bar_tick + step_idx * TICKS_PER_16TH
                    track.add_note(tick=t, duration_ticks=int(TICKS_PER_16TH * 0.55), note=note, velocity=v, channel=channel)
                    hits_count += 1

    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename("Acid_HiHat_Rave_16ths.mid", directory=output_dir)

    saved = seq.save(output_path, copy_to_bitwig=True)
    return saved, hits_count


def main():
    parser = argparse.ArgumentParser(description="Generador de Hi-Hats Acid Rave para Bitwig")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--note", type=str, default="42", help="Nota MIDI del Hi-Hat (default: 42 / F#1)")
    parser.add_argument("--bars", type=int, default=4, help="Cantidad de compases (default: 4)")
    parser.add_argument("--no-rolling", action="store_true", help="Desactivar semicorcheas rolling (dejar solo offbeats)")
    parser.add_argument("--no-fills", action="store_true", help="Desactivar redobles de fill")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        note_midi = int(args.note)
    except ValueError:
        note_midi = note_name_to_midi(args.note)

    saved_paths, count = generate_acid_hat(
        bpm=args.bpm,
        note=note_midi,
        total_bars=args.bars,
        enable_rolling=not args.no_rolling,
        enable_fills=not args.no_fills,
        output_path=args.output
    )

    print(f"\n[OK] Acid Hi-Hats generados:")
    print(f"  • Golpes totales: {count} | Tempo: {args.bpm} BPM | Nota: {note_midi}")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
