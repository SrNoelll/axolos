#!/usr/bin/env bash
# Captura el menú Bento del repositorio dentro de Plasma de verdad (plasmawindowed en un KWin
# virtual e invisible), con tus favoritas, recientes y categorías, en uno o varios idiomas.
#
#   tools/bento-dev/capturar.sh SALIDA_DIR [IDIOMA[:LOCALE] ...]
#   tools/bento-dev/capturar.sh /tmp/bento es en fr ru zh_CN ja
#
# IDIOMA va a LANGUAGE (traducciones); LOCALE a LANG (fechas). La locale tiene que estar
# generada (locale -a): si no, KDE ignora LANGUAGE y todo sale en inglés. Por defecto, tu LANG.
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$(realpath -m "${1:?uso: capturar.sh SALIDA_DIR [IDIOMA[:LOCALE] ...]}")"; shift
(( $# )) || set -- "${LANG%%_*}"
W=$(mktemp -d); sock="axolos-bento-$$"; trap 'rm -rf "$W"' EXIT
mkdir -p "$OUT" "$W/share/plasma/plasmoids"

# copia del plasmoide que abre el menú completo (en el panel sería solo el botón)
cp -r "$R/packages/axolos-menu/org.axolos.bento" "$W/share/plasma/plasmoids/"
sed -i 's/^    preferredRepresentation: .*/    preferredRepresentation: fullRepresentation/' \
    "$W/share/plasma/plasmoids/org.axolos.bento/contents/ui/main.qml"
for po in "$R"/packages/axolos-menu/po/*.po; do
    l=$(basename "$po" .po); mkdir -p "$W/share/locale/$l/LC_MESSAGES"
    msgfmt -o "$W/share/locale/$l/LC_MESSAGES/plasma_applet_org.axolos.bento.mo" "$po"
done

{
    echo '#!/bin/bash'
    echo "export QT_QPA_PLATFORM=wayland WAYLAND_DISPLAY=$sock QT_FORCE_STDERR_LOGGING=1"
    echo "export XDG_DATA_DIRS=$W/share:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
    for par in "$@"; do
        idioma=${par%%:*}; loc=$LANG; [[ $par == *:* ]] && loc=${par#*:}
        echo "LANGUAGE=$idioma LANG=$loc plasmawindowed org.axolos.bento > '$OUT/$idioma.log' 2>&1 &"
        echo 'pid=$!; sleep 7'
        echo "spectacle -b -n -f -o '$OUT/$idioma.png' >/dev/null 2>&1"
        echo 'kill $pid; wait $pid 2>/dev/null'
    done
    echo "touch '$W/hecho'"
} > "$W/run.sh"
chmod +x "$W/run.sh"
timeout $(( 30 + 12 * $# )) dbus-run-session -- kwin_wayland --virtual --width 1280 --height 900 \
    --socket "$sock" --no-lockscreen --no-global-shortcuts "$W/run.sh" > "$W/kwin.log" 2>&1 &
for _ in $(seq 1 $(( 5 * (30 + 12 * $#) ))); do [[ -f $W/hecho ]] && break; sleep 0.2; done
pkill -TERM -f -- "--socket $sock" 2>/dev/null || true; wait 2>/dev/null || true
grep -h -E "\.qml:[0-9]+" "$OUT"/*.log || true
ls "$OUT"/*.png
