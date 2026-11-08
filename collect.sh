#!/usr/bin/env bash
# =============================================================================
#  AxolOS · collect.sh
#  Hace una "foto" de tu escritorio actual y la guarda dentro del pack.
#  Vuelve a ejecutarlo cada vez que cambies algo (fondo, tema, panel...) y
#  quieras que AxolOS lo incluya.
#
#  No toca tu sistema: solo LEE de tu $HOME y ESCRIBE dentro de este repo.
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KINI="python3 -I $ROOT/tools/kini.py"

C="$HOME/.config"
L="$HOME/.local/share"

# Devuelve la primera ruta que exista: primero tu copia personal (si la
# tienes, es lo que estás usando), si no la que ya instaló AxolOS en el sistema.
pick() { local p; for p in "$@"; do [[ -e $p ]] && { echo "$p"; return; }; done; echo "$1"; }
SYS=/usr/share

# --- Origen de tus archivos (puedes sobrescribirlos con variables de entorno) --
WALLPAPER="${AXOLOS_WALLPAPER:-$(pick "$HOME/Imágenes/fondoAjo.jpg" $SYS/wallpapers/AxolOS/contents/images/*)}"
CUBE_IMG="${AXOLOS_CUBE:-$(pick "$HOME/Descargas/fondocubo.jpg" $SYS/axolos/cube.jpg)}"
LOGO_PNG="${AXOLOS_LOGO_PNG:-$(pick /usr/local/share/pixmaps/cachy-custom-logo.png /usr/share/pixmaps/axolos-logo.png)}"
LOGO_SVG="${AXOLOS_LOGO_SVG:-$(pick "$HOME/Descargas/logoajofinal.svg" $SYS/icons/hicolor/scalable/apps/axolos.svg)}"
FASTFETCH_CFG="${AXOLOS_FASTFETCH:-$(pick "$C/fastfetch/axolos.jsonc" $SYS/fastfetch/presets/axolos.jsonc)}"
WAL_KONSOLE="${AXOLOS_WAL_KONSOLE:-$(pick "$HOME/.cache/wal/colors-konsole.colorscheme" $SYS/konsole/AxolOS.colorscheme)}"
LNF_SRC="$(pick "$L/plasma/look-and-feel/com.noel.axolos" $SYS/plasma/look-and-feel/com.noel.axolos)"

# --- Destinos dentro del repo -------------------------------------------------
T="$ROOT/packages/axolos-themes/assets"        # -> /usr/share/...
B="$ROOT/packages/axolos-branding/files"       # logos, fastfetch
K="$ROOT/packages/axolos-kde-settings/skel"    # -> /etc/skel
X="$ROOT/packages/axolos-kde-settings/xdg"     # -> /etc/xdg
S="$ROOT/packages/axolos-kde-settings/sddm"    # -> /usr/lib/sddm/sddm.conf.d

say()  { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
warn() { printf '\e[1;33m  ! \e[0m%s\n' "$*"; }
need() { [[ -e "$1" ]] || { warn "No existe: $1 (se omite)"; return 1; }; }
cpdir() { need "$1" && { rm -rf "$2"; mkdir -p "$(dirname "$2")"; cp -a "$1" "$2"; }; }

img_size() {
  if command -v magick >/dev/null; then magick identify -format '%wx%h' "$1[0]"
  else file "$1" | grep -oE '[0-9]{3,5} ?x ?[0-9]{3,5}' | tail -1 | tr -d ' '; fi
}

rm -rf "$T" "$B" "$K" "$X" "$S"
mkdir -p "$T" "$B" "$K/.config" "$X" "$S"

# =============================================================================
say "1/4 Temas visuales"
# =============================================================================
cpdir "$LNF_SRC" "$T/plasma/look-and-feel/com.noel.axolos"
cpdir "$(pick "$L/plasma/desktoptheme/MacTahoe-Dark" $SYS/plasma/desktoptheme/MacTahoe-Dark)" "$T/plasma/desktoptheme/MacTahoe-Dark"
for v in MacTahoe-Dark MacTahoe-Dark-1.25x MacTahoe-Dark-1.5x; do
  cpdir "$(pick "$L/aurorae/themes/$v" $SYS/aurorae/themes/$v)" "$T/aurorae/themes/$v" || true
done
cpdir "$(pick "$C/Kvantum/MacTahoe" $SYS/Kvantum/MacTahoe)" "$T/Kvantum/MacTahoe"
# Tema de Plasma "AxolOS": MacTahoe-Dark sin azules (brillo del dock oculto, deslizadores, OSD…)
python3 -I "$ROOT/tools/plasma_axolos.py" "$T/plasma/desktoptheme/MacTahoe-Dark" "$T/plasma/desktoptheme/AxolOS" >/dev/null
# Sonidos "AxolOS" (sintetizados)
python3 -I "$ROOT/tools/sonidos_axolos.py" "$T/sounds/AxolOS" >/dev/null
# Botones de ventana "AxolOS": grafito en reposo, morado al pasar el ratón
python3 -I "$ROOT/tools/botones_axolos.py" "$T/aurorae/themes/MacTahoe-Dark" "$T/aurorae/themes/AxolOS" >/dev/null
# Iconos "AxolOS": Yaru morado + iconos Yaru (en morado) para las apps de KDE
python3 -I "$ROOT/tools/iconos_axolos.py" "$T/icons/AxolOS" >/dev/null
# Kvantum "AxolOS": MacTahoe oscuro con los azules pasados al morado de las carpetas
python3 -I "$ROOT/tools/kvantum_axolos.py" "$T/Kvantum/MacTahoe" "$T/Kvantum/AxolOS" >/dev/null

mkdir -p "$T/color-schemes"
cp "$(pick "$L/color-schemes/MacTahoeDark.colors" $SYS/color-schemes/MacTahoeDark.colors)" "$T/color-schemes/" 2>/dev/null || warn "MacTahoeDark.colors no encontrado"
cp "$(pick "$LNF_SRC/contents/color-schemes/AxolOSPurple.colors" $SYS/color-schemes/AxolOSPurple.colors)" "$T/color-schemes/"
# "AxolOS Obsidian": copia exacta de los colores que usas (todas las secciones)
python3 -I - "$C/kdeglobals" "$T/color-schemes/AxolOSObsidian.colors" <<'PY'
import re, sys
src, dst = sys.argv[1:3]
out, keep = [], False
for line in open(src, encoding="utf-8"):
    m = re.match(r"^\[(.*)\]\s*$", line)
    if m:
        keep = m.group(1).startswith(("ColorEffects:", "Colors:", "WM"))
    if keep:
        out.append(line.rstrip("\n"))
out = ["[General]", "ColorScheme=AxolOSObsidian", "Name=AxolOS Obsidian", "", "[KDE]", "contrast=4", ""] + out
open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY

# Fondo como paquete de wallpaper de Plasma (/usr/share/wallpapers/AxolOS)
if need "$WALLPAPER"; then
  size="$(img_size "$WALLPAPER")"; ext="${WALLPAPER##*.}"
  W="$T/wallpapers/AxolOS"
  mkdir -p "$W/contents/images"
  cp "$WALLPAPER" "$W/contents/images/${size}.${ext}"
  cat > "$W/metadata.json" <<EOF
{
    "KPlugin": {
        "Authors": [{ "Name": "Noel Alarcón" }],
        "Id": "AxolOS",
        "License": "CC-BY-SA-4.0",
        "Name": "AxolOS"
    }
}
EOF
  echo "${size}.${ext}" > "$ROOT/packages/axolos-themes/.wallpaper-file"
fi
mkdir -p "$T/axolos"
need "$CUBE_IMG" && cp "$CUBE_IMG" "$T/axolos/cube.jpg"

# Tema global AxolOS: valores por defecto completos (lo que aplica "Tema global")
LNF="$T/plasma/look-and-feel/com.noel.axolos"
cat > "$LNF/contents/defaults" <<'EOF'
[kdeglobals][General]
ColorScheme=AxolOSObsidian
AccentColor=166,154,254

[kdeglobals][Icons]
Theme=AxolOS

[kdeglobals][KDE]
widgetStyle=kvantum-dark

[kdeglobals][Sounds]
Theme=AxolOS

[plasmarc][Theme]
name=AxolOS

[kcminputrc][Mouse]
cursorTheme=WhiteSur-cursors

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae.v2
theme=__aurorae__svg__AxolOS

[ksplashrc][KSplash]
Engine=KSplashQML
Theme=com.noel.axolos

[Wallpaper]
Image=AxolOS
EOF
# Plasma 6 lee "contents/defaults"; el antiguo look-and-feel/defaults sobra
rm -rf "$LNF/contents/look-and-feel"
# La animación de inicio vive en packages/axolos-themes/splash (la instala el PKGBUILD)
rm -rf "$LNF/contents/splash"
# Icono del tema global -> logo de AxolOS
sed -i 's/"distributor-logo-cachyos"/"axolos"/' "$LNF/metadata.json"

# Perfil y paleta de Konsole AxolOS (grafito + morado; sustituye a la de pywal)
mkdir -p "$T/konsole"
python3 -I "$ROOT/tools/terminal_axolos.py" "$T/konsole" >/dev/null

# =============================================================================
say "2/4 Branding (logo, fastfetch)"
# =============================================================================
need "$LOGO_PNG" && cp "$LOGO_PNG" "$B/axolos-logo.png"
# icono "axolos" recortado al contorno (en el dock llena el hueco como los demás)
cp "$ROOT/tools/axolos-icono.svg" "$B/axolos.svg"
cp "$ROOT/tools/avatar-axolos.png" "$B/avatar-axolos.png"
if need "$FASTFETCH_CFG"; then
  sed 's#"source": *"[^"]*"#"source": "/usr/share/pixmaps/axolos-logo.png"#' \
      "$FASTFETCH_CFG" > "$B/fastfetch.jsonc"
fi

# =============================================================================
say "3/4 Ajustes de KDE para usuarios nuevos (/etc/skel)"
# =============================================================================
cfg() { mkdir -p "$(dirname "$K/.config/$2")"; cp "$C/$1" "$K/.config/$2"; }

# Ficheros que ya traía cachyos-kde-settings y que no personalizas
for f in Trolltech.conf arkrc baloofilerc dconf/user libinput-gestures.conf; do
  [[ -f /etc/skel/.config/$f ]] && { mkdir -p "$(dirname "$K/.config/$f")"; cp "/etc/skel/.config/$f" "$K/.config/$f"; }
done
cp /usr/lib/sddm/sddm.conf.d/general.conf /usr/lib/sddm/sddm.conf.d/zz-wayland.conf "$S/" 2>/dev/null \
  || warn "No se encontraron los .conf de SDDM de CachyOS"
# pantalla de inicio de sesión AxolOS
sed -i 's/^Current=.*/Current=AxolOS/' "$S/general.conf" 2>/dev/null || true
# avatar del ajolote para los usuarios nuevos
cp "$ROOT/tools/avatar-axolos.png" "$K/.face.icon"

# kdeglobals (colores AxolOS Obsidian, fuentes, iconos)
cfg kdeglobals kdeglobals
$KINI "$K/.config/kdeglobals" \
  --set 'KDE|LookAndFeelPackage=com.noel.axolos' \
  --set 'KDE|widgetStyle=kvantum-dark' \
  --drop-key 'General|widgetStyle' \
  --set 'General|ColorScheme=AxolOSObsidian' \
  --drop-key 'General|BrowserApplication' \
  --drop-section '^(DirSelect Dialog|KFileDialog Settings|PreviewSettings|WM)$' \
  --drop-value-regex '/home/'

# kwin: decoración MacTahoe, cubo, 4 escritorios (sin IDs ni escalado de tu pantalla)
cfg kwinrc kwinrc
$KINI "$K/.config/kwinrc" \
  --drop-section '^Tiling\]' --drop-section '^Xwayland$' \
  --drop-key 'Desktops|Id_1' --drop-key 'Desktops|Id_2' \
  --drop-key 'Desktops|Id_3' --drop-key 'Desktops|Id_4' \
  --set 'Effect-cube|SkyBox=/usr/share/axolos/cube.jpg'

cfg plasmarc plasmarc
$KINI "$K/.config/plasmarc" --drop-section '^Wallpapers$'
printf '[KSplash]\nEngine=KSplashQML\nTheme=com.noel.axolos\n' > "$K/.config/ksplashrc"

printf '[Mouse]\ncursorTheme=WhiteSur-cursors\ncursorSize=24\n' > "$K/.config/kcminputrc"

for g in gtk-3.0 gtk-4.0; do
  cfg "$g/settings.ini" "$g/settings.ini"
  $KINI "$K/.config/$g/settings.ini" --drop-key 'Settings|gtk-xft-dpi'
done
cp "$HOME/.gtkrc-2.0" "$K/.gtkrc-2.0"
# Botones AxolOS en apps GTK3/GTK4 (Brave, Chrome, Archivos…): finos, iguales que los de KWin
python3 -I "$ROOT/tools/gtk_botones_axolos.py" "$T/axolos/gtk-buttons" "$ROOT/build/gtk-css" /usr/share/axolos/gtk-buttons >/dev/null
for v in 3 4; do
  printf "@import 'colors.css';\n@import 'axolos-window-controls.css';\n" > "$K/.config/gtk-$v.0/gtk.css"
  cp "$ROOT/build/gtk-css/gtk$v.css" "$K/.config/gtk-$v.0/axolos-window-controls.css"
done
# Navegadores Chromium: Brave/Chrome con tema GTK, Chromium con barra de KWin
python3 -I "$ROOT/tools/navegadores_axolos.py" --skel "$K"
cfg xsettingsd/xsettingsd.conf xsettingsd/xsettingsd.conf
sed -i '/UnscaledDPI/d' "$K/.config/xsettingsd/xsettingsd.conf"

mkdir -p "$K/.config/Kvantum"; cp "$C/Kvantum/kvantum.kvconfig" "$K/.config/Kvantum/"

cfg starship.toml starship.toml

printf '[Desktop Entry]\nDefaultProfile=AxolOS.profile\n\n' > "$K/.config/konsolerc"
grep -v '^ColorScheme=$' "$C/konsolerc" | sed '/^\[Desktop Entry\]/,/^$/d' >> "$K/.config/konsolerc"

# Panel superior + dock + reloj del escritorio
cfg plasma-org.kde.plasma.desktop-appletsrc plasma-org.kde.plasma.desktop-appletsrc
A="$K/.config/plasma-org.kde.plasma.desktop-appletsrc"
# Contenedores del escritorio (plugin folder) y cuál es el de la pantalla principal
containments() {  # imprime "id lastScreen plugin" de cada contenedor de primer nivel
  awk '/^\[Containments\]\[[0-9]+\]$/ { if (id!="") print id, scr, plg; id=$0; gsub(/[^0-9]/,"",id); scr=""; plg=""; inhdr=1; next }
       /^\[/ { inhdr=0; next }
       inhdr && /^lastScreen=/ { scr=substr($0,12) }
       inhdr && /^plugin=/ { plg=substr($0,8) }
       END { if (id!="") print id, scr, plg }' "$1"
}
desk_ids=$(containments "$A" | awk '$3=="org.kde.plasma.folder"{print $1}')
main_desk=$(containments "$A" | awk '$3=="org.kde.plasma.folder" && $2=="0"{id=$1} END{print id}')
[[ -n $main_desk ]] || { warn "No encuentro el escritorio principal en el layout"; exit 1; }
drop=()
for id in $desk_ids; do [[ $id != "$main_desk" ]] && drop+=(--drop-section "^Containments\\]\\[$id(\\]|$)"); done
# Marco de fotos (mediaframe): son tus fotos personales -> fuera
frame_ids=$(grep -B2 '^plugin=org.kde.plasma.mediaframe' "$A" | grep -oE '\[Applets\]\[[0-9]+\]' | grep -oE '[0-9]+' || true)
for id in $frame_ids; do
  drop+=(--drop-section "\\]\\[Applets\\]\\[$id(\\]|$)")
  sed -i -E "s/Applet-$id:[^;]*;//g" "$A"
done
$KINI "$A" "${drop[@]}" \
  --sub "$LOGO_SVG" "axolos" \
  --drop-value-regex '/home/' \
  --drop-section 'ConfigDialog$' \
  --drop-section '^ScreenMapping$' \
  --drop-key "Containments][$main_desk][General|positions" \
  --drop-key "Containments][$main_desk][General|changedPositions" \
  --drop-key "Containments][$main_desk][General|lastResolution"
$KINI "$A" --set "Containments][$main_desk][Wallpaper][org.kde.image][General|Image=/usr/share/wallpapers/AxolOS/"
# Dock de AxolOS: fijo, con lo que todo AxolOS trae. Tus accesos personales (apps del AUR, Flatpak…)
# se quedan en tu equipo: en otro no existirían y saldrían como «?».
sed -i -E 's#^launchers=.*#launchers=preferred://filemanager,preferred://browser,applications:org.axolos.ia.desktop,applications:org.kde.konsole.desktop,applications:systemsettings.desktop#' "$A"
# Reloj del escritorio: lo crea axolos-reloj-escritorio.js medido sobre la pantalla de cada usuario
python3 -I "$ROOT/tools/quitar_reloj_skel.py" "$A"

# Actividad con el mismo ID que usa el escritorio del layout
act=$(sed -n "/^\[Containments\]\[$main_desk\]$/,/^\[/p" "$A" | sed -n 's/^activityId=//p')
if [[ -n "$act" ]]; then
  printf '[activities]\n%s=Predeterminada\n\n[main]\ncurrentActivity=%s\n' "$act" "$act" > "$K/.config/kactivitymanagerdrc"
fi

# Tamaño/flotado/autoocultar de los paneles
grep -q PlasmaViews "$C/plasmashellrc" && {
  cfg plasmashellrc plasmashellrc
  $KINI "$K/.config/plasmashellrc" --drop-section '^(Updates|KFileDialog Settings)$'
}

# Valores "por defecto" (lo que restaura el botón "Predeterminados" de Ajustes)
mkdir -p "$K/.config/kdedefaults"
echo -n com.noel.axolos > "$K/.config/kdedefaults/package"
printf '[General]\nColorScheme=AxolOSObsidian\n\n[Icons]\nTheme=AxolOS\n\n[KDE]\nwidgetStyle=kvantum-dark\n' > "$K/.config/kdedefaults/kdeglobals"
printf '[org.kde.kdecoration2]\nNoPlugin=false\nlibrary=org.kde.kwin.aurorae.v2\ntheme=__aurorae__svg__AxolOS\n' > "$K/.config/kdedefaults/kwinrc"
printf '[Theme]\nname=AxolOS\n' > "$K/.config/kdedefaults/plasmarc"
printf '[KSplash]\nEngine=KSplashQML\nTheme=com.noel.axolos\n' > "$K/.config/kdedefaults/ksplashrc"
printf '[Mouse]\ncursorTheme=WhiteSur-cursors\n' > "$K/.config/kdedefaults/kcminputrc"

# Pantalla de bloqueo con el fondo AxolOS (global, en /etc/xdg)
cat > "$X/kscreenlockerrc" <<'EOF'
[Greeter][Wallpaper][org.kde.image][General]
Image=/usr/share/wallpapers/AxolOS/
PreviewImage=/usr/share/wallpapers/AxolOS/
EOF

# =============================================================================
say "4/4 Lista de paquetes instalados"
# =============================================================================
pacman -Qqen > "$ROOT/pkglists/native.txt"
pacman -Qqem > "$ROOT/pkglists/aur.txt"

# Comprobación final: no debe quedar ninguna ruta a tu /home
if leftovers=$(grep -rIl "$HOME" "$K" "$X" "$B" "$T/konsole" 2>/dev/null) && [[ -n $leftovers ]]; then
  warn "Quedan rutas a $HOME en:"; echo "$leftovers" | sed 's/^/     /'
fi
say "Listo. Pack actualizado en: $ROOT/packages"
