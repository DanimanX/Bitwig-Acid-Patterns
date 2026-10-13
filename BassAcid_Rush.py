#!/usr/bin/env python3
"""
BassAcid_Rush.py - Generador de bajo Acid Trance / Neo-Acid Rave (Estilo KI/KI @ Warehouse Elementenstraat - Aeryeen "Rush", 1:17:04).
Genera variaciones de bajo 303 de alta energía (150-155 BPM, 4 compases, 64 semicorcheas) con slides legato,
acentos dinámicos extremos y rebotes de octava hipnóticos característicos de los sets de KI/KI.

Uso:
    python3 BassAcid_Rush.py
    python3 BassAcid_Rush.py --style all
    python3 BassAcid_Rush.py --style rolling --root F3 --bpm 155
    python3 BassAcid_Rush.py --style melodic_hook --root 53 --output ./output/Rush_Hook.mid
"""

import sys
import random
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from midi_core import (
    MidiSequence,
    TICKS_PER_16TH,
    TICKS_PER_BAR,
    note_name_to_midi,
    build_timestamped_filename,
)

# Estilos disponibles
RUSH_STYLES = {
    "rolling": "Rush Rolling Drive (Galope 16th hipnótico y rebote continuo)",
    "melodic_hook": "Acid Trance Hook (Melodía ácida eufórica 90s, saltos de 5ª y 7ª)",
    "octave_screamer": "Squelch & Octave Screamer (Acentos extremos, dobles octavas y scream)",
    "climax_drop": "Climax Drop & Turnaround (Evolución de 4 compases, subida y ráfaga previa al drop)"
}


def default_output_stem(style: str = "rolling") -> str:
    """
    Nombre canónico de salida (sin timestamp) para un estilo dado.
    Fuente única del nombre: lo usan este script, generate_all.py y gui_generator.py.
    """
    style = style.lower()
    if style not in RUSH_STYLES:
        style = "rolling"
    return f"BassAcid_Rush_{style.capitalize()}"


def generate_bass_acid_rush(
    bpm: float = 153.0,
    root_note: int = 53,       # F3 por defecto (tonalidad original de Aeryeen - Rush / Fa Menor)
    style: str = "rolling",    # 'rolling', 'melodic_hook', 'octave_screamer', 'climax_drop'
    total_bars: int = 4,
    accent_vol: int = 127,
    normal_vol: int = 84,
    ghost_vol: int = 56,
    seed: int = None,
    output_path: Path = None
) -> Tuple[List[Path], int]:
    """
    Genera una secuencia MIDI de bajo Acid estilo KI/KI / Aeryeen - Rush (1:17:04).
    """
    if seed is not None:
        random.seed(seed)

    style = style.lower()
    if style not in RUSH_STYLES:
        style = "rolling"

    seq_name = default_output_stem(style)
    seq = MidiSequence(name=seq_name, bpm=bpm)
    track = seq.track

    # Escala F Minor Acid Box / Phrygian Rave (Intervalos en semitonos sobre root_note):
    # -12: Sub-tónica, 0: Tónica, 1: 2ª menor (Frigio), 3: 3ª menor, 5: 4ª justa,
    # 6: Tritono / Blue note, 7: 5ª justa (ancla trance), 10: 7ª menor, 12: Octava alta,
    # 13: Octava + 2ª menor (scream), 15: Octava + 3ª menor, 24: Doble octava scream
    acid_intervals = [-12, 0, 0, 1, 3, 5, 6, 7, 10, 12, 13, 15, 24]

    # Construir la cuadrícula de 4 compases (64 pasos de semicorchea)
    grid: List[Dict[str, Any]] = []

    if style == "rolling":
        # Motivo base de 16 pasos con galope estricto y rebotes
        base_motif = []
        for step in range(1, 17):
            is_kick = ((step - 1) % 4 == 0)      # Pasos 1, 5, 9, 13
            is_offbeat = ((step - 1) % 4 == 2)   # Pasos 3, 7, 11, 15

            if is_kick:
                # 60% subgrave staccato para empujar con el kick, 40% silencio
                if random.random() > 0.40:
                    base_motif.append({
                        "type": "note",
                        "offset": 0 if random.random() > 0.3 else -12,
                        "accent": False,
                        "slide": False,
                        "vol": normal_vol,
                        "gate": 0.45
                    })
                else:
                    base_motif.append({"type": "off"})
            elif is_offbeat:
                # Contratiempo: rebote de octava o quinta con acento y slide
                is_oct = (random.random() > 0.30)
                offset = 12 if is_oct else (7 if random.random() > 0.5 else 3)
                base_motif.append({
                    "type": "note",
                    "offset": offset,
                    "accent": True,
                    "slide": True,
                    "vol": accent_vol,
                    "gate": 1.15
                })
            else:
                # Pasos 2, 4, 6, 8... notas de relleno galopante
                if random.random() > 0.15:
                    offset = random.choice([0, 0, 3, 7, 10, 12])
                    is_acc = (random.random() > 0.75)
                    is_sld = (random.random() > 0.65)
                    v = accent_vol if is_acc else (normal_vol if random.random() > 0.4 else ghost_vol)
                    base_motif.append({
                        "type": "note",
                        "offset": offset,
                        "accent": is_acc,
                        "slide": is_sld,
                        "vol": v,
                        "gate": 1.10 if is_sld else 0.75
                    })
                else:
                    base_motif.append({"type": "off"})

        # Ensamblar los 4 compases con variaciones progresivas
        for bar in range(total_bars):
            for step in range(1, 17):
                item = dict(base_motif[step - 1])
                # Variación compás 2: micro-síncopa en semicorcheas 6 y 14
                if bar == 1 and step in (6, 14):
                    item = {"type": "note", "offset": 10, "accent": True, "slide": True, "vol": accent_vol, "gate": 1.12}
                # Variación compás 3: melodía alta en contratiempos
                elif bar == 2 and step in (7, 11, 15):
                    item = {"type": "note", "offset": 15 if step == 15 else 12, "accent": True, "slide": True, "vol": accent_vol, "gate": 1.18}
                # Variación compás 4: fill de turnaround en pasos 9-16
                elif bar == 3 and step >= 9:
                    run_offsets = [0, 3, 5, 7, 10, 12, 13, 12]
                    idx = step - 9
                    item = {
                        "type": "note",
                        "offset": run_offsets[idx],
                        "accent": (step in (12, 15, 16)),
                        "slide": (step % 2 == 0),
                        "vol": accent_vol if (step in (12, 15, 16)) else normal_vol,
                        "gate": 1.15 if (step % 2 == 0) else 0.85
                    }
                grid.append(item)

    elif style == "melodic_hook":
        # Hook eufórico estilo KI/KI 90s Trance-Acid
        # Compás 1: Motivo principal
        # Compás 2: Respuesta sincopada
        # Compás 3: Elevación a la octava superior y quinta
        # Compás 4: Cascada ácida descendente
        c1 = [
            (0, False, False, normal_vol, 0.5),   # 1 Kick
            (0, False, False, ghost_vol, 0.7),    # 2
            (12, True, True, accent_vol, 1.15),   # 3 Octava alta slide
            (10, False, False, normal_vol, 0.8),  # 4 7ª menor
            (0, False, False, normal_vol, 0.5),   # 5 Kick
            (3, False, False, normal_vol, 0.8),   # 6 3ª menor
            (7, True, True, accent_vol, 1.15),    # 7 5ª justa slide
            (5, False, False, normal_vol, 0.8),   # 8 4ª
            (0, False, False, normal_vol, 0.5),   # 9 Kick
            (0, False, False, ghost_vol, 0.7),    # 10
            (12, True, True, accent_vol, 1.15),   # 11 Octava alta
            (15, True, True, accent_vol, 1.2),    # 12 Octava + 3ª scream
            (0, False, False, normal_vol, 0.5),   # 13 Kick
            (10, False, False, normal_vol, 0.8),  # 14
            (7, True, True, accent_vol, 1.15),    # 15
            (6, False, False, ghost_vol, 0.7),    # 16 Blue note
        ]
        c2 = list(c1)
        c2[11] = (13, True, True, accent_vol, 1.2)  # Variación frigia aguda
        c2[15] = (7, True, False, accent_vol, 0.9)

        c3 = [
            (0, False, False, normal_vol, 0.5),
            (7, True, True, accent_vol, 1.15),
            (12, True, True, accent_vol, 1.2),
            (10, False, False, normal_vol, 0.8),
            (0, False, False, normal_vol, 0.5),
            (12, True, True, accent_vol, 1.15),
            (15, True, True, accent_vol, 1.2),
            (13, True, True, accent_vol, 1.15),
            (0, False, False, normal_vol, 0.5),
            (7, False, False, normal_vol, 0.8),
            (12, True, True, accent_vol, 1.2),
            (10, False, False, normal_vol, 0.8),
            (0, False, False, normal_vol, 0.5),
            (5, False, False, normal_vol, 0.8),
            (7, True, True, accent_vol, 1.15),
            (3, False, False, normal_vol, 0.8),
        ]
        c4 = [
            (0, False, False, normal_vol, 0.5),
            (0, False, False, ghost_vol, 0.7),
            (12, True, True, accent_vol, 1.15),
            (10, False, False, normal_vol, 0.8),
            (0, False, False, normal_vol, 0.5),
            (7, True, True, accent_vol, 1.15),
            (6, False, False, normal_vol, 0.8),
            (5, False, False, normal_vol, 0.8),
            # Ráfaga descendente
            (15, True, True, accent_vol, 1.15),
            (13, True, True, accent_vol, 1.15),
            (12, True, True, accent_vol, 1.15),
            (10, True, True, accent_vol, 1.15),
            (7, True, True, accent_vol, 1.15),
            (5, True, True, accent_vol, 1.15),
            (3, True, True, accent_vol, 1.15),
            (1, True, False, accent_vol, 0.8),
        ]
        bars_data = [c1, c2, c3, c4]
        for b_idx in range(total_bars):
            cur_bar = bars_data[b_idx % len(bars_data)]
            for off, acc, sld, vol, gt in cur_bar:
                grid.append({
                    "type": "note",
                    "offset": off,
                    "accent": acc,
                    "slide": sld,
                    "vol": vol,
                    "gate": gt
                })

    elif style == "octave_screamer":
        # Screamer agresivo con contrastes dinámicos brutales y saltos a doble octava (+24)
        for bar in range(total_bars):
            for step in range(1, 17):
                is_kick = ((step - 1) % 4 == 0)
                is_off = ((step - 1) % 4 == 2)

                if is_kick:
                    if random.random() > 0.30:
                        grid.append({"type": "off"})
                    else:
                        grid.append({
                            "type": "note",
                            "offset": -12,
                            "accent": False,
                            "slide": False,
                            "vol": normal_vol,
                            "gate": 0.40
                        })
                elif is_off:
                    # Scream en contratiempo: 50% doble octava (+24), 50% octava frigia (+13 o +12)
                    scream_offset = 24 if random.random() > 0.4 else (13 if random.random() > 0.5 else 12)
                    grid.append({
                        "type": "note",
                        "offset": scream_offset,
                        "accent": True,
                        "slide": True,
                        "vol": accent_vol,
                        "gate": 1.22
                    })
                else:
                    # Rolling denso con ghost notes o acentos de latigazo
                    if random.random() > 0.18:
                        is_acc = (random.random() > 0.68)
                        is_sld = (random.random() > 0.55)
                        off = random.choice([0, 1, 3, 7, 10, 12, 13])
                        v = accent_vol if is_acc else (normal_vol if random.random() > 0.5 else ghost_vol)
                        grid.append({
                            "type": "note",
                            "offset": off,
                            "accent": is_acc,
                            "slide": is_sld,
                            "vol": v,
                            "gate": 1.15 if is_sld else 0.70
                        })
                    else:
                        grid.append({"type": "off"})

    elif style == "climax_drop":
        # Progresión pre-drop / segundo drop como el clímax de 1:17:04
        # Compás 1: Rolling tenso
        # Compás 2: Síncopas crecientes
        # Compás 3: Riser ascendente continuo
        # Compás 4: Ráfaga ametralladora (1-8), y remate con subida y caída (9-16)
        for bar in range(total_bars):
            if bar == 0:
                # Compás 1: Rolling
                for step in range(1, 17):
                    is_kick = ((step - 1) % 4 == 0)
                    if is_kick:
                        grid.append({"type": "note", "offset": 0, "accent": False, "slide": False, "vol": normal_vol, "gate": 0.5})
                    elif (step - 1) % 4 == 2:
                        grid.append({"type": "note", "offset": 12, "accent": True, "slide": True, "vol": accent_vol, "gate": 1.15})
                    else:
                        grid.append({"type": "note", "offset": random.choice([0, 3, 7]), "accent": False, "slide": False, "vol": normal_vol, "gate": 0.75})
            elif bar == 1:
                # Compás 2: Incremento de acentos y dobles notas
                for step in range(1, 17):
                    if step in (3, 7, 11, 14, 15):
                        grid.append({"type": "note", "offset": 12 if step < 14 else 15, "accent": True, "slide": True, "vol": accent_vol, "gate": 1.18})
                    elif (step - 1) % 4 == 0:
                        grid.append({"type": "note", "offset": 0, "accent": False, "slide": False, "vol": normal_vol, "gate": 0.5})
                    else:
                        grid.append({"type": "note", "offset": random.choice([0, 7, 10]), "accent": False, "slide": False, "vol": ghost_vol, "gate": 0.7})
            elif bar == 2:
                # Compás 3: Riser ascendente en las 16 semicorcheas
                riser_scale = [-12, -12, 0, 0, 1, 3, 5, 6, 7, 10, 12, 13, 15, 18, 22, 24]
                for step in range(1, 17):
                    grid.append({
                        "type": "note",
                        "offset": riser_scale[step - 1],
                        "accent": (step % 2 == 1),
                        "slide": (step >= 9),
                        "vol": min(127, 70 + step * 3),
                        "gate": 1.12 if step >= 9 else 0.85
                    })
            elif bar == 3:
                # Compás 4: Clímax ametralladora y resolución
                for step in range(1, 17):
                    if step <= 8:
                        # Machine gun repetitivo en la octava con velocidad máxima
                        grid.append({
                            "type": "note",
                            "offset": 12,
                            "accent": True,
                            "slide": (step % 2 == 0),
                            "vol": accent_vol,
                            "gate": 1.10 if (step % 2 == 0) else 0.85
                        })
                    elif step in (9, 10, 11, 12):
                        # Grito frigio ascendente
                        climbs = [13, 15, 24, 24]
                        grid.append({
                            "type": "note",
                            "offset": climbs[step - 9],
                            "accent": True,
                            "slide": True,
                            "vol": accent_vol,
                            "gate": 1.25
                        })
                    elif step in (13, 14):
                        # Silencio o nota fantasma de corte antes del drop final
                        grid.append({"type": "off"})
                    else:
                        # Pasos 15, 16: Golpe final de ancla que cae a la tónica
                        final_off = 12 if step == 15 else 0
                        grid.append({
                            "type": "note",
                            "offset": final_off,
                            "accent": True,
                            "slide": (step == 15),
                            "vol": accent_vol,
                            "gate": 1.15 if step == 15 else 0.90
                        })

    # Renderizar notas al MIDI Track
    notes_placed = 0
    total_steps = len(grid)

    for i, item in enumerate(grid):
        bar_idx = i // 16
        step_idx = i % 16
        step_tick = (bar_idx * TICKS_PER_BAR) + (step_idx * TICKS_PER_16TH)

        if item.get("type") == "note":
            note_num = max(0, min(127, root_note + item["offset"]))
            vel = item.get("vol", normal_vol)
            gate = item.get("gate", 0.80)
            duration = int(TICKS_PER_16TH * gate)

            track.add_note(
                tick=step_tick,
                duration_ticks=duration,
                note=note_num,
                velocity=vel,
                channel=0
            )
            notes_placed += 1

    # Definir ruta de guardado
    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename(seq_name, directory=output_dir)

    saved_paths = seq.save(output_path, copy_to_bitwig=True)
    return saved_paths, notes_placed


def generate_all_rush_variations(
    bpm: float = 153.0,
    root_note: int = 53,
    output_dir: Path = None
) -> List[Tuple[str, List[Path], int]]:
    """Genera un pack completo con las 4 variaciones del estilo Rush (KI/KI 1:17:04)."""
    if output_dir is None:
        output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    style_keys = ["rolling", "melodic_hook", "octave_screamer", "climax_drop"]

    for st in style_keys:
        out_file = build_timestamped_filename(default_output_stem(st), directory=output_dir)
        paths, count = generate_bass_acid_rush(
            bpm=bpm,
            root_note=root_note,
            style=st,
            total_bars=4,
            output_path=out_file
        )
        results.append((st, paths, count))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generador de Bass Acid estilo KI/KI @ Warehouse Elementenstraat (Aeryeen - Rush, 1:17:04)"
    )
    parser.add_argument("--bpm", type=float, default=153.0, help="Tempo en BPM (default: 153.0)")
    parser.add_argument("--root", type=str, default="F3", help="Nota raíz MIDI o nombre (default: F3 / 53)")
    parser.add_argument(
        "--style",
        type=str,
        default="rolling",
        choices=["rolling", "melodic_hook", "octave_screamer", "climax_drop", "all"],
        help="Estilo de variación (default: rolling, o 'all' para generar las 4)"
    )
    parser.add_argument("--bars", type=int, default=4, help="Cantidad de compases (default: 4)")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria opcional")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    print("=" * 68)
    print("  BASS ACID GENERATOR - STYLE: KI/KI @ ELEMENTENSTRAAT (RUSH 1:17:04)")
    print("=" * 68)
    print(f"Tempo:     {args.bpm} BPM")
    print(f"Nota Raíz: {root_midi} ({args.root.upper()}) | Compases: {args.bars}")

    if args.style == "all":
        print(f"Modo:      Generando las 4 variaciones completas...")
        pack = generate_all_rush_variations(bpm=args.bpm, root_note=root_midi)
        for st, paths, count in pack:
            print(f"\n[OK] Estilo '{st}' ({RUSH_STYLES[st]}):")
            print(f"  • Notas colocadas: {count}")
            for p in paths:
                print(f"  -> {p}")
    else:
        desc = RUSH_STYLES.get(args.style, args.style)
        print(f"Modo:      {args.style.upper()} - {desc}")
        out_p = Path(args.output) if args.output else None
        saved_paths, count = generate_bass_acid_rush(
            bpm=args.bpm,
            root_note=root_midi,
            style=args.style,
            total_bars=args.bars,
            seed=args.seed,
            output_path=out_p
        )
        print(f"\n[OK] Secuencia generada con éxito:")
        print(f"  • Notas colocadas: {count}")
        for p in saved_paths:
            print(f"  -> {p}")


if __name__ == "__main__":
    main()
