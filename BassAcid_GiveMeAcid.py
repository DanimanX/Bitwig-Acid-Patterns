#!/usr/bin/env python3
"""
BassAcid_GiveMeAcid.py - Generador de bajo Peak-Time / Driving Acid Techno estilo Marie Vaunt & A*S*Y*S - "Give Me Acid".
Referencia: https://www.youtube.com/watch?v=TO6VknhSKiU (135 BPM, Kurai Records).

Características del estilo:
- Tempo de 135 BPM: Mayor peso, pegada y espacio para apertura del filtro 303 (squelch y resonancia).
- Firma sonora de A*S*Y*S & Marie Vaunt:
  * Líneas motrices de 16 semicorcheas con acentos contundentes y notas fantasma (ghosts) para el groove.
  * Slides legato (gate 1.15 - 1.25) conectando la tónica con saltos de 5ª (+7), octava (+12) y screeches agudos (+13, +15).
  * Estructura de pregunta/respuesta (Call & Response) dejando espacio para el impacto del kick y el hook vocal.
  * Tonalidad por defecto: B♭ (A#) / MIDI 46 (Bb2) o 58 (Bb3).

Uso:
    python3 BassAcid_GiveMeAcid.py
    python3 BassAcid_GiveMeAcid.py --bpm 135 --root Bb2
    python3 BassAcid_GiveMeAcid.py --style all
    python3 BassAcid_GiveMeAcid.py --style driving_lead --root 46 --bars 4 --output ./output/BassAcid_GiveMeAcid.mid
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

# Estilos / variaciones disponibles para Give Me Acid
GIVE_ME_ACID_STYLES = {
    "driving_lead": "Peak-Time Driving Lead (Riff motriz principal implacable, acentos y slides de 5ª y 8ª)",
    "call_response": "Call & Response Hook (Impacto staccato en graves que responde con screaming 303 slides)",
    "squelch_roller": "Hypnotic Rolling 303 (Groove continuo y pesado a 135 BPM con modulación dinámica)",
    "climax_drop": "Climax Build & Drop (Progresión de 4 compases con tensión creciente, subidas y corte pre-drop)"
}

DEFAULT_OUTPUT_STEM = "BassAcid_GiveMeAcid"


def default_output_stem(style: str = "driving_lead") -> str:
    """
    Nombre canónico de salida (sin timestamp) para un estilo dado.
    Reutilizado por generate_all.py y gui_generator.py.
    """
    style = style.lower().strip()
    if style not in GIVE_ME_ACID_STYLES:
        style = "driving_lead"
    return f"{DEFAULT_OUTPUT_STEM}_{style.capitalize()}"


def generate_bass_acid_give_me_acid(
    bpm: float = 135.0,
    root_note: int = 46,       # Bb2 (MIDI 46) / Tonalidad original de Marie Vaunt & A*S*Y*S - Give Me Acid
    style: str = "driving_lead",
    total_bars: int = 4,
    accent_vol: int = 127,
    normal_vol: int = 88,
    ghost_vol: int = 58,
    seed: int = None,
    output_path: Path = None
) -> Tuple[List[Path], int]:
    """
    Genera una secuencia MIDI de bajo Acid estilo Marie Vaunt & A*S*Y*S - Give Me Acid @ 135 BPM.
    """
    if seed is not None:
        random.seed(seed)

    style = style.lower().strip()
    if style not in GIVE_ME_ACID_STYLES:
        style = "driving_lead"

    seq_name = default_output_stem(style)
    seq = MidiSequence(name=seq_name, bpm=bpm)
    track = seq.track

    # Intervalos Bb Minor Acid Box / Pentatónica / Tensión A*S*Y*S (semitonos sobre root_note):
    # -12: Sub-tónica (Bb1), 0: Tónica (Bb2), 1: 2ª menor frigia (B), 3: 3ª menor (Db),
    # 5: 4ª justa (Eb), 6: Tritono / Blue note (E), 7: 5ª justa (F), 10: 7ª menor (Ab),
    # 12: Octava (Bb3), 13: Octava + Frigio screamer (B3), 15: Octava + 3ª menor (Db4), 24: Doble octava scream
    acid_intervals = [-12, 0, 0, 1, 3, 5, 6, 7, 10, 12, 13, 15, 24]

    grid: List[Dict[str, Any]] = []

    if style == "driving_lead":
        # Riff motriz de 135 BPM: potente, con peso en los pulsos 1 y 3 de cada tiempo,
        # slides de 5ª y octava en contratiempos y rolling 16ths dinámicos
        base_motif = []
        for step in range(1, 17):
            is_kick = ((step - 1) % 4 == 0)       # Pasos 1, 5, 9, 13
            is_offbeat = ((step - 1) % 4 == 2)    # Pasos 3, 7, 11, 15

            if is_kick:
                # 65% tónica contundente corta para no tapar la pegada del bombo, 35% silencio
                if random.random() > 0.35:
                    base_motif.append({
                        "type": "note",
                        "offset": 0 if random.random() > 0.25 else -12,
                        "accent": (step == 1 or step == 9),
                        "slide": False,
                        "vol": accent_vol if (step == 1 or step == 9) else normal_vol,
                        "gate": 0.50
                    })
                else:
                    base_motif.append({"type": "off"})
            elif is_offbeat:
                # Contratiempos: stabs y slides característicos de A*S*Y*S
                scream = (random.random() > 0.35)
                target_off = 12 if scream else random.choice([7, 10, 3])
                base_motif.append({
                    "type": "note",
                    "offset": target_off,
                    "accent": True,
                    "slide": scream,
                    "vol": accent_vol,
                    "gate": 1.20 if scream else 0.85
                })
            else:
                # Pasos de enlace (2, 4, 6, 8, 10, 12, 14, 16)
                if random.random() > 0.15:
                    is_acc = (random.random() > 0.70)
                    is_sld = (random.random() > 0.60)
                    off = random.choice([0, 0, 1, 3, 6, 7, 10])
                    v = accent_vol if is_acc else (normal_vol if random.random() > 0.4 else ghost_vol)
                    base_motif.append({
                        "type": "note",
                        "offset": off,
                        "accent": is_acc,
                        "slide": is_sld,
                        "vol": v,
                        "gate": 1.15 if is_sld else 0.75
                    })
                else:
                    base_motif.append({"type": "off"})

        # Ensamblar los compases con variaciones compás a compás
        for bar in range(total_bars):
            for step in range(1, 17):
                item = dict(base_motif[step - 1])

                # Compás 2: Variación síncopa en semicorcheas 7 y 8
                if bar == 1 and step in (7, 8):
                    item = {
                        "type": "note",
                        "offset": 10 if step == 7 else 12,
                        "accent": True,
                        "slide": True,
                        "vol": accent_vol,
                        "gate": 1.22
                    }
                # Compás 3: Squelch scream agudo en pasos 11 y 12
                elif bar == 2 and step in (11, 12):
                    item = {
                        "type": "note",
                        "offset": 13 if step == 11 else 15,
                        "accent": True,
                        "slide": True,
                        "vol": accent_vol,
                        "gate": 1.20
                    }
                # Compás 4: Turnaround fill ascendente en pasos 10-16 hacia la octava
                elif bar == (total_bars - 1) and step >= 10:
                    run = [0, 3, 6, 7, 10, 12, 13]
                    idx = step - 10
                    item = {
                        "type": "note",
                        "offset": run[idx],
                        "accent": (step in (12, 15, 16)),
                        "slide": (step % 2 == 0 or step == 16),
                        "vol": accent_vol if (step in (12, 15, 16)) else normal_vol,
                        "gate": 1.18 if (step % 2 == 0 or step == 16) else 0.85
                    }
                grid.append(item)

    elif style == "call_response":
        # Estilo Call & Response ("Give Me Acid"):
        # Llamada: Pasos 1 a 6 con subgrave y staccato
        # Respuesta: Pasos 7 a 16 con ráfagas ácidas y slides chillones
        call_bar_1 = [
            (0, True, False, accent_vol, 0.45),    # 1 Kick staccato
            ("off",),                              # 2 Espacio
            (0, False, False, normal_vol, 0.50),   # 3
            ("off",),                              # 4 Espacio
            (-12, True, False, accent_vol, 0.50),  # 5 Sub grave
            ("off",),                              # 6
            # Respuesta ácida A*S*Y*S:
            (7, True, True, accent_vol, 1.20),     # 7 Slide a 5ª
            (10, False, False, normal_vol, 0.80),  # 8
            (12, True, True, accent_vol, 1.25),    # 9 Slide a 8ª
            (10, False, False, normal_vol, 0.75),  # 10
            (7, True, True, accent_vol, 1.15),     # 11
            (6, False, False, ghost_vol, 0.65),    # 12 Blue note
            (0, True, False, accent_vol, 0.50),    # 13 Tónica ancla
            (3, False, False, normal_vol, 0.75),   # 14
            (12, True, True, accent_vol, 1.20),    # 15 Octava scream
            (0, False, False, ghost_vol, 0.60),    # 16
        ]

        call_bar_2 = list(call_bar_1)
        call_bar_2[8] = (13, True, True, accent_vol, 1.25)   # Frigio agudo scream
        call_bar_2[14] = (15, True, True, accent_vol, 1.22)  # 3ª menor aguda scream

        call_bar_3 = [
            (0, True, False, accent_vol, 0.50),
            (0, False, False, ghost_vol, 0.60),
            (7, True, True, accent_vol, 1.20),
            (5, False, False, normal_vol, 0.75),
            (0, True, False, accent_vol, 0.50),
            (3, False, False, normal_vol, 0.75),
            (12, True, True, accent_vol, 1.25),
            (10, True, True, accent_vol, 1.15),
            (0, True, False, normal_vol, 0.50),
            (7, False, False, normal_vol, 0.75),
            (13, True, True, accent_vol, 1.22),
            (12, True, True, accent_vol, 1.20),
            (0, True, False, accent_vol, 0.50),
            (10, False, False, normal_vol, 0.75),
            (7, True, True, accent_vol, 1.20),
            (6, False, False, ghost_vol, 0.65),
        ]

        call_bar_4 = [
            (0, True, False, accent_vol, 0.50),
            ("off",),
            (0, False, False, normal_vol, 0.50),
            ("off",),
            (-12, True, False, accent_vol, 0.50),
            ("off",),
            # Clímax de ráfaga
            (12, True, True, accent_vol, 1.25),
            (13, True, True, accent_vol, 1.22),
            (15, True, True, accent_vol, 1.25),
            (13, True, True, accent_vol, 1.20),
            (12, True, True, accent_vol, 1.20),
            (10, True, True, accent_vol, 1.15),
            (7, True, True, accent_vol, 1.20),
            (6, True, True, accent_vol, 1.15),
            (3, True, True, accent_vol, 1.15),
            (0, True, False, accent_vol, 0.85),
        ]

        preset_bars = [call_bar_1, call_bar_2, call_bar_3, call_bar_4]
        for b_idx in range(total_bars):
            c_bar = preset_bars[b_idx % len(preset_bars)]
            for item in c_bar:
                if item[0] == "off":
                    grid.append({"type": "off"})
                else:
                    off, acc, sld, vol, gt = item
                    grid.append({
                        "type": "note",
                        "offset": off,
                        "accent": acc,
                        "slide": sld,
                        "vol": vol,
                        "gate": gt
                    })

    elif style == "squelch_roller":
        # Hypnotic 16th-note rolling acid: Galope constante con modulación
        # continua entre notas fantasma y acentos con filtro abierto
        for bar in range(total_bars):
            for step in range(1, 17):
                is_kick = ((step - 1) % 4 == 0)
                is_off = ((step - 1) % 4 == 2)

                if is_kick:
                    # Alternancia: compás 1 y 3 kick con tónica corta; compás 2 y 4 silencio para rumble
                    if bar % 2 == 0 or random.random() > 0.6:
                        grid.append({
                            "type": "note",
                            "offset": 0,
                            "accent": False,
                            "slide": False,
                            "vol": normal_vol,
                            "gate": 0.45
                        })
                    else:
                        grid.append({"type": "off"})
                elif is_off:
                    # Offbeats: Rebote a octava o quinta con slide legato
                    target = 12 if (random.random() > 0.35) else 7
                    grid.append({
                        "type": "note",
                        "offset": target,
                        "accent": True,
                        "slide": True,
                        "vol": accent_vol,
                        "gate": 1.20
                    })
                else:
                    # Rolling 16th: notas de apoyo con ritmo galopante
                    roll_off = random.choice([0, 0, 3, 6, 7, 10])
                    is_accent = (random.random() > 0.75)
                    is_slide = (random.random() > 0.65)
                    vol = accent_vol if is_accent else (normal_vol if random.random() > 0.5 else ghost_vol)
                    grid.append({
                        "type": "note",
                        "offset": roll_off,
                        "accent": is_accent,
                        "slide": is_slide,
                        "vol": vol,
                        "gate": 1.15 if is_slide else 0.75
                    })

    elif style == "climax_drop":
        # Progresión de 4 compases hacia el Drop:
        # Compás 1: Base sólida y contenida
        # Compás 2: Incremento de densidad y apertura de octavas
        # Compás 3: Squelch extremo a doble octava (+24) y staccato acelerado
        # Compás 4: Ráfaga en subida hasta el tiempo 3, parada pre-drop en el tiempo 4 (silencio dramático)
        for bar in range(total_bars):
            for step in range(1, 17):
                if bar == 0:
                    # Compás 1: Driving moderado
                    is_k = ((step - 1) % 4 == 0)
                    is_o = ((step - 1) % 4 == 2)
                    if is_k:
                        grid.append({"type": "note", "offset": 0, "accent": False, "slide": False, "vol": normal_vol, "gate": 0.5})
                    elif is_o:
                        grid.append({"type": "note", "offset": 7, "accent": True, "slide": True, "vol": accent_vol, "gate": 1.15})
                    else:
                        grid.append({"type": "note", "offset": 0, "accent": False, "slide": False, "vol": ghost_vol, "gate": 0.7})
                elif bar == 1:
                    # Compás 2: Subida a octavas
                    is_k = ((step - 1) % 4 == 0)
                    is_o = ((step - 1) % 4 == 2)
                    if is_k:
                        grid.append({"type": "note", "offset": 0, "accent": False, "slide": False, "vol": normal_vol, "gate": 0.5})
                    elif is_o:
                        grid.append({"type": "note", "offset": 12, "accent": True, "slide": True, "vol": accent_vol, "gate": 1.20})
                    else:
                        grid.append({"type": "note", "offset": random.choice([3, 7, 10]), "accent": (step % 2 == 0), "slide": False, "vol": normal_vol, "gate": 0.75})
                elif bar == 2:
                    # Compás 3: Tensión máxima y screams de doble octava
                    is_scream = (step in (3, 7, 11, 15))
                    off = 24 if (step == 11 or step == 15) else (12 if is_scream else random.choice([0, 7, 10, 13]))
                    grid.append({
                        "type": "note",
                        "offset": off,
                        "accent": is_scream or (step % 2 == 1),
                        "slide": is_scream,
                        "vol": accent_vol if is_scream else normal_vol,
                        "gate": 1.22 if is_scream else 0.80
                    })
                else:
                    # Compás 4: Ráfaga en semicorcheas 1 a 12, parada en 13 a 16
                    if step <= 12:
                        # Ráfaga ascendente hacia el corte
                        scale_run = [0, 3, 5, 7, 10, 12, 13, 15, 12, 13, 15, 24]
                        idx = step - 1
                        grid.append({
                            "type": "note",
                            "offset": scale_run[idx],
                            "accent": (step >= 9),
                            "slide": True,
                            "vol": accent_vol,
                            "gate": 1.20
                        })
                    else:
                        # Parada pre-drop (silencio o golpe final antes del drop)
                        if step == 16:
                            grid.append({
                                "type": "note",
                                "offset": 0,
                                "accent": True,
                                "slide": False,
                                "vol": accent_vol,
                                "gate": 0.35
                            })
                        else:
                            grid.append({"type": "off"})

    # Renderizar notas al MIDI Track
    notes_placed = 0
    raw_notes = []

    for i, item in enumerate(grid):
        bar_idx = i // 16
        step_idx = i % 16
        step_tick = (bar_idx * TICKS_PER_BAR) + (step_idx * TICKS_PER_16TH)

        if item.get("type") == "note":
            note_num = max(0, min(127, root_note + item["offset"]))
            vel = item.get("vol", normal_vol)
            gate = item.get("gate", 0.80)
            duration = max(1, int(TICKS_PER_16TH * gate))

            raw_notes.append({
                "tick": step_tick,
                "dur": duration,
                "note": note_num,
                "vel": vel,
                "slide": item.get("slide", False)
            })

    # Resolver solapes entre notas del MISMO tono para no matar la siguiente nota
    for i, current in enumerate(raw_notes):
        end_tick = current["tick"] + current["dur"]
        for later in raw_notes[i + 1:]:
            if later["tick"] >= end_tick:
                break
            if later["note"] == current["note"]:
                current["dur"] = max(1, later["tick"] - current["tick"])
                break

    for n in raw_notes:
        track.add_note(
            tick=n["tick"],
            duration_ticks=n["dur"],
            note=n["note"],
            velocity=n["vel"],
            channel=0
        )
        notes_placed += 1

    if output_path is None:
        output_dir = SCRIPT_DIR / "output"
        output_path = build_timestamped_filename(seq_name, directory=output_dir)

    saved_paths = seq.save(output_path, copy_to_bitwig=True)
    return saved_paths, notes_placed


def generate_all_give_me_acid_variations(
    bpm: float = 135.0,
    root_note: int = 46,
    output_dir: Path = None
) -> List[Tuple[str, List[Path], int]]:
    """Genera un pack completo con las 4 variaciones del estilo Give Me Acid (A*S*Y*S & Marie Vaunt)."""
    if output_dir is None:
        output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    style_keys = ["driving_lead", "call_response", "squelch_roller", "climax_drop"]

    for st in style_keys:
        out_file = build_timestamped_filename(default_output_stem(st), directory=output_dir)
        paths, count = generate_bass_acid_give_me_acid(
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
        description="Generador de Bass Acid estilo Marie Vaunt & A*S*Y*S - 'Give Me Acid' @ 135 BPM para Bitwig"
    )
    parser.add_argument("--bpm", type=float, default=135.0, help="Tempo en BPM (default: 135.0)")
    parser.add_argument("--root", type=str, default="Bb2", help="Nota raíz MIDI o nombre (default: Bb2 / 46)")
    parser.add_argument(
        "--style",
        type=str,
        default="driving_lead",
        choices=["driving_lead", "call_response", "squelch_roller", "climax_drop", "all"],
        help="Estilo de variación (default: driving_lead, o 'all' para generar las 4)"
    )
    parser.add_argument("--bars", type=int, default=4, help="Cantidad de compases (default: 4)")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria opcional")
    parser.add_argument("--output", type=str, default=None, help="Ruta de guardado para el archivo .mid")

    args = parser.parse_args()

    try:
        root_midi = int(args.root)
    except ValueError:
        root_midi = note_name_to_midi(args.root)

    print("=" * 72)
    print("  BASS ACID GENERATOR - STYLE: MARIE VAUNT & A*S*Y*S - GIVE ME ACID (135 BPM)")
    print("=" * 72)
    print(f"Tempo:     {args.bpm} BPM")
    print(f"Nota Raíz: {root_midi} ({args.root.upper()}) | Compases: {args.bars}")

    if args.style == "all":
        print("Modo:      Generando pack con las 4 variaciones completas...")
        pack = generate_all_give_me_acid_variations(bpm=args.bpm, root_note=root_midi)
        for st, paths, count in pack:
            print(f"\n[OK] Estilo '{st}' ({GIVE_ME_ACID_STYLES[st]}):")
            print(f"  • Notas colocadas: {count}")
            for p in paths:
                print(f"  -> {p}")
    else:
        desc = GIVE_ME_ACID_STYLES.get(args.style, args.style)
        print(f"Modo:      {args.style.upper()} - {desc}")
        out_p = Path(args.output) if args.output else None
        saved_paths, count = generate_bass_acid_give_me_acid(
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
