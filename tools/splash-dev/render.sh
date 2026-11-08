#!/usr/bin/env bash
# Renderiza la animación de arranque con la GPU, en un KWin virtual e
# invisible (no aparece nada en tu pantalla ni toca tu sesión).
#   render.sh hoja        <salida.png>   puerta 1: hoja de personaje
#   render.sh storyboard  <salida.png>   puerta 2: 9 fotogramas clave
#   render.sh draft       <salida.mp4>   puerta 3: borrador 960x540, 30 fps
#   render.sh final       <salida.mp4>   puerta 4: 1920x1080, 30 fps
set -euo pipefail
DEV="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
what="$1"; out="$(realpath -m "$2")"
work=$(mktemp -d)
case $what in
  hoja)               qml="$DEV/hoja.qml";       qargs=("$out") ;;
  storyboard|draft|final) qml="$DEV/storyboard.qml"; qargs=("$what" "$work") ;;
  t=*)                qml="$DEV/storyboard.qml"; qargs=("$what" "$work") ;;
  *) echo "uso: render.sh hoja|storyboard|draft <salida>"; exit 1 ;;
esac
inner="$work/run.sh"
sock="axolos-dev-$$"          # nombre único: solo cerraremos este KWin
{
  echo '#!/bin/bash'
  echo "export QT_QPA_PLATFORM=wayland WAYLAND_DISPLAY=$sock QT_FORCE_STDERR_LOGGING=1"
  printf '/usr/lib/qt6/bin/qml %q --' "$qml"; printf ' %q' "${qargs[@]}"; echo
  printf 'touch %q\n' "$work/done"
} > "$inner"
chmod +x "$inner"
timeout 180 dbus-run-session -- kwin_wayland --virtual --width 1920 --height 1080 \
  --socket "$sock" --no-lockscreen --no-global-shortcuts "$inner" > "$work/kwin.log" 2>&1 &
for _ in $(seq 1 1800); do [[ -f $work/done ]] && break; sleep 0.1; done
pkill -TERM -f -- "--socket $sock" 2>/dev/null || true
wait 2>/dev/null || true
grep -E "qml:|\.qml:[0-9]+|\.js:[0-9]+" "$work/kwin.log" || true

case $what in
  storyboard)
    titles=("Se enciende" "Anticipación" "Primer paso" "Pies apoyados" "Frena" "Coletazo" "Abre el ojo" "Iris de luz" "Tu escritorio")
    actions=("su luz sube en la oscuridad" "se echa atrás antes de arrancar" "pares diagonales, como un ajolote"
             "cada pie apoyado no resbala" "se pasa 24 px y vuelve" "la cola rebota y se calma"
             "destello en el ojo" "la luz sale de su ojo y enciende los tubos" "KSplash se cierra: ya es tu fondo")
    stamps=("0,06 s" "0,12 s" "0,40 s" "0,78 s" "1,12 s" "1,30 s" "1,35 s" "1,62 s" "2,30 s")
    for n in $(seq 0 8); do
      f=$(printf "%s/f-%04d.png" "$work" "$n")
      magick "$f" -resize 600x338 -background '#0b0b0e' -gravity south -splice 0x64 \
        -font "New-York-Extra-Large-Regular" -fill '#e8e8ee' -pointsize 22 -gravity southwest -annotate +14+34 "${titles[$n]}" \
        -font "iA-Writer-Mono-S-Regular" -fill '#8a8a94' -pointsize 13 -annotate +14+12 "${actions[$n]}" \
        -fill '#926ee4' -gravity southeast -annotate +14+38 "${stamps[$n]}" "$work/c-$n.png" 2>/dev/null \
      || magick "$f" -resize 600x338 -background '#0b0b0e' -gravity south -splice 0x64 \
        -fill '#e8e8ee' -pointsize 22 -gravity southwest -annotate +14+34 "${titles[$n]}" \
        -fill '#8a8a94' -pointsize 13 -annotate +14+12 "${actions[$n]}" \
        -fill '#926ee4' -gravity southeast -annotate +14+38 "${stamps[$n]}" "$work/c-$n.png"
    done
    magick montage "$work"/c-{0..8}.png -tile 3x -geometry +10+10 -background '#0b0b0e' "$out" ;;
  t=*) cp "$work/f-0000.png" "$out" ;;
  final)
    ffmpeg -loglevel error -y -framerate 30 -i "$work/f-%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -movflags +faststart "$out" ;;
  draft)
    ffmpeg -loglevel error -y -framerate 30 -i "$work/f-%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart "$out"
    # una sola imagen de control: hoja de contactos con ffmpeg (select + tile)
    ffmpeg -loglevel error -y -i "$out" -vf "select='not(mod(n\,6))',scale=320:-1,tile=4x4" -frames:v 1 "${out%.mp4}-contactos.png" ;;
esac
rm -rf "$work"
ls -la "$out"
