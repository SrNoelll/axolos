#!/bin/bash
# AxolOS · escritorio de prueba: un Plasma limpio con el aspecto DEL REPOSITORIO (no el instalado) dentro de
# un KWin virtual con el efecto Glass, y una captura. No toca la sesión ni la configuración del usuario.
#
#   tools/escritorio-prueba.sh SALIDA.png [oscuro|claro]
#
# Variables: VENTANAS="konsole dolphin" (la última queda con foco) · MENU=1 (abre Bento) · AVISO=1
#            IDIOMA=en · DISENO=1 (aplica el diseño del tema global en vez del de skel) · ESPERA=segundos
# El efecto Glass solo carga si la KWin del equipo es la misma para la que se compiló axolos-glass.
set -euo pipefail
SALIDA=$(readlink -f "$1"); MODO=${2:-oscuro}
REPO=$(cd "$(dirname "$0")/.." && pwd)
T=$(mktemp -d); RUN=/run/user/$(id -u)/axp-$$       # el socket de Wayland no admite rutas largas
mkdir -p "$RUN" && chmod 700 "$RUN"
trap 'rm -rf "$T" "$RUN"' EXIT
A=$REPO/packages/axolos-themes/assets

# usuario limpio: skel del repositorio + temas del repositorio por encima de los instalados
mkdir -p "$T/config" "$T/data/plasma/plasmoids" "$T/data/plasma/look-and-feel" "$T/data/aurorae/themes" "$T/cache" \
         "$T/plugins/kwin/effects/plugins"
cp -r "$REPO/packages/axolos-kde-settings/skel/.config/." "$T/config/"
cp -r "$A/plasma/desktoptheme" "$T/data/plasma/"
cp -r "$A/plasma/look-and-feel/." "$T/data/plasma/look-and-feel/"
cp -r "$REPO/packages/axolos-menu/org.axolos.bento" "$T/data/plasma/plasmoids/"
cp -a "$A/icons" "$A/wallpapers" "$A/color-schemes" "$A/konsole" "$T/data/"
cp -r "$A/aurorae/themes/." "$T/data/aurorae/themes/"
mkdir -p "$T/config/Kvantum" && cp -r "$A/Kvantum/AxolOS" "$T/config/Kvantum/"
# GTK: las hojas de cristal del repositorio en vez de las instaladas
for v in 3 4; do
  [[ -f "$T/config/gtk-$v.0/gtk.css" ]] && sed -i "s|file:///usr/share/axolos/gtk/|file://$A/axolos/gtk/|" "$T/config/gtk-$v.0/gtk.css"
done
glass=${GLASS_SO:-/usr/lib/qt6/plugins/kwin/effects/plugins/glass.so}
[[ -f $glass ]] || glass=/usr/lib/axolos/cristal/glass.so.otra-version
[[ -f $glass ]] && cp "$glass" "$T/plugins/kwin/effects/plugins/glass.so"
{ grep -v '^\[Plugins\]\|^cubeEnabled' "$T/config/kwinrc" 2>/dev/null || true
  if [[ -n "${SIN_CRISTAL:-}" ]]; then      # como si el cristal estuviera apartado: desenfoque normal
    sed -e 's/^glassEnabled=true/glassEnabled=false/' -e 's/^blurEnabled=false/blurEnabled=true/' \
      "$REPO/packages/axolos-glass/kwinrc"
  else cat "$REPO/packages/axolos-glass/kwinrc"; fi; } > "$T/kwinrc" && mv "$T/kwinrc" "$T/config/kwinrc"
# ventanas colocadas: la primera a la izquierda, la segunda a la derecha (con foco)
cat > "$T/config/kwinrulesrc" <<'EOF'
[1]
Description=izquierda
position=90,150
positionrule=2
size=860,560
sizerule=2
wmclass=konsole
wmclassmatch=2

[3]
Description=archivos
position=1000,380
positionrule=2
size=860,560
sizerule=2
wmclass=nautilus
wmclassmatch=2

[2]
Description=derecha
position=1000,380
positionrule=2
size=860,560
sizerule=2
wmclass=dolphin
wmclassmatch=2

[General]
count=3
rules=1,2,3
EOF

# apps de AxolOS: los módulos instalados con los del repositorio por encima
mkdir -p "$T/lib" && cp -r /usr/lib/axolos/. "$T/lib/" 2>/dev/null || true
cp "$REPO"/packages/axolos-branding/static/*.py "$T/lib/" 2>/dev/null || true

cat > "$T/sesion.sh" <<EOF
#!/bin/bash
/usr/lib/kactivitymanagerd >/dev/null 2>&1 &
sleep 1
plasmashell --no-respawn >"$T/plasmashell.log" 2>&1 &
sleep 10
if [[ "$MODO" == claro ]]; then
  plasma-apply-lookandfeel --apply com.noel.axolos.claro >/dev/null 2>&1
  qdbus6 org.kde.KWin /KWin reconfigure; sleep 5
fi
if [[ -n "${DISENO:-}" ]]; then
  plasma-apply-lookandfeel --apply com.noel.axolos$([[ "$MODO" == claro ]] && echo .claro) --resetLayout >/dev/null 2>&1
  sleep 6
fi
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
  'print(panels().map(function(p){return p.location+":"+p.opacity+":"+p.widgets().map(function(w){return w.type}).join(",")}).join(" | "))' \
  >"$T/paneles.txt" 2>&1
for v in ${VENTANAS:-konsole dolphin}; do
  case \$v in
    konsole) konsole --workdir /usr/share/axolos >/dev/null 2>&1 & ;;
    dolphin) dolphin /usr/share/wallpapers >/dev/null 2>&1 & ;;
    nautilus) nautilus --new-window /usr/share/wallpapers >/dev/null 2>&1 & ;;
    *) \$v >/dev/null 2>&1 & ;;
  esac
  sleep 4
done
[[ -n "${AVISO:-}" ]] && notify-send -a AxolOS -i axolos "Liquid glass" "Panels, menus and windows refract what is behind them"
[[ -n "${MENU:-}" ]] && qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.activateLauncherMenu
sleep ${ESPERA:-3}
spectacle -b -n -f -o "$SALIDA" >/dev/null 2>&1
EOF
chmod +x "$T/sesion.sh"

export XDG_CONFIG_HOME="$T/config" XDG_DATA_HOME="$T/data" XDG_CACHE_HOME="$T/cache" XDG_RUNTIME_DIR="$RUN"
export XDG_CONFIG_DIRS="$T/config/kdedefaults:/etc/xdg" QT_PLUGIN_PATH="$T/plugins:/usr/lib/qt6/plugins"
export AXOLOS_LIB="$T/lib"
export KDE_FULL_SESSION=true XDG_CURRENT_DESKTOP=KDE
# libadwaita sigue el modo por el portal, que en el KWin virtual no está: se le dice aquí
export ADW_DEBUG_COLOR_SCHEME=$([[ $MODO == claro ]] && echo prefer-light || echo prefer-dark)
[[ -n "${IDIOMA:-}" ]] && export LANGUAGE=$IDIOMA LANG=en_US.UTF-8
unset WAYLAND_DISPLAY DISPLAY DBUS_SESSION_BUS_ADDRESS
timeout 120 dbus-run-session -- kwin_wayland --virtual --width 1920 --height 1080 --socket "axp-$$" \
  --exit-with-session "$T/sesion.sh" >"$T/kwin.log" 2>&1 || true
cat "$T/paneles.txt" 2>/dev/null || true
[[ -s $SALIDA ]] && echo "captura: $SALIDA" || { echo "sin captura"; tail -20 "$T/kwin.log"; exit 1; }
