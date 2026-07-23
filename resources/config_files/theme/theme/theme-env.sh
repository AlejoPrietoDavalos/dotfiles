#!/bin/sh

export GTK_THEME="Adwaita:dark"

if command -v qt6ct >/dev/null 2>&1; then
  export QT_QPA_PLATFORMTHEME="qt6ct"
elif command -v qt5ct >/dev/null 2>&1; then
  export QT_QPA_PLATFORMTHEME="qt5ct"
fi
