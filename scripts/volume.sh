#!/bin/bash

DELTA_VOLUME=5

# Sinks que están recibiendo audio ahora mismo (streams activos), uno por línea.
# Si no hay nada sonando, devuelve vacío y se usa el sink por defecto.
get_playing_sinks() {
    pw-dump 2>/dev/null | jq -r '
      ([ .[] | select(.type=="PipeWire:Interface:Node")
         | {key: (.id|tostring), value: (.info.props["media.class"] // "")} ] | from_entries) as $cls
      | [ .[] | select(.type=="PipeWire:Interface:Link")
          | select($cls[.info["output-node-id"]|tostring] == "Stream/Output/Audio")
          | select($cls[.info["input-node-id"]|tostring] == "Audio/Sink")
          | .info["input-node-id"] ]
      | unique | .[]' 2>/dev/null
}

# Si el sink que está sonando no es el default, lo hace default. Así polybar
# (internal/pulseaudio sigue al default) muestra el volumen que realmente cambia,
# y las apps nuevas salen por donde ya está sonando el audio.
sync_default_sink() {
    local sink="$1" default_id
    default_id="$(wpctl inspect @DEFAULT_AUDIO_SINK@ 2>/dev/null \
        | sed -n '1s/^id \([0-9]\+\),.*/\1/p')"
    if [ -n "$sink" ] && [ "$sink" != "$default_id" ]; then
        wpctl set-default "$sink"
    fi
}

run_with_wpctl() {
    local sinks=""
    if command -v pw-dump >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
        sinks="$(get_playing_sinks)"
    fi
    if [ -n "$sinks" ]; then
        sync_default_sink "$(echo "$sinks" | head -n1)"
    fi
    sinks="${sinks:-@DEFAULT_AUDIO_SINK@}"
    local sink
    for sink in $sinks; do
        case "$1" in
            mute) wpctl set-mute "$sink" toggle ;;
            decrease) wpctl set-volume "$sink" "${DELTA_VOLUME}%-" ;;
            increase) wpctl set-volume -l 1.0 "$sink" "${DELTA_VOLUME}%+" ;;
            *) echo "Comando no reconocido: $1"; return 1 ;;
        esac
    done
}

run_with_pamixer() {
    case "$1" in
        mute) pamixer --toggle-mute ;;
        decrease) pamixer --decrease "$DELTA_VOLUME" ;;
        increase) pamixer --increase "$DELTA_VOLUME" ;;
        *) echo "Comando no reconocido: $1"; return 1 ;;
    esac
}

# wpctl primero: permite apuntar al sink que está sonando (ej: auris bluetooth
# cuando el default sigue siendo los parlantes). pamixer solo maneja el default.
if command -v wpctl >/dev/null 2>&1; then
    run_with_wpctl "$1"
elif command -v pamixer >/dev/null 2>&1; then
    run_with_pamixer "$1"
else
    echo "No se encontro ni 'wpctl' ni 'pamixer' para controlar volumen."
    exit 1
fi
