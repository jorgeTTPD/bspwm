# My Dotfiles

Backup de mi entorno de escritorio para recuperar mi config si Arch se rompe.

## Entornos

### bspwm (X11)
```bash
cp -r bspwm/* ~/.config/
cp -r polybar/* ~/.config/polybar/
cp -r scripts/* ~/.config/scripts/
cp -r rofi/* ~/.config/rofi/
cp .Xresources ~/
cp .fehbg ~/
cp picom.conf ~/
cp greenclip.toml ~/.config/
cp libinput-gestures.conf ~/.config/
```

### Hyprland (Wayland)
```bash
cp hyprland/* ~/.config/hypr/
cp waybar/* ~/.config/waybar/
cp wofi/* ~/.config/wofi/
cp mako/* ~/.config/mako/
```

## Paquetes necesarios

### bspwm
```bash
sudo pacman -S bspwm sxhkd polybar picom feh rofi xclip scrot brightnessctl playerctl greenclip
```

### Hyprland
```bash
sudo pacman -S hyprland hyprpaper waybar wofi mako grim slurp brightnessctl playerctl
```

## Colores
Catppuccin Mocha:
- Fondo: `#1e1e2e`
- Texto: `#cdd6f4`
- Acento: `#89b4fa`
- Superficie: `#313244`
- Inactivo: `#6c7086`
