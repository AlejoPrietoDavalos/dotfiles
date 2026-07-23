
# SDDM (Simple Desktop Display Manager)
- Habilida SDDM para que inicie automáticamente con el sistema.
```bash
sudo systemctl enable sddm.service --force
```


# Keepass + Syncthing
### Instalar Keepass
- `Arch:` sudo pacman -S keepassxc
- `Windows:`
- `Android:` Google Play Store `KeePassDX`
### Instalar Syncthing
- `Arch Linux:` sudo pacman -S syncthing
- `Windows:` Descargar instalador en [syncthing.net](https://www.syncthing.net).
- `Android:` Google Play Store `Syncthing-Fork`.
### Crear y compartir keepass en Syncthing.
- Guardar credenciales en `$HOME/.config/Sync/credentials.kdbx`.

# Bluetooth (blueman)
sudo systemctl enable bluetooth.service
sudo systemctl start bluetooth.service


### Etc...
- Search Google Hack: `gatitos filetype:png`

# WM Automation
La automatizacion vive en `main.py` y se ejecuta con:

```bash
PYTHONPATH=. python3 ./main.py --action <action> --program <program>
```

Acciones soportadas:
- `install`
- `uninstall`
- `install-requirement`
- `uninstall-requirement`
- `install-files`
- `uninstall-files`
- `dirty_install_all_packages` (solo testing)

## CLI `dot`
La CLI `dot` reemplaza al Makefile. Instalala una vez para tenerla en el PATH:

```bash
./dot self install    # crea symlink en ~/.local/bin/dot + completado bash
```

Hay 6 comandos genericos y todos reciben el `<program>` como argumento posicional:

```bash
dot install <program>
dot uninstall <program>
dot install-requirement <program>
dot uninstall-requirement <program>
dot install-files <program>
dot uninstall-files <program>
dot install-all
```

Programas disponibles:
- `bspwm`, `sxhkd`, `polybar`, `kitty`, `ranger`, `picom`, `rofi`, `playerctl`, `scrot`, `thunar`, `theme-dark`, `vscode`, `xclip`, `pulseaudio`, `arandr`, `xorg`, `nvidia`, `docker`.

Ejemplos:
```bash
dot install bspwm
dot install theme-dark
dot install-files sxhkd
dot uninstall polybar
```

Notas:
- `dot install-files sxhkd` copia `resources/config_files/sxhkd/sxhkdrc` a `~/.config/sxhkd/sxhkdrc`.
- `dot sxhkd-reload` recarga `sxhkd` enviando `USR1` al proceso.
- `vscode` usa copia de `settings.json` (no symlink).
- `dot install docker` instala `docker` + `docker-compose`, ejecuta `sudo systemctl enable --now docker.service`, y agrega tu usuario al grupo `docker` si hace falta.
- Luego de agregar usuario al grupo `docker`, hay que cerrar sesion/abrir sesion (o reiniciar) para que aplique.
- `dot install-all` usa la accion dirty para instalar paquetes+files de todos los programas del registry.

## Tema global oscuro (GTK + Qt)
- Instalar capa de tema: `dot install theme-dark`
- Aplica archivos en `~/.config/gtk-3.0`, `~/.config/gtk-4.0`, `~/.config/qt5ct`, `~/.config/qt6ct`, `~/.config/xsettingsd` y `~/.config/theme/theme-env.sh`.
- `bspwmrc` ahora carga `~/.config/theme/theme-env.sh` y levanta `xsettingsd` si está instalado.
- El tema por defecto queda en oscuro para GTK (`Adwaita-dark`) y Qt usa `qt5ct/qt6ct` cuando exista.

## Comandos auxiliares
```bash
dot install-core
dot install-all
dot remove-core
dot remove-core --purge
dot bspwm bootstrap
dot bspwm install-session
dot bspwm check-display
dot bspwm restart
dot sxhkd-reload
dot scripts-chmod
dot clock-set
dot keyboard latam
dot sddm install
dot sddm enable
dot sddm start
```

Otros comandos utiles:
```bash
dot menu                 # menu interactivo de programas
dot wifi                 # conectar a una red wifi (interactivo)
dot wifi saved           # redes guardadas
dot wifi status          # estado de los dispositivos de red
dot mirrors-update       # refresca mirrors de pacman (reflector)
```
