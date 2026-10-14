#!/usr/bin/env python3
"""
gui_generator.py - Interfaz gráfica de escritorio para generar secuencias MIDI Acid para Bitwig Studio.
Permite generar con un solo clic patrones de bajo 303, agresivo, Blade (16 notas), Rush (KI/KI),
Give Me Acid (Marie Vaunt & A*S*Y*S @ 135 BPM), bombos y hi-hats.
Soporta selector de estilos con auto-ajuste de BPM/Tónica y configuración de carpeta de Clips multiplataforma.
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from midi_core import (
    get_current_os,
    get_os_display_name,
    get_bitwig_library_dir,
    set_bitwig_library_dir,
    open_folder,
    get_timestamp_prefix,
    build_timestamped_filename,
)
from BassAcid import generate_bass_acid, DEFAULT_OUTPUT_STEM as BASS_ROLLING_STEM
from BassAcid_Aggressive import generate_bass_acid_aggressive, DEFAULT_OUTPUT_STEM as BASS_AGGRESSIVE_STEM
from BassAcid_Blade import generate_bass_acid_blade, DEFAULT_OUTPUT_STEM as BASS_BLADE_STEM
from BassAcid_Rush import (
    generate_bass_acid_rush,
    generate_all_rush_variations,
    RUSH_STYLES,
    default_output_stem as rush_output_stem,
)
from BassAcid_GiveMeAcid import (
    generate_bass_acid_give_me_acid,
    generate_all_give_me_acid_variations,
    GIVE_ME_ACID_STYLES,
    default_output_stem as give_me_acid_output_stem,
    DEFAULT_OUTPUT_STEM as BASS_GIVE_ME_ACID_STEM,
)
from acid_kick_pattern import generate_acid_kick, default_output_stem as kick_output_stem
from acid_hat_pattern import generate_acid_hat, DEFAULT_OUTPUT_STEM as HAT_STEM


class AcidGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.os_name = get_current_os()
        self.os_display = get_os_display_name(self.os_name)

        self.title(f"Bitwig Acid MIDI Generator [{self.os_display}] - by DanimanX")
        self.geometry("720x780")
        self.minsize(680, 720)
        self.configure(bg="#1E1E1E")

        self.clips_dir_path = get_bitwig_library_dir()
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#FF6600", height=50)
        header.pack(fill="x")
        title_lbl = tk.Label(
            header,
            text=f"BITWIG ACID MIDI GENERATOR  •  {self.os_display.upper()}",
            bg="#FF6600",
            fg="#FFFFFF",
            font=("Helvetica", 14, "bold")
        )
        title_lbl.pack(pady=10)

        main_frame = tk.Frame(self, bg="#1E1E1E", padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        # 1. Configuración de Carpeta Bitwig Clips (Multiplataforma)
        folder_frame = tk.LabelFrame(
            main_frame,
            text=f" Carpeta Bitwig Clips ({self.os_display}) ",
            bg="#282828",
            fg="#FF6600",
            font=("Helvetica", 9, "bold"),
            padx=12,
            pady=8
        )
        folder_frame.pack(fill="x", pady=(0, 10))

        self.clips_dir_var = tk.StringVar(value=str(self.clips_dir_path))
        clips_entry = tk.Entry(
            folder_frame,
            textvariable=self.clips_dir_var,
            bg="#333333",
            fg="#00FFCC",
            font=("Monospace", 9),
            readonlybackground="#333333",
            state="readonly"
        )
        clips_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        change_btn = tk.Button(
            folder_frame,
            text="Cambiar...",
            bg="#444444",
            fg="#FFFFFF",
            font=("Helvetica", 8, "bold"),
            command=self.choose_clips_dir
        )
        change_btn.pack(side="right")

        # 2. Controles de Parámetros Globales y Selectores de Estilo
        params_frame = tk.LabelFrame(
            main_frame,
            text=" Configuración de Estilos y Parámetros ",
            bg="#282828",
            fg="#FF6600",
            font=("Helvetica", 9, "bold"),
            padx=12,
            pady=8
        )
        params_frame.pack(fill="x", pady=(0, 10))

        # Selector de Estilo Acid Principal (Preset con auto-ajuste de BPM / Tono)
        tk.Label(
            params_frame,
            text="Estilo Acid (Preset):",
            bg="#282828",
            fg="#00FFCC",
            font=("Helvetica", 9, "bold")
        ).grid(row=0, column=0, sticky="w", pady=4)

        self.bass_style_var = tk.StringVar(value="Give Me Acid (A*S*Y*S & Marie Vaunt - 135 BPM)")
        self.bass_style_combo = ttk.Combobox(
            params_frame,
            textvariable=self.bass_style_var,
            values=[
                "Give Me Acid (A*S*Y*S & Marie Vaunt - 135 BPM)",
                "Rolling 303 (Clásico Hipnótico - 155 BPM)",
                "Aggressive (Marie Vaunt Verknipt - 155 BPM)",
                "Blade (16 semicorcheas - 155 BPM)",
                "Rush (KI/KI @ Elementenstraat - 153 BPM)",
            ],
            width=38,
            state="readonly"
        )
        self.bass_style_combo.grid(row=0, column=1, columnspan=3, sticky="w", padx=10, pady=4)
        self.bass_style_combo.bind("<<ComboboxSelected>>", self.on_bass_style_selected)

        # BPM
        tk.Label(params_frame, text="Tempo (BPM):", bg="#282828", fg="#E0E0E0").grid(row=1, column=0, sticky="w", pady=4)
        self.bpm_var = tk.StringVar(value="135.0")
        bpm_entry = tk.Entry(params_frame, textvariable=self.bpm_var, width=8, bg="#333333", fg="#FFFFFF", insertbackground="#FFFFFF")
        bpm_entry.grid(row=1, column=1, sticky="w", padx=10, pady=4)

        # Nota Raíz
        tk.Label(params_frame, text="Nota Raíz (Tónica):", bg="#282828", fg="#E0E0E0").grid(row=1, column=2, sticky="w", pady=4)
        self.root_var = tk.StringVar(value="46 (Bb2 / La#2 - Give Me Acid)")
        self.root_combo = ttk.Combobox(
            params_frame,
            textvariable=self.root_var,
            values=[
                "46 (Bb2 / La#2 - Give Me Acid)",
                "58 (Bb3 / La#3)",
                "50 (D3 / Re)",
                "53 (F3 / Fa - Rush)",
                "38 (D2)",
                "48 (C3)",
                "45 (A2)",
                "43 (G2)"
            ],
            width=26,
            state="readonly"
        )
        self.root_combo.grid(row=1, column=3, sticky="w", padx=10, pady=4)

        # Variación Give Me Acid (A*S*Y*S @ 135 BPM)
        tk.Label(params_frame, text="Variación Give Me Acid:", bg="#282828", fg="#E0E0E0").grid(row=2, column=0, sticky="w", pady=4)
        self.give_me_acid_style_var = tk.StringVar(value="driving_lead (Peak-Time Driving Acid)")
        gma_style_combo = ttk.Combobox(
            params_frame,
            textvariable=self.give_me_acid_style_var,
            values=[
                "driving_lead (Peak-Time Driving Acid)",
                "call_response (Call & Response Hook)",
                "squelch_roller (Hypnotic Rolling 303)",
                "climax_drop (Build-up & Climax Drop)",
                "all (Pack 4 variaciones completas)"
            ],
            width=34,
            state="readonly"
        )
        gma_style_combo.grid(row=2, column=1, columnspan=3, sticky="w", padx=10, pady=4)

        # Estilo de BassAcid Rush (KI/KI 1:17:04)
        tk.Label(params_frame, text="Estilo Bass Rush (KI/KI):", bg="#282828", fg="#E0E0E0").grid(row=3, column=0, sticky="w", pady=4)
        self.rush_style_var = tk.StringVar(value="rolling (Galope hipnótico)")
        rush_style_combo = ttk.Combobox(
            params_frame,
            textvariable=self.rush_style_var,
            values=[
                "rolling (Galope hipnótico)",
                "melodic_hook (Hook eufórico trance-acid)",
                "octave_screamer (Squelch & Octave Screamer)",
                "climax_drop (Clímax pre-drop 4 compases)",
                "all (Pack 4 variaciones completas)"
            ],
            width=34,
            state="readonly"
        )
        rush_style_combo.grid(row=3, column=1, columnspan=3, sticky="w", padx=10, pady=4)

        # Estilo de Kick Hard Techno
        tk.Label(params_frame, text="Variación Kick Techno:", bg="#282828", fg="#E0E0E0").grid(row=4, column=0, sticky="w", pady=4)
        self.kick_style_var = tk.StringVar(value="hybrid (Evolución 4 compases)")
        kick_style_combo = ttk.Combobox(
            params_frame,
            textvariable=self.kick_style_var,
            values=[
                "hybrid (Evolución 4 compases)",
                "rolling (Rolling Rumble)",
                "syncopated (Industrial Sincopado)",
                "stutter (Schranz / Ametralladora)",
                "offbeat_push (Offbeat Push)",
                "predrop_break (Pre-Drop Break)"
            ],
            width=34,
            state="readonly"
        )
        kick_style_combo.grid(row=4, column=1, columnspan=3, sticky="w", padx=10, pady=4)

        # 3. Botones Generadores Individuales
        gens_frame = tk.LabelFrame(
            main_frame,
            text=" Generar Patrones ",
            bg="#282828",
            fg="#FF6600",
            font=("Helvetica", 9, "bold"),
            padx=12,
            pady=6
        )
        gens_frame.pack(fill="both", expand=True, pady=(0, 10))

        btn_style = {
            "bg": "#383838",
            "fg": "#FFFFFF",
            "activebackground": "#505050",
            "activeforeground": "#FFFFFF",
            "font": ("Helvetica", 9, "bold"),
            "bd": 1,
            "relief": "raised"
        }

        # Botón para generar el estilo de bajo actualmente seleccionado en el combo
        sel_btn = tk.Button(
            gens_frame,
            text="⚡ GENERAR ESTILO SELECCIONADO ARRIBA",
            bg="#006666",
            fg="#00FFCC",
            activebackground="#008888",
            activeforeground="#FFFFFF",
            font=("Helvetica", 9, "bold"),
            bd=1,
            relief="raised",
            command=self._safe(self.gen_selected_bass, "Estilo Seleccionado")
        )
        sel_btn.grid(row=0, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="Genera el bajo según el selector principal", bg="#282828", fg="#00FFCC").grid(row=0, column=1, sticky="w", padx=8)

        # Give Me Acid (A*S*Y*S & Marie Vaunt)
        gma_btn = tk.Button(gens_frame, text="▶ BassAcid (Give Me Acid @ 135 BPM)", **btn_style, command=self._safe(self.gen_bass_give_me_acid, "BassAcid Give Me Acid"))
        gma_btn.grid(row=1, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="Marie Vaunt & A*S*Y*S, slides 303, driving y acentos", bg="#282828", fg="#AAAAAA").grid(row=1, column=1, sticky="w", padx=8)

        # Bass 303 Rolling
        b1_btn = tk.Button(gens_frame, text="▶ BassAcid (Rolling 303)", **btn_style, command=self._safe(self.gen_bass_rolling, "BassAcid Rolling 303"))
        b1_btn.grid(row=2, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="4 compases con slides legato y acentos", bg="#282828", fg="#AAAAAA").grid(row=2, column=1, sticky="w", padx=8)

        # Bass Aggressive
        b2_btn = tk.Button(gens_frame, text="▶ BassAcid (Aggressive Marie Vaunt)", **btn_style, command=self._safe(self.gen_bass_aggressive, "BassAcid Aggressive"))
        b2_btn.grid(row=3, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="Frigio/Tritono, screeches agudos de octava", bg="#282828", fg="#AAAAAA").grid(row=3, column=1, sticky="w", padx=8)

        # Bass Blade (16 notas)
        b3_btn = tk.Button(gens_frame, text="▶ BassAcid (Blade - 16 notas)", **btn_style, command=self._safe(self.gen_bass_blade, "BassAcid Blade"))
        b3_btn.grid(row=4, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="1 compás, 16 semicorcheas, acentos 303 y slides", bg="#282828", fg="#AAAAAA").grid(row=4, column=1, sticky="w", padx=8)

        # Bass Rush (KI/KI 1:17:04 Style)
        b4_btn = tk.Button(gens_frame, text="▶ BassAcid Rush (KI/KI 1:17:04)", **btn_style, command=self._safe(self.gen_bass_rush, "BassAcid Rush"))
        b4_btn.grid(row=5, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="Estilo Aeryeen 'Rush', 4 variaciones", bg="#282828", fg="#AAAAAA").grid(row=5, column=1, sticky="w", padx=8)

        # Kick
        k_btn = tk.Button(gens_frame, text="▶ Acid Kick (4x4 Rumble)", **btn_style, command=self._safe(self.gen_kick, "Acid Kick"))
        k_btn.grid(row=6, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="Bombo 4x4, ghost kicks para rumble y redoble", bg="#282828", fg="#AAAAAA").grid(row=6, column=1, sticky="w", padx=8)

        # Hi-Hats
        h_btn = tk.Button(gens_frame, text="▶ Acid Hi-Hats (Rave 16ths)", **btn_style, command=self._safe(self.gen_hats, "Acid Hi-Hats"))
        h_btn.grid(row=7, column=0, sticky="ew", padx=4, pady=2)
        tk.Label(gens_frame, text="Contratiempos abiertos + galope semicorcheas", bg="#282828", fg="#AAAAAA").grid(row=7, column=1, sticky="w", padx=8)

        gens_frame.grid_columnconfigure(0, weight=1)

        # 4. Botón Maestro y Explorador
        bottom_frame = tk.Frame(main_frame, bg="#1E1E1E")
        bottom_frame.pack(fill="x")

        all_btn = tk.Button(
            bottom_frame,
            text="★ GENERAR KIT COMPLETO (TODOS LOS PATRONES) ★",
            bg="#FF6600",
            fg="#FFFFFF",
            activebackground="#FF8533",
            font=("Helvetica", 11, "bold"),
            bd=2,
            pady=6,
            command=self._safe(self.gen_all, "Kit completo")
        )
        all_btn.pack(fill="x", pady=(0, 6))

        folder_btn = tk.Button(
            bottom_frame,
            text=f"📁 Abrir Carpeta de Bitwig Clips ({self.os_display})",
            bg="#2A2A2A",
            fg="#CCCCCC",
            font=("Helvetica", 9),
            command=self.open_bitwig_folder
        )
        folder_btn.pack(side="left")

        # Barra de estado
        self.status_var = tk.StringVar(value=f"Listo para {self.os_display}. Los archivos se guardan en tu biblioteca de Bitwig.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bg="#111111",
            fg="#00FF66",
            anchor="w",
            padx=10,
            pady=5,
            font=("Monospace", 9)
        )
        status_bar.pack(side="bottom", fill="x")

    def on_bass_style_selected(self, event=None):
        """Ajusta automáticamente el BPM y la nota raíz sugerida al seleccionar un estilo."""
        selected = self.bass_style_var.get().lower()
        if "give me acid" in selected:
            self.bpm_var.set("135.0")
            self.root_var.set("46 (Bb2 / La#2 - Give Me Acid)")
            self.status_var.set("Estilo 'Give Me Acid' seleccionado: Tempo ajustado a 135 BPM | Tónica Bb2")
        elif "rush" in selected:
            self.bpm_var.set("153.0")
            self.root_var.set("53 (F3 / Fa - Rush)")
            self.status_var.set("Estilo 'Rush' seleccionado: Tempo ajustado a 153 BPM | Tónica F3")
        elif "rolling" in selected:
            self.bpm_var.set("155.0")
            self.root_var.set("50 (D3 / Re)")
            self.status_var.set("Estilo 'Rolling 303' seleccionado: Tempo ajustado a 155 BPM | Tónica D3")
        elif "aggressive" in selected:
            self.bpm_var.set("155.0")
            self.root_var.set("50 (D3 / Re)")
            self.status_var.set("Estilo 'Aggressive Marie Vaunt' seleccionado: Tempo ajustado a 155 BPM | Tónica D3")
        elif "blade" in selected:
            self.bpm_var.set("155.0")
            self.root_var.set("50 (D3 / Re)")
            self.status_var.set("Estilo 'Blade' seleccionado: Tempo ajustado a 155 BPM | Tónica D3")

    def choose_clips_dir(self):
        """Permite al usuario seleccionar interactivamente la carpeta de clips de Bitwig."""
        initial_dir = str(self.clips_dir_path.parent if self.clips_dir_path.exists() else Path.home())
        new_dir = filedialog.askdirectory(
            title=f"Seleccionar Carpeta de Clips para {self.os_display}",
            initialdir=initial_dir
        )
        if new_dir:
            target = Path(new_dir) / "Acid_Sequences" if not new_dir.endswith("Acid_Sequences") else Path(new_dir)
            target.mkdir(parents=True, exist_ok=True)
            set_bitwig_library_dir(target, os_name=self.os_name, confirmed=True)
            self.clips_dir_path = target
            self.clips_dir_var.set(str(target))
            self.status_var.set(f"✔ Ruta actualizada para {self.os_display}: {target}")

    def _safe(self, action, label):
        """Envuelve un callback del generador capturando errores y reportándolos en la UI."""
        def runner():
            try:
                action()
            except Exception as e:
                self.status_var.set(f"ERROR en {label}: {e}")
                messagebox.showerror("Error al generar", f"No se pudo generar {label}:\n{e}")
        return runner

    def get_params(self):
        try:
            bpm = float(self.bpm_var.get())
        except ValueError:
            bpm = 135.0

        root_str = self.root_var.get().split()[0]
        try:
            root_midi = int(root_str)
        except ValueError:
            root_midi = 46

        kick_style = self.kick_style_var.get().split()[0].lower()
        rush_style = self.rush_style_var.get().split()[0].lower()
        gma_style = self.give_me_acid_style_var.get().split()[0].lower()
        bass_style = self.bass_style_var.get()
        return bpm, root_midi, kick_style, rush_style, gma_style, bass_style

    def gen_selected_bass(self):
        _, _, _, _, _, bass_style = self.get_params()
        lowered = bass_style.lower()
        if "give me acid" in lowered:
            self.gen_bass_give_me_acid()
        elif "rolling" in lowered:
            self.gen_bass_rolling()
        elif "aggressive" in lowered:
            self.gen_bass_aggressive()
        elif "blade" in lowered:
            self.gen_bass_blade()
        elif "rush" in lowered:
            self.gen_bass_rush()

    def gen_bass_give_me_acid(self):
        bpm, root_midi, _, _, gma_style, _ = self.get_params()
        if gma_style == "all":
            pack = generate_all_give_me_acid_variations(bpm=bpm, root_note=root_midi)
            self.status_var.set("OK: ¡Pack Give Me Acid generado (4 variaciones)!")
        else:
            out = build_timestamped_filename(give_me_acid_output_stem(gma_style), directory=SCRIPT_DIR / "output")
            paths, notes = generate_bass_acid_give_me_acid(
                bpm=bpm,
                root_note=root_midi,
                style=gma_style,
                output_path=out
            )
            self.status_var.set(f"OK: Generado Give Me Acid '{out.name}' ({notes} notas - {gma_style})")

    def gen_bass_rolling(self):
        bpm, root_midi, _, _, _, _ = self.get_params()
        out = build_timestamped_filename(BASS_ROLLING_STEM, directory=SCRIPT_DIR / "output")
        paths, notes = generate_bass_acid(bpm=bpm, root_note=root_midi, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({notes} notas)")

    def gen_bass_aggressive(self):
        bpm, root_midi, _, _, _, _ = self.get_params()
        out = build_timestamped_filename(BASS_AGGRESSIVE_STEM, directory=SCRIPT_DIR / "output")
        paths, notes = generate_bass_acid_aggressive(bpm=bpm, root_note=root_midi, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({notes} notas)")

    def gen_bass_blade(self):
        bpm, root_midi, _, _, _, _ = self.get_params()
        out = build_timestamped_filename(BASS_BLADE_STEM, directory=SCRIPT_DIR / "output")
        paths, notes = generate_bass_acid_blade(bpm=bpm, root_note=root_midi, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({notes} notas)")

    def gen_kick(self):
        bpm, _, kick_style, _, _, _ = self.get_params()
        out = build_timestamped_filename(kick_output_stem(kick_style, 4), directory=SCRIPT_DIR / "output")
        paths, mains, ghosts = generate_acid_kick(
            bpm=bpm,
            note=36,
            total_bars=4,
            style=kick_style,
            output_path=out
        )
        self.status_var.set(f"OK: Generado Kick {kick_style.upper()} '{out.name}' ({mains + ghosts} hits)")

    def gen_hats(self):
        bpm, _, _, _, _, _ = self.get_params()
        out = build_timestamped_filename(HAT_STEM, directory=SCRIPT_DIR / "output")
        paths, count = generate_acid_hat(bpm=bpm, note=42, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({count} hits)")

    def gen_bass_rush(self):
        bpm, root_midi, _, rush_style, _, _ = self.get_params()
        if rush_style == "all":
            pack = generate_all_rush_variations(bpm=bpm, root_note=root_midi)
            self.status_var.set("OK: ¡Pack BassAcid Rush generado (4 variaciones)!")
        else:
            out = build_timestamped_filename(rush_output_stem(rush_style), directory=SCRIPT_DIR / "output")
            paths, notes = generate_bass_acid_rush(bpm=bpm, root_note=root_midi, style=rush_style, output_path=out)
            self.status_var.set(f"OK: Generado Rush '{out.name}' ({notes} notas - Estilo {rush_style})")

    def gen_all(self):
        bpm, root_midi, kick_style, rush_style, gma_style, _ = self.get_params()
        out_dir = SCRIPT_DIR / "output"
        ts = get_timestamp_prefix()

        active_gma = "driving_lead" if gma_style == "all" else gma_style
        active_rush = "rolling" if rush_style == "all" else rush_style

        out_gma = build_timestamped_filename(give_me_acid_output_stem(active_gma), directory=out_dir, timestamp=ts)
        out1 = build_timestamped_filename(BASS_ROLLING_STEM, directory=out_dir, timestamp=ts)
        out2 = build_timestamped_filename(BASS_AGGRESSIVE_STEM, directory=out_dir, timestamp=ts)
        out3 = build_timestamped_filename(BASS_BLADE_STEM, directory=out_dir, timestamp=ts)
        out4 = build_timestamped_filename(kick_output_stem(kick_style, 4), directory=out_dir, timestamp=ts)
        out5 = build_timestamped_filename(HAT_STEM, directory=out_dir, timestamp=ts)
        out6 = build_timestamped_filename(rush_output_stem(active_rush), directory=out_dir, timestamp=ts)

        generate_bass_acid_give_me_acid(bpm=bpm, root_note=root_midi, style=active_gma, output_path=out_gma)
        generate_bass_acid(bpm=bpm, root_note=root_midi, output_path=out1)
        generate_bass_acid_aggressive(bpm=bpm, root_note=root_midi, output_path=out2)
        generate_bass_acid_blade(bpm=bpm, root_note=root_midi, output_path=out3)
        generate_acid_kick(bpm=bpm, note=36, total_bars=4, style=kick_style, output_path=out4)
        generate_acid_hat(bpm=bpm, note=42, output_path=out5)
        generate_bass_acid_rush(bpm=bpm, root_note=root_midi, style=active_rush, output_path=out6)

        self.status_var.set(f"OK: ¡Kit completo (7 pistas con Give Me Acid y Rush) generado con prefijo {ts}!")

    def open_bitwig_folder(self):
        try:
            self.clips_dir_path.mkdir(parents=True, exist_ok=True)
            open_folder(self.clips_dir_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")


if __name__ == "__main__":
    app = AcidGeneratorGUI()
    app.mainloop()
