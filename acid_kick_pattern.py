#!/usr/bin/env python3
"""
acid_kick_pattern.py - Generador de Kick dinámico estilo Hard Techno / Acid para Bitwig Studio.
Permite generar frases estructuradas en compases de 4 con múltiples variaciones de Hard Techno:
- Rolling Rumble (Hard Techno moderno / Klangkuenstler / Verknipt)
- Industrial Sincopado (Kicks dobles y acentos cruzados)
- Schranz / Stutter Ametralladora (Redobles en fusas 32nds)
- Reverse / Offbeat Push (Empuje en contratiempos)
- Pre-Drop Break (Parada de compás 4 con silencio antes de caer)
- Híbrido / Máxima Dinámica (Evolución de 4 compases con variaciones compás a compás)

Uso:
    python3 acid_kick_pattern.py
    python3 acid_kick_pattern.py --style syncopated --bars 4
    python3 acid_kick_pattern.py --style stutter --bpm 155
"""

import sys
import random
import argparse
from pathlib import Path
from typing import List, Tuple

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

# Estilos disponibles de Hard Techno
KICK_STYLES = [
    "hybrid",         # 1. Híbrido dinámico: compás a compás evolucionando
    "rolling",        # 2. Rolling Rumble: galope constante de semicorcheas
    "syncopated",     # 3. Industrial Sincopado: bombos dobles y acentos cruzados
    "stutter",        # 4. Schranz / Ametralladora: redobles rápidos en fusas (32nds)
    "offbeat_push",   # 5. Offbeat Push: empuje con acentos en contratiempo
    "predrop_break",  # 6. Pre-Drop Break: parada dramática al final del compás 4
]


def generate_acid_kick(
    bpm: float = 155.0,
    note: int = 36,  # MIDI 36 (C1 - Bombo estándar Drum Machine / Sampler)
    total_bars: int = 4,
    style: str = "hybrid",
    main_vol: int = 127,
    ghost_vol: int = 62,
    enable_ghosts: bool = True,
    enable_fill: bool = True,
    humanize: bool = True,
    seed: int = None,
    output_path: str = None,
    channel: int = 0,
) -> Tuple[List[Path], int, int]:
    """
    Genera una secuencia MIDI de bombo Hard Techno de 4 compases (o múltiplos)
    con dinámica avanzada, variaciones rítmicas y micro-timing.
    """
    if seed is not None:
        random.seed(seed)

    style_clean = style.lower().strip()
    if style_clean not in KICK_STYLES:
        style_clean = "hybrid"

    seq_name = f"Acid_Kick_{style_clean.capitalize()}_{total_bars}Bars"
    seq = MidiSequence(name=seq_name, bpm=bpm)
    track = seq.track

    main_hits = 0
    ghost_hits = 0

    def add_kick(tick: int, velocity: int, duration_ratio: float = 0.8, is_ghost: bool = False):
        nonlocal main_hits, ghost_hits
        # Humanización sutil (micro-desplazamiento de timing y variación de volumen)
        timing_offset = 0
        if humanize:
            timing_offset = random.randint(-3, 3)
            if is_ghost:
                velocity = max(25, min(100, velocity + random.randint(-6, 6)))
            else:
                velocity = max(100, min(127, velocity + random.randint(-3, 2)))

        actual_tick = max(0, tick + timing_offset)
        duration = max(20, int(TICKS_PER_16TH * duration_ratio))
        track.add_note(tick=actual_tick, duration_ticks=duration, note=note, velocity=velocity, channel=channel)

        if is_ghost:
            ghost_hits += 1
        else:
            main_hits += 1

    # =========================================================================
    # GENERACIÓN DE KICKS POR COMPÁS (ESTRUCTURA DE 4 COMPASES DINÁMICOS)
    # =========================================================================
    for bar in range(total_bars):
        bar_idx = bar % 4  # Índice cíclico del compás dentro de la frase de 4
        bar_tick = bar * TICKS_PER_BAR
        is_last_bar_of_phrase = (bar_idx == 3) or (bar == total_bars - 1)

        # ---------------------------------------------------------------------
        # A. KICKS PRINCIPALES 4-ON-THE-FLOOR (Beats 1, 2, 3, 4)
        # ---------------------------------------------------------------------
        # Dinámica por beat: el Beat 1 es el más pesado, Beat 3 fuerte, Beats 2 y 4 ligeramente matizados
        beat_velocities = [
            main_vol,
            int(main_vol * 0.96),
            int(main_vol * 0.99),
            int(main_vol * 0.95),
        ]

        for beat in range(4):
            # En el estilo pre-drop break, silenciar los últimos 2 tiempos del compás 4
            if style_clean == "predrop_break" and is_last_bar_of_phrase and beat >= 2:
                continue

            # En el compás final con fill activo, omitir el beat 4 si entra redoble continuo
            if enable_fill and is_last_bar_of_phrase and beat == 3 and style_clean in ["stutter", "hybrid"]:
                continue

            beat_tick = bar_tick + (beat * 4) * TICKS_PER_16TH
            add_kick(beat_tick, beat_velocities[beat], duration_ratio=0.85, is_ghost=False)

        # ---------------------------------------------------------------------
        # B. GHOST KICKS, RUMBLE Y GALOPES ESPECÍFICOS SEGÚN ESTILO
        # ---------------------------------------------------------------------
        if enable_ghosts:
            if style_clean == "rolling" or (style_clean == "hybrid" and bar_idx in [0, 2]):
                # ROLLING RUMBLE: empuje continuo en semicorcheas 2, 3 y 4 de cada tiempo
                for beat in range(4):
                    if style_clean == "predrop_break" and is_last_bar_of_phrase and beat >= 2:
                        continue
                    if enable_fill and is_last_bar_of_phrase and beat == 3:
                        continue

                    # Semicorcheas previas al beat (paso 3 = semicorchea 4) tienen más fuerza
                    beat_base = bar_tick + (beat * 4) * TICKS_PER_16TH

                    # Semicorchea 2 (paso 1): ghost leve
                    if random.random() > 0.35:
                        add_kick(beat_base + 1 * TICKS_PER_16TH, int(ghost_vol * 0.85), duration_ratio=0.45, is_ghost=True)

                    # Semicorchea 3 (paso 2 / offbeat): ghost medio
                    if random.random() > 0.25:
                        add_kick(beat_base + 2 * TICKS_PER_16TH, int(ghost_vol * 0.95), duration_ratio=0.50, is_ghost=True)

                    # Semicorchea 4 (paso 3 / pre-beat): empuje rumble fuerte
                    if random.random() > 0.15:
                        add_kick(beat_base + 3 * TICKS_PER_16TH, ghost_vol + 8, duration_ratio=0.60, is_ghost=True)

            elif style_clean == "syncopated" or (style_clean == "hybrid" and bar_idx == 1):
                # INDUSTRIAL SINCOPADO: kicks dobles inesperados y acentos cruzados
                # Compás con bombos extras en semicorchea 6 (beat 2 contratiempo) y 14 (beat 4 contratiempo)
                sync_steps = [6, 14]
                for s in sync_steps:
                    if random.random() > 0.20:
                        s_tick = bar_tick + s * TICKS_PER_16TH
                        add_kick(s_tick, int(main_vol * 0.90), duration_ratio=0.70, is_ghost=False)

                # Rumble de soporte en pasos 3, 7, 11, 15
                for s in [3, 7, 11]:
                    if random.random() > 0.30:
                        s_tick = bar_tick + s * TICKS_PER_16TH
                        add_kick(s_tick, ghost_vol, duration_ratio=0.50, is_ghost=True)

            elif style_clean == "offbeat_push":
                # OFFBEAT PUSH: Bombo secundario pesado en contratiempo (pasos 2, 6, 10, 14)
                for beat in range(4):
                    s_tick = bar_tick + (beat * 4 + 2) * TICKS_PER_16TH
                    add_kick(s_tick, int(main_vol * 0.88), duration_ratio=0.75, is_ghost=False)

            elif style_clean == "stutter":
                # SCHRANZ STUTTER: Kicks con micro-redobles cada 2 compases
                if bar_idx in [1, 3]:
                    # Stutter en el tiempo 4 (semicorcheas 12, 13, 14, 15 en ráfaga rápida)
                    for step_idx in [12, 13, 14, 15]:
                        s_tick = bar_tick + step_idx * TICKS_PER_16TH
                        v = int(ghost_vol + (step_idx - 11) * 15)
                        add_kick(s_tick, min(127, v), duration_ratio=0.55, is_ghost=(step_idx < 14))

        # ---------------------------------------------------------------------
        # C. REDOBLES Y REMATES EN EL COMPÁS 4 (O CADA 4 COMPASES)
        # ---------------------------------------------------------------------
        if enable_fill and is_last_bar_of_phrase:
            if style_clean in ["stutter", "hybrid"]:
                # Clímax de fusas (32nd notes): ametralladora en los pasos 12 a 16
                fill_start = bar_tick + 12 * TICKS_PER_16TH
                # 8 golpes en fusas (32nd notes) desde la semicorchea 13 hasta el final
                for f_idx in range(8):
                    f_tick = fill_start + f_idx * TICKS_PER_32ND
                    f_vol = int(85 + (f_idx / 7.0) * 42)  # Crescendo dinámico de 85 a 127
                    add_kick(f_tick, f_vol, duration_ratio=0.45, is_ghost=(f_idx < 4))

            elif style_clean in ["rolling", "syncopated"]:
                # Fill clásico hard techno: semicorcheas aceleradas 10, 12, 13, 14, 15
                accel_steps = [(10, 105), (12, 112), (13, 118), (14, 124), (15, 127)]
                for step_idx, v in accel_steps:
                    s_tick = bar_tick + step_idx * TICKS_PER_16TH
                    add_kick(s_tick, v, duration_ratio=0.60, is_ghost=False)

            elif style_clean == "predrop_break":
                # Silencio total en los tiempos 3 y 4 para dejar caer el drop en el siguiente compás
                # No se añaden notas en las líneas 9 a 16
                pass

    # Guardar archivo MIDI
    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        out_name = f"Acid_Kick_{style_clean.capitalize()}_{total_bars}Bars.mid"
        output_path = build_timestamped_filename(out_name, directory=output_dir)

    saved_paths = seq.save(output_path, copy_to_bitwig=True)
    return saved_paths, main_hits, ghost_hits


def main():
    parser = argparse.ArgumentParser(description="Generador de Kick Hard Techno dinámico (compases de 4) para Bitwig Studio")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--note", type=str, default="36", help="Nota MIDI del Kick (default: 36 / C1)")
    parser.add_argument("--bars", type=int, default=4, help="Cantidad de compases (default: 4)")
    parser.add_argument("--style", type=str, default="hybrid", choices=KICK_STYLES,
                        help="Estilo/variación de Hard Techno: hybrid, rolling, syncopated, stutter, offbeat_push, predrop_break")
    parser.add_argument("--no-ghosts", action="store_true", help="Desactivar ghost kicks / rumble")
    parser.add_argument("--no-fill", action="store_true", help="Desactivar redoble final")
    parser.add_argument("--no-humanize", action="store_true", help="Desactivar humanización de micro-timing y velocity")
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
        style=args.style,
        enable_ghosts=not args.no_ghosts,
        enable_fill=not args.no_fill,
        humanize=not args.no_humanize,
        output_path=args.output
    )

    print(f"\n[OK] Kick Hard Techno ({args.style.upper()}) generado:")
    print(f"  • Estilo: {args.style} | Compases: {args.bars} ({args.bars * 4} beats)")
    print(f"  • Kicks principales: {mains} | Ghost/Rumble: {ghosts} | Nota: {note_midi}")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
