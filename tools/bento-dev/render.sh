#!/usr/bin/env bash
# Renderiza la maqueta del menú Bento con la GPU en un KWin virtual e invisible.
set -euo pipefail
DEV="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$(realpath -m "$1")"; work=$(mktemp -d); sock="axolos-bento-$$"
cat > "$work/run.sh" <<EOS
#!/bin/bash
export QT_QPA_PLATFORM=wayland WAYLAND_DISPLAY=$sock QT_FORCE_STDERR_LOGGING=1
/usr/lib/qt6/bin/qml "$DEV/maqueta.qml" -- "$out" > "$work/qml.log" 2>&1
touch "$work/done"
EOS
chmod +x "$work/run.sh"
timeout 60 dbus-run-session -- kwin_wayland --virtual --width 1920 --height 1080 --socket "$sock" \
  --no-lockscreen --no-global-shortcuts "$work/run.sh" > "$work/kwin.log" 2>&1 &
for _ in $(seq 1 300); do [[ -f $work/done ]] && break; sleep 0.2; done
pkill -TERM -f -- "--socket $sock" 2>/dev/null || true; wait 2>/dev/null || true
grep -E "\.qml:[0-9]+" "$work/qml.log" || true
rm -rf "$work"; ls -la "$out"
