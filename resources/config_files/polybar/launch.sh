#!/bin/bash
# Estrategia de ARRANQUE de polybar: una instancia por monitor conectado.
# La parada vive en stop.sh; acá solo se llama para no duplicar instancias.

"$(dirname "$0")/stop.sh"

if command -v xrandr >/dev/null 2>&1; then
    for m in $(xrandr --query | grep " connected" | cut -d" " -f1); do
        MONITOR=$m polybar example &
    done
else
    polybar --reload example &
fi
