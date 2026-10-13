-- BassAcid_Aggressive.lua
-- Script generador de bajo Hard / Aggressive Acid Techno (Estilo Marie Vaunt @ Verknipt).
-- Tempo recomendado: 155 BPM (LPB 4, 64 líneas = 4 compases).
-- Caracterizado por: rolling implacable de semicorcheas, slides agresivos (0G),
-- saltos de doble octava (screeches 303), intervalos frigios/tritono y acentos extremos.
-- Uso: Tools > Scripter > abrir este archivo > F6 (Run).

if rawget(_G, "_ENV") == nil then
  _ENV = setmetatable({}, { __index = _G })
end

local settings = {
  pattern_index   = 4,                    -- Índice 1-based del patrón
  track           = 3,                    -- Track secuenciador para el bajo
  instrument      = "BassAcid",           -- Nombre del instrumento en el rack
  total_lines     = 64,                   -- Longitud del patrón (4 compases de 16 líneas)
  root_note       = 50,                   -- D-2 (MIDI 50, tonalidad Re)
  accent_vol      = 128,                  -- Volumen máximo para acentos (TB-303 Accent al rojo vivo)
  normal_vol      = 80,                   -- Volumen base (mayor contraste con los acentos)
  ghost_vol       = 54,                   -- Volumen para notas fantasma de arrastre
  fast_glide      = 28,                   -- Velocidad de slide estándar (0G1C en hex)
  slow_glide      = 12,                   -- Velocidad de slide largo / desgarrado (0G0C en hex)
}

-- Inicializar generador aleatorio
math.randomseed(os.time())

local current_song = renoise.song()

-- 1. Validar existencia del patrón
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

-- 2. Buscar el índice numérico 0-based del instrumento
local inst_index = nil
local instruments = current_song.instruments
for i = 1, #instruments do
  if instruments[i].name:lower() == settings.instrument:lower() then
    inst_index = i
    break
  end
end

if not inst_index then
  renoise.app():show_error("Instrumento '" .. settings.instrument .. "' no encontrado en el rack.")
  return
end

local inst_val_0_based = inst_index - 1

-- 3. Validar el track
local track = current_song:track(settings.track)
if track == nil then
  renoise.app():show_error("Track secuenciador " .. tostring(settings.track) .. " no encontrado")
  return
end

local pattern_track = pattern:track(settings.track)

-- 4. Limpiar todas las líneas del track antes de escribir
for line_num = 1, settings.total_lines do
  local line = pattern_track:line(line_num)
  line:note_column(1):clear()
  line:effect_column(1):clear()
end

-- Intervalos oscuros y agresivos (D Frigio / Tritono / Octavas punzantes):
-- -12: D-1 (subgrave)
--   0: D-2 (tónica raíz)
--   1: D#2 (tensión frigia brutal)
--   3: F-2 (tercera menor)
--   5: G-2 (cuarta)
--   6: G#2 (tritono / blue note disonante)
--   7: A-2 (quinta justa)
--  12: D-3 (octava alta con punch)
--  13: D#3 (chillido frigio agudo)
--  24: D-4 (chillido de doble octava tipo 303 scream)
local dark_intervals = { -12, 0, 0, 1, 3, 5, 6, 7, 12, 12, 13, 24 }

-- Generador de motivo motriz de 16 semicorcheas agresivo (Marie Vaunt / Verknipt style)
local base_riff = {}
for step = 1, 16 do
  local is_kick_beat = ((step - 1) % 4 == 0) -- Pasos 1, 5, 9, 13
  local is_offbeat   = ((step - 1) % 4 == 2) -- Pasos 3, 7, 11, 15 (contratiempos)

  if is_kick_beat then
    -- En el golpe del kick:
    -- Dejamos que el kick respire con Note-off o metemos una tónica sub muy seca
    if math.random() > 0.35 then
      base_riff[step] = { type = "off" }
    else
      base_riff[step] = {
        type = "note",
        offset = (math.random() > 0.5) and 0 or -12,
        accent = false,
        slide = false,
        vol = settings.normal_vol
      }
    end
  elseif is_offbeat then
    -- Los contratiempos son el ancla energética: notas acentuadas o saltos de octava
    local scream = (math.random() > 0.40)
    base_riff[step] = {
      type = "note",
      offset = scream and 12 or dark_intervals[math.random(#dark_intervals)],
      accent = true,
      slide = scream,
      vol = settings.accent_vol
    }
  else
    -- Rolling 16ths continuas (pasos 2, 4, 6, 8, 10, 12, 14, 16)
    if math.random() > 0.15 then
      local is_acc = (math.random() > 0.70)
      local is_sld = (math.random() > 0.60)
      local offset = dark_intervals[math.random(#dark_intervals)]
      base_riff[step] = {
        type = "note",
        offset = offset,
        accent = is_acc,
        slide = is_sld,
        vol = is_acc and settings.accent_vol or ((math.random() > 0.5) and settings.normal_vol or settings.ghost_vol)
      }
    else
      base_riff[step] = { type = "off" }
    end
  end
end

-- Renderizado de 4 compases (64 líneas) con progresión de ferocidad rave
local total_notes = 0

for bar = 0, 3 do
  local bar_offset = bar * 16

  for step = 1, 16 do
    local current_line_num = bar_offset + step
    local line = pattern_track:line(current_line_num)
    local col = line:note_column(1)
    local fx_col = line:effect_column(1)

    local item = base_riff[step]

    -- Variaciones progresivas según el compás:
    if bar == 1 then
      -- Compás 2: Más slides agudos en contratiempos
      if step == 7 or step == 15 then
        item = { type = "note", offset = 12, accent = true, slide = true, vol = settings.accent_vol }
      end
    elseif bar == 2 then
      -- Compás 3: Subida de tensión con intervalos disonantes (tritono y semitono frigio)
      if step == 3 or step == 11 then
        item = { type = "note", offset = (math.random() > 0.5) and 6 or 1, accent = true, slide = true, vol = settings.accent_vol }
      end
    elseif bar == 3 then
      -- Compás 4: Clímax y fill salvaje tipo ametralladora antes de resolver
      if step >= 9 then
        local fill_offsets = { 0, 12, 13, 24, 12, 6, 1, 0 }
        local fill_idx = (step - 8)
        item = {
          type = "note",
          offset = fill_offsets[fill_idx] or 12,
          accent = true,
          slide = (step % 2 == 0),
          vol = settings.accent_vol
        }
      end
    end

    -- Escribir en Renoise
    if item.type == "note" then
      col.note_value = math.max(0, math.min(119, settings.root_note + item.offset))
      col.instrument_value = inst_val_0_based
      col.volume_value = item.vol or settings.normal_vol

      if item.slide then
        fx_col.number_string = "0G"
        -- Si la nota salta a octavas altas, slide más rápido y cortante
        if item.offset >= 12 then
          fx_col.amount_value = settings.fast_glide
        else
          fx_col.amount_value = settings.slow_glide
        end
      end

      total_notes = total_notes + 1
    elseif item.type == "off" then
      col.note_value = renoise.PatternTrackLine.NOTE_OFF
    end
  end
end

renoise.app():show_status(string.format("OK: Bajo Aggressive Acid (Marie Vaunt style) generado: %d notas, 155 BPM en Track %d", total_notes, settings.track))
