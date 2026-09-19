"""El objetivo actual de un engagement: contra qué máquina estás trabajando.

Tenerlo A LA VISTA en la barra no es cosmético. El error más caro de un pentest es correr
algo contra la caja equivocada —y en un lab con tres máquinas abiertas y varias terminales,
"me confundí de IP" pasa—. Si además el target es de un cliente, deja de ser un error y
pasa a ser acceso no autorizado.

Por eso el estado es explícito y se declara a mano: `dot target set <ip>`. No se adivina
del historial ni de la última conexión.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass

# Hostname RFC-1123 simplificado: lo justo para atajar un pegado con basura, sin pelearse
# con los nombres raros que aparecen en los labs (`web.htb`, `dc01.lab.local`).
_HOSTNAME = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9-]+)*$")

_MAX_LABEL = 40


@dataclass(frozen=True)
class Target:
    """Una IP (o hostname) y un nombre opcional para reconocerla."""

    host: str
    label: str = ""

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("El target no puede estar vacío.")
        if not self._is_valid_host(self.host):
            raise ValueError(
                f"'{self.host}' no parece una IP ni un hostname. "
                "Ejemplos válidos: 10.10.11.23, web.htb, dc01.lab.local"
            )
        if len(self.label) > _MAX_LABEL:
            raise ValueError(f"El nombre no puede pasar de {_MAX_LABEL} caracteres.")
        if "\n" in self.host or "\n" in self.label:
            # El archivo de estado es UNA línea y lo lee un script de shell: un salto de
            # línea partiría el valor en dos y la barra mostraría cualquier cosa.
            raise ValueError("Ni el host ni el nombre pueden tener saltos de línea.")

    @staticmethod
    def _is_valid_host(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return bool(_HOSTNAME.match(value))

    def to_line(self) -> str:
        """La línea que se guarda. Formato: `host` o `host<TAB>label`.

        TAB y no espacio como separador porque el label puede tener espacios y el lector es
        un script de shell: con TAB, `cut -f1` alcanza y no hay que parsear nada.
        """
        return f"{self.host}\t{self.label}" if self.label else self.host

    @classmethod
    def from_line(cls, line: str) -> Target | None:
        """None si la línea está vacía o mal formada. Un estado corrupto no rompe la barra."""
        host, _, label = line.strip().partition("\t")
        if not host:
            return None
        try:
            return cls(host=host, label=label.strip())
        except ValueError:
            return None
