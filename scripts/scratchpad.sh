#!/bin/bash
#===========================================================================
# Scratchpad / terminal desplegable para bspwm.
#
# bspwm no tiene scratchpad nativo: se emula con una ventana flotante `sticky`
# a la que se le prende/apaga el flag `hidden`. La regla que la deja flotante y
# pegada a todos los desktops del monitor está en bspwmrc (clase "scratchpad").
#
# Uso (desde sxhkd):
#   super + grave         -> toggle: muestra/oculta la terminal scratchpad
#                            SIEMPRE en el monitor que tiene el foco
#                            (la notebook o la pantalla grande, la que mires).
#
# La primera vez la crea; después sólo la muestra u oculta. Como es `sticky`,
# la misma instancia te sigue entre la notebook y el monitor grande.
#===========================================================================
set -euo pipefail

CLASS="scratchpad"
TERM_CMD=(kitty --class "$CLASS")

# ¿Ya existe la ventana? (xdotool encuentra también las ocultas/no mapeadas)
wid="$(xdotool search --classname "$CLASS" 2>/dev/null | head -n1 || true)"

if [ -z "$wid" ]; then
    # No existe: la creamos. La regla de bspwm la pone flotante/sticky.
    "${TERM_CMD[@]}" &
    exit 0
fi

# xdotool devuelve el id en decimal; bspc usa el id en hexadecimal (0x...).
node="$(printf '0x%08x' "$wid")"

if [ -n "$(bspc query -N -n "${node}.hidden" 2>/dev/null)" ]; then
    # Está oculta: traerla al monitor con foco, mostrarla y enfocarla.
    bspc node "$node" --to-monitor focused --flag hidden=off --focus
else
    # Está visible: ocultarla.
    bspc node "$node" --flag hidden=on
fi
