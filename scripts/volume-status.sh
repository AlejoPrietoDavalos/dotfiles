#!/bin/bash
# Volumen. Reemplaza a `internal/pulseaudio` de polybar, con el mismo formato de salida
# ("Vol:42%" / "~Mute~") para que la barra se vea igual.

set -uo pipefail

if ! command -v pamixer >/dev/null 2>&1; then
  printf 'Vol:N/A\n'
  exit 0
fi

if [ "$(pamixer --get-mute 2>/dev/null)" = "true" ]; then
  printf '~Mute~\n'
  exit 0
fi

printf 'Vol:%s%%\n' "$(pamixer --get-volume 2>/dev/null || echo 0)"
