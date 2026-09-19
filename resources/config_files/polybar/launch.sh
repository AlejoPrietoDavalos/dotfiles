#!/bin/bash
# Estrategia de ARRANQUE de polybar: una instancia por monitor conectado.
# La parada vive en stop.sh; acá solo se llama para no duplicar instancias.

"$(dirname "$0")/stop.sh"

if command -v xrandr >/dev/null 2>&1; then
    monitors=($(xrandr --query | grep " connected" | cut -d" " -f1))
    # Con 1 solo monitor, bar/single separa el "+" del pad del "1" numérico.
    bar="example"
    [ ${#monitors[@]} -eq 1 ] && bar="single"
    for m in "${monitors[@]}"; do
        MONITOR=$m polybar "$bar" &
    done
else
    polybar --reload example &
fi
