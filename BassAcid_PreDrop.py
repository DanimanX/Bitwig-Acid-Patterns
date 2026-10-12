#!/usr/bin/env python3
"""
BassAcid_PreDrop.py - Generador de bajo para Build-up y Pre-Drop (155 BPM, 4 compases, 64 semicorcheas).
Basado en BassAcid_PreDrop.lua.
Crea tensión progresiva (riser ácido, octavas ascendentes, ráfagas de ametralladora retrigger)
y remata con SILENCIO PRE-DROP dramático en los últimos 2 tiempos para que el drop explote con fuerza.

Uso:
    python3 BassAcid_PreDrop.py
    python3 BassAcid_PreDrop.py --bpm 155 --root 50 --output ./output/BassAcid_PreDrop.mid
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
    TICKS_PER_32ND,
    TICKS_PER_BAR,
    note_name_to_midi,
    build_timestamped_filename,
)


def generate_bass_acid_predrop(
    bpm: float = 155.0,
    root_note: int = 50,  # D3 (MIDI 50)
    total_bars: int = 4,
    max_vol: int = 127,
    pre_drop_silence_steps: int = 8,  # 8 semicorcheas = 2 tiempos completos en silencio absoluto
    enable_retrigger: bool = True,
    seed: int = None,
    output_path: str = None
):
    if seed is not None:
        random.seed(seed)

    seq = MidiSequence(name="BassAcid_PreDrop_Build", bpm=bpm)
    track = seq.track

    notes_placed = 0

    # =========================================================================
    # COMPÁS 1 (Semicorcheas 1-16): ESPACIO Y TENSIÓN INICIAL
    # =========================================================================
    bar1_hits = [
        {"step": 1,  "offset": -12, "vol": 80},  # Subgrave D-1
        {"step": 5,  "offset": 0,   "vol": 75},  # D-2
        {"step": 9,  "offset": 7,   "vol": 85},  # A-2
        {"step": 13, "offset": 6,   "vol": 90},  # G#2 tritono disonante
    ]
    for h in bar1_hits:
        tick = (h["step"] - 1) * TICKS_PER_16TH
        note_num = max(0, min(127, root_note + h["offset"]))
        duration = int(TICKS_PER_16TH * 1.5)  # Gate controlado
        track.add_note(tick=tick, duration_ticks=duration, note=note_num, velocity=h["vol"], channel=0)
        notes_placed += 1

    # =========================================================================
    # COMPÁS 2 (Semicorcheas 17-32): ENTRADA DEL ROLLING Y PRIMERA ESCALADA
    # =========================================================================
    bar2_tick = 1 * TICKS_PER_BAR
    for step in range(1, 17):
        if step % 2 == 0:  # Pasos pares
            step_tick = bar2_tick + (step - 1) * TICKS_PER_16TH
            vol = int(70 + (step / 16.0) * 25)
            offset = 12 if (step % 4 == 0) else 0
            note_num = max(0, min(127, root_note + offset))
            # Slide legato
            duration = int(TICKS_PER_16TH * 1.10)
            track.add_note(tick=step_tick, duration_ticks=duration, note=note_num, velocity=vol, channel=0)
            notes_placed += 1

    # =========================================================================
    # COMPÁS 3 (Semicorcheas 33-48): EL RISER ÁCIDO (Escalada frenética de 2 octavas)
    # =========================================================================
    bar3_tick = 2 * TICKS_PER_BAR
    scale_up = [0, 1, 3, 5, 6, 7, 10, 12, 13, 15, 17, 18, 19, 22, 24, 25]
    for step in range(1, 17):
        step_tick = bar3_tick + (step - 1) * TICKS_PER_16TH
        vol = int(95 + (step / 16.0) * 25)
        offset = scale_up[step - 1] if (step - 1) < len(scale_up) else 24
        note_num = max(0, min(127, root_note + offset))
        is_slide = (step % 2 == 0)
        duration = int(TICKS_PER_16TH * (1.10 if is_slide else 0.85))
        track.add_note(tick=step_tick, duration_ticks=duration, note=note_num, velocity=vol, channel=0)
        notes_placed += 1

    # =========================================================================
    # COMPÁS 4 (Semicorcheas 49-64): CLÍMAX AMETRALLADORA + SILENCIO PRE-DROP
    # =========================================================================
    bar4_tick = 3 * TICKS_PER_BAR
    cutoff_step = 16 - pre_drop_silence_steps  # Paso 8 (semicorchea 56)

    high_scream = max(0, min(127, root_note + 24))  # D scream 2 octavas arriba

    for step in range(1, cutoff_step + 1):
        step_tick = bar4_tick + (step - 1) * TICKS_PER_16TH

        if enable_retrigger:
            # Retrigger estilo Renoise 0R: dos fusas (32nd notes) por semicorchea creando el roll veloz
            d = int(TICKS_PER_32ND * 0.80)
            track.add_note(tick=step_tick, duration_ticks=d, note=high_scream, velocity=max_vol, channel=0)
            track.add_note(tick=step_tick + TICKS_PER_32ND, duration_ticks=d, note=high_scream, velocity=max_vol, channel=0)
            notes_placed += 2
        else:
            duration = int(TICKS_PER_16TH * 0.85)
            track.add_note(tick=step_tick, duration_ticks=duration, note=high_scream, velocity=max_vol, channel=0)
            notes_placed += 1

    # Del paso cutoff_step + 1 al 16 (Pre-drop): SILENCIO ABSOLUTO (sin notas)

    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename("BassAcid_PreDrop_Build.mid", directory=output_dir)

    saved = seq.save(output_path, copy_to_bitwig=True)
    return saved, notes_placed


def main():
    parser = argparse.ArgumentParser(description="Generador de BassAcid PreDrop (Build-up y Silencio) para Bitwig")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--root", type=str, default="50", help="Nota raíz MIDI o nombre (default: 50 / D3)")
    parser.add_argument("--silence-steps", type=int, default=8, help="Semicorcheas finales en silencio (default: 8 = 2 beats)")
    parser.add_argument("--no-retrigger", action="store_true", help="Desactivar ráfagas de repetición en el clímax")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    saved_paths, count = generate_bass_acid_predrop(
        bpm=args.bpm,
        root_note=root_midi,
        pre_drop_silence_steps=args.silence_steps,
        enable_retrigger=not args.no_retrigger,
        output_path=args.output
    )

    print(f"\n[OK] BassAcid Pre-Drop generado:")
    print(f"  • Notas colocadas: {count}")
    print(f"  • Build-up: compases 1 a 3 | Clímax ametralladora: compás 4 (1-8) | Silencio: compás 4 (9-16)")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
