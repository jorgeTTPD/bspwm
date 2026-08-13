#!/bin/bash
# Cheat Sheet de keybindings para bspwm
# Se muestra con super+h

cat << 'EOF' | rofi -dmenu -p "⌨ Keybindings" -config ~/.config/rofi/cheatsheet.rasi -selected-row 0 -no-select
  super + Return         → Terminal (st)
  super + d              → App Launcher (rofi)
  super + p              → Menu principal
  super + h              → Este cheat sheet
  super + Escape         → Power Menu
  super + shift + q      → Cerrar ventana
  super + alt + e        → Salir sesión
  super + m              → Alternar monocle
  super + v              → Clipboard history
  super + s              → Control de música
  Print                  → Screenshot
  super + arrows         → Mover foco
  super + 1-5            → Cambiar escritorio
  super + shift + 1-5    → Mover ventana a escritorio
  super + space          → Rotar árbol
  super + ctrl + m       → Alternar modo del mouse
  super + alt + {h,j,k,l} → Redimensionar ventana
  super + alt + shift + {h,j,k,l} → Mover ventana flotante
  XF86Audio              → Control de volumen/música
  XF86MonBrightness      → Control de brillo
EOF
