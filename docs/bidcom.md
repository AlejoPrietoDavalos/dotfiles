# `dot bidcom` — automatizaciones del trabajo

Arma el escritorio de trabajo en un solo paso: abre los repos en VSCode,
terminales con el venv activado y las apps de siempre, cada cosa en su desktop
de bspwm.

```bash
dot bidcom start-work              # vscode + terminales + apps
dot bidcom start-work --only vscode --only terminals
dot bidcom config                  # dónde vive la config privada
```

## Config privada (no se versiona)

Todo lo específico del trabajo (repos, qué va en cada desktop, qué apps) vive en
`private/bidcom.json`, que está en `.gitignore`. El primer `start-work` escribe
una plantilla de ejemplo; se edita a mano y manda ella.

```jsonc
{
  "workspaces_root": "/home/<user>/documentos/python",
  "venv_dirname": "env",
  "terminal": { "program": "kitty", "wm_class": "kitty" },
  // ojo: bspwm matchea WM_CLASS case-sensitive
  "vscode": { "wm_class": "code", "workspaces": [ { "repo": "repo-a", "desktop": "1" } ] },
  // desktop acepta "n1".."n4" o los símbolos del pad "/" "*" "-" "+"
  "terminals": [ { "repo": "repo-a", "desktop": "/", "count": 1, "venv": true } ],
  "apps": [
    { "name": "docker-desktop", "desktop": "9", "wm_class": "Docker Desktop",
      "systemd_user_unit": "docker-desktop.service", "process": "Docker Desktop" }
  ],
  "final_focus_desktop": "1"
}
```

## Detalles que importan

- **Carrera de desktops**: lanzar una app y cambiar de desktop rápido hace que la
  ventana nazca donde no era. Por ventana se usa una regla one-shot
  (`bspc rule -a <clase> -o desktop=<destino>`), se espera a que aparezca de
  verdad (poll de `bspc query -N` + `xprop WM_CLASS`) y, si igual quedó mal, se
  mueve con `bspc node <id> -d <destino>`. Recién ahí va la siguiente.
- **Venv**: la terminal se abre con un rcfile generado que sourcea `~/.bashrc` y
  después `source env/bin/activate`.
- **Desktops del pad**: se llaman `n1`–`n4` en bspwm (polybar los muestra como
  `/ * - +`); la config acepta ambos nombres. Si no existen (distribución `pad`
  no aplicada), esa parte se saltea con un aviso: aplicala con `dot monitors`.

## Arquitectura

Sigue la clean architecture del repo: entidad `src/core/entities/bidcom_workspace.py`,
caso de uso `src/core/use_cases/bidcom_start_work.py`, contratos en
`src/core/repositories/system/` y drivers (JSON privado, `bspc`/`xprop`, kitty,
`systemctl --user`/`pgrep`) en `src/app/drivers/repositories/system/`.

## TODO

- `dot bidcom setup-envs`: crear/recrear los venvs leyendo los repos de la config
  privada (hoy eso vive en un Makefile aparte).
- Campo `notes` por workspace para mostrar un resumen del contexto al arrancar.
- `dot bidcom stop-work`: cierre ordenado.
