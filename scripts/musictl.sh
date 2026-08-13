#!/usr/bin/env bash
# ============================================================
#  musictl.sh — Control de música (Super+S)
#  Diseño adaptado de mdfk15/Rofi (menú iconos + carátula + lista)
#  Backend: playerctl (spotifyd preferido, ncspot si no)
#  Playlists/Cola: spotify_queue.py (Web API con tu token)
#  Barra: ⏮ ▶/⏸ ⏭ · 🔁 repetir · 🔀 aleatorio · 📋 cola · 🎶 playlists
# ============================================================

# ----- Selección de reproductor -----
PLAYERS="$(playerctl -l 2>/dev/null)"
PLAYER=""
for p in $PLAYERS; do
    if [[ "$p" == spotifyd* ]] && [[ "$(playerctl -p "$p" status 2>/dev/null)" == "Playing" ]]; then
        PLAYER="$p"
        break
    fi
done
if [ -z "$PLAYER" ]; then
    for p in $PLAYERS; do
        if [[ "$(playerctl -p "$p" status 2>/dev/null)" == "Playing" ]]; then
            PLAYER="$p"
            break
        fi
    done
fi
[ -z "$PLAYER" ] && PLAYER="$(echo "$PLAYERS" | head -1)"
if [ -z "$PLAYER" ]; then
    notify-send "🎵 Música" "No hay reproductor activo (spotifyd/ncspot)" 2>/dev/null
    exit 0
fi

pc() { playerctl -p "$PLAYER" "$@"; }

# ----- Metadatos -----
status=$(pc status 2>/dev/null)
song=$(pc metadata --format "{{title}}" 2>/dev/null)
artist=$(pc metadata --format "{{artist}}" 2>/dev/null)
album=$(pc metadata --format "{{album}}" 2>/dev/null)
arturl=$(pc metadata --format "{{mpris:artUrl}}" 2>/dev/null)

# ----- Iconos (Nerd Font; mdfk15 usa feather, aquí Nerd Font) -----
if [[ "$status" == "Playing" ]]; then play="⏸"; else play="▶"; fi
prev="⏮"
next="⏭"
repeat="🔁"
shuffle="🔀"
queue="📋"
plists="🎶"

# ----- Carátula (descarga solo si hay artUrl) -----
cover="/tmp/rofi-music-cover.png"
[ -n "$arturl" ] && curl -sL --max-time 2 "$arturl" -o "$cover" 2>/dev/null

if [ -n "$arturl" ] && [ -f "$cover" ]; then
    cover_opt="background-image: url(\"$cover\", width);"
    message_opt="background-color:transparent; expand:false; padding: 200px calc( 1% ) calc( 2% );"
    window_h="380px"
else
    cover_opt=""
    message_opt="expand:false; padding: 6px calc( 1% ) calc( 1% );"
    window_h="120px"
fi

# ----- Mensaje -----
msg="<b>$song</b>"
[ -n "$artist" ] && msg+="\n$artist"
[ -n "$album" ] && msg+="\n$album"

# ============================================================
#  Funciones de menú (estructura mdfk15)
# ============================================================
icon_menu="music.rasi"

rofi_icon() {
    # Menú de iconos: carátula + info arriba, controles en UNA fila abajo
    echo -e "$1" | rofi -dmenu -p "Music" \
        -theme-str "textbox-prompt-colon { enabled: false; }" \
        -theme-str "listview { columns: 7; lines: 1; layout: horizontal; spacing: 2px; expand: false; }" \
        -theme-str "window { width: 430px; height: $window_h; }" \
        -theme-str "coverbox {$cover_opt}" \
        -theme-str "textbox {$message_opt}" \
        -theme "$HOME/.config/rofi/$icon_menu" \
        -mesg "$msg" -selected-row 1
}

play_playlists() {
    # Lista las playlists reales y reproduce (spotify_queue.py)
    "$HOME/.config/scripts/spotify_queue.py" --playlists
}

show_queue() {
    # Muestra la cola de reproducción (spotify_queue.py)
    "$HOME/.config/scripts/spotify_queue.py"
}

main_menu() {
    options="$prev\n$play\n$next\n$repeat\n$shuffle\n$queue\n$plists"
    chosen=$(rofi_icon "$options")
    [ -z "$chosen" ] && exit 0

    case "$chosen" in
        "$play")    pc play-pause 2>/dev/null ;;
        "$prev")    pc previous 2>/dev/null ;;
        "$next")    pc next 2>/dev/null ;;
        "$repeat")
            if [[ "$(pc repeat 2>/dev/null)" == "On" ]]; then pc repeat off 2>/dev/null
            else pc repeat on 2>/dev/null; fi ;;
        "$shuffle")
            if [[ "$(pc shuffle 2>/dev/null)" == "On" ]]; then pc shuffle off 2>/dev/null
            else pc shuffle on 2>/dev/null; fi ;;
        "$queue")   show_queue ;;
        "$plists")  play_playlists ;;
    esac
}

main_menu
