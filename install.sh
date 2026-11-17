#!/usr/bin/env bash
# =============================================================================
#  AxolOS · install.sh — convierte un CachyOS (KDE Plasma) ya instalado en AxolOS
#
#    ./install.sh            añade el repositorio firmado de AxolOS e instala AxolOS
#    ./install.sh --apply    además aplica el aspecto de AxolOS a tu usuario (con copia)
#    ./install.sh --apps     además instala la colección de aplicaciones de AxolOS
#
#  También sin clonar el repositorio:
#    bash <(curl -fsSL https://raw.githubusercontent.com/SrNoelll/axolos/main/install.sh)
#  Los mensajes salen en el idioma del sistema (es, en, fr, ru, zh, ja).
# =============================================================================
set -euo pipefail
SERVER="https://github.com/SrNoelll/axolos/releases/download/x86_64"
CLAVE_URL="https://raw.githubusercontent.com/SrNoelll/axolos/main/axolos.gpg"
FPR="3F7DA47A1271EB49F17F573F992DB143AB099E91"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo .)"

# --- mensajes en el idioma del sistema ---------------------------------------------------
IDIOMA=${LC_ALL:-${LC_MESSAGES:-${LANG:-en}}}; IDIOMA=${IDIOMA%%_*}; IDIOMA=${IDIOMA%%.*}
t() {  # t CLAVE → texto
  local k=$1
  case "$IDIOMA:$k" in
    es:raiz) echo "Ejecútalo como tu usuario: pedirá la contraseña cuando haga falta." ;;
    es:arch) echo "AxolOS se instala sobre CachyOS (o Arch Linux) con pacman." ;;
    es:nocachy) echo "Aviso: no parece CachyOS. AxolOS está pensado para CachyOS con KDE Plasma." ;;
    es:clave) echo "Confiando en la clave de firma de AxolOS" ;;
    es:huella) echo "La clave descargada no es la de AxolOS: me detengo." ;;
    es:repo) echo "Añadiendo el repositorio [axolos]" ;;
    es:copia) echo "copia de tu configuración anterior" ;;
    es:inst) echo "Instalando AxolOS (si pacman pregunta por reemplazar cachyos-kde-settings, acepta)" ;;
    es:aplicar) echo "Aplicando el aspecto de AxolOS a tu usuario (copia en" ;;
    es:sesion) echo "Cierra sesión y vuelve a entrar para ver el escritorio de AxolOS." ;;
    es:listo) echo "Listo. Te damos la bienvenida a AxolOS 🦎" ;;
    es:opcion) echo "Opción desconocida" ;;
    fr:raiz) echo "Lancez-le avec votre utilisateur : le mot de passe sera demandé si nécessaire." ;;
    fr:arch) echo "AxolOS s'installe sur CachyOS (ou Arch Linux) avec pacman." ;;
    fr:nocachy) echo "Attention : ce n'est pas CachyOS. AxolOS est conçu pour CachyOS avec KDE Plasma." ;;
    fr:clave) echo "Ajout de la clé de signature d'AxolOS" ;;
    fr:huella) echo "La clé téléchargée n'est pas celle d'AxolOS : arrêt." ;;
    fr:repo) echo "Ajout du dépôt [axolos]" ;;
    fr:copia) echo "copie de votre configuration précédente" ;;
    fr:inst) echo "Installation d'AxolOS (si pacman propose de remplacer cachyos-kde-settings, acceptez)" ;;
    fr:aplicar) echo "Application de l'apparence d'AxolOS à votre utilisateur (copie dans" ;;
    fr:sesion) echo "Déconnectez-vous puis reconnectez-vous pour voir le bureau d'AxolOS." ;;
    fr:listo) echo "Terminé. Bienvenue dans AxolOS 🦎" ;;
    fr:opcion) echo "Option inconnue" ;;
    ru:raiz) echo "Запускайте от своего пользователя: пароль будет запрошен при необходимости." ;;
    ru:arch) echo "AxolOS устанавливается поверх CachyOS (или Arch Linux) через pacman." ;;
    ru:nocachy) echo "Внимание: это не CachyOS. AxolOS рассчитан на CachyOS с KDE Plasma." ;;
    ru:clave) echo "Добавление ключа подписи AxolOS" ;;
    ru:huella) echo "Загруженный ключ не принадлежит AxolOS: остановка." ;;
    ru:repo) echo "Добавление репозитория [axolos]" ;;
    ru:copia) echo "копия прежней конфигурации" ;;
    ru:inst) echo "Установка AxolOS (если pacman предложит заменить cachyos-kde-settings, согласитесь)" ;;
    ru:aplicar) echo "Применение оформления AxolOS к вашему пользователю (копия в" ;;
    ru:sesion) echo "Выйдите из сеанса и войдите снова, чтобы увидеть рабочий стол AxolOS." ;;
    ru:listo) echo "Готово. Добро пожаловать в AxolOS 🦎" ;;
    ru:opcion) echo "Неизвестный параметр" ;;
    zh:raiz) echo "请以普通用户运行：需要时会请求密码。" ;;
    zh:arch) echo "AxolOS 通过 pacman 安装在 CachyOS（或 Arch Linux）之上。" ;;
    zh:nocachy) echo "注意：这似乎不是 CachyOS。AxolOS 专为搭载 KDE Plasma 的 CachyOS 设计。" ;;
    zh:clave) echo "正在信任 AxolOS 签名密钥" ;;
    zh:huella) echo "下载的密钥不是 AxolOS 的密钥：已停止。" ;;
    zh:repo) echo "正在添加 [axolos] 软件源" ;;
    zh:copia) echo "原配置的备份" ;;
    zh:inst) echo "正在安装 AxolOS（如 pacman 询问是否替换 cachyos-kde-settings，请同意）" ;;
    zh:aplicar) echo "正在为你的用户应用 AxolOS 外观（备份位于" ;;
    zh:sesion) echo "注销并重新登录即可看到 AxolOS 桌面。" ;;
    zh:listo) echo "完成。欢迎使用 AxolOS 🦎" ;;
    zh:opcion) echo "未知选项" ;;
    ja:raiz) echo "一般ユーザーで実行してください（必要なときにパスワードを求めます）。" ;;
    ja:arch) echo "AxolOS は pacman で CachyOS（または Arch Linux）の上にインストールします。" ;;
    ja:nocachy) echo "注意: CachyOS ではないようです。AxolOS は KDE Plasma の CachyOS 向けです。" ;;
    ja:clave) echo "AxolOS の署名鍵を信頼しています" ;;
    ja:huella) echo "ダウンロードした鍵は AxolOS のものではありません。中止します。" ;;
    ja:repo) echo "[axolos] リポジトリを追加しています" ;;
    ja:copia) echo "以前の設定のバックアップ" ;;
    ja:inst) echo "AxolOS をインストールしています（cachyos-kde-settings の置き換えを聞かれたら承認してください）" ;;
    ja:aplicar) echo "AxolOS の外観をユーザーに適用しています（バックアップ:" ;;
    ja:sesion) echo "ログアウトして再ログインすると AxolOS のデスクトップになります。" ;;
    ja:listo) echo "完了しました。AxolOS へようこそ 🦎" ;;
    ja:opcion) echo "不明なオプション" ;;
    *:raiz) echo "Run it as your user: it will ask for your password when needed." ;;
    *:arch) echo "AxolOS installs on top of CachyOS (or Arch Linux) with pacman." ;;
    *:nocachy) echo "Warning: this does not look like CachyOS. AxolOS is built for CachyOS with KDE Plasma." ;;
    *:clave) echo "Trusting the AxolOS signing key" ;;
    *:huella) echo "The downloaded key is not the AxolOS key: stopping." ;;
    *:repo) echo "Adding the [axolos] repository" ;;
    *:copia) echo "backup of your previous configuration" ;;
    *:inst) echo "Installing AxolOS (if pacman offers to replace cachyos-kde-settings, accept)" ;;
    *:aplicar) echo "Applying the AxolOS look to your user (backup in" ;;
    *:sesion) echo "Log out and back in to see the AxolOS desktop." ;;
    *:listo) echo "Done. Welcome to AxolOS 🦎" ;;
    *:opcion) echo "Unknown option" ;;
  esac
}
say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
die() { printf '\e[1;31m!!\e[0m %s\n' "$*" >&2; exit 1; }

apply=false apps=false
for a in "$@"; do
  case $a in
    --apply) apply=true ;;
    --apps) apps=true ;;
    -h|--help) sed -n '3,11p' "$0" 2>/dev/null; exit 0 ;;
    *) die "$(t opcion): $a" ;;
  esac
done
[[ $EUID -eq 0 ]] && die "$(t raiz)"
command -v pacman >/dev/null || die "$(t arch)"
grep -qi cachyos /etc/os-release /usr/lib/os-release /var/lib/axolos/os-release.orig 2>/dev/null || say "$(t nocachy)"

# 1. Clave de firma: la del repositorio clonado o la de GitHub, comprobando su huella
say "$(t clave) ($FPR)"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
if [[ -f $DIR/axolos.gpg ]]; then cp "$DIR/axolos.gpg" "$tmp/axolos.gpg"
else curl -fsSL --max-time 30 "$CLAVE_URL" -o "$tmp/axolos.gpg"; fi
huella=$(gpg --show-keys --with-colons "$tmp/axolos.gpg" 2>/dev/null | awk -F: '/^fpr/{print $10; exit}')
[[ $huella == "$FPR" ]] || die "$(t huella)"
sudo pacman-key --add "$tmp/axolos.gpg"
sudo pacman-key --lsign-key "$FPR"

# 2. Repositorio
if ! grep -q '^\[axolos\]' /etc/pacman.conf; then
  say "$(t repo)"
  sudo cp /etc/pacman.conf /etc/pacman.conf.antes-de-axolos
  printf '\n# AxolOS\n[axolos]\nServer = %s\n' "$SERVER" | sudo tee -a /etc/pacman.conf >/dev/null
  echo "   $(t copia): /etc/pacman.conf.antes-de-axolos"
fi

# 3. AxolOS
say "$(t inst)"
sudo pacman -Syu --needed axolos-keyring axolos-desktop

# 4. Opcional: tu usuario y tus aplicaciones
if $apply; then
  backup="$HOME/.axolos-backup/$(date +%Y%m%d-%H%M%S)"
  say "$(t aplicar) $backup)"
  while IFS= read -r -d '' f; do
    rel="${f#/etc/skel/}"
    if [[ -e $HOME/$rel ]]; then mkdir -p "$backup/$(dirname "$rel")"; cp -a "$HOME/$rel" "$backup/$rel"; fi
    mkdir -p "$HOME/$(dirname "$rel")"; cp "$f" "$HOME/$rel"
  done < <(pacman -Qlq axolos-kde-settings | grep '^/etc/skel/.*[^/]$' | tr '\n' '\0')
  plasma-apply-lookandfeel -a com.noel.axolos >/dev/null 2>&1 || true
  echo "   $(t sesion)"
fi
$apps && axolos-apps
say "$(t listo)"
