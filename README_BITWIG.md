# Bitwig Studio - Generador de Secuencias MIDI Acid Techno (155 BPM)

Este conjunto de scripts replica y extiende la lógica algorítmica de los scripts de Renoise (`.lua`) para **Bitwig Studio**, generando secuencias estándar `.mid` de 4 compases (64 semicorcheas).

Los archivos se exportan automáticamente en dos lugares:
1. **Localmente**: En la carpeta `output/`.
2. **Biblioteca de Bitwig**: En la carpeta de Clips de Bitwig según tu sistema operativo (`macOS`, `Linux` o `Windows`), accesibles al instante desde el navegador lateral de Bitwig (Pestaña *Clips* o *My Library* -> *Acid_Sequences*).

---

## 🌍 Detección Multiplataforma Inteligente (macOS vs Linux)

El proyecto detecta automáticamente el sistema operativo y gestiona las rutas correspondientes en [bitwig_config.json](bitwig_config.json) sin conflictos (incluso al sincronizar con Insync / Google Drive entre varias máquinas):

| Sistema Operativo | Ruta por Defecto de Bitwig Clips |
|---|---|
| **macOS (Mac)** | `~/Documents/Bitwig Studio/Library/Clips/Acid_Sequences/` |
| **Linux** | `~/Bitwig Studio/Library/Clips/Acid_Sequences/` *(o `~/Documents/...` si existe)* |
| **Windows** | `~/Documents/Bitwig Studio/Library/Clips/Acid_Sequences/` |

### ¿Cómo cambiar o confirmar la carpeta de Clips?
- **Desde la interfaz gráfica:** Abre `python3 gui_generator.py` y haz clic en el botón **"Cambiar..."**.
- **Desde la terminal:** Ejecuta `python3 generate_all.py --configure` (o `python3 midi_core.py`) para confirmar o ingresar una ruta personalizada.
- **Por parámetro directo:** `python3 generate_all.py --clips-dir "/tu/ruta/personalizada"`.

---

## 🎛️ Scripts Disponibles

| Script Python | Script Renoise Original | Descripción / Características |
|---|---|---|
| [`BassAcid.py`](BassAcid.py) | `BassAcid.lua` | **Rolling 303 clásico**: Escala pentatónica menor en Re, huecos en el beat para dejar pegar el Kick, acentos de volumen y slides (legato overlap). Fill en el compás 4. |
| [`BassAcid_Aggressive.py`](BassAcid_Aggressive.py) | `BassAcid_Aggressive.lua` | **Hard Acid estilo Marie Vaunt / Verknipt**: Intervalos frigios y de tritono, acentos extremos (127 vs 80 vs 54), screeches de doble octava (+24 semitonos) y fill ametralladora. |
| [`BassAcid_PreDrop.py`](BassAcid_PreDrop.py) | `BassAcid_PreDrop.lua` | **Build-up & Pre-Drop**: Tensión espaciada en compás 1, rolling en compás 2, riser ascendente de 2 octavas en compás 3, ráfaga ametralladora en compás 4 y **silencio absoluto en los últimos 2 tiempos** antes del drop. |
| [`acid_kick_pattern.py`](acid_kick_pattern.py) | `acid_kick_pattern.lua` | **Hard Techno Kick Dinámico (4 compases)**: Fraseo evolutivo de 4 compases, micro-humanización (timing y velocity), ghost/rumble notes y 6 estilos de Hard Techno (`hybrid`, `rolling`, `syncopated`, `stutter`, `offbeat_push`, `predrop_break`). |
| [`acid_hat_pattern.py`](acid_hat_pattern.py) | `acid_hat_pattern.lua` | **Hi-Hats Rave / Festival**: Contratiempos abiertos potentes (offbeats), galope de semicorcheas con micro-delay analógico (swing) y redobles en compases 2 y 4. |
| [`generate_all.py`](generate_all.py) | — | **Generador Maestro**: Genera el kit completo de los 5 patrones de una sola vez o con múltiples variaciones. |
| [`gui_generator.py`](gui_generator.py) | — | **Interfaz Gráfica de Escritorio**: Ventana interactiva con selector de SO, botón de cambio de carpeta y ajuste de BPM / tono. |

---

## 🎼 Nomenclatura de Notas y Parámetro `--root`

El parámetro `--root` (y `--note` en los patrones de bombo/hi-hat) acepta tres formatos, siempre con la **numeración científica de octavas (Do central C4 = 60, estándar MIDI)**:

| Formato | Ejemplo | Resultado MIDI |
|---|---|---|
| Número MIDI | `--root 50` | 50 |
| Nota (notación científica) | `--root D3` | 50 |
| Nota con guion (estilo tracker) | `--root D-3` | 50 |

La raíz por defecto, **MIDI 50 = D3**, coincide con el Kick afinado en Re.

> [!IMPORTANT]
> Los nombres de nota usan **C4 = 60** (Do central). Por tanto `D3` (y `D-3`) = MIDI 50, mientras que `D-2` = MIDI 38. Los scripts `.lua` originales rotulaban MIDI 50 como "D-2" bajo otra convención de octavas (C3 = 60); aquí se unificó a la numeración estándar MIDI.

---

## 🚀 Modos de Uso

### 1. Interfaz Gráfica (Recomendado)
Para abrir la ventana gráfica interactiva:
```bash
python3 gui_generator.py
```
Haz clic en cualquier botón o en **"GENERAR KIT COMPLETO"** para crear las secuencias. Puedes abrir la carpeta de Clips en Finder o tu explorador de archivos con el botón inferior.

---

### 2. Generar el Kit Completo por Terminal
```bash
python3 generate_all.py
```
O con parámetros personalizados y estilo de bombo:
```bash
python3 generate_all.py --bpm 155 --root 50 --kick-style stutter --variations 3
```

Reconfigurar la carpeta de Clips:
```bash
python3 generate_all.py --configure
```

---

### 3. Variaciones de Kick Hard Techno Disponibles

| Estilo | Flag | Descripción Musical |
|---|---|---|
| **Híbrido Evolutivo** *(default)* | `--style hybrid` | Progresión completa de 4 compases: base sólida (compás 1), síncopa en semicorchea 6 (compás 2), máxima tensión (compás 3) y redoble ametralladora en fusas (*32nd notes*) en compás 4. |
| **Rolling Rumble** | `--style rolling` | Sub-kick continuo en semicorcheas (pasos 2, 3 y 4 de cada tiempo) con velocidades escalonadas para el clásico efecto *rolling bassline*. |
| **Síncopa Industrial** | `--style syncopated` | Dobles golpes de bombo en contratiempos (pasos 6 y 14) con cross-accents en compases pares. |
| **Schranz Stutter** | `--style stutter` | Ráfagas de fusas ultra rápidas (ráfagas ametralladora de 4 notas en *32nd notes*) en compases 2 y 4 (estilo *Verknipt / Klangkuenstler*). |
| **Offbeat Push** | `--style offbeat_push` | Bombos contundentes en las corcheas a contratiempo (pasos 2, 6, 10, 14) que empujan el groove hacia adelante. |
| **Pre-Drop Break** | `--style predrop_break` | Compases 1 al 3 a máxima potencia y compás 4 con **silencio absoluto en los últimos 2 tiempos** antes del drop. |

---

### 4. Generar Patrones Individuales

```bash
# Bajo 303 Rolling
python3 BassAcid.py --bpm 155 --root 50

# Bajo Agresivo
python3 BassAcid_Aggressive.py --bpm 155 --root 50

# Pre-Drop con silencio
python3 BassAcid_PreDrop.py --bpm 155 --root 50

# Kick Hard Techno dinámico (Estilo híbrido por defecto, 4 compases)
python3 acid_kick_pattern.py --style hybrid --bars 4 --bpm 155

# Kick con Rumble continuo (Rolling)
python3 acid_kick_pattern.py --style rolling --bars 4

# Kick con ráfagas Schranz / Stutter (fusas / semicorcheas rápidas)
python3 acid_kick_pattern.py --style stutter --bars 4

# Kick Sincopado o con contratiempos pesados (Offbeat Push)
python3 acid_kick_pattern.py --style syncopated --bars 4
python3 acid_kick_pattern.py --style offbeat_push --bars 4

# Kick de Pre-Drop (silencio en compás 4 antes del drop)
python3 acid_kick_pattern.py --style predrop_break --bars 4

# Hi-Hats (Nota 42 = F#1 Closed Hat)
python3 acid_hat_pattern.py --bpm 155 --note 42

# La raíz admite número MIDI o nombre de nota (D3 y D-3 equivalen a MIDI 50)
python3 BassAcid.py --bpm 155 --root D3
```

---

## 🎹 Cómo usar los clips en Bitwig Studio

1. **Abrir Bitwig Studio**.
2. En el panel navegador de la derecha (o presiona `F1` / abre el navegador de archivos):
   - Ve a **"Clips"** o **"My Library"** -> **"Acid_Sequences"**.
3. Verás todos los archivos `.mid` generados (con prefijo de fecha/hora `YYYYMMDDHHMM_`):
   - `01_BassAcid_Rolling_303.mid`
   - `02_BassAcid_Aggressive.mid`
   - `03_BassAcid_PreDrop_Build.mid`
   - `04_Acid_Kick_<Estilo>_4x4.mid` (p. ej. `04_Acid_Kick_Hybrid_4x4.mid`; el estilo depende de `--kick-style`)
   - `05_Acid_HiHat_Rave.mid`
4. **Arrastra y suelta** cualquier clip directamente sobre una pista de instrumento en la vista *Arranger* o en el *Clip Launcher*.

> [!TIP]
> **Slides y Acentos 303 en VSTs / Bitwig:**
> - Los **slides** se programan con solapamiento *legato* (>100% de duración de paso). En sintes como *AudioRealism ABL3*, *D16 Phoscyon 2*, *Arturia Acid V*, *Roland TB-303* o el propio *Polymer* de Bitwig (modo mono con Glide activado), esto activa automáticamente el portamento suave entre notas.
> - Los **acentos** se activan por velocidad MIDI (127 para acento, 80 para normal, 54 para notas fantasma).

---

## 🔧 Notas Técnicas y Cambios Recientes

**Dependencias:** solo la biblioteca estándar de Python 3. El motor [`midi_core.py`](midi_core.py) no importa nada externo; la GUI requiere `tkinter` (incluido en la mayoría de instalaciones de Python).

**Características del motor MIDI:**
- Escribe **SMF formato 0** (una sola pista) a 480 PPQ, en el **canal 1** (índice MIDI 0) — compatible con Bitwig y con drum machines.
- Los **slides** 303 se codifican como solapamiento *legato* (>100% de duración de paso); los **acentos**, vía velocidad MIDI.
- Nombres de archivo con prefijo `YYYYMMDDHHMM_`; ante colisión dentro del mismo minuto añade un contador incremental (`..._1.mid`, `..._2.mid`) para no sobreescribir.

**Cambios aplicados:**
- `note_name_to_midi` ahora acepta **cadenas numéricas** (`"50"`) y el **guion como separador** (`"D-3"`); las entradas inválidas lanzan `ValueError` con mensaje claro.
- Importar `midi_core` **ya no lee ni escribe** `bitwig_config.json` (la ruta de Clips se resuelve de forma perezosa).
- La GUI captura los errores de generación y los muestra en un diálogo y en la barra de estado.
- Se eliminó código sin uso (pitch bend no utilizado, ramas inalcanzables y imports sin uso).
