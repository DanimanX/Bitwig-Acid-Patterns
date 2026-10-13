 -- acid_kick_pattern.lua
-- Patrón de kick estilo Hard Acid / Rolling Rumble (155 BPM, LPB 4, 64 líneas).
-- Genera bombo 4x4 sólido, ghost kicks para el rumble y redoble al final.
-- Uso: Tools > Scripter > abrir este archivo > F6 (Run).

if rawget(_G, "_ENV") == nil then
  _ENV = setmetatable({}, { __index = _G })
end

local settings = {
  pattern_index   = 2,                    -- Índice 1-based del patrón
  track           = 1,                    -- Track secuenciador (Kick)
  instrument      = "DGRS_HTE_KICK_HIT_12",
  note            = "D-4",                -- Nota principal del kick
  total_lines     = 64,                   -- Longitud total (4 compases de 16 líneas)
  main_vol        = 128,                  -- 0x80 (Volumen completo del golpe principal)
  ghost_vol       = 58,                   -- Volumen atenuado para ghost kicks / rumble
  enable_ghosts   = true,                 -- Activar ghost kicks sutiles para el groove rolling
  enable_fill     = true,                 -- Activar redoble de variación en el compás final (líneas 49-64)
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

-- Buscar el índice numérico 0-based del instrumento
local inst_index = nil
local instruments = current_song.instruments
for i = 1, #instruments do
  if instruments[i].name:lower() == settings.instrument:lower() then
    inst_index = i
    break
  end
end

if not inst_index then
  renoise.app():show_error("Instrumento '" .. settings.instrument .. "' no encontrado")
  return
end

local inst_val_0_based = inst_index - 1

local track = current_song:track(settings.track)
if track == nil then
  renoise.app():show_error("Track secuenciador " .. tostring(settings.track) .. " no encontrado")
  return
end

local pattern_track = pattern:track(settings.track)

-- Limpiar todas las líneas del track primero
for line_num = 1, settings.total_lines do
  local line = pattern_track:line(line_num)
  line:note_column(1):clear()
  line:effect_column(1):clear()
end

local main_hits = 0
local ghost_hits = 0

-- Función auxiliar para escribir un kick
local function set_kick(line_index, volume)
  if line_index > settings.total_lines then return end
  local line = pattern_track:line(line_index)
  local col = line:note_column(1)
  col.note_string = settings.note
  col.instrument_value = inst_val_0_based
  col.volume_value = volume
end

-- 1. Escribir Kicks principales 4-on-the-floor (cada 4 líneas: 1, 5, 9, 13...)
for line_num = 1, settings.total_lines, 4 do
  set_kick(line_num, settings.main_vol)
  main_hits = main_hits + 1
end

-- 2. Añadir Ghost Kicks para crear el empuje "Rolling Rumble"
if settings.ghosts_enabled or settings.enable_ghosts then
  for bar = 0, 3 do
    local bar_start = bar * 16
    -- No saturar el compás final si hay fill
    if not (settings.enable_fill and bar == 3) then
      -- Ghost kicks en la semicorchea previa al beat (líneas 4, 8, 12, 16)
      local rumble_lines = { bar_start + 4, bar_start + 8, bar_start + 12, bar_start + 16 }
      for _, l in ipairs(rumble_lines) do
        if math.random() > 0.25 and l <= settings.total_lines then
          local vol_variation = settings.ghost_vol + math.random(-6, 8)
          set_kick(l, math.max(30, math.min(85, vol_variation)))
          ghost_hits = ghost_hits + 1
        end
      end
    end
  end
end

-- 3. Redoble / Fill al final del ciclo (Compás 4: líneas 49 a 64)
if settings.enable_fill then
  -- Construir aceleración rítmica hacia el final
  local fill_pattern = {
    { line = 57, vol = 128 },
    { line = 59, vol = 95 },
    { line = 61, vol = 110 },
    { line = 62, vol = 118 },
    { line = 63, vol = 125 },
    { line = 64, vol = 128 },
  }
  for _, hit in ipairs(fill_pattern) do
    set_kick(hit.line, hit.vol)
  end
end

renoise.app():show_status(string.format("OK: Kick Hard Acid generado (4x4: %d, Ghosts/Rumble: %d hits a 155 BPM)", main_hits, ghost_hits))
