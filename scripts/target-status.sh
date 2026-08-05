#!/bin/bash
# La máquina objetivo del engagement. Vacío si no hay ninguna seteada.
#
# Se setea con `dot target set <ip>`. Lo escribe FileTargetRepository; el formato es
# `host` o `host<TAB>label`, definido en `Target.to_line()`.
#
# Lo lee bash y no Python a propósito: el módulo poll cada 2s y arrancar un intérprete cada
# vez para leer una línea es tirar CPU.
#
#   (sin argumentos)  `host` o `host (label)`, vacío si no hay
#                     -> eww decide color y ícono por clase CSS, que es donde va
#   --host            solo el host, sin label -> para copiar al portapapeles
#   --polybar         con ícono y color propios de polybar, que no puede componer
#
# La mira SIEMPRE se dibuja, apagada cuando no hay target: deja el lugar reservado y
# recuerda que existe.

set -uo pipefail

TARGET_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/dotfiles/target"
COLOR_TARGET='#D66A56'  # mismo $target que eww.scss — las dos barras, un solo color
COLOR_IDLE='#2C6AA6'    # [colors] foreground-alt

mode="${1:-}"

host=""
label=""
if [ -r "$TARGET_FILE" ]; then
  IFS=$'\t' read -r host label < "$TARGET_FILE" || true
fi

if [ "$mode" = "--host" ]; then
  printf '%s\n' "${host:-}"
  exit 0
fi

if [ -z "${host:-}" ]; then
  [ "$mode" = "--polybar" ] && printf '%%{F%s}%%{F-}\n' "$COLOR_IDLE"
  exit 0
fi

text="$host"
[ -n "${label:-}" ] && text="$host ($label)"

if [ "$mode" = "--polybar" ]; then
  printf '%%{F%s} %s%%{F-}\n' "$COLOR_TARGET" "$text"
else
  printf '%s\n' "$text"
fi
