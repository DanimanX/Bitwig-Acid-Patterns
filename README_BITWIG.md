# Bitwig Studio — Generador de Secuencias MIDI Acid Techno (155 BPM)

Scripts que generan clips `.mid` de bajo ácido, bombo y hi-hats para **Bitwig Studio** (SMF formato 0, 480 PPQ).

Cada script escribe el clip en dos sitios:

1. **`output/`** (local).
2. **Biblioteca de Bitwig** (`.../Library/Clips/Acid_Sequences/`), visible al instante en el navegador lateral (*Clips* → *Acid_Sequences*).

El nombre sigue el formato `YYYYMMDDHHMM_<nombre>.mid`: **un archivo por script**. Si repites dentro del mismo minuto, se sobrescribe.

---

## Scripts

| Script | Genera |
|---|---|
| [`BassAcid_GiveMeAcid.py`](BassAcid_GiveMeAcid.py) | **Give Me Acid (Marie Vaunt & A\*S\*Y\*S @ 135 BPM)**: Peak-Time / Driving Acid Techno. 4 variaciones (`driving_lead`, `call_response`, `squelch_roller`, `climax_drop`), slides 303 legato, afinación en Si♭ (Bb2/46) y acentos con filtro abierto. |
| [`BassAcid.py`](BassAcid.py) | **Rolling 303** clásico: pentatónica menor en Re, huecos en el beat para el kick, acentos y slides. Fill en el compás 4. |
| [`BassAcid_Aggressive.py`](BassAcid_Aggressive.py) | **Hard Acid (Marie Vaunt / Verknipt)**: frigio y tritono, acentos extremos, screams de doble octava (+24) y fill ametralladora. |
| [`BassAcid_Blade.py`](BassAcid_Blade.py) | **Blade (16 notas)**: un compás con 16 semicorcheas sin huecos, al estilo del acid techno de *Blade* (1998) / New Order – "Confusion" (Pump Panel Reconstruction Mix). Acentos en los 4 pulsos, stabs de octava y quinta con slide, espiral ascendente final. |
| [`BassAcid_Rush.py`](BassAcid_Rush.py) | **KI/KI @ Elementenstraat**: 4 variaciones (`rolling`, `melodic_hook`, `octave_screamer`, `climax_drop`), galopes de 16ths y rebotes de octava. |
| [`acid_kick_pattern.py`](acid_kick_pattern.py) | **Kick Hard Techno** de 4 compases: fraseo evolutivo, humanización, ghost/rumble y 6 estilos (ver abajo). |
| [`acid_hat_pattern.py`](acid_hat_pattern.py) | **Hi-Hats Rave**: offbeats abiertos, galope de semicorcheas con swing y redobles en compases 2 y 4. |
| [`generate_all.py`](generate_all.py) | **Generador maestro**: el kit completo de 7 clips de una sola vez. |
| [`gui_generator.py`](gui_generator.py) | **GUI (tkinter)**: selector de estilo de bajo con auto-ajuste de BPM/tónica, botones por patrón, kit completo y carpeta de Clips. |

---

## Uso

**GUI (recomendado)**

```bash
python3 gui_generator.py
```

**Kit completo**

```bash
python3 generate_all.py
python3 generate_all.py --bpm 155 --root 50 --kick-style stutter --variations 3
```

**Patrones individuales**

```bash
python3 BassAcid_GiveMeAcid.py --style all --root Bb2 --bpm 135   # pack de 4 variaciones Give Me Acid
python3 BassAcid.py --bpm 155 --root 50
python3 BassAcid_Aggressive.py --bpm 155 --root 50
python3 BassAcid_Blade.py --bpm 155 --root 50
python3 BassAcid_Rush.py --style all --root F3 --bpm 153    # pack de 4 variaciones
python3 acid_kick_pattern.py --style hybrid --bars 4 --bpm 155
python3 acid_hat_pattern.py --bpm 155 --note 42             # 42 = F#1 closed hat
```

### Estilos de kick (`--kick-style` en el kit / `--style` individual)

- `hybrid` *(default)* — evolución de 4 compases: base, síncopa, tensión máxima y redoble en fusas.
- `rolling` — sub-kick continuo en semicorcheas (rolling bassline).
- `syncopated` — bombos dobles en contratiempos con cross-accents.
- `stutter` — ráfagas de fusas (estilo Verknipt / Klangkuenstler).
- `offbeat_push` — bombos en las corcheas a contratiempo.
- `predrop_break` — compases 1-3 a tope y silencio en los 2 últimos tiempos del compás 4.

---

## Raíz y nomenclatura de notas

`--root` (y `--note`) acepta número MIDI o nombre de nota, con **C4 = 60** (Do central): `50` = `D3` = `D-3`.

La raíz por defecto es **MIDI 50 = D3**, afinada con el kick en Re.

---

## Carpeta de Clips (multiplataforma)

Se resuelve por SO desde [`bitwig_config.json`](bitwig_config.json), sin conflictos al sincronizar entre máquinas:

| SO | Ruta por defecto |
|---|---|
| macOS | `~/Documents/Bitwig Studio/Library/Clips/Acid_Sequences/` |
| Linux | `~/Bitwig Studio/Library/Clips/Acid_Sequences/` (o `~/Documents/...` si existe) |
| Windows | `~/Documents/Bitwig Studio/Library/Clips/Acid_Sequences/` |

Para cambiarla: botón **"Cambiar…"** en la GUI, `python3 generate_all.py --configure`, o `--clips-dir "/ruta"`.

---

## Cómo usar los clips en Bitwig

1. Navegador lateral → **Clips / My Library** → **Acid_Sequences**.
2. Arrastra el `.mid` a una pista de instrumento (*Arranger* o *Clip Launcher*).

> **Slides y acentos 303**
> - **Slides**: se codifican como solapamiento *legato* (>100% del paso). En sintes como ABL3, Phoscyon 2, Arturia Acid V, Roland TB-303 o Polymer (mono + Glide) activan el portamento.
> - **Acentos**: por velocidad MIDI (p. ej. 127 acento, ~80-100 normal, ~54-76 fantasma, según el patrón).

---

## Notas técnicas

- **Dependencias**: solo la librería estándar de Python 3 ([`midi_core.py`](midi_core.py) no importa nada externo); la GUI necesita `tkinter`.
- **Salida MIDI**: SMF formato 0, una pista, 480 PPQ, canal 1 (índice 0).
- **Config perezosa**: importar `midi_core` no lee ni escribe `bitwig_config.json`; la ruta se resuelve al usarla.
- **Aleatoriedad**: los scripts de bajo (`BassAcid.py`, `BassAcid_Aggressive.py`, `BassAcid_Blade.py`, `BassAcid_Rush.py`) generan una variación distinta en cada ejecución y sobrescriben el clip. Usa `--seed <n>` (donde exista) para reproducir una toma concreta.
