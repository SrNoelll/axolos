#!/bin/sh
# AxolOS · quita del sistema recién copiado lo que solo sirve en el live (instalación sin conexión).
# uso: limpiar-live.sh RAIZ_DEL_SISTEMA_NUEVO
R=${1:?falta la raíz del sistema nuevo}
[ "$R" = "/" ] && { echo "limpiar-live: me niego a tocar /"; exit 1; }
D=/usr/share/axolos/instalador                      # en el sistema nuevo
LIVE=${AXOLOS_DATOS:-$D}                            # en el live (para pruebas, otra carpeta)
# lanzador del instalador y marca de «Bienvenida hecha» del live (en el sistema nuevo sí debe salir)
rm -f "$R/etc/skel/.config/axolos/bienvenida.hecha" \
      "$R/etc/skel/.config/autostart/axolos-instalar.desktop" \
      "$R/usr/local/bin/axolos-instalar" "$R/usr/local/bin/axolos-instalar-sin-red" \
      "$R/usr/share/applications/axolos-instalar.desktop" \
      "$R/usr/share/icons/hicolor/scalable/apps/axolos-instalar.svg"
# librerías que se añadieron solo para que arranque el instalador (compat-calamares.sh)
if [ -f "$LIVE/compat-libs.txt" ]; then
  while read -r lib; do [ -n "$lib" ] && rm -f "$R/usr/lib/$lib"; done < "$LIVE/compat-libs.txt"
fi
# pantalla de arranque AxolOS (el modo sin conexión no tiene ese paso; va antes de crear el initramfs)
f="$R/etc/plymouth/plymouthd.conf"
if grep -q '^Theme=' "$f" 2>/dev/null; then
  sed -i 's/^Theme=.*/Theme=axolos/' "$f"
else
  mkdir -p "$R/etc/plymouth"
  printf '[Daemon]\nTheme=axolos\n' > "$f"
fi
rm -rf "$R$D"
echo "limpiar-live: sistema nuevo sin restos del live"
