#!/usr/bin/env bash
# =============================================================================
#  AxolOS · install.sh
#  Convierte una instalación de CachyOS (KDE) en AxolOS sin reinstalar.
#
#    ./install.sh             instala los paquetes AxolOS (marca + tema + ajustes)
#    ./install.sh --apply     además aplica el aspecto a TU usuario
#                             (guarda copia de lo que sustituye)
#    ./install.sh --apps      además instala tus aplicaciones (pkglists/)
#
#  Los usuarios creados después de instalar reciben AxolOS automáticamente.
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$ROOT/repo"
say()  { printf '\e[1;35m==>\e[0m %s\n' "$*"; }

apply=false apps=false
for a in "$@"; do
  case $a in
    --apply) apply=true ;;
    --apps)  apps=true ;;
    -h|--help) sed -n '3,11p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $a"; exit 1 ;;
  esac
done
[[ $EUID -eq 0 ]] && { echo "Ejecútalo como tu usuario (pedirá sudo cuando haga falta)."; exit 1; }
command -v pacman >/dev/null || { echo "Esto solo funciona en CachyOS/Arch."; exit 1; }

"$ROOT/build-packages.sh"

say "Instalando AxolOS"
echo "   Si pacman pregunta por reemplazar cachyos-kde-settings, responde 's' (sí)."
mapfile -t pkgs < <(ls "$REPO"/*.pkg.tar.zst)
# --overwrite: ficheros AxolOS que quizá copiaste a mano antes de tener el pack
sudo pacman -U --needed \
  --overwrite '/usr/share/color-schemes/AxolOS*' \
  --overwrite '/usr/share/plasma/look-and-feel/com.noel.axolos/*' \
  --overwrite '/usr/share/pixmaps/axolos*' \
  "${pkgs[@]}"

if $apply; then
  backup="$HOME/.axolos-backup/$(date +%Y%m%d-%H%M%S)"
  say "Aplicando AxolOS a $USER (copia de seguridad en $backup)"
  while IFS= read -r -d '' f; do
    rel="${f#/etc/skel/}"
    if [[ -e $HOME/$rel ]]; then mkdir -p "$backup/$(dirname "$rel")"; cp -a "$HOME/$rel" "$backup/$rel"; fi
    mkdir -p "$HOME/$(dirname "$rel")"; cp "$f" "$HOME/$rel"
  done < <(pacman -Qlq axolos-kde-settings | grep '^/etc/skel/.*[^/]$' | tr '\n' '\0')
  plasma-apply-lookandfeel -a com.noel.axolos >/dev/null 2>&1 || true
  echo "   Cierra sesión y vuelve a entrar para ver el panel y el dock nuevos."
fi

$apps && axolos-apps

say "Listo. Bienvenido a AxolOS 🦎"
