#!/bin/bash
# Estado de red para la barra (polybar y eww comparten este script).
#
# SALIDA (siempre UNA línea, siempre en stdout):
#   LAN        ethernet conectada
#   ▂▄▆█       wifi conectada, con la intensidad de señal
#   OFF        sin conexión
#   ERR        nmcli no está instalado
#   NM!        nmcli falló  ← algo está roto, mirá el log
#   ...!       el sufijo `!` avisa que nmcli escribió warnings
#
# POR QUÉ ASÍ: la barra captura stderr ADEMÁS de stdout, así que un warning de nmcli se
# dibuja encima del indicador. Pasó de verdad tras un `pacman -Syu`: nmcli (nuevo) avisa
# que no coincide con el daemon NetworkManager (viejo, aún en memoria) y ese texto tapaba
# la señal hasta reiniciar.
#
# Pero MANDAR stderr a /dev/null es peor: si NetworkManager se cae, nmcli falla, el script
# llega al final y muestra `OFF` — indistinguible de "no hay wifi". Un problema real
# disfrazado de estado normal, que es como los problemas sobreviven meses.
#
# Entonces: stderr va al LOG (no a la barra), y lo que la barra muestra distingue los tres
# casos — anda / no hay red / está roto.

set -uo pipefail

REPO="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
LOG="$REPO/logs/network-status.err"

mkdir -p "$(dirname "$LOG")"
# Se TRUNCA en cada corrida: el módulo corre cada 3s, y un log que solo crece llenaría el
# disco en días. Siempre queda el stderr de la última ejecución, que es el que importa.
: >"$LOG"

# Sufijo `!` si nmcli dejó algo en stderr. La barra sigue mostrando el valor real —el
# warning de versiones no impide leer la señal—, pero deja de ser invisible.
warn_suffix() {
  [ -s "$LOG" ] && printf '!'
}

nm() {
  nmcli "$@" 2>>"$LOG"
}

if ! command -v nmcli >/dev/null 2>&1; then
  printf 'ERR\n'
  exit 0
fi

# El estado se captura UNA vez y se consulta en memoria: así se distingue "nmcli falló"
# de "nmcli anduvo pero no hay nada conectado", que con un pipe directo a grep se
# confunden (los dos dan exit != 0).
if ! dev_status="$(nm -t -f TYPE,STATE dev status)"; then
  printf 'NM!\n'
  exit 0
fi

if grep -q '^ethernet:connected$' <<<"$dev_status"; then
  printf 'LAN%s\n' "$(warn_suffix)"
  exit 0
fi

if grep -q '^wifi:connected$' <<<"$dev_status"; then
  signal="$(nm -t -f IN-USE,SIGNAL dev wifi list | awk -F: '$1=="*"{print $2; exit}')"
  signal="${signal:-0}"

  if [ "$signal" -ge 75 ]; then
    bars='▂▄▆█'
  elif [ "$signal" -ge 50 ]; then
    bars='▂▄▆_'
  elif [ "$signal" -ge 25 ]; then
    bars='▂▄__'
  else
    bars='▂___'
  fi

  printf '%s%s\n' "$bars" "$(warn_suffix)"
  exit 0
fi

printf 'OFF%s\n' "$(warn_suffix)"
