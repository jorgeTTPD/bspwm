#!/usr/bin/env bash

status=$(playerctl status 2>/dev/null)
song=$(playerctl metadata --format "{{title}}" 2>/dev/null)
artist=$(playerctl metadata --format "{{artist}}" 2>/dev/null)
album=$(playerctl metadata --format "{{album}}" 2>/dev/null)
arturl=$(playerctl metadata --format "{{mpris:artUrl}}" 2>/dev/null)

if [[ "$status" == "Playing" ]]; then
    play="⏸"
else
    play="▶"
fi

prev="⏮"
next="⏭"
repeat="🔁"

cover="/tmp/rofi-music-cover.png"
[ -n "$arturl" ] && curl -sL --max-time 2 "$arturl" -o "$cover" 2>/dev/null

msg="<b>$song</b>\n$artist"
[ -n "$album" ] && msg+="\n$album"

[ -f "$cover" ] && cv="background-image: url(\"$cover\", width);" mi="background-color:transparent;" ii=""

options="$prev\n$play\n$next\n$repeat"

chosen=$(echo -e "$options" | rofi -dmenu -p "Music" \
    -theme-str "textbox-prompt-colon {str: \"\"; }" \
    -theme-str "coverbox {$cv}" \
    -theme-str "textbox {$mi}" \
    -theme-str "inputbar {$ii}" \
    -theme "$HOME/.config/rofi/music.rasi" \
    -mesg "$msg" -selected-row 1)

case $chosen in
    "$play")  playerctl play-pause 2>/dev/null ;;
    "$prev")  playerctl previous 2>/dev/null ;;
    "$next")  playerctl next 2>/dev/null ;;
    "$repeat")
        if [[ "$(playerctl repeat 2>/dev/null)" == "On" ]]; then
            playerctl repeat off 2>/dev/null
        else
            playerctl repeat on 2>/dev/null
        fi ;;
esac
