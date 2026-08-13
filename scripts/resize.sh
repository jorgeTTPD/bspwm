#!/bin/bash
DISPLAY=:0

case "$1" in
    right)
        bspc node -r +0.03 2>/dev/null
        ;;
    left)
        bspc node -r -0.03 2>/dev/null
        ;;
    down)
        bspc node -r +0.03 2>/dev/null
        ;;
    up)
        bspc node -r -0.03 2>/dev/null
        ;;
esac
