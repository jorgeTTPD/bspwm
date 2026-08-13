#!/usr/bin/env bash
# instalador de dotfiles bspwm — copia la config a ~/.config y $HOME
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ Instalando dotfiles bspwm..."

# Carpetas de config
for d in bspwm polybar sxhkd picom rofi scripts; do
    if [ -d "$DIR/$d" ]; then
        mkdir -p "$HOME/.config/$d"
        cp -r "$DIR/$d"/. "$HOME/.config/$d"/
        echo "  ✓ ~/.config/$d"
    fi
done

# Dotfiles sueltos en ~/.config
for f in greenclip.toml libinput-gestures.conf; do
    if [ -f "$DIR/$f" ]; then
        cp "$DIR/$f" "$HOME/.config/$f"
        echo "  ✓ ~/.config/$f"
    fi
done

# Dotfiles en $HOME
for f in .Xresources .fehbg; do
    if [ -f "$DIR/$f" ]; then
        cp "$DIR/$f" "$HOME/$f"
        echo "  ✓ ~/$f"
    fi
done

echo "✅ Listo. Reinicia bspwm (bspc restart) o inicia sesión para aplicar."