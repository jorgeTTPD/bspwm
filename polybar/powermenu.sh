#!/usr/bin/env bash
chosen=$(echo -e " Apagar\n Reiniciar\n󰍃 Cerrar sesión" | rofi -dmenu -i -theme-str 'window {width: 200px;}')
case "$chosen" in
    " Apagar") poweroff ;;
    " Reiniciar") reboot ;;
    "󰍃 Cerrar sesión") bspc quit ;;
esac
