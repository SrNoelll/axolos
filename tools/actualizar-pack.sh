#!/usr/bin/env bash
# =============================================================================
#  AxolOS · actualizar-pack.sh   (ejecútalo como tu usuario; pide la contraseña una vez)
#  1. Instala en el sistema la última versión de los paquetes AxolOS
#  2. Activa la pantalla de arranque (Plymouth) y pone tu avatar en el inicio de sesión
#  3. Recoge las copias sueltas de tu usuario que ahora trae el sistema
#     (no borra nada: las mueve a ~/.axolos-limpieza/)
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
[[ $EUID -eq 0 ]] && { echo "Ejecútalo como tu usuario, sin sudo delante."; exit 1; }

latest() { ls -1 "$ROOT"/repo/"$1"-[0-9]*.pkg.tar.zst | sort -V | tail -1; }
pkgs=()
for p in axolos-branding axolos-themes axolos-menu axolos-kde-settings axolos-dev axolos-ia axolos-bienvenida axolos-desktop; do pkgs+=("$(latest "$p")"); done

say "1/3 Instalando: ${pkgs[*]##*/}"
sudo -v
sudo pacman -U --needed --noconfirm \
  --overwrite '/usr/share/color-schemes/AxolOS*' \
  --overwrite '/usr/share/plasma/look-and-feel/com.noel.axolos/*' \
  --overwrite '/usr/share/pixmaps/axolos*' \
  "${pkgs[@]}"

say "2/3 Arranque y avatar"
if command -v plymouth-set-default-theme >/dev/null && [[ $(plymouth-set-default-theme) != axolos ]]; then
  sudo plymouth-set-default-theme -R axolos      # reconstruye el initramfs (tarda un poco)
fi
# animación de inicio de Plasma: el vídeo del ajolote
kwriteconfig6 --file ksplashrc --group KSplash --key Engine KSplashQML
kwriteconfig6 --file ksplashrc --group KSplash --key Theme com.noel.axolos
# Que la pantalla de login use tus mismos modos (HDMI a 144 Hz y no a 60):
# así al entrar el monitor no se resincroniza y no se queda en negro
if [[ -f $HOME/.config/kwinoutputconfig.json ]] && id sddm >/dev/null 2>&1; then
  sudo install -d -o sddm -g sddm -m 755 /var/lib/sddm/.config
  sudo install -o sddm -g sddm -m 644 "$HOME/.config/kwinoutputconfig.json" /var/lib/sddm/.config/kwinoutputconfig.json
fi
# IA local: aceleración por gráfica (ollama-cuda/rocm/vulkan), Docker con GPU y servicio activo
sudo /usr/lib/axolos/axolos-root ia-gpu
# Modelos ya descargados durante la prueba de velocidad (~/.cache/axolos-bench): se copian al
# servicio en vez de volver a bajar 25 GB (btrfs: --reflink no duplica espacio). Después se
# quita qwen3:8b, que solo sirvió para comparar motores.
BENCH="$HOME/.cache/axolos-bench/models"
if [[ -d $BENCH/blobs ]]; then
  for d in blobs manifests manifests-v2 metadata; do
    [[ -d $BENCH/$d ]] && sudo cp -rn --reflink=auto --no-preserve=ownership "$BENCH/$d" /var/lib/ollama/
  done
  sudo chown -R ollama:ollama /var/lib/ollama
  sudo systemctl restart ollama.service
  for _ in $(seq 30); do curl -sf -o /dev/null http://127.0.0.1:11434/api/version && break; sleep 1; done
  curl -sf -X DELETE http://127.0.0.1:11434/api/delete -d '{"model":"qwen3:8b"}' >/dev/null || true
  echo "   modelos de la prueba copiados: $(curl -s http://127.0.0.1:11434/api/tags | python3 -c 'import json,sys;print(", ".join(m["name"] for m in json.load(sys.stdin)["models"]))')"
fi
sudo install -Dm644 /usr/share/axolos/avatar.png "/var/lib/AccountsService/icons/$USER"
if [[ -f /var/lib/AccountsService/users/$USER ]]; then
  sudo sed -i "s|^Icon=.*|Icon=/var/lib/AccountsService/icons/$USER|" "/var/lib/AccountsService/users/$USER"
  sudo grep -q '^Icon=' "/var/lib/AccountsService/users/$USER" || \
    echo "Icon=/var/lib/AccountsService/icons/$USER" | sudo tee -a "/var/lib/AccountsService/users/$USER" >/dev/null
else
  printf '[User]\nIcon=/var/lib/AccountsService/icons/%s\n' "$USER" | sudo tee "/var/lib/AccountsService/users/$USER" >/dev/null
  sudo chmod 600 "/var/lib/AccountsService/users/$USER"
fi

say "3/3 Recogiendo copias sueltas que ya trae el sistema"
BK="$HOME/.axolos-limpieza/sueltos-$(date +%Y%m%d-%H%M%S)"
move() {   # $1 = copia de tu usuario · $2 = la del sistema
  if [[ -e $1 && -e $2 ]]; then
    mkdir -p "$BK/$(dirname "${1#$HOME/}")"; mv "$1" "$BK/${1#$HOME/}"; echo "   ${1/#$HOME/~} → ya está en ${2}"
  fi
}
move "$HOME/.local/share/icons/AxolOS"                     /usr/share/icons/AxolOS
move "$HOME/.local/share/icons/hicolor/scalable/apps/axolos.svg" /usr/share/icons/hicolor/scalable/apps/axolos.svg
move "$HOME/.config/Kvantum/AxolOS"                         /usr/share/Kvantum/AxolOS
move "$HOME/.local/share/aurorae/themes/AxolOS"            /usr/share/aurorae/themes/AxolOS
move "$HOME/.local/share/sounds/AxolOS"                    /usr/share/sounds/AxolOS
move "$HOME/.local/share/plasma/desktoptheme/AxolOS"       /usr/share/plasma/desktoptheme/AxolOS
move "$HOME/.local/share/plasma/plasmoids/org.axolos.bento" /usr/share/plasma/plasmoids/org.axolos.bento
move "$HOME/.local/share/konsole/AxolOS.colorscheme"       /usr/share/konsole/AxolOS.colorscheme
move "$HOME/.local/share/konsole/AxolOS.profile"           /usr/share/konsole/AxolOS.profile
# botones GTK: apuntar a los del sistema y retirar la copia del usuario
for v in 3 4; do
  f="$HOME/.config/gtk-$v.0/axolos-window-controls.css"
  [[ -f $f ]] && sed -i "s|$HOME/.local/share/axolos/gtk-buttons|/usr/share/axolos/gtk-buttons|g" "$f"
done
move "$HOME/.local/share/axolos/gtk-buttons"               /usr/share/axolos/gtk-buttons
# CSS de botones al día (el módulo de KDE tapaba el fondo del botón en GTK3)
for v in 3 4; do
  f="$HOME/.config/gtk-$v.0/axolos-window-controls.css"
  if [[ -f /etc/skel/.config/gtk-$v.0/axolos-window-controls.css ]] && { [[ ! -e $f ]] || grep -q 'AxolOS · botones' "$f"; }; then
    cp /etc/skel/.config/gtk-$v.0/axolos-window-controls.css "$f"
  fi
done
# Navegadores Chromium (solo los que estén cerrados)
python3 -I "$ROOT/tools/navegadores_axolos.py"

# Tema AxolOS en VS Code (y demás editores basados en él)
axolos-dev editores || true

systemctl --user restart plasma-plasmashell.service || true
# KRunner (Alt+Espacio) solo lee sus complementos al arrancar: se cierra y se reabre solo
kquitapp6 krunner >/dev/null 2>&1 || true
say "Listo. Reinicia para ver la nueva pantalla de arranque y la de inicio de sesión."
