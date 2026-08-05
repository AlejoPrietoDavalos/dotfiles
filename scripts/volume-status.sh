#!/bin/bash
# Volumen. Reemplaza a `internal/pulseaudio` de polybar, con el mismo formato de salida
# ("Vol:42%" / "~Mute~") para que la barra se vea igual.
#
# MODO `--watch`: emite una línea cada vez que el volumen CAMBIA, hasta que lo maten. Es el
# que usa eww.
#
#   Como `defpoll` cada 1s, mover la ruedita de volumen tardaba en promedio medio segundo en
#   verse: medido, p50 400 ms y picos de 1 s. No es que eww dibuje lento — es que nadie le
#   avisaba y la barra esperaba a que le tocara preguntar. Un dato que cambia por una acción
#   TUYA tiene que verse instantáneo o se siente roto.
#
#   PulseAudio publica los cambios: `pactl subscribe` emite una línea por evento, 28 ms
#   después de mover el volumen (medido). Escuchar en vez de preguntar es más rápido Y más
#   barato: corre cuando pasa algo, no 86.400 veces por día.
#
# polybar sigue usando el modo de una sola corrida (su `custom/script` con `interval`), así
# que la salida por default no cambia.

set -uo pipefail

estado() {
  if ! command -v pamixer >/dev/null 2>&1; then
    printf 'Vol:N/A\n'
    return
  fi

  if [ "$(pamixer --get-mute 2>/dev/null)" = "true" ]; then
    printf '~Mute~\n'
    return
  fi

  printf 'Vol:%s%%\n' "$(pamixer --get-volume 2>/dev/null || echo 0)"
}

vigilar() {
  if ! command -v pactl >/dev/null 2>&1; then
    # Sin pactl no hay a qué suscribirse. Se degrada a un poll interno en vez de morir: la
    # barra sigue mostrando el volumen, tarde pero lo muestra.
    while :; do
      estado
      sleep 1
    done
    return
  fi

  local ultimo
  ultimo="$(estado)"
  printf '%s\n' "$ultimo"

  # Solo eventos de `sink`, `source` y `server`. Los de `client` NO: pactl emite uno por cada
  # invocación de pamixer —incluidas las de este mismo script y las de volume.sh—, así que
  # escucharlos sería reaccionar al propio ruido.
  #
  # `while read` en vez de leer el archivo entero: pactl empuja eventos y nunca termina.
  pactl subscribe 2>/dev/null | while IFS= read -r evento; do
    case "$evento" in
      *"on sink"* | *"on source"* | *"on server"*) ;;
      *) continue ;;
    esac

    # Un solo paso de la ruedita dispara varios eventos (el sink, la card, el server). Sin
    # este filtro la barra recibiría la misma línea tres veces por cada paso.
    actual="$(estado)"
    if [ "$actual" != "$ultimo" ]; then
      ultimo="$actual"
      printf '%s\n' "$actual"
    fi
  done
}

if [ "${1:-}" = "--watch" ]; then
  vigilar
else
  estado
fi
