#!/bin/bash
opcion=$(echo -e "Apagar\nReiniciar\nCerrar sesión" | rofi -dmenu -p "Power Menu")

case "$opcion" in
    "Apagar") systemctl poweroff ;;
    "Reiniciar") systemctl reboot ;;
    "Cerrar sesión") bspc quit ;;
esac
