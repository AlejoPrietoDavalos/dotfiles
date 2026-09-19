#!/usr/bin/env python3
"""Elige uno de los tres íconos de la barra, al azar, una vez por sesión.

Son los mismos tres que la polybar mostraba SIEMPRE los tres a la vez (módulos `python`,
`arch` y `linux`). Acá se muestra uno solo y rota en cada arranque: ocupa menos, y el que
salga es el que hace de botón para desplegar RAM/GPU/CPU.

Se llama desde un `defpoll` de intervalo largo, así que en la práctica se sortea al
arrancar el daemon y no vuelve a cambiar durante la sesión.
"""

from __future__ import annotations

import random

# Mismos codepoints que `polybar/config.ini` — si cambiás uno, cambialo en los dos lados.
ICONS = (
    "\ue235",  # python
    "\uf303",  # arch
    "\uf31a",  # tux
)


def main() -> int:
    print(random.choice(ICONS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
