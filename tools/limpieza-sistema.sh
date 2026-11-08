#!/usr/bin/env bash
# =============================================================================
#  AxolOS · limpieza-sistema.sh   (ejecutar UNA vez con: sudo bash ...)
#  1. Sustituye cachyos-kde-settings por los paquetes AxolOS
#  2. Desinstala temas/iconos/fondos de sistema que no se usan
#  3. Mueve a copia de seguridad lo suelto sin dueño (tema SDDM omarchy, logo viejo)
#  No toca: WindozeXP (arranque, en uso), fuentes, ni nada de tu /home.
# =============================================================================
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Ejecútalo con sudo"; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USR="${SUDO_USER:-noel}"
HOMEU=$(getent passwd "$USR" | cut -d: -f6)
BK="$HOMEU/.axolos-limpieza/$(date +%Y%m%d-%H%M%S)/sistema"
LOG="$ROOT/build/limpieza-sistema.log"
mkdir -p "$ROOT/build" "$BK"
exec > >(tee "$LOG") 2>&1

say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }

say "1/3 Instalando AxolOS en el sistema"
if pacman -Qq cachyos-kde-settings >/dev/null 2>&1 && ! pacman -Qq axolos-kde-settings >/dev/null 2>&1; then
  pacman -R --noconfirm cachyos-kde-settings
fi
pacman -U --noconfirm --needed \
  --overwrite '/usr/share/color-schemes/AxolOS*' \
  --overwrite '/usr/share/pixmaps/axolos*' \
  "$ROOT"/repo/axolos-*.pkg.tar.zst
# Fondo de SDDM (el .install solo lo pone si no existía)
grep -q '^ID=axolos' /usr/lib/os-release && echo "   os-release: AxolOS ✔"

say "2/3 Desinstalando temas de sistema sin usar"
UNUSED=(
  whitesur-icon-theme            # iconos WhiteSur (usas Yaru-purple-dark)
  cachyos-nord-kde-theme-git char-white
  cachyos-emerald-kde-theme-git
  cachyos-iridescent-kde
  capitaine-cursors              # cursor (usas WhiteSur-cursors)
  cachyos-wallpapers
  cachyos-plymouth-theme cachyos-plymouth-bootanimation   # arranque (usas WindozeXP)
)
mapfile -t present < <(pacman -Qq "${UNUSED[@]}" 2>/dev/null || true)
if ((${#present[@]})); then
  pacman -Rs --noconfirm "${present[@]}"
else
  echo "   (ya no queda ninguno)"
fi

say "3/3 Guardando en copia lo suelto sin paquete"
for f in /usr/share/sddm/themes/omarchy /usr/local/share/pixmaps/cachy-custom-logo.png; do
  if [[ -e $f ]] && ! pacman -Qoq "$f" >/dev/null 2>&1; then
    mkdir -p "$BK$(dirname "$f")"; mv "$f" "$BK$f"; echo "   movido: $f"
  fi
done
rmdir /usr/local/share/pixmaps 2>/dev/null || true
chown -R "$USR:$USR" "$HOMEU/.axolos-limpieza"

say "TERMINADO-OK  (copia: $BK)"
