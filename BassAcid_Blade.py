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
  * **Espiral ascendente** en las 4 últimas semicorcheas que remata el compás y engancha con
    el siguiente.

**Cada ejecución genera una variación distinta.** Se conserva la firma del estilo (16 notas sin
huecos, acentos en los 4 pulsos, espiral final) y varían las notas de relleno, los stabs y la
espiral. Usa `--seed` para congelar y reproducir una toma concreta.

Como el bajo ocupa las 16 semicorcheas, en Bitwig conviene **sidechainear el bajo contra el
bombo** (o dejar que el kick mande) para que el 4x4 no se embarre.

Uso:
    python3 BassAcid_Blade.py
    python3 BassAcid_Blade.py --bpm 155 --root 50
    python3 BassAcid_Blade.py --seed 1234 --root F3 --bpm 153 --output ./output/BassAcid_Blade.mid
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

# Paleta ácida sobre la raíz: 0 tónica | 3 3ª menor | 6 tritono | 7 5ª justa | 12 octava
PALETTE = (0, 3, 6, 7, 12)

# Stabs de contratiempo (quinta y octava) y espirales finales ascendentes hacia la octava.
STAB_OFFSETS = (7, 12)
SPIRALS = ((3, 6, 12), (3, 7, 12), (5, 6, 12), (5, 7, 12), (6, 7, 12))

# Papel de cada semicorchea en el riff. Es la columna vertebral del estilo Blade: fija,
# mientras el resto de la frase se genera con variación.
PILLAR_STEPS = (1, 5, 9, 13)   # 4x4: acento sobre la tónica
STAB_STEPS = (3, 7, 12)        # stabs de quinta/octava con slide
SPIRAL_STEPS = (14, 15, 16)    # espiral ascendente que remata el compás


def _fill_layer(rng: random.Random) -> str:
    """Capa dinámica de una nota de relleno: mayoría ghosts, algunos acentos."""
    r = rng.random()
    if r < 0.50:
        return "g"
    if r < 0.85:
        return "n"
    return "a"


def _build_motif(rng: random.Random) -> tuple:
    """
    Construye UNA variación del riff Blade conservando su firma rítmica.

    Fijo:     pasos 1/5/9/13 acento sobre la tónica, y la espiral ascendente final.
    Variable: notas de relleno (altura + capa + slide) y stabs de contratiempo.
    """
    offsets: dict = {}
    layers: dict = {}
    slides: dict = {}

    spiral = rng.choice(SPIRALS)

    for step in range(1, 17):
        if step in PILLAR_STEPS:
            offsets[step], layers[step], slides[step] = 0, "a", False
        elif step in STAB_STEPS:
            offsets[step] = rng.choice(STAB_OFFSETS)
            layers[step] = "a"
            slides[step] = rng.random() < 0.75
        elif step in SPIRAL_STEPS:
            offsets[step] = spiral[SPIRAL_STEPS.index(step)]
            layers[step] = "a" if step > 14 else rng.choice(("n", "a"))
            slides[step] = True
        else:  # relleno
            offsets[step] = rng.choice(PALETTE)
            layers[step] = _fill_layer(rng)
            slides[step] = rng.random() < 0.30

    # Mecanismo: un slide solo vale si la nota siguiente tiene OTRA altura; si no, el Note-Off
    # del mismo pitch cortaría la nota siguiente y el slide no haría nada.
    for step in range(1, 17):
        if slides[step] and offsets[(step % 16) + 1] == offsets[step]:
            slides[step] = False

    return tuple((s, offsets[s], layers[s], slides[s]) for s in range(1, 17))


def _validate_motif(motif: tuple):
    """La firma del estilo se verifica por mecanismo, no por confianza."""
    steps = [step for step, _off, _layer, _slide in motif]
    if steps != list(range(1, 17)):
        raise ValueError(f"El motivo debe cubrir los 16 pasos en orden; recibido: {steps}")

    for i, (_step, offset, _layer, slide) in enumerate(motif):
        if slide and motif[(i + 1) % 16][1] == offset:
            raise ValueError(
                f"Slide sin destino distinto en el paso {i + 1}: offset {offset}"
            )

    for step in KICK_GRID_STEPS:
        _s, offset, layer, slide = motif[step - 1]
        if (offset, layer, slide) != (0, "a", False):
            raise ValueError(
                f"El pulso {step} debe ser acento sobre la tónica; es {(offset, layer, slide)}"
            )


def _resolve_notes(motif: tuple, root_note: int, total_bars: int) -> List[dict]:
    """Expande el motivo a notas concretas y resuelve solapes de mismo pitch."""
    notes: List[dict] = []
    for bar in range(max(1, int(total_bars))):
        bar_tick = bar * TICKS_PER_BAR
        for step, offset, layer, slide in motif:
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
    seed: int = None,      # None = variación aleatoria; entero = toma reproducible
    output_path: str = None
) -> Tuple[List[Path], int]:
    """Genera una variación de la línea de bajo ácido estilo Blade y la exporta a .mid."""
    rng = random.Random(seed)
    motif = _build_motif(rng)
    _validate_motif(motif)

    seq = MidiSequence(name=DEFAULT_OUTPUT_STEM, bpm=bpm)
    track = seq.track

    notes = _resolve_notes(motif, root_note, total_bars)
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
    parser.add_argument("--seed", type=int, default=None, help="Semilla para reproducir una toma concreta (default: aleatoria)")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    # Sin --seed la toma es aleatoria; se reporta la semilla usada para poder reproducirla.
    effective_seed = args.seed if args.seed is not None else random.randrange(1_000_000_000)

    saved_paths, count = generate_bass_acid_blade(
        bpm=args.bpm,
        root_note=root_midi,
        total_bars=args.bars,
        seed=effective_seed,
        output_path=args.output
    )

    print(f"\n[OK] BassAcid Blade (16 notas, estilo Blade) generado:")
    print(f"  • Notas colocadas: {count}")
    print(f"  • Tempo: {args.bpm} BPM | Compases: {args.bars} | Raíz: {root_midi}")
    print(f"  • Semilla: {effective_seed}  (repítela con --seed {effective_seed})")
    for p in saved_paths:
        print(f"  -> {p}")


if __name__ == "__main__":
    main()
