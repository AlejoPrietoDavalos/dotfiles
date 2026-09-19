#!/bin/bash
# Estrategia de PARADA de polybar. La contraparte de launch.sh.
# Idempotente: parar algo que no corre no es un error (por eso los `|| true`).

polybar-msg cmd quit >/dev/null 2>&1 || true
killall -q polybar 2>/dev/null || true
exit 0
