# Completado de bash para la CLI `dot`.
# Se instala con: dot self install (symlink en ~/.local/share/bash-completion/completions/dot)

_dot() {
  local cur cmd
  cur="${COMP_WORDS[COMP_CWORD]}"
  cmd="${COMP_WORDS[1]}"

  local commands="install uninstall install-requirement uninstall-requirement \
install-files uninstall-files install-all install-core remove-core menu wifi \
clock-set keyboard mirrors-update sddm bspwm sxhkd-reload scripts-chmod self"

  if [ "$COMP_CWORD" -eq 1 ]; then
    COMPREPLY=($(compgen -W "$commands" -- "$cur"))
    return
  fi

  case "$cmd" in
    install|uninstall|install-requirement|uninstall-requirement|install-files|uninstall-files)
      local root programs
      root="$(dirname "$(readlink -f "$(command -v dot)")")"
      programs="$(python3 -c "import json; print(' '.join(sorted(json.load(open('$root/programs.json')))))" 2>/dev/null)"
      COMPREPLY=($(compgen -W "$programs" -- "$cur"))
      ;;
    wifi)
      if [ "$COMP_CWORD" -eq 2 ]; then
        COMPREPLY=($(compgen -W "saved forget status" -- "$cur"))
      elif [ "${COMP_WORDS[2]}" = "forget" ]; then
        local saved
        saved="$(nmcli -t -f NAME,TYPE connection show 2>/dev/null | awk -F: '$2=="802-11-wireless"{print $1}')"
        local IFS=$'\n'
        COMPREPLY=($(compgen -W "$saved" -- "$cur"))
      fi
      ;;
    sddm)
      COMPREPLY=($(compgen -W "install enable start" -- "$cur"))
      ;;
    bspwm)
      COMPREPLY=($(compgen -W "bootstrap install-session check-display restart" -- "$cur"))
      ;;
    keyboard)
      COMPREPLY=($(compgen -W "latam us es" -- "$cur"))
      ;;
    remove-core)
      COMPREPLY=($(compgen -W "--purge" -- "$cur"))
      ;;
    mirrors-update)
      COMPREPLY=($(compgen -W "--countries --age" -- "$cur"))
      ;;
    self)
      COMPREPLY=($(compgen -W "install" -- "$cur"))
      ;;
  esac
}

complete -F _dot dot
