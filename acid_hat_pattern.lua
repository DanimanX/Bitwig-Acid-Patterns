-- acid_hat_pattern.lua
-- Script generador de Hi-Hats estilo Hard Acid Techno / Rave (155 BPM, LPB 4, 64 líneas).
-- Genera contratiempos marcados (offbeats), rolling de semicorcheas con dinámica y redobles.
-- Uso: Tools > Scripter > abrir este archivo > F6 (Run).

if rawget(_G, "_ENV") == nil then
  _ENV = setmetatable({}, { __index = _G })
end

local settings = {
  pattern_index   = 3,                    -- Índice 1-based del patrón
  track           = 2,                    -- Track secuenciador para el Hi-Hat
  instrument      = "DGRS_HTE_HAT_HIT_18",-- Nombre exacto del instrumento en el rack
  note            = "C-4",                -- Tono base para disparar el sample (C-4 es estándar)
  total_lines     = 64,                   -- Longitud total (4 compases de 16 líneas)
  offbeat_vol     = 128,                  -- Volumen máximo para el contratiempo principal (offbeat)
  rolling_vol     = 76,                   -- Volumen base para el galope de semicorcheas
  ghost_vol       = 52,                   -- Volumen para notas fantasma
  enable_rolling  = true,                 -- Activar semicorcheas continuas (drive estilo festival)
  enable_fills    = true,                 -- Activar redobles en compases 2 y 4
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

-- Función auxiliar para insertar un golpe de Hat
local function set_hat(line_index, volume, delay)
  if line_index > settings.total_lines then return end
  local line = pattern_track:line(line_index)
  local col = line:note_column(1)
  col.note_string = settings.note
  col.instrument_value = inst_val_0_based
  col.volume_value = math.max(10, math.min(128, volume))
  if delay and delay > 0 then
    col.delay_value = delay
  end
end

local hits_count = 0

-- 5. Generar patrón rítmico a lo largo de las 64 líneas
for bar = 0, 3 do
  local bar_offset = bar * 16

  for step = 1, 16 do
    local line_num = bar_offset + step
    local is_kick_beat = ((step - 1) % 4 == 0) -- Pasos 1, 5, 9, 13 (encima del Kick)
    local is_offbeat   = ((step - 1) % 4 == 2) -- Pasos 3, 7, 11, 15 (Contratiempo clásico)

    if is_offbeat then
      -- CONTRATIEMPO (Offbeat Hat): El pulso principal que hace bailar el techno
      -- Volumen alto con ligeras micro-variaciones humanas (+/- 4)
      local vol = settings.offbeat_vol - math.random(0, 8)
      set_hat(line_num, vol)
      hits_count = hits_count + 1

    elseif settings.enable_rolling then
      if is_kick_beat then
        -- En el golpe del Kick: a 155 BPM usualmente se deja libre o se mete un ghost muy bajito
        if math.random() > 0.65 then
          set_hat(line_num, settings.ghost_vol + math.random(-6, 6))
          hits_count = hits_count + 1
        end
      else
        -- Pasos intermedios (semicorcheas 2, 4, 6, 8, 10, 12, 14, 16):
        -- Generan el "chugga-chugga" / "rolling drive" veloz
        if math.random() > 0.15 then
          local vol = settings.rolling_vol + math.random(-8, 10)
          -- Micro-delay sutil para dar swing/groove analógico
          local micro_delay = math.random(0, 12)
          set_hat(line_num, vol, micro_delay)
          hits_count = hits_count + 1
        end
      end
    end
  end

  -- Redobles / Fills especiales:
  if settings.enable_fills then
    if bar == 1 then
      -- Final del compás 2 (líneas 31-32): mini redoble rápido
      set_hat(bar_offset + 15, 110)
      set_hat(bar_offset + 16, 125)
    elseif bar == 3 then
      -- Final del compás 4 (líneas 61 a 64): ametralladora de hi-hats creciente
      local fill_lines = {
        { line = bar_offset + 13, vol = 95 },
        { line = bar_offset + 14, vol = 108 },
        { line = bar_offset + 15, vol = 120 },
        { line = bar_offset + 16, vol = 128 },
      }
      for _, f in ipairs(fill_lines) do
        set_hat(f.line, f.vol)
      end
    end
  end
end

renoise.app():show_status(string.format("OK: Hi-Hats generados (%d hits, 155 BPM en Track %d para '%s')", hits_count, settings.track, settings.instrument))
