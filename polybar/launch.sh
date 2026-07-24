#!/usr/bin/env bash

killall -q polybar yad

while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

polybar mi_barra 2>&1 | tee -a /tmp/polybar.log & disown
nohup ~/.config/polybar/scripts/lyric_popup.sh > /dev/null 2>&1 &

echo "Polybar lanzada..."
