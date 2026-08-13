#!/bin/bash
# Screenshot con Rofi - Estilo Hyprland

options=(
    " 󰩬  Captura completa"
    " 󰩫  Captura de ventana"
    " 󰩭  Captura de selección"
    " 󰩯  Grabar pantalla (ffmpeg)"
    " 󰅖  Cancelar"
)

selected=$(printf '%s\n' "${options[@]}" | rofi -dmenu -p "📸 Screenshot" -config ~/.config/rofi/screenshot.rasi -selected-row 2)

case $selected in
    *"Completa"*)
        scrot ~/Imágenes/screenshots/full_%Y%m%d_%H%M%S.png
        notify-send "Screenshot" "Captura completa guardada"
        ;;
    *"Ventana"*)
        scrot -u ~/Imágenes/screenshots/window_%Y%m%d_%H%M%S.png
        notify-send "Screenshot" "Captura de ventana guardada"
        ;;
    *"Selección"*)
        scrot -s ~/Imágenes/screenshots/selection_%Y%m%d_%H%M%S.png
        notify-send "Screenshot" "Captura de selección guardada"
        ;;
    *"Grabar"*)
        ffmpeg -f x11grab -r 30 -s $(xdpyinfo | grep dimensions | awk '{print $2}') -i :0.0 ~/Imágenes/screenshots/record_$(date +%Y%m%d_%H%M%S).mkv &
        notify-send "Recording" "Grabando... (mata ffmpeg para parar)"
        ;;
    *"Cancelar"*)
        exit 0
        ;;
esac
