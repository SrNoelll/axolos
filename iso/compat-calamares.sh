#!/usr/bin/env bash
# =============================================================================
#  AxolOS · compat-calamares.sh <airootfs>
#  El instalador de CachyOS (cachyos-calamares-next) a veces va compilado contra una versión de
#  boost anterior a la de los repositorios (depende de «boost-libs» sin versión). Entonces no arranca:
#      calamares: error while loading shared libraries: libboost_python314.so.1.91.0
#  Este script lo detecta al construir la ISO y, solo si hace falta, añade al sistema live las
#  librerías de boost que pide, sacadas del archivo oficial de Arch y con la firma comprobada.
#  Van con su número de versión en el nombre: no chocan con las de boost-libs ni llegan al
#  sistema instalado. Cuando CachyOS recompile el instalador, deja de añadirse nada.
# =============================================================================
set -euo pipefail
AIROOTFS=${1:?uso: $0 <airootfs>}
ARCHIVO=https://archive.archlinux.org/packages/b/boost-libs
KEYRING=/usr/share/pacman/keyrings/archlinux.gpg
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
say() { echo "   $*"; }

paquete() {  # descarga (o toma de la caché) el paquete de los repositorios: imprime la ruta
  local url; url=$(pacman -Sddp "$1" 2>/dev/null | tail -1)
  [[ -n $url ]] || { echo "No encuentro $1 en los repositorios" >&2; return 1; }
  if [[ $url == file://* ]]; then echo "${url#file://}"
  else curl -fsSL --max-time 120 -o "$T/$1.pkg.tar.zst" "$url" && echo "$T/$1.pkg.tar.zst"; fi
}
necesita_boost() {  # sonames de boost que piden los binarios de un directorio
  find "$1" -type f \( -name '*.so*' -o -perm -u+x \) -exec readelf -d {} + 2>/dev/null \
    | grep -o 'libboost_[^]]*\.so\.[0-9.]*' | sort -u
}

cal=$(paquete cachyos-calamares-next); mkdir -p "$T/cal"; bsdtar -xf "$cal" -C "$T/cal" usr
bv=$(pacman -Si boost-libs | awk -F': *' '/^(Versión|Version) /{print $2; exit}'); bv=${bv%%-*}
mapfile -t piden < <(necesita_boost "$T/cal")
faltan=(); for s in "${piden[@]}"; do [[ $s == *".so.$bv" ]] || faltan+=("$s"); done
# Lista de lo añadido: la instalación sin conexión lo quita del sistema nuevo (offline/limpiar-live.sh)
MANIFIESTO="$AIROOTFS/usr/share/axolos/instalador/compat-libs.txt"
mkdir -p "${MANIFIESTO%/*}"; : > "$MANIFIESTO"
if ((${#faltan[@]} == 0)); then
  say "instalador de CachyOS y boost $bv coinciden: no hace falta nada"
  exit 0
fi

# Versión que pide (todas las sonames de boost de una compilación comparten versión)
v=${faltan[0]##*.so.}
say "el instalador de CachyOS pide boost $v y los repositorios tienen $bv: añado ${faltan[*]}"
rel=$(curl -fsSL --max-time 30 "$ARCHIVO/" | grep -o "boost-libs-$v-[0-9.]*-x86_64\.pkg\.tar\.zst\"" | tr -d '"' | sort -V | tail -1)
[[ -n $rel ]] || { echo "No encuentro boost-libs $v en $ARCHIVO" >&2; exit 1; }
curl -fsSL --max-time 300 -o "$T/$rel" "$ARCHIVO/$rel"
curl -fsSL --max-time 60 -o "$T/$rel.sig" "$ARCHIVO/$rel.sig"
# Firma de un empaquetador de Arch (llavero oficial, en un gpg temporal)
G="$T/gnupg"; mkdir -m700 "$G"
gpg --homedir "$G" --batch --quiet --import "$KEYRING" 2>/dev/null
gpg --homedir "$G" --batch --status-fd 1 --verify "$T/$rel.sig" "$T/$rel" 2>/dev/null | grep -q '^\[GNUPG:\] VALIDSIG' \
  || { echo "La firma de $rel no es válida" >&2; exit 1; }
say "firma de Arch correcta: $rel"

mkdir -p "$T/boost"; bsdtar -xf "$T/$rel" -C "$T/boost" usr/lib
# Las que pide el instalador y, a su vez, las de boost que pidan esas
pendientes=("${faltan[@]}"); puestas=()
while ((${#pendientes[@]})); do
  s=${pendientes[0]}; pendientes=("${pendientes[@]:1}")
  [[ " ${puestas[*]} " == *" $s "* ]] && continue
  [[ -f $T/boost/usr/lib/$s ]] || { echo "boost-libs $v no trae $s" >&2; exit 1; }
  install -Dm644 "$T/boost/usr/lib/$s" "$AIROOTFS/usr/lib/$s"
  puestas+=("$s")
  while read -r d; do [[ $d == *".so.$v" ]] && pendientes+=("$d"); done < <(readelf -d "$T/boost/usr/lib/$s" | grep -o 'libboost_[^]]*\.so\.[0-9.]*')
done
printf '%s\n' "${puestas[@]}" > "$MANIFIESTO"
say "añadidas al live: ${puestas[*]}"
