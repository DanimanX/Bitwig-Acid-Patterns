#!/usr/bin/env python3
"""
BassAcid_Blade.py - Línea de bajo ácido de 16 notas estilo BLADE (1 compás, 16 semicorcheas).

Referencia del estilo
---------------------
"Blade-style acid techno" es el sonido que popularizó la escena de apertura de la película
*Blade* (1998): **New Order - "Confusion" (Pump Panel Reconstruction Mix"**, el remix de Tim
Taylor y Dan Zamani que sobrealimentó su 303 con un pedal de guitarra distorsionado y dejó
cuatro minutos de acid techno a todo volumen (fuente: Red Bull Music Academy Daily, "Acid Over
Hollywood: How 'Blade' Immortalized a 303 Anthem", 2019). Sus señas de identidad, aplicables
a un patrón MIDI:

  * **303 dominante**: la línea de bajo es el gancho, no un acompañamiento.
  * **Implacable**: 16 semicorcheas sin un solo hueco ("sirena antiaérea" que gira sobre sí misma).
  * **4x4 machacón** debajo y energía nocturna / "full-blast".

Qué genera este script
----------------------
**16 notas, una por semicorchea, en un solo compás** (loop hipnótico):

  * Acentos duros en los cuatro pulsos (pasos 1, 5, 9, 13) que clavan junto al bombo.
  * Stabs de octava (+12) y quinta (+7) en los contratiempos, con **slide legato 303** (gate > 1.0)
    para el squelch característico. Cada slide apunta a OTRA altura, así que el Note-Off del
    mismo pitch nunca corta la nota siguiente.
  * **Espiral ascendente** en las 4 últimas semicorcheas (3ª menor -> tritono -> octava) que
    remata el compás y engancha con el siguiente.

El patrón es determinista a propósito (el groove no depende del azar). Como el bajo ocupa las 16
semicorcheas, en Bitwig conviene **sidechainear el bajo contra el bombo** (o dejar que el kick
mande) para que el 4x4 no se embarre.

Uso:
    python3 BassAcid_Blade.py
    python3 BassAcid_Blade.py --bpm 155 --root 50
    python3 BassAcid_Blade.py --bars 4 --root F3 --bpm 153 --output ./output/Blade.mid
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple

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
DEFAULT_OUTPUT_STEM = "BassAcid_Blade"

# Dinámica 303 en tres capas: el acento abre el filtro (squelch), el ghost apenas roza.
ACCENT_VOL = 127
NORMAL_VOL = 100
GHOST_VOL = 76
LAYER_VOL = {"a": ACCENT_VOL, "n": NORMAL_VOL, "g": GHOST_VOL}

# Gate como múltiplo de semicorchea. > 1.0 = solape legato (slide 303).
GATE_SLIDE = 1.12
GATE_NORMAL = 0.80
GATE_GHOST = 0.60

# Pasos donde el bombo 4x4 golpea: aquí el bajo acentúa para "clavar" con el kick.
KICK_GRID_STEPS = (1, 5, 9, 13)

# El riff Blade: (paso 1..16, offset en semitonos sobre root_note, capa, slide)
#   offset: 0 tónica | 3 3ª menor | 6 tritono | 7 5ª justa | 12 octava
BLADE_MOTIF = (
    (1,   0, "a", False),   # pulso 1: martillo sobre la tónica
    (2,   0, "g", False),
    (3,  12, "a", True),    # octava con slide -> (4) 0
    (4,   0, "g", False),
    (5,   0, "a", False),   # pulso 2
    (6,   0, "g", False),
    (7,   7, "a", True),    # quinta con slide -> (8) 0
    (8,   0, "g", False),
    (9,   0, "a", False),   # pulso 3
    (10, 12, "n", False),   # octava
    (11,  0, "g", False),
    (12,  7, "a", True),    # quinta con slide -> (13) 0
    (13,  0, "a", False),   # pulso 4
    (14,  3, "a", True),    # espiral ascendente: 3ª menor
    (15,  6, "a", True),    # ... tritono
    (16, 12, "a", True),    # ... octava -> slide al compás siguiente
)


def _validate_motif():
    """El motivo debe ser exactamente 16 notas, una por semicorchea, y coherente."""
    steps = [step for step, _off, _layer, _slide in BLADE_MOTIF]
    if steps != list(range(1, 17)):
        raise ValueError(f"El motivo debe cubrir los 16 pasos en orden; recibido: {steps}")
    if len(BLADE_MOTIF) != 16:
        raise ValueError(f"El motivo debe tener 16 notas; tiene {len(BLADE_MOTIF)}")

    # Cada slide tiene que apuntar a OTRA altura: si no, el Note-Off del mismo pitch
    # cortaría la nota siguiente y el slide no haría nada.
    for i, (_step, offset, _layer, slide) in enumerate(BLADE_MOTIF):
        if not slide:
            continue
        next_offset = BLADE_MOTIF[(i + 1) % 16][1]
        if next_offset == offset:
            raise ValueError(
                f"Slide sin destino distinto en el paso {i + 1}: "
                f"offset {offset} -> {next_offset}"
            )


def _resolve_notes(root_note: int, total_bars: int) -> List[dict]:
    """Expande el motivo a notas concretas y resuelve solapes de mismo pitch."""
    notes: List[dict] = []
    for bar in range(max(1, int(total_bars))):
        bar_tick = bar * TICKS_PER_BAR
        for step, offset, layer, slide in BLADE_MOTIF:
            gate = GATE_SLIDE if slide else (GATE_GHOST if layer == "g" else GATE_NORMAL)
            notes.append({
                "tick": bar_tick + (step - 1) * TICKS_PER_16TH,
                "note": max(0, min(127, root_note + offset)),
                "dur": max(1, int(round(gate * TICKS_PER_16TH))),
                "vel": max(1, min(127, LAYER_VOL[layer])),
            })

    notes.sort(key=lambda n: (n["tick"], n["note"]))

    # Mecanismo: dos notas del MISMO pitch nunca pueden solaparse (el Note-Off de la primera
    # mataría la segunda). Se acorta la anterior hasta el ataque de la siguiente.
    for i, current in enumerate(notes):
        end = current["tick"] + current["dur"]
        for later in notes[i + 1:]:
            if later["tick"] >= end:
                break
            if later["note"] == current["note"]:
                current["dur"] = max(1, later["tick"] - current["tick"])
                break

    return notes


def generate_bass_acid_blade(
    bpm: float = 155.0,
    root_note: int = 50,   # D3 (MIDI 50)
    total_bars: int = 1,   # 1 compás = 16 notas (el motivo); el clip hace loop en Bitwig
    seed: int = None,      # aceptado por compatibilidad: el patrón es determinista a propósito
    output_path: str = None
) -> Tuple[List[Path], int]:
    """Genera la línea de bajo ácido de 16 notas estilo Blade y la exporta a .mid."""
    _validate_motif()

    seq = MidiSequence(name="BassAcid_Blade", bpm=bpm)
    track = seq.track

    notes = _resolve_notes(root_note, total_bars)
    for n in notes:
        track.add_note(
            tick=n["tick"],
            duration_ticks=n["dur"],
            note=n["note"],
            velocity=n["vel"],
            channel=0,
        )

    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename(DEFAULT_OUTPUT_STEM, directory=output_dir)

    saved_paths = seq.save(output_path, copy_to_bitwig=True)
    return saved_paths, len(notes)


def main():
    parser = argparse.ArgumentParser(
        description="Generador de línea de bajo ácido de 16 notas estilo Blade (acid techno) para Bitwig"
    )
    parser.add_argument("--bpm", type=float, default=155.0, help="Tempo en BPM (default: 155.0)")
    parser.add_argument("--root", type=str, default="50", help="Nota raíz MIDI o nombre (default: 50 / D3)")
    parser.add_argument("--bars", type=int, default=1, help="Compases a repetir el motivo de 16 notas (default: 1)")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria (el patrón es determinista; se acepta por compatibilidad)")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    saved_paths, count = generate_bass_acid_blade(
        bpm=args.bpm,
        root_note=root_midi,
        total_bars=args.bars,
        seed=args.seed,
        output_path=args.output
    )

    print(f"\n[OK] BassAcid Blade (16 notas, estilo Blade) generado:")
    print(f"  • Notas colocadas: {count}")
    print(f"  • Tempo: {args.bpm} BPM | Compases: {args.bars} | Raíz: {root_midi}")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
