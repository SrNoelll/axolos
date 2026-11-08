#!/usr/bin/env bash
# =============================================================================
#  AxolOS · build-packages.sh
#  Compila los paquetes de AxolOS (+ los del AUR que necesita el tema) y los
#  deja en ./repo como un repositorio de pacman llamado "axolos".
#
#    ./build-packages.sh            todo
#    ./build-packages.sh --no-aur   solo los paquetes axolos-* (rápido)
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$ROOT/repo"
BUILD="$ROOT/build"

AXOLOS_PKGS=(axolos-keyring axolos-branding axolos-themes axolos-menu axolos-kde-settings axolos-dev axolos-ia axolos-bienvenida axolos-desktop)
# Del AUR: los que el tema necesita y no están en los repos de CachyOS/Arch
# apple-fonts NO se publica: su licencia no permite redistribuirla (opcional, con respaldo libre)
AUR_PKGS=(yaru-icon-theme whitesur-cursor-theme-git ttf-ia-writer)
# AXOLOS_SOLO="axolos-x axolos-y": compilar solo esos (los demás ya están en repo/ y no se tocan)
[[ -v AXOLOS_SOLO ]] && read -ra AXOLOS_PKGS <<<"$AXOLOS_SOLO"

with_aur=true
[[ ${1:-} == --no-aur ]] && with_aur=false
[[ $EUID -eq 0 ]] && { echo "No lo ejecutes como root (makepkg no lo permite)."; exit 1; }

say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
mkdir -p "$REPO" "$BUILD/makepkg" "$BUILD/aur"
export PKGDEST="$REPO" BUILDDIR="$BUILD/makepkg" SRCDEST="$BUILD/src"
# Firma: si en este equipo está la clave de AxolOS, se firman paquetes y base de datos
FPR=${AXOLOS_FPR:-$(<"$ROOT/iso/instalador/axolos.fpr")}   # AXOLOS_FPR: otra clave (pruebas)
FIRMA=()
if gpg --list-secret-keys "$FPR" >/dev/null 2>&1; then
  FIRMA=(--sign --key "$FPR")
  export PACKAGER="AxolOS <159236885+SrNoelll@users.noreply.github.com>" GPGKEY="$FPR"
fi
mkdir -p "$SRCDEST"

[[ -f $ROOT/packages/axolos-themes/.wallpaper-file ]] || {
  say "Primero hay que copiar tu escritorio al pack"; "$ROOT/collect.sh"; }

for p in "${AXOLOS_PKGS[@]}"; do
  say "Compilando $p"
  # -d: no exige tener ya instaladas las dependencias (algunas son del AUR)
  (cd "$ROOT/packages/$p" && makepkg -f -d --noconfirm "${FIRMA[@]}")
done

if $with_aur; then
  for p in "${AUR_PKGS[@]}"; do
    if compgen -G "$REPO/$p-[0-9r]*.pkg.tar.zst" >/dev/null; then
      say "$p ya está compilado (borra repo/$p-* para recompilarlo)"; continue
    fi
    say "Compilando $p desde el AUR"
    if [[ -d $BUILD/aur/$p/.git ]]; then git -C "$BUILD/aur/$p" pull -q
    else git clone -q --depth 1 "https://aur.archlinux.org/$p.git" "$BUILD/aur/$p"; fi
    # -s instala lo necesario para compilar (pedirá sudo)
    (cd "$BUILD/aur/$p" && makepkg -f -s --noconfirm --needed)
  done
fi

say "Actualizando el índice del repositorio"
if ((${#FIRMA[@]})); then      # los paquetes del AUR se compilan sin firma: se firman aquí
  for f in "$REPO"/*.pkg.tar.zst; do
    [[ -f $f.sig ]] || gpg --batch --yes -u "$FPR" --detach-sign --no-armor "$f"
  done
fi
rm -f "$REPO"/axolos.db* "$REPO"/axolos.files*
repo-add -q -n -R ${FIRMA:+--sign --key "$FPR"} "$REPO/axolos.db.tar.gz" "$REPO"/*.pkg.tar.zst
say "Paquetes listos en $REPO:"
ls -1 "$REPO"/*.pkg.tar.zst | sed 's#.*/#   #'
