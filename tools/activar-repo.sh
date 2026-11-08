#!/usr/bin/env bash
# =============================================================================
#  AxolOS · activar-repo.sh   (ejecútalo como tu usuario; pide la contraseña)
#  Pasa este equipo al repositorio online de AxolOS: desde entonces
#  «sudo pacman -Syu» actualiza también AxolOS, como en cualquier instalación nueva.
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER="https://github.com/SrNoelll/axolos/releases/download/x86_64"
FPR=$(<"$ROOT/iso/instalador/axolos.fpr")
say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
[[ $EUID -eq 0 ]] && { echo "Ejecútalo como tu usuario, sin sudo delante."; exit 1; }

if ! curl -fsIL --max-time 20 "$SERVER/axolos.db" >/dev/null; then
  echo "El repositorio aún no está publicado. Primero:  $ROOT/tools/publicar-repo.sh"
  exit 1
fi

say "1/3 Confiando en la clave de AxolOS ($FPR)"
sudo pacman-key --add "$ROOT/iso/instalador/axolos.gpg"
sudo pacman-key --lsign-key "$FPR"

say "2/3 Añadiendo [axolos] a /etc/pacman.conf"
if grep -q '^\[axolos\]' /etc/pacman.conf; then
  echo "   ya estaba"
else
  sudo cp /etc/pacman.conf "/etc/pacman.conf.antes-de-axolos"
  printf '\n# AxolOS: tema, Bento, Axo, herramientas de desarrollo (paquetes firmados)\n[axolos]\nServer = %s\n' \
    "$SERVER" | sudo tee -a /etc/pacman.conf >/dev/null
  echo "   copia de la configuración anterior: /etc/pacman.conf.antes-de-axolos"
fi

say "3/3 Actualizando el sistema con el repositorio de AxolOS"
sudo pacman -Syu --needed axolos-keyring axolos-desktop
say "Listo: «sudo pacman -Syu» ya trae también las novedades de AxolOS."
