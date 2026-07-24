#!/usr/bin/env bash

export PATH="$HOME/.local/bin:$PATH"

dir="$HOME/Pictures"
mkdir -p "$dir"

options() {
    select="✂"
    window="☐"
    screen="⊞"
    delay="⏱"
    options="$select\n$window\n$screen\n$delay"
}

setFilename() {
    filename="screenshot_$(date +%Y%m%d_%H%M%S).png"
    filepath="$dir/$filename"
}

check_case() {
    case $chosen in
        $select)
            setFilename
            scrot -s "$filepath"
            xclip -selection clipboard -t image/png < "$filepath" ;;
        $window)
            setFilename
            scrot -u "$filepath"
            xclip -selection clipboard -t image/png < "$filepath" ;;
        $screen)
            setFilename
            scrot "$filepath"
            xclip -selection clipboard -t image/png < "$filepath" ;;
        $delay)
            setFilename
            scrot -d 5 "$filepath"
            xclip -selection clipboard -t image/png < "$filepath" ;;
    esac
    notify-send "Screenshot" "Lista para pegar (Ctrl+V)"
}

path=$(dirname "$0")
source $path/base.sh

title='Screenshot'
icon=''
icon_menu='vertical.rasi'

case $1 in
    --status) pass ;;
    *) main_menu ;;
esac
