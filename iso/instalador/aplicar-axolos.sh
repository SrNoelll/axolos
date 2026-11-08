#!/usr/bin/env bash
# =============================================================================
#  AxolOS · capa sobre el instalador de CachyOS (se ejecuta en la ISO, como root)
#
#  El instalador de CachyOS se descarga actualizado al arrancar la ISO
#  (cachyos-calamares-next) e instala por internet: el sistema queda al día y con
#  los repositorios optimizados para el procesador (v3/v4/znver4) y los
#  controladores de la gráfica (chwd). Esta capa se aplica DESPUÉS de esa
#  actualización y solo cambia lo necesario para que el sistema instalado sea AxolOS:
#    1. añade el repositorio [axolos] a la configuración de pacman del sistema nuevo
#    2. la lista de paquetes de Plasma instala axolos-desktop (en vez de cachyos-kde-settings)
#       y no instala cachyos-hello (la bienvenida de AxolOS es axolos-bienvenida)
#    3. pantalla de arranque AxolOS (Plymouth)
#    4. inicio de sesión con SDDM (tema AxolOS) en vez de plasma-login-manager
#    5. menú de arranque (Limine) con un solo grupo, «AxolOS»
#    6. aspecto de Limine (fondo y colores) de AxolOS
#    7. marca del instalador: «Instalador de AxolOS», logos, colores y presentación
#    8. página «Escritorio» con solo AxolOS · KDE Plasma
#    9. textos con «CachyOS» escritos a mano (pasos, instantánea inicial, Limine-snapper)
#   10. instalación sin conexión (modo offline de CachyOS) completa como AxolOS
#  La clave de AxolOS la confía el propio instalador: su «pacman-key --populate»
#  importa todas las de /usr/share/pacman/keyrings, y la ISO trae axolos-keyring.
# =============================================================================
set -uo pipefail
ETC="${AXOLOS_ETC:-/etc}"                       # para probarlo fuera de la ISO
DATOS="${AXOLOS_DATOS:-/usr/share/axolos/instalador}"
CAL_LIB="${AXOLOS_CAL_LIB:-/usr/lib/calamares}"
SERVER="https://github.com/SrNoelll/axolos/releases/download/x86_64"
NETINSTALL_URL="https://raw.githubusercontent.com/CachyOS/cachyos-calamares/cachyos-dev/src/modules/netinstall/netinstall.yaml"
log() { echo "[AxolOS] $*"; }

# 1. Repositorio AxolOS en el pacman.conf que se copia al sistema instalado
if [[ -f $ETC/pacman-more.conf ]] && ! grep -q '^\[axolos\]' "$ETC/pacman-more.conf"; then
  printf '\n# AxolOS: tema, Bento, Axo, herramientas de desarrollo (paquetes firmados)\n[axolos]\nServer = %s\n' \
    "$SERVER" >> "$ETC/pacman-more.conf"
  log "repositorio [axolos] añadido"
fi

# 2. Lista de paquetes: la más reciente de CachyOS (o la que trae la ISO) con AxolOS en Plasma
ni="$ETC/calamares/modules/netinstall-axolos.yaml"
tmp=$(mktemp)
if curl -fsSL --max-time 20 "$NETINSTALL_URL" -o "$tmp" && grep -q 'cachyos-kde-settings' "$tmp"; then
  log "lista de paquetes de CachyOS descargada"
else
  cp "$DATOS/netinstall-cachyos.yaml" "$tmp"
  log "sin conexión con GitHub: uso la lista de paquetes que trae la ISO"
fi
# misma sangría que la línea original: «    - cachyos-kde-settings»
# cachyos-hello fuera: en AxolOS la bienvenida es axolos-bienvenida (si no, se abrirían las dos)
# sddm en vez de plasma-login-manager: la pantalla de inicio de sesión de AxolOS es un tema de SDDM
sed -E -e 's/^([[:space:]]*-[[:space:]]*)cachyos-kde-settings[[:space:]]*$/\1axolos-desktop\n\1axolos-keyring/' \
       -e '/^[[:space:]]*-[[:space:]]*cachyos-hello[[:space:]]*$/d' \
       -e 's/^([[:space:]]*-[[:space:]]*)plasma-login-manager[[:space:]]*$/\1sddm/' "$tmp" > "$ni"
rm -f "$tmp"
if grep -q 'axolos-desktop' "$ni"; then
  conf="$ETC/calamares/modules/netinstall.conf"
  if [[ -f $conf ]]; then
    # groupsUrl: solo nuestra lista (la de CachyOS en GitHub volvería a poner cachyos-kde-settings)
    awk -v url="file://$ni" '
      /^groupsUrl:/ { print "groupsUrl:"; print " - " url; skip=1; next }
      skip && /^[[:space:]]*-/ { next }
      { skip=0; print }' "$conf" > "$conf.axolos" && mv "$conf.axolos" "$conf"
    log "lista de paquetes de Plasma: axolos-desktop"
  fi
else
  log "AVISO: no encontré cachyos-kde-settings en la lista de paquetes; AxolOS no se añadirá"
fi

# 3. Pantalla de arranque AxolOS (Plymouth)
pc="$ETC/calamares/modules/plymouthcfg.conf"
if [[ -f $pc ]]; then
  sed -i -E 's/^(plymouth_theme(_amdgpu)?):.*/\1: axolos/' "$pc"
  log "pantalla de arranque: axolos"
fi

# 4. Inicio de sesión: SDDM el primero (el instalador activa el primero de la lista que esté instalado)
dm="$ETC/calamares/modules/displaymanager.conf"
if [[ -f $dm ]] && grep -qE '^[[:space:]]*-[[:space:]]*sddm[[:space:]]*$' "$dm"; then
  awk '/^displaymanagers:/ { print; print "  - sddm"; enlista=1; next }
       enlista && /^[[:space:]]*-[[:space:]]*sddm[[:space:]]*$/ { next }
       enlista && !/^[[:space:]]*-/ { enlista=0 }
       { print }' "$dm" > "$dm.axolos" && mv "$dm.axolos" "$dm"
  log "inicio de sesión: sddm (tema AxolOS)"
fi

# 5. Menú de arranque (Limine): el instalador escribe el grupo «/+CachyOS» a mano en limine.conf y
#    limine-entry-tool crea después «/+AxolOS» con los kernels (nombre del sistema): quedarían dos
bl="$CAL_LIB/modules/bootloader/main.py"
if [[ -f $bl ]] && grep -q '"/+CachyOS\\n"' "$bl"; then
  sed -i 's|"/+CachyOS\\n"|"/+AxolOS\\n"|' "$bl"
  log "menú de arranque: AxolOS"
elif [[ -f $bl ]] && ! grep -q '"/+AxolOS\\n"' "$bl"; then
  log "AVISO: el instalador ya no escribe «/+CachyOS» en limine.conf; revisa el paso 5"
fi

# 6. Aspecto de Limine: fondo y colores de AxolOS (el instalador escribe a mano el tema de CachyOS).
#    El fondo lo trae axolos-themes, que ya está instalado cuando se configura el arranque.
blc="$ETC/calamares/modules/bootloader.conf"
if [[ -f $blc ]] && grep -q '^limineSplashLogo:' "$blc"; then
  sed -i 's|^limineSplashLogo:.*|limineSplashLogo: "/usr/share/axolos/arranque/limine.png"|' "$blc"
fi
if [[ -f $bl ]] && grep -q 'term_palette: 1e1e2e' "$bl"; then
  sed -i -e 's|# CachyOS Limine theme\\n|# Tema de Limine de AxolOS\\n|' \
         -e 's|# Author: diegons490 (https://github.com/diegons490/cachyos-limine-theme)\\n|# Colores de AxolOS sobre el tema de CachyOS (diegons490)\\n|' \
         -e 's|term_palette: [0-9a-f;]*\\n|term_palette: 17171d;ff7a93;7ddfb4;f3cf7a;a69afe;cdc6ff;7fd4e4;e6e6ee\\n|' \
         -e 's|term_palette_bright: [0-9a-f;]*\\n|term_palette_bright: 5b5b68;ff7a93;7ddfb4;f3cf7a;a69afe;cdc6ff;7fd4e4;ffffff\\n|' \
         -e 's|term_foreground: [0-9a-f]*\\n|term_foreground: e6e6ee\\n|' \
         -e 's|term_foreground_bright: [0-9a-f]*\\n|term_foreground_bright: ffffff\\n|' "$bl"
  log "aspecto de Limine: AxolOS"
elif [[ -f $bl ]] && ! grep -q 'Tema de Limine de AxolOS' "$bl"; then
  log "AVISO: el tema de Limine del instalador ha cambiado; revisa el paso 6"
fi

# 7. Marca del instalador: textos, logos, colores y presentación de AxolOS
CAL_SHARE="${AXOLOS_CAL_SHARE:-/usr/share/calamares}"
if [[ -d $DATOS/marca/axolos && -d $CAL_SHARE/branding ]]; then
  rm -rf "$CAL_SHARE/branding/axolos"
  cp -r "$DATOS/marca/axolos" "$CAL_SHARE/branding/axolos"
  for s in "$CAL_SHARE"/settings_online.conf "$CAL_SHARE"/settings_offline.conf; do
    [[ -f $s ]] && sed -i 's/^branding:.*/branding: axolos/' "$s"
  done
  log "marca del instalador: AxolOS"
fi

# 8. Página «Escritorio»: solo AxolOS (Plasma). Con otro escritorio el sistema no sería AxolOS.
pcd="$ETC/calamares/modules/packagechooser_desktop.conf"
if [[ -f $pcd ]] && grep -q '^method:[[:space:]]*netinstall-select' "$pcd" && grep -q 'id:[[:space:]]*KDE-Desktop' "$pcd"; then
  cp "$DATOS/marca/packagechooser_desktop.conf" "$pcd"
  log "página Escritorio: AxolOS · KDE Plasma"
elif [[ -f $pcd ]] && ! grep -q 'AxolOS · KDE Plasma' "$pcd"; then
  log "AVISO: la página Escritorio del instalador ha cambiado; revisa el paso 8"
fi

# 9. Textos con «CachyOS» escritos a mano: nombre de los pasos, instantánea inicial y Limine-snapper
#    (TARGET_OS_NAME="CachyOS" crearía otra vez un grupo «CachyOS» en el menú de arranque)
for f in "$ETC"/calamares/modules/shellprocess-before.conf "$ETC"/calamares/modules/shellprocess-before-online.conf; do
  [[ -f $f ]] && sed -i -E 's/^([[:space:]]*name: "Preparing your system for (online installation of )?)CachyOS"/\1AxolOS"/' "$f"
done
f="$ETC/calamares/scripts/btrfs-installation-snapshot"
[[ -f $f ]] && sed -i 's/"Fresh CachyOS Installation"/"Instalación nueva de AxolOS"/' "$f"
f="$ETC/calamares/scripts/bootloader-post-setup"
if [[ -f $f ]] && grep -q 'TARGET_OS_NAME="CachyOS"' "$f"; then
  sed -i 's/TARGET_OS_NAME="CachyOS"/TARGET_OS_NAME="AxolOS"/' "$f"
  log "instantáneas en el menú de arranque: AxolOS"
fi

# 10. Instalación sin conexión (settings_offline.conf: copia el live al disco). Dos pasos de AxolOS:
#     justo tras copiar (repositorios con [axolos], pantalla de arranque, quitar lo del live) y antes
#     de configurar el inicio de sesión (llavero, y SDDM y Limine desde los paquetes de la ISO).
so="$CAL_SHARE/settings_offline.conf"
if [[ -f $so && -d $DATOS/offline/paquetes ]] && ! grep -q 'shellprocess@axolos_copiar' "$so"; then
  cp "$DATOS"/offline/shellprocess_axolos_*.conf "$ETC/calamares/modules/"
  if grep -q '^  - unpackfs$' "$so" && grep -q '^  - displaymanager$' "$so" && grep -q '^instances:' "$so"; then
    awk '
      /^instances:/ { print
        print "- id:       axolos_copiar"; print "  module:   shellprocess"; print "  config:   shellprocess_axolos_copiar.conf"
        print "- id:       axolos_paquetes"; print "  module:   shellprocess"; print "  config:   shellprocess_axolos_paquetes.conf"
        next }
      /^  - displaymanager$/ { print "  - shellprocess@axolos_paquetes" }
      { print }
      /^  - unpackfs$/ { print "  - shellprocess@axolos_copiar" }' "$so" > "$so.axolos" && mv "$so.axolos" "$so"
    log "instalación sin conexión: pasos de AxolOS añadidos"
  else
    log "AVISO: settings_offline.conf de CachyOS ha cambiado; revisa el paso 10"
  fi
fi
exit 0
