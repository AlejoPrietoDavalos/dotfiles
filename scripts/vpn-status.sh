#!/bin/bash
# IP de tu interfaz de VPN — la que ven los targets. Vacío si no hay VPN levantada.
#
# Es EL dato que más se pega durante un engagement: reverse shells, payloads de SSRF,
# listeners. Tenerla en la barra evita el `ip a | grep tun0` cincuenta veces por máquina.
#
# Sin salida (no "N/A") cuando no hay VPN: así el MISMO script sirve en la máquina de todos
# los días y en la VM de ataque, sin ninguna condición por máquina. Donde no hay VPN, el
# módulo simplemente no se ve.
#
#   (sin argumentos)  la IP sola  -> la consume eww, que le pone el ícono por CSS
#   --polybar         con ícono   -> polybar no puede componer, necesita el string armado

set -uo pipefail

for iface in tun0 tun1 tun2 wg0; do
  address="$(ip -4 addr show "$iface" 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1)"
  [ -n "$address" ] || continue
  if [ "${1:-}" = "--polybar" ]; then
    printf ' %s\n' "$address"
  else
    printf '%s\n' "$address"
  fi
  exit 0
done

exit 0
