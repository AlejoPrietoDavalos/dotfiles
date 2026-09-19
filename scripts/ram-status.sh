#!/bin/bash
# Uso de RAM en porcentaje. Reemplaza a `internal/memory` de polybar.
# Se usa MemAvailable (no MemFree): MemFree ignora cache/buffers reclamables y da un
# número alarmista que no refleja la memoria realmente disponible.

set -euo pipefail

read -r total available < <(
  awk '/^MemTotal:/{t=$2} /^MemAvailable:/{a=$2} END{print t, a}' /proc/meminfo
)

[ "${total:-0}" -gt 0 ] || { printf 'RAM N/A\n'; exit 0; }

printf 'RAM %3d%%\n' $(( (total - available) * 100 / total ))
