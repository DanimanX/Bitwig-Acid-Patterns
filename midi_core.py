#!/usr/bin/env python3
"""
midi_core.py - Motor independiente de generación MIDI para Bitwig Studio.
No requiere dependencias externas (usa exclusivamente la librería estándar de Python).
Soporta detección y configuración multiplataforma de carpetas de Clips (macOS, Linux y Windows).
"""

import os
import sys
import json
import struct
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Union

# Constantes estándar de tiempo MIDI (PPQ = 480)
PPQ = 480                  # Pulsos por negra (quarter note)
TICKS_PER_BAR = PPQ * 4     # 1920 ticks en compás de 4/4
TICKS_PER_16TH = PPQ // 4   # 120 ticks por semicorchea
TICKS_PER_32ND = PPQ // 8   # 60 ticks por fusa
TICKS_PER_64TH = PPQ // 16  # 30 ticks por semifusa

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "bitwig_config.json"


def get_current_os() -> str:
    """Retorna el identificador normalizado del sistema operativo: 'darwin', 'linux' o 'windows'."""
    p = platform.system().lower()
    if "darwin" in p or "mac" in p:
        return "darwin"
    elif "windows" in p or sys.platform.startswith("win"):
        return "windows"
    return "linux"


def get_os_display_name(os_name: Optional[str] = None) -> str:
    """Retorna un nombre legible para el sistema operativo."""
    os_name = os_name or get_current_os()
    mapping = {
        "darwin": "macOS",
        "linux": "Linux",
        "windows": "Windows"
    }
    return mapping.get(os_name, os_name.capitalize())


def get_default_clips_dir_for_os(os_name: Optional[str] = None) -> Path:
    """
    Retorna la ruta predeterminada de Bitwig Clips según el sistema operativo:
    - macOS: ~/Documents/Bitwig Studio/Library/Clips/Acid_Sequences
    - Linux: ~/Bitwig Studio/Library/Clips/Acid_Sequences (o ~/Documents si existe)
    - Windows: ~/Documents/Bitwig Studio/Library/Clips/Acid_Sequences
    """
    os_name = os_name or get_current_os()
    home = Path.home()

    if os_name == "darwin":
        # En macOS, Bitwig almacena los datos de usuario en Documents/Bitwig Studio
        doc_candidate = home / "Documents" / "Bitwig Studio" / "Library" / "Clips" / "Acid_Sequences"
        return doc_candidate

    elif os_name == "linux":
        # En Linux, Bitwig suele residir directamente en ~/Bitwig Studio
        std_candidate = home / "Bitwig Studio" / "Library" / "Clips" / "Acid_Sequences"
        doc_candidate = home / "Documents" / "Bitwig Studio" / "Library" / "Clips" / "Acid_Sequences"
        if doc_candidate.parent.exists() and not std_candidate.parent.exists():
            return doc_candidate
        return std_candidate

    else:
        # Windows
        return home / "Documents" / "Bitwig Studio" / "Library" / "Clips" / "Acid_Sequences"


def load_bitwig_config() -> dict:
    """Carga la configuración desde bitwig_config.json si existe."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Aviso] No se pudo leer {CONFIG_FILE.name}: {e}")
    return {}


def save_bitwig_config(config: dict):
    """Guarda la configuración en bitwig_config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Aviso] No se pudo guardar {CONFIG_FILE.name}: {e}")


def get_bitwig_library_dir(interactive: bool = False, force_prompt: bool = False) -> Path:
    """
    Obtiene la ruta activa de Clips para el sistema operativo en uso.
    1. Respeta la variable de entorno BITWIG_CLIPS_DIR si está definida.
    2. Consulta bitwig_config.json para el SO actual.
    3. Si force_prompt=True o (interactive=True y la ruta no fue confirmada), pregunta al usuario.
    4. Usa la ruta sugerida por omisión para ese SO.
    """
    # 1. Variable de entorno
    env_dir = os.environ.get("BITWIG_CLIPS_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    current_os = get_current_os()
    config = load_bitwig_config()
    os_config = config.get(current_os, {})

    saved_path_str = os_config.get("clips_dir")
    is_confirmed = os_config.get("confirmed", False)

    default_path = get_default_clips_dir_for_os(current_os)
    active_path = Path(saved_path_str).expanduser() if saved_path_str else default_path

    # Preguntar si se fuerza o si se ejecuta interactivamente sin confirmar
    if force_prompt or (interactive and not is_confirmed and sys.stdin.isatty()):
        active_path = prompt_and_configure_clips_dir(current_os, active_path)
    elif not saved_path_str:
        # Guardar valor por omisión para el SO actual
        set_bitwig_library_dir(default_path, os_name=current_os, confirmed=True)

    return active_path


def set_bitwig_library_dir(new_path: Union[str, Path], os_name: Optional[str] = None, confirmed: bool = True):
    """Guarda la ruta de Clips para un sistema operativo específico en bitwig_config.json."""
    os_name = os_name or get_current_os()
    path_obj = Path(new_path).expanduser()

    # Si es ruta dentro del HOME del usuario, guardar con ~ para portabilidad entre usuarios
    try:
        rel_home = path_obj.relative_to(Path.home())
        path_str = f"~/{rel_home}"
    except ValueError:
        path_str = str(path_obj)

    config = load_bitwig_config()
    config[os_name] = {
        "clips_dir": path_str,
        "confirmed": confirmed
    }
    save_bitwig_config(config)


def prompt_and_configure_clips_dir(os_name: Optional[str] = None, current_suggestion: Optional[Path] = None) -> Path:
    """Pregunta interactivamente en terminal la ruta de Clips según el sistema operativo."""
    os_name = os_name or get_current_os()
    os_display = get_os_display_name(os_name)
    suggested = current_suggestion or get_default_clips_dir_for_os(os_name)

    print("\n" + "=" * 65)
    print(f"  CONFIGURACIÓN DE CARPETA BITWIG CLIPS - [{os_display}]")
    print("=" * 65)
    print(f"Sistema operativo detectado: {os_display} ({os_name})")
    print(f"Ruta recomendada/actual:    {suggested}")
    print("\nOpciones:")
    print("  [Enter]  Confirmar y usar la ruta recomendada")
    print("  [Ruta]   Ingresar una ruta personalizada completa")
    print("-" * 65)

    try:
        user_input = input("Selecciona o ingresa la ruta de clips: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nManteniendo ruta predeterminada.")
        user_input = ""

    chosen_path = Path(user_input).expanduser() if user_input else suggested
    set_bitwig_library_dir(chosen_path, os_name=os_name, confirmed=True)
    print(f"✔ Guardado para {os_display}: {chosen_path}\n")
    return chosen_path


def open_folder(path: Union[str, Path]):
    """Abre la carpeta en el explorador de archivos nativo según el SO (Finder en Mac, Nautilus en Linux, etc.)."""
    p = Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    os_name = get_current_os()

    try:
        if os_name == "darwin":
            subprocess.Popen(["open", str(p)])
        elif os_name == "windows":
            # os.startfile solo existe en Windows; se resuelve en tiempo de ejecución
            opener = getattr(os, "startfile", None)
            if opener is None:
                raise RuntimeError("os.startfile no está disponible en esta plataforma")
            opener(str(p))
        else:
            # Linux y BSD
            subprocess.Popen(["xdg-open", str(p)])
    except Exception as e:
        print(f"[Aviso] No se pudo abrir el explorador de archivos: {e}")


# Compatibilidad hacia atrás: BITWIG_LIBRARY_DIR se resuelve de forma perezosa
# (PEP 562). Importar el módulo NO lee ni escribe bitwig_config.json; la ruta se
# calcula solo cuando se accede al atributo.
def __getattr__(name: str):
    if name == "BITWIG_LIBRARY_DIR":
        return get_bitwig_library_dir()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def get_timestamp_prefix() -> str:
    """Retorna un prefijo de fecha y hora en formato YYYYMMDDHHMM_"""
    return datetime.now().strftime("%Y%m%d%H%M_")


def build_timestamped_filename(
    base_name: str,
    directory: Optional[Union[str, Path]] = None,
    timestamp: Optional[str] = None
) -> Path:
    """
    Construye la ruta de salida con el formato `YYYYMMDDHHMM_<nombre>.mid`.

    Un script produce UN único archivo por ejecución: si ya existe un archivo con ese mismo
    timestamp, se sobrescribe. No se añaden sufijos (_1, _2, ...) porque romperían el formato
    de nombre fecha + nombre del fichero generado.
    """
    if timestamp is None:
        timestamp = get_timestamp_prefix()
    elif not timestamp.endswith("_"):
        timestamp += "_"

    clean_name = base_name if base_name.endswith(".mid") else f"{base_name}.mid"
    dir_path = Path(directory) if directory else Path(".")
    dir_path.mkdir(parents=True, exist_ok=True)

    return dir_path / f"{timestamp}{clean_name}"


def encode_vlq(value: int) -> bytes:
    """Codifica un entero a Variable-Length Quantity (VLQ) del estándar MIDI."""
    buf = bytearray()
    buf.append(value & 0x7F)
    value >>= 7
    while value > 0:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    buf.reverse()
    return bytes(buf)


def note_name_to_midi(val: Union[str, int]) -> int:
    """
    Convierte una nota o un número MIDI a entero (0-127).

    Acepta:
      - Entero o cadena numérica: 50, "50" -> 50.
      - Notación científica (MIDI estándar, C4 = 60): "D3", "C4", "F#3", "Bb2".
      - La misma notación con guion separador (estilo tracker): "D-3", "C-4".

    La octava usa SIEMPRE la numeración científica (C4 = 60). Por tanto la raíz
    habitual de estos generadores, MIDI 50, se escribe "D3" (o "D-3").
    """
    if isinstance(val, int):
        return max(0, min(127, val))

    s = str(val).strip().upper()

    # Cadena numérica directa (p. ej. "50")
    if s.lstrip("+-").isdigit():
        return max(0, min(127, int(s)))

    notes = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3,
             "E": 4, "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8,
             "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11}

    # El guion es solo un separador opcional entre nota y octava ("D-3" == "D3")
    name = "".join(ch for ch in s if ch.isalpha() or ch == "#")
    octave_str = "".join(ch for ch in s if ch.isdigit())

    if name in notes and octave_str:
        octave = int(octave_str)
        # MIDI estándar: C4 = 60
        return max(0, min(127, (octave + 1) * 12 + notes[name]))

    raise ValueError(f"Formato de nota desconocido: {val}")


class MidiTrack:
    """Representa una pista MIDI y acumula eventos."""

    def __init__(self, name: str = "Acid Track"):
        self.name = name
        self.events: List[Tuple[int, bytes]] = []

    def add_meta(self, tick: int, meta_type: int, data: bytes):
        payload = bytes([0xFF, meta_type]) + encode_vlq(len(data)) + data
        self.events.append((tick, payload))

    def set_track_name(self, name: str):
        self.add_meta(0, 0x03, name.encode("utf-8", errors="ignore"))

    def set_tempo(self, tick: int, bpm: float):
        us_per_beat = int(round(60_000_000 / bpm))
        data = us_per_beat.to_bytes(3, "big")
        self.add_meta(tick, 0x51, data)

    def set_time_signature(self, tick: int, numerator: int = 4, denominator: int = 4):
        # Denominador expresado como potencia de 2: 4/4 -> nn=4, dd=2
        dd_pow = 2 if denominator == 4 else (1 if denominator == 2 else 3)
        self.add_meta(tick, 0x58, bytes([numerator, dd_pow, 24, 8]))

    def add_note(self, tick: int, duration_ticks: int, note: int, velocity: int, channel: int = 0):
        """Inserta un par Note-On y Note-Off."""
        ch = channel & 0x0F
        note = max(0, min(127, int(note)))
        velocity = max(1, min(127, int(velocity)))

        note_on = bytes([0x90 | ch, note, velocity])
        note_off = bytes([0x80 | ch, note, 0])

        self.events.append((tick, note_on))
        self.events.append((tick + duration_ticks, note_off))

    def build_track_chunk(self) -> bytes:
        def sort_key(item):
            tick, data = item
            priority = 0
            if data.startswith(b"\xff"):
                priority = -2
            elif (data[0] & 0xF0) == 0x80:
                priority = -1
            return (tick, priority)

        sorted_events = sorted(self.events, key=sort_key)
        track_bytes = bytearray()
        last_tick = 0

        for tick, data in sorted_events:
            delta = tick - last_tick
            last_tick = tick
            track_bytes.extend(encode_vlq(delta))
            track_bytes.extend(data)

        track_bytes.extend(encode_vlq(0) + b"\xff\x2f\x00")
        return b"MTrk" + struct.pack(">I", len(track_bytes)) + bytes(track_bytes)


class MidiSequence:
    """Contenedor de secuencia MIDI (SMF formato 0, una sola pista) listo para exportar."""

    def __init__(self, name: str = "Acid Sequence", bpm: float = 155.0):
        self.name = name
        self.bpm = bpm
        self.track = MidiTrack(name)
        self.track.set_track_name(name)
        self.track.set_tempo(0, bpm)
        self.track.set_time_signature(0, 4, 4)

    def save(self, filepath: Union[str, Path], copy_to_bitwig: bool = True, custom_bitwig_dir: Optional[Union[str, Path]] = None) -> List[Path]:
        """
        Guarda el archivo .mid localmente y opcionalmente en la carpeta de biblioteca de Bitwig.
        Retorna la lista de rutas generadas.
        """
        path = Path(filepath).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        track_data = self.track.build_track_chunk()
        header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ)
        midi_bytes = header + track_data

        with open(path, "wb") as f:
            f.write(midi_bytes)

        saved_paths = [path]

        if copy_to_bitwig:
            try:
                target_dir = Path(custom_bitwig_dir).expanduser().resolve() if custom_bitwig_dir else get_bitwig_library_dir()
                target_dir.mkdir(parents=True, exist_ok=True)
                bw_path = target_dir / path.name
                with open(bw_path, "wb") as f:
                    f.write(midi_bytes)
                saved_paths.append(bw_path)
            except Exception as e:
                print(f"[Aviso] No se pudo copiar a Bitwig Library ({target_dir}): {e}")

        return saved_paths


if __name__ == "__main__":
    # Permite ejecutar `python3 midi_core.py` o `python3 midi_core.py --configure`
    prompt_and_configure_clips_dir()
