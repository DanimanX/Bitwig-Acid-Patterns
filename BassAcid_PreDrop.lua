-- BassAcid_PreDrop.lua
-- Script generador de bajo para Build-up y Pre-Drop (155 BPM, LPB 4, 64 líneas).
-- Crea tensión progresiva (riser, octavas ascendentes, ráfagas retrigger) y remata
-- con un SILENCIO PRE-DROP dramático en los últimos tiempos para que el drop explote con máxima fuerza.
-- Uso: Tools > Scripter > abrir este archivo > F6 (Run).

if rawget(_G, "_ENV") == nil then
  _ENV = setmetatable({}, { __index = _G })
end

local settings = {
  pattern_index           = 2,            -- Índice del patrón donde se colocará el build-up (ej. Patrón 2 o el previo al drop)
  track                   = 3,            -- Track secuenciador para el bajo (BassAcid)
  instrument              = "BassAcid",   -- Nombre del instrumento en el rack
  total_lines             = 64,           -- Longitud del patrón (4 compases de 16 líneas)
  root_note               = 50,           -- D-2 (MIDI 50)
  max_vol                 = 128,          -- Volumen pico al final del build-up
  pre_drop_silence_lines  = 8,            -- Últimas líneas en silencio absoluto (8 líneas = 2 beats completos vacíos)
  enable_retrigger        = true,         -- Aplicar efecto de repetición rápida (0Rxx) en el clímax
  glide_speed             = 24,           -- Velocidad de slide (0G18 en hex)
}

-- Inicializar generador aleatorio
math.randomseed(os.time())

local current_song = renoise.song()

-- 1. Validar existencia del patrón
local patterns_count = #current_song.patterns
if settings.pattern_index < 1 or settings.pattern_index > patterns_count then
  renoise.app():show_error(string.format("Pattern index %d no existe (Total en proyecto: %d). Ajusta 'settings.pattern_index'.", settings.pattern_index, patterns_count))
  return
end

local pattern = current_song:pattern(settings.pattern_index)
if pattern == nil then
  renoise.app():show_error("No se pudo cargar el patrón en el índice: " .. tostring(settings.pattern_index))
  return
end

-- 2. Buscar el instrumento en el rack
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

-- Función auxiliar para escribir una nota con propiedades
local function set_bass(line_num, note_val, vol, fx_cmd, fx_val)
  if line_num > settings.total_lines then return end
  local line = pattern_track:line(line_num)
  local col = line:note_column(1)
  local fx_col = line:effect_column(1)

  col.note_value = math.max(0, math.min(119, note_val))
  col.instrument_value = inst_val_0_based
  col.volume_value = math.max(0, math.min(128, vol))

  if fx_cmd and fx_val then
    fx_col.number_string = fx_cmd
    fx_col.amount_value = fx_val
  end
end

local function set_off(line_num)
  if line_num > settings.total_lines then return end
  local line = pattern_track:line(line_num)
  line:note_column(1).note_value = renoise.PatternTrackLine.NOTE_OFF
end

-- ============================================================================
-- ESTRUCTURA DEL BUILD-UP / PRE-DROP (4 COMPASES = 64 LÍNEAS)
-- ============================================================================

-- COMPÁS 1 (Líneas 1-16): ESPACIO Y TENSIÓN INICIAL (El ritmo se vacía)
-- Notas graves aisladas (tónica y quinta) con pausas largas para desarmar el groove
local bar1_hits = {
  { line = 1,  offset = -12, vol = 80 },  -- D-1 subgrave profundo
  { line = 5,  offset = 0,   vol = 75 },  -- D-2
  { line = 9,  offset = 7,   vol = 85 },  -- A-2
  { line = 13, offset = 6,   vol = 90 },  -- G#2 (disonancia tritono)
}
for _, h in ipairs(bar1_hits) do
  set_bass(h.line, settings.root_note + h.offset, h.vol)
  set_off(h.line + 2) -- Gate corto
end

-- COMPÁS 2 (Líneas 17-32): ENTRADA DEL ROLLING Y PRIMERAS ESCALADAS
-- Empiezan semicorcheas en contratiempos con slides (0G) subiendo de volumen (70 -> 95)
for step = 1, 16 do
  local line = 16 + step
  local is_even = (step % 2 == 0)
  if is_even then
    local vol = math.floor(70 + (step / 16) * 25)
    local offset = (step % 4 == 0) and 12 or 0 -- Saltos a octava D-3
    set_bass(line, settings.root_note + offset, vol, "0G", settings.glide_speed)
  else
    if step % 4 == 1 then
      set_off(line)
    end
  end
end

-- COMPÁS 3 (Líneas 33-48): EL RISER ÁCIDO (Escalada frenética de octavas)
-- Todas las semicorcheas activas, subiendo de tono hacia los agudos con volumen creciente (95 -> 120)
local scale_up = { 0, 1, 3, 5, 6, 7, 10, 12, 13, 15, 17, 18, 19, 22, 24, 25 }
for step = 1, 16 do
  local line = 32 + step
  local vol = math.floor(95 + (step / 16) * 25)
  local offset = scale_up[step] or 24 -- Escalando hasta D-4 agudo
  -- Alternar entre slide 0G y acentos cortantes
  local fx = (step % 2 == 0) and "0G" or nil
  local fx_val = fx and settings.glide_speed or nil
  set_bass(line, settings.root_note + offset, vol, fx, fx_val)
end

-- COMPÁS 4 (Líneas 49-64): CLÍMAX DE AMETRALLADORA + SILENCIO PRE-DROP
-- Líneas 49 a 56: Ráfaga máxima de tensión a 128 con Retrigger (0R) en octava aguda
local cutoff_line = settings.total_lines - settings.pre_drop_silence_lines -- Línea 56

for line = 49, cutoff_line do
  -- Ráfaga rápida en D-4 con efecto 0R12 (retrigger cada 2 ticks) para simular ametralladora 303
  local fx_cmd = settings.enable_retrigger and "0R" or "0G"
  local fx_val = settings.enable_retrigger and 18 or 12 -- 0R12 = retrigger veloz
  set_bass(line, settings.root_note + 24, settings.max_vol, fx_cmd, fx_val)
end

-- LÍNEAS PRE-DROP (Por defecto 57 a 64): CORTE Y SILENCIO DRAMÁTICO TOTAL
-- Se coloca un NOTE_OFF en la primera línea de corte y se deja el resto vacío.
set_off(cutoff_line + 1)

renoise.app():show_status(string.format("OK: Pre-Drop Bass generado en Patrón %d (Build-up 1-56, Silencio Pre-Drop 57-64 a 155 BPM)", settings.pattern_index))
