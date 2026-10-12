#!/usr/bin/env python3
"""
generate_all.py - Generador maestro de secuencias MIDI Acid Techno para Bitwig Studio.
Genera el kit completo o patrones individuales y los exporta directamente a la biblioteca de Bitwig.
Soporta detección y configuración por sistema operativo (macOS / Linux / Windows).

Uso:
    python3 generate_all.py
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
from BassAcid import generate_bass_acid
from BassAcid_Aggressive import generate_bass_acid_aggressive
from BassAcid_PreDrop import generate_bass_acid_predrop
from acid_kick_pattern import generate_acid_kick
from acid_hat_pattern import generate_acid_hat


def generate_full_kit(
    bpm: float = 155.0,
    root_midi: int = 50,
    variations: int = 1,
    use_timestamp: bool = True,
    custom_clips_dir: str = None
):
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if custom_clips_dir:
        set_bitwig_library_dir(custom_clips_dir)

    active_clips_dir = get_bitwig_library_dir()
    os_name = get_current_os()
    os_display = get_os_display_name(os_name)

    print("=" * 65)
    print("   GENERADOR ACID TECHNO MIDI PARA BITWIG STUDIO (155 BPM)")
    print("=" * 65)
    print(f"Sistema Operativo: {os_display} ({os_name})")
    print(f"Tempo: {bpm} BPM | Nota Raíz: {root_midi} | Variaciones: {variations}")
    print(f"Destino local:   {output_dir}")
    print(f"Destino Bitwig:  {active_clips_dir}\n")

    for v in range(1, variations + 1):
        suffix = f"_var{v}" if variations > 1 else ""
        ts = get_timestamp_prefix() if use_timestamp else ""

        print(f"--- [Variación {v}/{variations}] Generando archivos MIDI ---")

        # 1. BassAcid (Rolling 303)
        b1_out = build_timestamped_filename(f"01_BassAcid_Rolling_303{suffix}.mid", directory=output_dir, timestamp=ts) if use_timestamp else output_dir / f"01_BassAcid_Rolling_303{suffix}.mid"
        b1_paths, b1_notes = generate_bass_acid(
            bpm=bpm,
            root_note=root_midi,
            total_bars=4,
            output_path=b1_out
        )
        print(f"  [1/5] {b1_out.name} ({b1_notes} notas)")

        # 2. BassAcid Aggressive (Marie Vaunt style)
        b2_out = build_timestamped_filename(f"02_BassAcid_Aggressive{suffix}.mid", directory=output_dir, timestamp=ts) if use_timestamp else output_dir / f"02_BassAcid_Aggressive{suffix}.mid"
        b2_paths, b2_notes = generate_bass_acid_aggressive(
            bpm=bpm,
            root_note=root_midi,
            total_bars=4,
            output_path=b2_out
        )
        print(f"  [2/5] {b2_out.name} ({b2_notes} notas)")

        # 3. BassAcid PreDrop (Build-up & Silence)
        b3_out = build_timestamped_filename(f"03_BassAcid_PreDrop_Build{suffix}.mid", directory=output_dir, timestamp=ts) if use_timestamp else output_dir / f"03_BassAcid_PreDrop_Build{suffix}.mid"
        b3_paths, b3_notes = generate_bass_acid_predrop(
            bpm=bpm,
            root_note=root_midi,
            output_path=b3_out
        )
        print(f"  [3/5] {b3_out.name} ({b3_notes} notas)")

        # 4. Acid Kick (4x4 Rumble)
        k_out = build_timestamped_filename(f"04_Acid_Kick_Rumble_4x4{suffix}.mid", directory=output_dir, timestamp=ts) if use_timestamp else output_dir / f"04_Acid_Kick_Rumble_4x4{suffix}.mid"
        k_paths, k_main, k_ghost = generate_acid_kick(
            bpm=bpm,
            note=36,
            output_path=k_out
        )
        print(f"  [4/5] {k_out.name} ({k_main + k_ghost} hits)")

        # 5. Acid Hi-Hats (Offbeat + Rolling)
        h_out = build_timestamped_filename(f"05_Acid_HiHat_Rave{suffix}.mid", directory=output_dir, timestamp=ts) if use_timestamp else output_dir / f"05_Acid_HiHat_Rave{suffix}.mid"
        h_paths, h_hits = generate_acid_hat(
            bpm=bpm,
            note=42,
            output_path=h_out
        )
        print(f"  [5/5] {h_out.name} ({h_hits} hits)\n")

    print("[COMPLETADO] Todos los clips MIDI están disponibles:")
    print(f"  1. En Bitwig Studio: Abre el navegador lateral -> 'My Library' / 'Clips' -> 'Acid_Sequences'")
    print(f"     (Ruta en disco: {active_clips_dir})")
    print(f"  2. En el explorador de archivos: {output_dir}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Generador completo de secuencias MIDI Acid para Bitwig Studio")
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--root", type=str, default="50", help="Nota raíz MIDI o nombre (default: 50 / D3)")
    parser.add_argument("--variations", type=int, default=1, help="Número de variaciones a generar (default: 1)")
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
        custom_clips_dir=args.clips_dir
    )


if __name__ == "__main__":
    main()
