#!/usr/bin/env bash
# =============================================================================
#  AxolOS · build-iso.sh
#  Crea la ISO instalable de AxolOS a partir de la ISO oficial de CachyOS
#  (github.com/CachyOS/CachyOS-Live-ISO) + tus paquetes AxolOS.
#
#  Necesita: archiso, git, grub (solo sus herramientas: no cambia tu arranque), ~25 GB libres, conexión a internet y sudo.
#      sudo pacman -S --needed archiso git grub
#      ./build-iso.sh               (usa los paquetes de repo/, los publicados)
#      ./build-iso.sh --recompilar  (los compila antes)
#  Resultado: ./out/axolos-*.iso
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$ROOT/build/iso"
UP="$WORK/CachyOS-Live-ISO"
P="$UP/archiso"
REF="${CACHYOS_ISO_REF:-master}"   # puedes fijar una versión: CACHYOS_ISO_REF=<commit>

say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
die() { printf '\e[1;31m!!\e[0m %s\n' "$*"; exit 1; }
[[ $EUID -eq 0 ]] && die "Ejecútalo como tu usuario (el script pedirá sudo)."
command -v mkarchiso >/dev/null || die "Falta archiso:  sudo pacman -S --needed archiso"
command -v git >/dev/null       || die "Falta git:  sudo pacman -S --needed git"
command -v grub-install >/dev/null || die "Falta grub (la ISO lo usa para arrancar en UEFI; no cambia el arranque de tu equipo):  sudo pacman -S --needed grub"

say "1/5 Paquetes AxolOS"
# Por defecto se usan los de repo/: son los mismos que publica tools/publicar-repo.sh (firmados y
# compilados desde una carpeta neutra). --recompilar los vuelve a compilar aquí.
faltan=()
for p in $(grep -v '^#' "$ROOT/iso/packages.add"); do
  [[ $p == axolos-* || $p == yaru-icon-theme || $p == whitesur-cursor-theme-git || $p == ttf-ia-writer ]] || continue
  compgen -G "$ROOT/repo/$p-[0-9r]*.pkg.tar.zst" >/dev/null || faltan+=("$p")
done
if [[ ${1:-} == --recompilar ]] || ((${#faltan[@]})) || [[ ! -e $ROOT/repo/axolos.db ]]; then
  ((${#faltan[@]})) && echo "   faltan en repo/: ${faltan[*]}"
  "$ROOT/build-packages.sh"
else
  echo "   uso los paquetes de repo/ ($(ls -1 "$ROOT"/repo/*.pkg.tar.zst | wc -l), los publicados)"
fi

say "2/5 Descargando la base de CachyOS ($REF)"
mkdir -p "$WORK"
if [[ -d $UP/.git ]]; then
  git -C "$UP" fetch -q origin "$REF" && git -C "$UP" reset -q --hard FETCH_HEAD && git -C "$UP" clean -qfdx -e /build -e /out
  # build/ y out/ son de root (mkarchiso): build/ lo borra buildiso.sh con sudo al empezar
else
  git clone -q https://github.com/CachyOS/CachyOS-Live-ISO "$UP" && git -C "$UP" checkout -q "$REF"
fi
echo "   base: $(git -C "$UP" log -1 --format='%h %s')"

say "3/5 Aplicando AxolOS al perfil"
list="$P/packages_desktop.x86_64"
[[ -f $list ]] || die "No encuentro $list (¿ha cambiado el repo de CachyOS?)"
tmp=$(mktemp)
grep -vxF -f <(grep -v '^#' "$ROOT/iso/packages.remove") "$list" > "$tmp" || true
{ echo; echo "# --- AxolOS ---"; grep -v '^#' "$ROOT/iso/packages.add"; } >> "$tmp"
mv "$tmp" "$list"

# Repositorio local con los paquetes AxolOS, antes que los de CachyOS
awk -v repo="$ROOT/repo" '
  !done && /^\[(cachyos|core)/ { print "[axolos]\nSigLevel = Optional TrustAll\nServer = file://" repo "\n"; done=1 }
  { print }' "$P/pacman.conf" > "$P/pacman.conf.new" && mv "$P/pacman.conf.new" "$P/pacman.conf"

# Nombre de la ISO
sed -i -e 's/^iso_name=.*/iso_name="axolos"/' \
       -e 's/COS_/AXOLOS_/' \
       -e 's|^iso_publisher=.*|iso_publisher="AxolOS <Noel Alarcón>"|' \
       -e 's|^iso_application=.*|iso_application="AxolOS Live"|' "$P/profiledef.sh"

# Los hooks del live que apuntan a la config KDE de CachyOS -> la de AxolOS
grep -rl 'Target = cachyos-kde-settings' "$P/airootfs/etc/pacman.d/hooks" 2>/dev/null \
  | xargs -r sed -i 's/Target = cachyos-kde-settings/Target = axolos-kde-settings/'

# Ficheros propios del sistema live (os-release, hostname, y la Bienvenida marcada como hecha
# en el live: se usa en el sistema instalado, no encima del instalador)
cp -a "$ROOT/iso/airootfs/." "$P/airootfs/"

# mkarchiso no conserva los permisos de airootfs: los ejecutables se declaran en profiledef.sh
# (si no, el lanzador «Instalar AxolOS» quedaría sin permiso de ejecución)
ejecutables=(/usr/share/axolos/instalador/aplicar-axolos.sh)
while IFS= read -r f; do ejecutables+=("/${f#./}"); done < <(cd "$ROOT/iso/airootfs" && find . -type f -perm -u+x)
for f in "${ejecutables[@]}"; do
  grep -qF "[\"$f\"]" "$P/profiledef.sh" || sed -i "/^file_permissions=(/a\\  [\"$f\"]=\"0:0:755\"" "$P/profiledef.sh"
done

# Capa AxolOS sobre el instalador de CachyOS. El instalador se actualiza solo al arrancar la ISO
# (calamares-online.sh hace «pacman -Sy cachyos-calamares-next»), así que la capa se aplica
# justo DESPUÉS de esa actualización; si se tocara aquí /etc/calamares, se perdería.
# Log propio: calamares-online.sh vacía el suyo («inxi -F > $log») justo después.
I="$P/airootfs/usr/share/axolos/instalador"
install -Dm755 "$ROOT/iso/instalador/aplicar-axolos.sh" "$I/aplicar-axolos.sh"
# Marca del instalador (tools/instalador_marca_axolos.py): textos, logos, colores y presentación
[[ -f $ROOT/iso/instalador/marca/axolos/branding.desc ]] || die "Falta la marca del instalador: tools/instalador_marca_axolos.py"
cp -r "$ROOT/iso/instalador/marca" "$I/"
# Instalación sin conexión: pasos de AxolOS y paquetes que el live no lleva (SDDM, Limine)
mkdir -p "$I/offline"
cp "$ROOT"/iso/instalador/offline/*.conf "$ROOT/iso/instalador/offline/limpiar-live.sh" "$I/offline/"
"$ROOT/iso/paquetes-offline.sh" "$list" "$I/offline/paquetes" || die "No pude preparar los paquetes de la instalación sin conexión"
curl -fsSL --max-time 60 -o "$I/netinstall-cachyos.yaml" \
  https://raw.githubusercontent.com/CachyOS/cachyos-calamares/cachyos-dev/src/modules/netinstall/netinstall.yaml \
  || die "No pude descargar la lista de paquetes de CachyOS (netinstall.yaml)"
grep -q cachyos-kde-settings "$I/netinstall-cachyos.yaml" || die "netinstall.yaml de CachyOS ha cambiado: revisa aplicar-axolos.sh"
co="$P/airootfs/usr/local/bin/calamares-online.sh"
[[ -f $co ]] || die "No encuentro $co (¿ha cambiado la ISO de CachyOS?)"
grep -q 'pacman -Sy --noconfirm cachyos-calamares-next' "$co" || die "calamares-online.sh ha cambiado: revisa dónde aplicar la capa AxolOS"
sed -i '/pacman -Sy --noconfirm cachyos-calamares-next/a\    sudo bash /usr/share/axolos/instalador/aplicar-axolos.sh >> /home/liveuser/axolos-instalador.log 2>\&1  # AxolOS' "$co"
grep -q 'aplicar-axolos.sh' "$co" || die "No pude enganchar la capa AxolOS al instalador"

# Que el instalador de CachyOS arranque aunque vaya compilado contra una boost anterior
"$ROOT/iso/compat-calamares.sh" "$P/airootfs" || die "No pude preparar las librerías que necesita el instalador"

# Menú de arranque de la ISO: fondo y nombres de AxolOS (solo los textos visibles; ids y rutas igual)
install -m644 "$ROOT/iso/arranque/splash.png" "$P/grub/splash.png"
install -m644 "$ROOT/iso/arranque/splash.png" "$P/syslinux/splash.png"
sed -i -E '/^[[:space:]]*menuentry /s/CachyOS/AxolOS/' "$P"/grub/*.cfg
sed -i -E '/^[[:space:]]*MENU (TITLE|LABEL)/s/CachyOS/AxolOS/' "$P"/syslinux/*.cfg
find "$P/efiboot" -name '*.conf' -exec sed -i -E '/^title/s/CachyOS/AxolOS/' {} +

# El script de CachyOS renombra la ISO buscando «cachyos-FECHA-x86_64.iso»: con nuestro iso_name se llama axolos-…
u="$UP/util-iso.sh"
sed -i -e 's|/cachyos-\$(date|/axolos-$(date|' -e 's|vars+=("cachyos")|vars+=("axolos")|' "$u"
grep -q '/axolos-\$(date' "$u" && grep -q 'vars+=("axolos")' "$u" || die "util-iso.sh de CachyOS ha cambiado: revisa el nombre de la ISO"

# La ISO instala desde la caché de pacman de este equipo si ya tiene el archivo: si una copia no
# coincide con la de repo/ (p. ej. un paquete recompilado con la misma versión), pacman la daría por
# corrupta y fallaría. Se quitan esas copias de la caché; la buena está en repo/.
malas=()
for f in "$ROOT"/repo/*.pkg.tar.zst; do
  c="/var/cache/pacman/pkg/${f##*/}"
  [[ -f $c ]] && ! cmp -s "$f" "$c" && malas+=("$c" "$c.sig")
done
if ((${#malas[@]})); then
  echo "   quitando de la caché de pacman $((${#malas[@]}/2)) copias que no coinciden con repo/"
  sudo rm -f "${malas[@]}"
fi

# buildiso.sh de CachyOS imprime «ERROR: An unknown error» al salir SIEMPRE (trap EXIT), también
# cuando todo ha ido bien. Se desactiva solo tras terminar con éxito: los fallos de verdad se siguen viendo.
b="$UP/buildiso.sh"
grep -q '^run_build "${build_list_iso}"$' "$b" || die "buildiso.sh de CachyOS ha cambiado: revisa el aviso final"
sed -i '/^run_build "${build_list_iso}"$/a trap - EXIT  # AxolOS' "$b"

say "4/5 Construyendo la ISO (tarda un buen rato)"
(cd "$UP" && ./buildiso.sh -p desktop -w)

say "5/5 Copiando el resultado"
mkdir -p "$ROOT/out"
find "$UP/out" -type f \( -name '*.iso*' -o -name '*.pkgs.txt' \) -exec mv -f -t "$ROOT/out/" {} +
FPR=$(<"$ROOT/iso/instalador/axolos.fpr")
for iso in "$ROOT"/out/*.iso; do
  [[ -f $iso.sha256 && $iso.sha256 -nt $iso ]] || (cd "$ROOT/out" && sha256sum "${iso##*/}" > "${iso##*/}.sha256")
  if gpg --list-secret-keys "$FPR" >/dev/null 2>&1 && ! [[ -f $iso.sig && $iso.sig -nt $iso ]]; then
    gpg --batch --yes -u "$FPR" --detach-sign --no-armor "$iso"     # firma AxolOS: gpg --verify x.iso.sig x.iso
  fi
done
ls -lh "$ROOT/out"
