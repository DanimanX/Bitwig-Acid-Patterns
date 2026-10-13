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
```

---

## 🎹 Cómo usar los clips en Bitwig Studio

1. **Abrir Bitwig Studio**.
2. En el panel navegador de la derecha (o presiona `F1` / abre el navegador de archivos):
   - Ve a **"Clips"** o **"My Library"** -> **"Acid_Sequences"**.
3. Verás todos los archivos `.mid` generados:
   - `01_BassAcid_Rolling_303.mid`
   - `02_BassAcid_Aggressive.mid`
   - `03_BassAcid_PreDrop_Build.mid`
   - `04_Acid_Kick_Rumble_4x4.mid`
   - `05_Acid_HiHat_Rave.mid`
4. **Arrastra y suelta** cualquier clip directamente sobre una pista de instrumento en la vista *Arranger* o en el *Clip Launcher*.

> [!TIP]
> **Slides y Acentos 303 en VSTs / Bitwig:**
> - Los **slides** se programan con solapamiento *legato* (>100% de duración de paso). En sintes como *AudioRealism ABL3*, *D16 Phoscyon 2*, *Arturia Acid V*, *Roland TB-303* o el propio *Polymer* de Bitwig (modo mono con Glide activado), esto activa automáticamente el portamento suave entre notas.
> - Los **acentos** se activan por velocidad MIDI (127 para acento, 80 para normal, 54 para notas fantasma).
