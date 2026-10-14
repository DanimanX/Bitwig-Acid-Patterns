#!/usr/bin/env python3
"""
generate_all.py - Generador maestro de secuencias MIDI Acid Techno para Bitwig Studio.
Genera el kit completo o patrones individuales y los exporta directamente a la biblioteca de Bitwig.
Soporta detección y configuración por sistema operativo (macOS / Linux / Windows).

Uso:
    python3 generate_all.py
    python3 generate_all.py --bpm 135 --root 46 --variations 1
    python3 generate_all.py --bpm 155 --root 50 --variations 3
    python3 generate_all.py --configure
    python3 generate_all.py --clips-dir "/ruta/personalizada"
"""

import sys
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from midi_core import (
    get_current_os,
    get_os_display_name,
    get_bitwig_library_dir,
    set_bitwig_library_dir,
    prompt_and_configure_clips_dir,
    note_name_to_midi,
    get_timestamp_prefix,
    build_timestamped_filename,
)
from BassAcid import generate_bass_acid, DEFAULT_OUTPUT_STEM as BASS_ROLLING_STEM
from BassAcid_Aggressive import generate_bass_acid_aggressive, DEFAULT_OUTPUT_STEM as BASS_AGGRESSIVE_STEM
from BassAcid_Blade import generate_bass_acid_blade, DEFAULT_OUTPUT_STEM as BASS_BLADE_STEM
from BassAcid_Rush import generate_bass_acid_rush, default_output_stem as rush_output_stem
from BassAcid_GiveMeAcid import (
    generate_bass_acid_give_me_acid,
    default_output_stem as give_me_acid_output_stem,
    DEFAULT_OUTPUT_STEM as BASS_GIVE_ME_ACID_STEM
)
from acid_kick_pattern import generate_acid_kick, default_output_stem as kick_output_stem
from acid_hat_pattern import generate_acid_hat, DEFAULT_OUTPUT_STEM as HAT_STEM


def resolve_output(stem: str, suffix: str, output_dir: Path, timestamp: str, use_timestamp: bool) -> Path:
    """
    Resuelve la ruta de salida usando el nombre canónico del script (un archivo por script),
    idéntico al que genera cada script de forma individual.
    """
    name = f"{stem}{suffix}"
    if use_timestamp:
        return build_timestamped_filename(name, directory=output_dir, timestamp=timestamp)
    return output_dir / f"{name}.mid"


def generate_full_kit(
    bpm: float = 155.0,
    root_midi: int = 50,
    variations: int = 1,
    use_timestamp: bool = True,
    custom_clips_dir: str = None,
    kick_style: str = "hybrid",
    include_rush: bool = True,
    rush_style: str = "rolling",
    include_give_me_acid: bool = True,
    give_me_acid_style: str = "driving_lead"
):
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if custom_clips_dir:
        set_bitwig_library_dir(custom_clips_dir)

    active_clips_dir = get_bitwig_library_dir()
    os_name = get_current_os()
    os_display = get_os_display_name(os_name)

    total_tracks = 5 + (1 if include_rush else 0) + (1 if include_give_me_acid else 0)

    print("=" * 68)
    print("   GENERADOR ACID TECHNO MIDI PARA BITWIG STUDIO")
    print("=" * 68)
    print(f"Sistema Operativo: {os_display} ({os_name})")
    print(f"Tempo: {bpm} BPM | Nota Raíz: {root_midi} | Variaciones: {variations}")
    print(f"Pistas por kit:    {total_tracks}")
    print(f"Estilo de Kick:    {kick_style.upper()} (Compases de 4 dinámicos)")
    print(f"Destino local:     {output_dir}")
    print(f"Destino Bitwig:    {active_clips_dir}\n")

    for v in range(1, variations + 1):
        suffix = f"_var{v}" if variations > 1 else ""
        ts = get_timestamp_prefix() if use_timestamp else ""

        print(f"--- [Variación {v}/{variations}] Generando archivos MIDI ---")
        idx = 1

        # 1. BassAcid Give Me Acid (Marie Vaunt & A*S*Y*S style)
        if include_give_me_acid:
            gma_out = resolve_output(give_me_acid_output_stem(give_me_acid_style), suffix, output_dir, ts, use_timestamp)
            gma_paths, gma_notes = generate_bass_acid_give_me_acid(
                bpm=bpm,
                root_note=root_midi,
                style=give_me_acid_style,
                total_bars=4,
                output_path=gma_out
            )
            print(f"  [{idx}/{total_tracks}] {gma_out.name} ({gma_notes} notas - Give Me Acid {give_me_acid_style})")
            idx += 1

        # 2. BassAcid (Rolling 303)
        b1_out = resolve_output(BASS_ROLLING_STEM, suffix, output_dir, ts, use_timestamp)
        b1_paths, b1_notes = generate_bass_acid(
            bpm=bpm,
            root_note=root_midi,
            total_bars=4,
            output_path=b1_out
        )
        print(f"  [{idx}/{total_tracks}] {b1_out.name} ({b1_notes} notas)")
        idx += 1

        # 3. BassAcid Aggressive (Marie Vaunt style)
        b2_out = resolve_output(BASS_AGGRESSIVE_STEM, suffix, output_dir, ts, use_timestamp)
        b2_paths, b2_notes = generate_bass_acid_aggressive(
            bpm=bpm,
            root_note=root_midi,
            total_bars=4,
            output_path=b2_out
        )
        print(f"  [{idx}/{total_tracks}] {b2_out.name} ({b2_notes} notas)")
        idx += 1

        # 4. BassAcid Blade (16 notas, acid techno estilo Blade)
        b3_out = resolve_output(BASS_BLADE_STEM, suffix, output_dir, ts, use_timestamp)
        b3_paths, b3_notes = generate_bass_acid_blade(
            bpm=bpm,
            root_note=root_midi,
            output_path=b3_out
        )
        print(f"  [{idx}/{total_tracks}] {b3_out.name} ({b3_notes} notas)")
        idx += 1

        # 5. Acid Kick (Hard Techno dinámico según estilo)
        k_out = resolve_output(kick_output_stem(kick_style, 4), suffix, output_dir, ts, use_timestamp)
        k_paths, k_main, k_ghost = generate_acid_kick(
            bpm=bpm,
            note=36,
            total_bars=4,
            style=kick_style,
            output_path=k_out
        )
        print(f"  [{idx}/{total_tracks}] {k_out.name} ({k_main + k_ghost} hits)")
        idx += 1

        # 6. Acid Hi-Hats (Offbeat + Rolling)
        h_out = resolve_output(HAT_STEM, suffix, output_dir, ts, use_timestamp)
        h_paths, h_hits = generate_acid_hat(
            bpm=bpm,
            note=42,
            output_path=h_out
        )
        print(f"  [{idx}/{total_tracks}] {h_out.name} ({h_hits} hits)")
        idx += 1

        # 7. BassAcid Rush (KI/KI @ Elementenstraat 1:17:04 style)
        if include_rush:
            r_out = resolve_output(rush_output_stem(rush_style), suffix, output_dir, ts, use_timestamp)
            r_paths, r_notes = generate_bass_acid_rush(
                bpm=bpm,
                root_note=root_midi,
                style=rush_style,
                total_bars=4,
                output_path=r_out
            )
            print(f"  [{idx}/{total_tracks}] {r_out.name} ({r_notes} notas - Estilo {rush_style})\n")
        else:
            print()

    print("[COMPLETADO] Todos los clips MIDI están disponibles:")
    print(f"  1. En Bitwig Studio: Abre el navegador lateral -> 'My Library' / 'Clips' -> 'Acid_Sequences'")
    print(f"     (Ruta en disco: {active_clips_dir})")
    print(f"  2. En el explorador de archivos: {output_dir}")
    print("=" * 68)


def main():
    parser = argparse.ArgumentParser(description="Generador completo de secuencias MIDI Acid para Bitwig Studio")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--root", type=str, default="50", help="Nota raíz MIDI o nombre (default: 50 / D3)")
    parser.add_argument("--variations", type=int, default=1, help="Número de variaciones a generar (default: 1)")
    parser.add_argument("--kick-style", type=str, default="hybrid",
                        choices=["hybrid", "rolling", "syncopated", "stutter", "offbeat_push", "predrop_break"],
                        help="Estilo del Kick: hybrid, rolling, syncopated, stutter, offbeat_push, predrop_break")
    parser.add_argument("--give-me-acid-style", type=str, default="driving_lead",
                        choices=["driving_lead", "call_response", "squelch_roller", "climax_drop"],
                        help="Estilo para BassAcid Give Me Acid (Marie Vaunt & A*S*Y*S): driving_lead, call_response, squelch_roller, climax_drop")
    parser.add_argument("--no-give-me-acid", action="store_true", help="Omitir generación del patrón BassAcid Give Me Acid")
    parser.add_argument("--rush-style", type=str, default="rolling",
                        choices=["rolling", "melodic_hook", "octave_screamer", "climax_drop"],
                        help="Estilo para BassAcid Rush (KI/KI 1:17:04): rolling, melodic_hook, octave_screamer, climax_drop")
    parser.add_argument("--no-rush", action="store_true", help="Omitir generación del patrón BassAcid Rush")
    parser.add_argument("--configure", action="store_true", help="Preguntar y configurar la carpeta de Bitwig Clips para el SO actual")
    parser.add_argument("--clips-dir", type=str, default=None, help="Especificar una ruta personalizada para los Clips de Bitwig")

    args = parser.parse_args()

    if args.configure:
        prompt_and_configure_clips_dir()
        return

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    generate_full_kit(
        bpm=args.bpm,
        root_midi=root_midi,
        variations=args.variations,
        custom_clips_dir=args.clips_dir,
        kick_style=args.kick_style,
        include_rush=(not args.no_rush),
        rush_style=args.rush_style,
        include_give_me_acid=(not args.no_give_me_acid),
        give_me_acid_style=args.give_me_acid_style
    )


if __name__ == "__main__":
    main()
