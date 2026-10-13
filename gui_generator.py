#!/usr/bin/env python3
"""
gui_generator.py - Interfaz gráfica de escritorio para generar secuencias MIDI Acid para Bitwig Studio.
Permite generar con un solo clic patrones de bajo 303, agresivo, pre-drop, bombos y hi-hats.
Soporta selección y configuración de carpeta de Clips multiplataforma (macOS, Linux y Windows).
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
from BassAcid import generate_bass_acid
from BassAcid_Aggressive import generate_bass_acid_aggressive
from BassAcid_PreDrop import generate_bass_acid_predrop
from BassAcid_Rush import generate_bass_acid_rush, generate_all_rush_variations, RUSH_STYLES
from acid_kick_pattern import generate_acid_kick
from acid_hat_pattern import generate_acid_hat


class AcidGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.os_name = get_current_os()
        self.os_display = get_os_display_name(self.os_name)

        self.title(f"Bitwig Acid MIDI Generator [{self.os_display}] - by DanimanX (155 BPM)")
        self.geometry("680x670")
        self.minsize(640, 620)
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

        main_frame = tk.Frame(self, bg="#1E1E1E", padx=20, pady=12)
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

        # 2. Controles de Parámetros Globales
        params_frame = tk.LabelFrame(
            main_frame,
            text=" Configuración Global ",
            bg="#282828",
            fg="#FF6600",
            font=("Helvetica", 9, "bold"),
            padx=12,
            pady=8
        )
        params_frame.pack(fill="x", pady=(0, 12))

        # BPM
        tk.Label(params_frame, text="Tempo (BPM):", bg="#282828", fg="#E0E0E0").grid(row=0, column=0, sticky="w", pady=4)
        self.bpm_var = tk.StringVar(value="155.0")
        bpm_entry = tk.Entry(params_frame, textvariable=self.bpm_var, width=8, bg="#333333", fg="#FFFFFF", insertbackground="#FFFFFF")
        bpm_entry.grid(row=0, column=1, sticky="w", padx=10, pady=4)

        # Nota Raíz
        tk.Label(params_frame, text="Nota Raíz (Tónica):", bg="#282828", fg="#E0E0E0").grid(row=0, column=2, sticky="w", pady=4)
        self.root_var = tk.StringVar(value="50 (D3 / Re)")
        root_combo = ttk.Combobox(
            params_frame,
            textvariable=self.root_var,
            values=["53 (F3 / Fa - Rush)", "50 (D3 / Re)", "38 (D2)", "48 (C3)", "45 (A2)", "43 (G2)"],
            width=18,
            state="readonly"
        )
        root_combo.grid(row=0, column=3, sticky="w", padx=10, pady=4)

        # Estilo de Kick Hard Techno
        tk.Label(params_frame, text="Variación Kick Hard Techno:", bg="#282828", fg="#E0E0E0").grid(row=1, column=0, sticky="w", pady=4)
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
            width=28,
            state="readonly"
        )
        kick_style_combo.grid(row=1, column=1, columnspan=3, sticky="w", padx=10, pady=4)

        # Estilo de BassAcid Rush (KI/KI 1:17:04)
        tk.Label(params_frame, text="Estilo Bass Rush (KI/KI 1:17:04):", bg="#282828", fg="#E0E0E0").grid(row=2, column=0, sticky="w", pady=4)
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
            width=28,
            state="readonly"
        )
        rush_style_combo.grid(row=2, column=1, columnspan=3, sticky="w", padx=10, pady=4)

        # 3. Botones Generadores Individuales
        gens_frame = tk.LabelFrame(
            main_frame,
            text=" Generar Patrones Individuales ",
            bg="#282828",
            fg="#FF6600",
            font=("Helvetica", 9, "bold"),
            padx=12,
            pady=8
        )
        gens_frame.pack(fill="both", expand=True, pady=(0, 12))

        btn_style = {
            "bg": "#383838",
            "fg": "#FFFFFF",
            "activebackground": "#505050",
            "activeforeground": "#FFFFFF",
            "font": ("Helvetica", 9, "bold"),
            "bd": 1,
            "relief": "raised"
        }

        # Bass 303 Rolling
        b1_btn = tk.Button(gens_frame, text="▶ BassAcid (Rolling 303)", **btn_style, command=self._safe(self.gen_bass_rolling, "BassAcid Rolling 303"))
        b1_btn.grid(row=0, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="4 compases con slides legato y acentos", bg="#282828", fg="#AAAAAA").grid(row=0, column=1, sticky="w", padx=8)

        # Bass Aggressive
        b2_btn = tk.Button(gens_frame, text="▶ BassAcid (Aggressive Marie Vaunt)", **btn_style, command=self._safe(self.gen_bass_aggressive, "BassAcid Aggressive"))
        b2_btn.grid(row=1, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="Frigio/Tritono, screeches agudos de octava", bg="#282828", fg="#AAAAAA").grid(row=1, column=1, sticky="w", padx=8)

        # Bass PreDrop
        b3_btn = tk.Button(gens_frame, text="▶ BassAcid (PreDrop & Silencio)", **btn_style, command=self._safe(self.gen_bass_predrop, "BassAcid PreDrop"))
        b3_btn.grid(row=2, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="Build-up, riser, ametralladora + silencio 2 beats", bg="#282828", fg="#AAAAAA").grid(row=2, column=1, sticky="w", padx=8)

        # Kick
        k_btn = tk.Button(gens_frame, text="▶ Acid Kick (4x4 Rumble)", **btn_style, command=self._safe(self.gen_kick, "Acid Kick"))
        k_btn.grid(row=3, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="Bombo 4x4, ghost kicks para rumble y redoble", bg="#282828", fg="#AAAAAA").grid(row=3, column=1, sticky="w", padx=8)

        # Hi-Hats
        h_btn = tk.Button(gens_frame, text="▶ Acid Hi-Hats (Rave 16ths)", **btn_style, command=self._safe(self.gen_hats, "Acid Hi-Hats"))
        h_btn.grid(row=4, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="Contratiempos abiertos + galope semicorcheas", bg="#282828", fg="#AAAAAA").grid(row=4, column=1, sticky="w", padx=8)

        # Bass Rush (KI/KI 1:17:04 Style)
        b4_btn = tk.Button(gens_frame, text="▶ BassAcid Rush (KI/KI 1:17:04)", **btn_style, command=self._safe(self.gen_bass_rush, "BassAcid Rush"))
        b4_btn.grid(row=5, column=0, sticky="ew", padx=4, pady=3)
        tk.Label(gens_frame, text="Estilo Aeryeen 'Rush', 4 variaciones (Rolling/Hook/Scream/Drop)", bg="#282828", fg="#AAAAAA").grid(row=5, column=1, sticky="w", padx=8)

        gens_frame.grid_columnconfigure(0, weight=1)

        # 4. Botón Maestro y Explorador
        bottom_frame = tk.Frame(main_frame, bg="#1E1E1E")
        bottom_frame.pack(fill="x")

        all_btn = tk.Button(
            bottom_frame,
            text="★ GENERAR KIT COMPLETO (TODOS) ★",
            bg="#FF6600",
            fg="#FFFFFF",
            activebackground="#FF8533",
            font=("Helvetica", 11, "bold"),
            bd=2,
            pady=6,
            command=self._safe(self.gen_all, "Kit completo")
        )
        all_btn.pack(fill="x", pady=(0, 8))

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
            bpm = 155.0

        root_str = self.root_var.get().split()[0]
        try:
            root_midi = int(root_str)
        except ValueError:
            root_midi = 50

        kick_style = self.kick_style_var.get().split()[0].lower()
        rush_style = self.rush_style_var.get().split()[0].lower()
        return bpm, root_midi, kick_style, rush_style

    def gen_bass_rolling(self):
        bpm, root_midi, _, _ = self.get_params()
        out = build_timestamped_filename("01_BassAcid_Rolling_303.mid", directory=SCRIPT_DIR / "output")
        paths, notes = generate_bass_acid(bpm=bpm, root_note=root_midi, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({notes} notas)")

    def gen_bass_aggressive(self):
        bpm, root_midi, _, _ = self.get_params()
        out = build_timestamped_filename("02_BassAcid_Aggressive.mid", directory=SCRIPT_DIR / "output")
        paths, notes = generate_bass_acid_aggressive(bpm=bpm, root_note=root_midi, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({notes} notas)")

    def gen_bass_predrop(self):
        bpm, root_midi, _, _ = self.get_params()
        out = build_timestamped_filename("03_BassAcid_PreDrop_Build.mid", directory=SCRIPT_DIR / "output")
        paths, notes = generate_bass_acid_predrop(bpm=bpm, root_note=root_midi, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({notes} notas)")

    def gen_kick(self):
        bpm, _, kick_style, _ = self.get_params()
        out = build_timestamped_filename(f"04_Acid_Kick_{kick_style.capitalize()}_4x4.mid", directory=SCRIPT_DIR / "output")
        paths, mains, ghosts = generate_acid_kick(
            bpm=bpm,
            note=36,
            total_bars=4,
            style=kick_style,
            output_path=out
        )
        self.status_var.set(f"OK: Generado Kick {kick_style.upper()} '{out.name}' ({mains + ghosts} hits)")

    def gen_hats(self):
        bpm, _, _, _ = self.get_params()
        out = build_timestamped_filename("05_Acid_HiHat_Rave.mid", directory=SCRIPT_DIR / "output")
        paths, count = generate_acid_hat(bpm=bpm, note=42, output_path=out)
        self.status_var.set(f"OK: Generado '{out.name}' ({count} hits)")

    def gen_bass_rush(self):
        bpm, root_midi, _, rush_style = self.get_params()
        if rush_style == "all":
            pack = generate_all_rush_variations(bpm=bpm, root_note=root_midi)
            self.status_var.set(f"OK: ¡Pack BassAcid Rush generado (4 variaciones)!")
        else:
            out = build_timestamped_filename(f"06_BassAcid_Rush_{rush_style.capitalize()}.mid", directory=SCRIPT_DIR / "output")
            paths, notes = generate_bass_acid_rush(bpm=bpm, root_note=root_midi, style=rush_style, output_path=out)
            self.status_var.set(f"OK: Generado Rush '{out.name}' ({notes} notas - Estilo {rush_style})")

    def gen_all(self):
        bpm, root_midi, kick_style, rush_style = self.get_params()
        out_dir = SCRIPT_DIR / "output"
        ts = get_timestamp_prefix()

        out1 = build_timestamped_filename("01_BassAcid_Rolling_303.mid", directory=out_dir, timestamp=ts)
        out2 = build_timestamped_filename("02_BassAcid_Aggressive.mid", directory=out_dir, timestamp=ts)
        out3 = build_timestamped_filename("03_BassAcid_PreDrop_Build.mid", directory=out_dir, timestamp=ts)
        out4 = build_timestamped_filename(f"04_Acid_Kick_{kick_style.capitalize()}_4x4.mid", directory=out_dir, timestamp=ts)
        out5 = build_timestamped_filename("05_Acid_HiHat_Rave.mid", directory=out_dir, timestamp=ts)
        active_rush = "rolling" if rush_style == "all" else rush_style
        out6 = build_timestamped_filename(f"06_BassAcid_Rush_{active_rush.capitalize()}.mid", directory=out_dir, timestamp=ts)

        generate_bass_acid(bpm=bpm, root_note=root_midi, output_path=out1)
        generate_bass_acid_aggressive(bpm=bpm, root_note=root_midi, output_path=out2)
        generate_bass_acid_predrop(bpm=bpm, root_note=root_midi, output_path=out3)
        generate_acid_kick(bpm=bpm, note=36, total_bars=4, style=kick_style, output_path=out4)
        generate_acid_hat(bpm=bpm, note=42, output_path=out5)
        generate_bass_acid_rush(bpm=bpm, root_note=root_midi, style=active_rush, output_path=out6)
        self.status_var.set(f"OK: ¡Kit completo (6 pistas con BassAcid Rush) generado con prefijo {ts}!")

    def open_bitwig_folder(self):
        try:
            self.clips_dir_path.mkdir(parents=True, exist_ok=True)
            open_folder(self.clips_dir_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")


if __name__ == "__main__":
    app = AcidGeneratorGUI()
    app.mainloop()
