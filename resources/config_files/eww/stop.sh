#!/bin/bash
# Estrategia de PARADA de eww. Idempotente.
#
# `eww kill` baja el daemon y con él todas las ventanas — no hace falta cerrarlas una por
# una. El `pkill` es la red por si el daemon quedó zombie y no responde al socket.

CONFIG_DIR="$(dirname "$(readlink -f "$0")")"

eww --config "$CONFIG_DIR" kill >/dev/null 2>&1 || true
pkill -x eww >/dev/null 2>&1 || true
exit 0
