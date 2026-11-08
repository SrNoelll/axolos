# Manual de AxolOS
Guía general del sistema. Es igual para todos los equipos; los datos concretos de este equipo
están en el apartado anterior. Cada sección solo aparece si lo que describe está instalado.

## Qué es AxolOS
AxolOS es una distribución Linux basada en CachyOS (que a su vez se basa en Arch Linux), con el
escritorio KDE Plasma y una identidad propia: el ajolote como mascota, tema oscuro morado,
iconos, sonidos y animaciones propias. Es «rolling release»: no hay versiones grandes, se
actualiza todo de forma continua. Los paquetes de CachyOS están optimizados para procesadores
modernos.

## Actualizar e instalar programas
- Actualizar todo el sistema: `sudo pacman -Syu`. Hazlo con regularidad (p. ej. cada semana) y
  reinicia si se actualiza el kernel o el controlador gráfico.
- Nunca uses `pacman -Sy paquete` (actualización parcial): instala con `sudo pacman -S paquete`
  y, si da error 404, actualiza primero con `sudo pacman -Syu`.
- Buscar: `pacman -Ss texto` · información: `pacman -Si paquete` · ¿de qué paquete es un fichero?:
  `pacman -Qo /ruta` · desinstalar con dependencias que ya no hacen falta: `sudo pacman -Rns paquete`.
<!-- si: paru|yay -->
- AUR (programas de la comunidad): `paru -S paquete` o `yay -S paquete` (sin sudo). `paru` a secas
  actualiza el sistema y el AUR a la vez. Revisa el PKGBUILD de paquetes AUR poco conocidos.
<!-- fin -->
<!-- si: pacman-contrib -->
- Liberar espacio de la caché de paquetes: `sudo paccache -rk1` (deja una versión anterior).
<!-- fin -->
<!-- si: axolos-branding -->
- `axolos-apps` instala la colección de aplicaciones recomendada de AxolOS (solo lo que falte).
<!-- fin -->
<!-- si: cachyos-hello -->
- «CachyOS Hello» (en el menú) tiene ajustes del sistema y utilidades de CachyOS.
<!-- fin -->

<!-- si: snapper -->
## Copias de seguridad del sistema (instantáneas)
- El disco usa Btrfs con instantáneas de snapper.
<!-- fin -->
<!-- si: snap-pac -->
- Se crea una instantánea automáticamente antes y después de cada instalación o actualización con pacman.
<!-- fin -->
<!-- si: snapper -->
- Ver las instantáneas en la terminal: `sudo snapper list` (número, fecha y descripción, p. ej.
  «pacman -Syu»). Comparar cambios: `sudo snapper status N1..N2`.
<!-- fin -->
<!-- si: btrfs-assistant -->
- Volver atrás con el escritorio funcionando: abre «Btrfs Assistant» (en el menú; pide la
  contraseña) → pestaña «Snapper» → elige la instantánea de antes del problema (fíjate en la fecha
  y en la descripción del comando de pacman) → «Restaurar» → reinicia.
<!-- fin -->
<!-- si: limine-snapper-sync -->
- Si el sistema ya no arranca bien: reinicia y, en el menú de arranque Limine, entra en el apartado
  de instantáneas y elige una anterior a la actualización. Arrancará esa versión (solo lectura de
  forma temporal). Una vez dentro, abre «Limine Snapper Restore» (en el menú) para dejarla como
  sistema definitivo, y reinicia.
<!-- fin -->
<!-- si: snapper -->
- Las instantáneas protegen el sistema, no son copia de tus documentos: guarda lo importante también
  en otro disco o en la nube.
<!-- fin -->

<!-- si: axolos-themes|axolos-kde-settings -->
## Escritorio y apariencia
- Tema global «AxolOS»: Preferencias del sistema → Colores y temas → Tema global. Esquemas de color
  AxolOS (Obsidian, Purple), estilo de aplicaciones Kvantum, iconos AxolOS, cursor WhiteSur.
- Los botones de las ventanas son puntos finos: cerrar siempre morado; minimizar y maximizar en
  gris. Los símbolos aparecen al pasar el ratón. Se ven igual en apps KDE, GTK y Brave/Chrome.
- Fondo de escritorio: clic derecho en el escritorio → «Configurar escritorio y fondo de pantalla».
- Al encender: animación del ajolote (Plymouth), pantalla de inicio de sesión AxolOS (SDDM) y la
  animación de inicio de Plasma con el ajolote.
- Panel superior con menú global (los menús de la app activa salen arriba, como en macOS) y un dock
  abajo. Clic derecho en un panel → «Mostrar ajustes del panel» para cambiarlo.
- Preferencias del sistema: atajo Meta+I si no se ha cambiado (ver atajos activos más arriba).
<!-- fin -->
<!-- si: axolos-menu -->
- Bento es el menú de aplicaciones de AxolOS: favoritas, recientes, búsqueda y accesos del sistema
  en mosaicos. Se abre desde el dock (y con la tecla Meta si es el lanzador del panel).
<!-- fin -->
- KRunner (Alt+Espacio por defecto) busca aplicaciones, ficheros, hace cálculos y conversiones.

<!-- si: fish -->
## Terminal
- Konsole con el perfil AxolOS, shell fish (autocompletado y sugerencias en gris: → para aceptarlas)
  y el prompt Starship. `fastfetch` muestra el resumen del sistema.
- fish no es bash: las variables se ponen con `set -x NOMBRE valor` (o `set -Ux` para siempre);
  la configuración propia va en `~/.config/fish/config.fish`. Para scripts de bash: `bash script.sh`.
<!-- fin -->
<!-- si: axolos-dev -->
- Atajos de la terminal en AxolOS: Ctrl+R busca en todo el historial (atuin); Ctrl+T busca ficheros
  (fzf); Alt+C entra en una carpeta buscándola; `z nombre` salta a una carpeta usada antes (zoxide)
  y `zi` la elige de una lista.
- Comandos modernos incluidos: `bat` (cat con colores), `eza` (ls mejorado), `rg` (buscar texto),
  `fd` (buscar ficheros), `tldr comando` (ejemplos rápidos), `lazygit` (git visual), `just`
  (tareas del proyecto), `xh` (peticiones HTTP), `jq`/`yq` (JSON/YAML), `hyperfine`, `tokei`.
- Desactivar estas integraciones de fish: `set -U AXOLOS_NO_DEV_SHELL 1`.

## Desarrollo
- `axolos-dev` lista los perfiles de lenguajes (web, python, datos/ML, rust, go, c, java,
  contenedores, android, bases de datos); `axolos-dev instalar web python` los instala (pide la
  contraseña una vez). `axolos-dev editores` pone el tema AxolOS en VS Code y derivados.
- Versiones por proyecto: `mise use node@22` (o python, go…) crea `.mise.toml`; Python con
  `uv init`, `uv add paquete`, `uv run script.py`. `direnv` carga el `.envrc` de cada carpeta
  (actívalo con `direnv allow`).
- Git: ya viene configurado con delta (diferencias en color con números de línea), rama inicial
  `main`, `push` crea la rama remota sola y `zdiff3` en conflictos. Esa configuración está en
  `/etc/gitconfig`; lo que pongas en `~/.gitconfig` manda. GitHub: `gh auth login`.
- Docker arranca solo al usarlo (socket). Para usarlo sin sudo el usuario debe estar en el grupo
  `docker` y volver a iniciar sesión. `lazydocker` lo muestra de forma visual.
- distrobox crea contenedores con otras distribuciones integrados en el escritorio:
  `distrobox create -n ubuntu -i ubuntu:24.04` y `distrobox enter ubuntu`.
- Temas AxolOS de editor: VS Code (tema «AxolOS»), Kate/KWrite (por defecto) y Neovim
  (`:colorscheme axolos`).
<!-- fin -->

<!-- si: axolos-ia -->
## IA local (Axo)
- Axo es la IA de este equipo: funciona sin internet y nada sale del ordenador. Se abre desde el
  menú («Axo») o desde KRunner escribiendo `ia` y la pregunta. Guarda el historial en
  `~/.local/share/axolos/axo/conversaciones`; las borradas van a `~/.local/share/axolos/axo/papelera`.
- En Axo: Ctrl+N nueva conversación, Ctrl+K buscar en el historial, Ctrl+B ocultar el historial,
  Esc detiene la respuesta, F11 pantalla completa. «Pensar a fondo» razona antes de responder.
  Con modelos que ven imágenes se pueden adjuntar o arrastrar imágenes.
- El motor es Ollama (servicio `ollama.service`, API en http://127.0.0.1:11434, compatible con la
  API de OpenAI en /v1). Solo escucha en este equipo. Usa la gráfica si está la aceleración
  (ollama-cuda en NVIDIA, ollama-rocm en AMD, ollama-vulkan en otras) y la libera a los 5 minutos
  sin uso.
- Comandos: `axolos-ia` (estado), `axolos-ia gpu` (activar la gráfica), `axolos-ia modelos`
  (catálogo según el equipo), `axolos-ia descargar modelo`, `axolos-ia vscode` (VS Code con
  Continue: chat con Ctrl+L y autocompletado), `axolos-ia web` (Open WebUI en
  http://localhost:3000 con Docker), `axolos-ia contexto` (lo que Axo sabe del equipo).
  También `ollama list`, `ollama rm modelo`, `ollama ps` (qué está cargado).
- Buscar archivos por lo que contienen: en Bento o en KRunner escribe `ia busco` y lo que recuerdes
  («ia busco una foto de la playa», «ia busco el pdf de mis apuntes de redes», «ia busco la
  presentación de marketing»). Entiende tipos (foto, vídeo, pdf, presentación, documento…) y fechas
  («de ayer», «del mes pasado», «de 2025», «el último…»). Con el botón de carpeta se abre su
  ubicación. Funciona con un índice local: las fotos y vídeos los describe el modelo de visión, de
  los PDF y documentos se lee el texto (los PDF escaneados también los lee la visión).
- Los archivos nuevos se añaden solos a los pocos segundos de aparecer (un vigilante muy ligero,
  `axolos-indice-vigia`), y cada 2 horas, con el portátil enchufado, se repasa todo
  (`axolos-indice.timer`). Con batería, las tandas grandes esperan a enchufarlo. Ya:
  `axolos-ia indexar`. Desde la terminal: `axolos-ia buscar frase`. Carpetas
  indexadas: Escritorio, Documentos, Descargas, Imágenes y Vídeos; para cambiarlas, escribe una
  por línea en `~/.config/axolos/indice.conf`. El índice está en `~/.local/share/axolos/indice`.
- Ver el uso de la gráfica: `nvtop`.
- Si la IA no responde: `axolos-ia` para ver el estado; `systemctl status ollama` y
  `journalctl -u ollama -b` para el registro; `sudo systemctl restart ollama` para reiniciarla.
  Si «ia …» no sale en KRunner tras instalar: `kquitapp6 krunner`.
<!-- fin -->
<!-- si: axolos-bienvenida -->
- El asistente «Bienvenida a AxolOS» (en el menú, o `axolos-bienvenida`) prepara perfiles de
  programación, Git/GitHub con clave SSH y la IA local. Se puede abrir cuantas veces se quiera.
- El «Centro de AxolOS» (en el menú, o `axolos-centro`) cambia después lo que preparó la
  Bienvenida, sin tocar la terminal:
  - Resumen: versión de AxolOS, el equipo y si hay actualizaciones (botón «Actualizar ahora»).
  - Programación: añadir perfiles de lenguajes y el tema AxolOS en VS Code / VSCodium.
  - IA local: estado del servicio y de la gráfica, y descargar o quitar modelos.
  - Búsqueda: estado del índice, actualizarlo ya y activar el indexado al momento.
  - Apariencia: botones AxolOS en Brave/Chrome/Chromium y el menú de arranque de AxolOS.
  Se puede abrir directamente en una sección: `axolos-centro ia` (resumen, programacion, ia,
  busqueda, apariencia).
<!-- fin -->

## Problemas frecuentes
- Ver errores del arranque actual: `journalctl -b -p err`. De la sesión gráfica:
  `journalctl --user -b -p warning`.
- El escritorio o el panel se cuelgan: `systemctl --user restart plasma-plasmashell`.
- Una aplicación no responde: Meta+Ctrl+Esc y clic en su ventana para cerrarla (o `kill PID`).
- Sin espacio en disco: `du -sh ~/* | sort -h` para ver qué ocupa;
  limpiar la caché de paquetes y las instantáneas antiguas.
- Error de claves al actualizar: `sudo pacman -Sy archlinux-keyring cachyos-keyring && sudo pacman -Su`.
- Wi-Fi, Bluetooth, sonido, pantallas y energía se configuran en Preferencias del sistema; también
  desde los iconos de la bandeja del panel.
- Más ayuda: wiki de CachyOS (wiki.cachyos.org) y la ArchWiki (wiki.archlinux.org), que vale para
  casi todo en AxolOS.
