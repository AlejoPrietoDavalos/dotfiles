#!/bin/bash
# Estrategia de ARRANQUE de eww: un daemon + una ventana por monitor conectado.
#
# Diferencia clave con polybar, que lanza un PROCESO por monitor con `$MONITOR`: eww tiene
# un solo daemon y N ventanas, cada una con su `--id` y el nombre del monitor como
# argumento (lo consume `(defwindow bar [monitor] ...)`).

set -uo pipefail

CONFIG_DIR="$(dirname "$(readlink -f "$0")")"

"$CONFIG_DIR/stop.sh"

# El daemon tiene que estar arriba antes de abrir ventanas.
eww --config "$CONFIG_DIR" daemon >/dev/null 2>&1 || true

# Los monitores se leen de bspwm y NO de xrandr: `apply_monitors.py` ya corrió y fijó el
# orden y los desktops. Preguntarle a xrandr acá podría dar un orden distinto al que la
# barra necesita para mapear sus workspaces.
monitors="$(bspc query -M --names 2>/dev/null)"
if [ -z "$monitors" ]; then
    monitors="$(xrandr --query 2>/dev/null | grep " connected" | cut -d" " -f1)"
fi

for monitor in $monitors; do
    eww --config "$CONFIG_DIR" open bar \
        --id "bar-${monitor}" \
        --arg "monitor=${monitor}" \
        >/dev/null 2>&1 &
done

# "Activate Linux": marca de agua opcional, en todos los monitores.
# Se prende/apaga con un archivo y no con una variable en el config para que sobreviva a
# `dot install-files` — la config se reescribe, el flag no.
#   prender:  touch ~/.config/dotfiles/activate-linux
#   apagar:   rm    ~/.config/dotfiles/activate-linux
if [ -e "${XDG_CONFIG_HOME:-$HOME/.config}/dotfiles/activate-linux" ]; then
    for monitor in $monitors; do
        eww --config "$CONFIG_DIR" open activate-linux \
            --id "activate-linux-${monitor}" \
            --arg "monitor=${monitor}" \
            >/dev/null 2>&1 &
    done
fi

wait
