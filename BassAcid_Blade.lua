-- BassAcid_Blade.lua
-- Línea de bajo ácido de 16 notas estilo BLADE (LPB 4, 16 líneas = 1 compás).
-- Referencia: el "Blade-style acid techno" de la escena de apertura de Blade (1998)
-- (New Order - "Confusion" / Pump Panel Reconstruction Mix): 303 dominante, 16
-- semicorcheas sin huecos, acentos duros que clavan con el 4x4 y slides para el squelch.
-- Uso: Tools > Scripter > abrir este archivo > F6 (Run).

if rawget(_G, "_ENV") == nil then
  _ENV = setmetatable({}, { __index = _G })
end

local settings = {
  pattern_index  = 1,          -- Patrón donde se escribirá el bajo
  track          = 3,          -- Track secuenciador para el bajo
  instrument     = "BassAcid", -- Nombre del instrumento en el rack
  root_note      = 50,         -- D-2 (MIDI 50) -> D3 en notación científica
  total_lines    = 16,         -- 16 líneas = 1 compás a LPB 4
  glide_speed    = 24,         -- Velocidad de slide (0G18 en hex)
  accent_vol     = 128,        -- Acento (abre el filtro: squelch)
  normal_vol     = 96,
  ghost_vol      = 64,
}

-- El riff Blade: { linea, offset sobre la raíz, capa, slide }
--   capa: "a" acento | "n" normal | "g" ghost ; slide = true -> efecto 0G (glide)
local motif = {
  {  1,   0, "a", false }, -- pulso 1: martillo sobre la tónica
  {  2,   0, "g", false },
  {  3,  12, "a", true  }, -- octava con slide -> linea 4
  {  4,   0, "g", false },
  {  5,   0, "a", false }, -- pulso 2
  {  6,   0, "g", false },
  {  7,   7, "a", true  }, -- quinta con slide -> linea 8
  {  8,   0, "g", false },
  {  9,   0, "a", false }, -- pulso 3
  { 10,  12, "n", false }, -- octava
  { 11,   0, "g", false },
  { 12,   7, "a", true  }, -- quinta con slide -> linea 13
  { 13,   0, "a", false }, -- pulso 4
  { 14,   3, "a", true  }, -- espiral ascendente: 3ª menor
  { 15,   6, "a", true  }, -- ... tritono
  { 16,  12, "a", true  }, -- ... octava -> slide al compás siguiente
}

local layer_vol = {
  a = settings.accent_vol,
  n = settings.normal_vol,
  g = settings.ghost_vol,
}

-- Inicializar generador aleatorio (el patrón es determinista; no se usa azar)
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

-- ============================================================================
-- ESCRITURA DEL PATRÓN (16 NOTAS, UNA POR LÍNEA)
-- ============================================================================
for _, hit in ipairs(motif) do
  local line_num = hit[1]
  local offset = hit[2]
  local layer = hit[3]
  local slide = hit[4]

  local vol = layer_vol[layer] or settings.normal_vol
  local fx_cmd = slide and "0G" or nil
  local fx_val = slide and settings.glide_speed or nil

  set_bass(line_num, settings.root_note + offset, vol, fx_cmd, fx_val)
end

renoise.app():show_status(string.format("OK: BassAcid Blade (16 notas) generado en Patrón %d, Track %d", settings.pattern_index, settings.track))
