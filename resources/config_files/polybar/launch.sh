#!/bin/bash

# Terminate already running bar instances
# If all your bars have ipc enabled, you can use
polybar-msg cmd quit
# Otherwise you can use the nuclear option:
killall -q polybar

if type "xrandr"; then
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
