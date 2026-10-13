-- BassAcid.lua
-- Script generador de línea de bajo estilo Hard Acid / Rolling 303 (155 BPM, LPB 4, 64 líneas).
-- Diseñado para interactuar con el Kick 4x4 y crear un groove hipnótico con slides y acentos.
-- Uso: Tools > Scripter > abrir este archivo > F6 (Run).

if rawget(_G, "_ENV") == nil then
  _ENV = setmetatable({}, { __index = _G })
end

local settings = {
  pattern_index   = 2,                    -- Índice 1-based del patrón
  track           = 3,                    -- Track secuenciador para el bajo
  instrument      = "BassAcid",           -- Nombre del instrumento en el rack
  total_lines     = 64,                   -- Longitud del patrón (4 compases de 16 líneas)
  root_note       = 50,                   -- D-2 (MIDI 50), afinado con el Kick en D
  accent_vol      = 128,                  -- Volumen máximo para notas con acento (TB-303 Accent)
  normal_vol      = 84,                   -- Volumen estándar para notas base
  glide_amount    = 24,                   -- Velocidad de slide (0G18 en hex)
}

-- Inicializar generador aleatorio
math.randomseed(os.time())

local current_song = renoise.song()

-- Verificar que el patrón exista
local patterns_count = #current_song.patterns
if settings.pattern_index < 1 or settings.pattern_index > patterns_count then
  renoise.app():show_error("Pattern index " .. tostring(settings.pattern_index) .. " no existe (Total: " .. tostring(patterns_count) .. ")")
  return
end

local pattern = current_song:pattern(settings.pattern_index)
if pattern == nil then
  renoise.app():show_error("No se pudo cargar el patrón en el índice: " .. tostring(settings.pattern_index))
  return
end

-- Buscar el índice numérico 0-based del instrumento "BassAcid"
local inst_index = nil
local instruments = current_song.instruments
for i = 1, #instruments do
  if instruments[i].name:lower() == settings.instrument:lower() then
    inst_index = i
    break
  end
end

if not inst_index then
  renoise.app():show_error("Instrumento '" .. settings.instrument .. "' no encontrado. Asegúrate de nombrarlo así en el rack.")
  return
end

local inst_val_0_based = inst_index - 1

local track = current_song:track(settings.track)
if track == nil then
  renoise.app():show_error("Track secuenciador " .. tostring(settings.track) .. " no encontrado")
  return
end

local pattern_track = pattern:track(settings.track)

-- Limpiar las 64 líneas del track antes de escribir
for line_num = 1, settings.total_lines do
  local line = pattern_track:line(line_num)
  line:note_column(1):clear()
  line:effect_column(1):clear()
end

-- Escala: D Minor Pentatonic / Acid Box (D-1, D-2, F-2, G-2, G#-2, A-2, C-3, D-3)
local scale_intervals = { -12, 0, 0, 3, 5, 6, 7, 10, 12, 15 }

-- Generar una frase motriz hipnótica de 16 semicorcheas (1 compás base)
-- Cada paso tiene: { note_offset, is_accent, is_slide, is_gate }
local base_riff = {}
for step = 1, 16 do
  local is_kick_beat = ((step - 1) % 4 == 0) -- Pasos 1, 5, 9, 13 (golpe fuerte de kick)
  
  if is_kick_beat then
    -- En el golpe del Kick: 75% silencio/off para dejar pegar el bombo, o nota corta
    if math.random() > 0.25 then
      base_riff[step] = { type = "off" }
    else
      base_riff[step] = {
        type = "note",
        offset = 0, -- Tónica raíz corta
        accent = false,
        slide = false,
      }
    end
  else
    -- En contratiempos y rolling 16ths: alta actividad rítmica
    local r = math.random()
    if r > 0.20 then
      local note_off = scale_intervals[math.random(#scale_intervals)]
      local is_acc = (math.random() > 0.65)
      local is_sld = (math.random() > 0.70)
      base_riff[step] = {
        type = "note",
        offset = note_off,
        accent = is_acc,
        slide = is_sld,
      }
    else
      base_riff[step] = { type = "off" }
    end
  end
end

-- Renderizar los 4 compases (64 líneas) con evolución musical
local notes_placed = 0

for bar = 0, 3 do
  local bar_offset = bar * 16
  
  for step = 1, 16 do
    local current_line_num = bar_offset + step
    local line = pattern_track:line(current_line_num)
    local col = line:note_column(1)
    local fx_col = line:effect_column(1)
    
    local item = base_riff[step]
    
    -- Compás 4: Modificar hacia el final para crear fill / redoble de bajo
    if bar == 3 and step >= 9 then
      -- Fill activo en las últimas semicorcheas
      if math.random() > 0.25 then
        item = {
          type = "note",
          offset = (step % 2 == 0) and 12 or scale_intervals[math.random(#scale_intervals)],
          accent = (step >= 13),
          slide = (step % 3 == 0),
        }
      end
    end
    
    if item.type == "note" then
      col.note_value = math.max(0, math.min(119, settings.root_note + item.offset))
      col.instrument_value = inst_val_0_based
      col.volume_value = item.accent and settings.accent_vol or settings.normal_vol
      
      -- Si tiene slide, aplicar comando 0G (Portamento)
      if item.slide then
        fx_col.number_string = "0G"
        fx_col.amount_value = settings.glide_amount
      end
      
      notes_placed = notes_placed + 1
    elseif item.type == "off" then
      -- Note-Off para cerrar el decay y definir el golpe
      col.note_value = renoise.PatternTrackLine.NOTE_OFF
    end
  end
end

renoise.app():show_status(string.format("OK: Bajo Rolling Acid generado (%d notas, articulación 303 en Track %d)", notes_placed, settings.track))
