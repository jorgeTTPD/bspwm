#!/usr/bin/env bash
if ! command -v playerctl &>/dev/null; then
    exit 0
fi

status=$(playerctl status 2>/dev/null)
[ "$status" != "Playing" ] && exit 0

artist=$(playerctl metadata artist 2>/dev/null)
title=$(playerctl metadata title 2>/dev/null)

if [ -z "$artist" ] && [ -z "$title" ]; then
    exit 0
fi

echo " ${artist} - ${title}"