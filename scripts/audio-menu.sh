#!/bin/bash

set -euo pipefail

if ! command -v wpctl >/dev/null 2>&1; then
  rofi -e "wpctl no esta instalado (PipeWire)"
  exit 1
fi

if ! command -v rofi >/dev/null 2>&1; then
  notify-send "Audio" "Instala rofi para abrir el menu"
  exit 1
fi

default_id="$(wpctl inspect @DEFAULT_AUDIO_SINK@ 2>/dev/null \
  | sed -n '1s/^id \([0-9]\+\),.*/\1/p')"

# id + descripción de cada salida de audio disponible.
sinks="$(pw-dump | jq -r '
  .[] | select(.type=="PipeWire:Interface:Node")
      | select(.info.props["media.class"]=="Audio/Sink")
      | "\(.id)\t\(.info.props["node.description"] // .info.props["node.name"])"')"
[ -z "$sinks" ] && { rofi -e "No se encontraron salidas de audio"; exit 0; }

menu="$(printf '%s\n' "$sinks" | awk -F'\t' -v def="$default_id" '
{
  active=($1 == def ? "* " : "  ");
  printf "%s%s  [%s]\n", active, $2, $1;
}')"

choice="$(printf '%s\n' "$menu" | rofi -dmenu -i -p "Audio")"
[ -z "$choice" ] && exit 0

sink_id="$(printf '%s\n' "$choice" | sed -E 's/.*\[([0-9]+)\]$/\1/')"

wpctl set-default "$sink_id"

# Mueve los streams que están sonando a la salida elegida (WirePlumber
# recuerda el ruteo por app, con cambiar el default no alcanza).
sink_serial="$(pw-dump | jq -r --argjson id "$sink_id" '
  .[] | select(.id==$id) | .info.props["object.serial"]')"

pw-dump | jq -r '
  .[] | select(.type=="PipeWire:Interface:Node")
      | select(.info.props["media.class"]=="Stream/Output/Audio")
      | .id' \
  | while read -r stream_id; do
      pw-metadata "$stream_id" target.object "$sink_serial" >/dev/null 2>&1 || true
    done

sink_name="$(printf '%s\n' "$sinks" | awk -F'\t' -v id="$sink_id" '$1==id{print $2; exit}')"
command -v notify-send >/dev/null 2>&1 && notify-send "Audio" "Salida: $sink_name"
exit 0
