#!/usr/bin/env bash
# =============================================================================
#  AxolOS · paquetes-offline.sh LISTA_DEL_LIVE DESTINO
#  La instalación sin conexión copia el sistema live al disco. AxolOS necesita además SDDM (su
#  pantalla de inicio de sesión) y Limine (el arranque), que el live no lleva: el gancho de
#  limine-mkinitcpio-hook cambiaría cómo se genera el propio initramfs del live. Así que van en
#  la ISO como archivos y se instalan solo en el sistema nuevo.
#  Calcula lo que falta (esos paquetes y sus dependencias que no estén ya en el live) y lo descarga.
# =============================================================================
set -euo pipefail
LISTA=${1:?uso: $0 LISTA_DEL_LIVE DESTINO}; DESTINO=${2:?uso: $0 LISTA_DEL_LIVE DESTINO}
OBJETIVOS=(sddm limine limine-mkinitcpio-hook)
say() { echo "   $*"; }

# Todo lo que tendrá el live: su lista de paquetes y sus dependencias
mapfile -t base < <(grep -v -E '^\s*(#|$)' "$LISTA" | awk '{print $1}' | sort -u)
live=$(for p in "${base[@]}"; do pactree -s -lu "$p" 2>/dev/null || echo "$p"; done | sort -u)
# Lo que necesitan los objetivos y el live no tiene (los nombres virtuales —libgl, awk, so…— los
# da algún paquete del live: se descartan, solo cuentan los paquetes reales)
mapfile -t faltan < <(for t in "${OBJETIVOS[@]}"; do pactree -s -lu "$t"; done | sort -u |
  comm -23 - <(printf '%s\n' "$live") |
  while read -r n; do pacman -Si "$n" >/dev/null 2>&1 && echo "$n"; done)
for t in "${OBJETIVOS[@]}"; do
  printf '%s\n' "${faltan[@]}" | grep -qx "$t" || { echo "!! $t ya estaría en el live: revisa la lista" >&2; exit 1; }
done
say "para la instalación sin conexión: ${faltan[*]}"

rm -rf "$DESTINO"; mkdir -p "$DESTINO"
# -Sw descarga sin instalar, a esta carpeta. -dd: solo la lista calculada (las dependencias que pacman
# resolvería serían las que faltan en ESTE equipo, no en el live)
sudo pacman -Sddw --noconfirm --cachedir "$DESTINO" "${faltan[@]}" >/dev/null
sudo chown -R "$(id -u):$(id -g)" "$DESTINO"
rm -f "$DESTINO"/*.sig
for n in "${faltan[@]}"; do
  compgen -G "$DESTINO/$n-[0-9r]*.pkg.tar.zst" >/dev/null || { echo "!! no se descargó $n" >&2; exit 1; }
done
say "descargados: $(ls -1 "$DESTINO" | wc -l) paquetes ($(du -sh "$DESTINO" | cut -f1))"
