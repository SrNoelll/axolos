# 🦎 AxolOS · desarrollo

Distribución basada en **CachyOS + KDE Plasma** con el escritorio de Noel Alarcón
empaquetado: fondo del ajolote, tema MacTahoe-Dark con colores *AxolOS Obsidian*,
iconos Yaru morados, cursor WhiteSur, panel superior con menú global, dock
flotante, reloj analógico, Konsole con colores pywal y fastfetch de AxolOS.

Todo lo que antes estaba repartido entre `~/.config`, `~/.local/share`,
`/usr/local` y paquetes del AUR está ahora en **paquetes de pacman**.

## Qué hay dentro

| Paquete | Qué instala |
|---|---|
| `axolos-branding` | Nombre del sistema (`os-release`, `lsb-release`), logo `axolos`, fastfetch por defecto, comando `axolos-apps` |
| `axolos-themes` | Tema global *AxolOS*, **animación de arranque propia**, MacTahoe-Dark (Plasma, ventanas, Kvantum), esquemas de color, fondo `AxolOS`, perfil de Konsole |
| `axolos-kde-settings` | Ajustes para usuarios nuevos (`/etc/skel`): panel, dock, fuentes, colores, Konsole, starship, fondo de bloqueo e inicio de sesión. **Sustituye a `cachyos-kde-settings`** |
| `axolos-dev` | Para desarrolladores: git con delta, fzf/zoxide/atuin/direnv/mise en fish, uv, just, Docker, distrobox, temas AxolOS para Kate/Neovim/VS Code y perfiles de lenguajes (`axolos-dev`) |
| `axolos-ia` | IA local: Ollama afinado (flash attention, caché q8), **Axo** (chat), búsqueda «ia …» en KRunner, VS Code con Continue, Open WebUI opcional (`axolos-ia`) |
| `axolos-bienvenida` | Asistente del primer inicio: perfiles, Git/GitHub/SSH, aceleración por gráfica y modelos según la VRAM |
| `axolos-desktop` | Metapaquete: instala todo lo anterior y sus dependencias (Yaru, WhiteSur, SF Pro, JetBrains Mono Nerd, fish, starship…) |

## Estructura

```
AxolOS/
├── collect.sh          # copia tu escritorio actual al pack
├── build-packages.sh   # compila los paquetes -> repo/
├── install.sh          # convierte un CachyOS ya instalado en AxolOS
├── build-iso.sh        # crea la ISO instalable de AxolOS
├── VERSION             # versión de los paquetes
├── packages/           # PKGBUILDs + ficheros
├── iso/                # cambios sobre la ISO de CachyOS
│   ├── packages.add / packages.remove
│   └── airootfs/       # ficheros del sistema live
├── pkglists/           # tus aplicaciones (native.txt, aur.txt)
└── tools/kini.py       # editor de configs de KDE usado por collect.sh
```

## Uso

### 1. Guardar tu escritorio en el pack
Ejecútalo cada vez que cambies el fondo, el panel, el tema…
```bash
./collect.sh
```
Lee de tu `$HOME` y escribe solo dentro de este repo. Quita automáticamente
rutas personales, el marco de fotos y las posiciones de tus carpetas.

Si algo está en otra ruta, cámbialo con variables:
`AXOLOS_WALLPAPER=~/otro-fondo.jpg ./collect.sh`

### 2. Instalar AxolOS en otro PC con CachyOS (sin reinstalar)
```bash
./install.sh --apply --apps
```
- sin opciones: instala los paquetes (los usuarios nuevos ya salen con AxolOS)
- `--apply`: aplica el aspecto a tu usuario (copia de seguridad en `~/.axolos-backup/`)
- `--apps`: instala también tus aplicaciones de `pkglists/`

### 3. Crear la ISO de AxolOS
```bash
sudo pacman -S --needed archiso git
./build-iso.sh
```
Descarga la base oficial de CachyOS, le añade los paquetes AxolOS y genera
`out/axolos-AAAA.MM.DD-x86_64.iso`. Tarda un buen rato y necesita unos 25 GB libres.
Para probarla sin grabarla: `run_archiso -u -i out/axolos-*.iso` (paquete `qemu-desktop`).

> En el instalador (Calamares) elige la instalación **offline**: copia el sistema
> live tal cual, con AxolOS incluido. La instalación online descarga la
> configuración KDE de CachyOS.

Tras instalar, `axolos-apps` instala tus aplicaciones (Brave, VS Code, Spotify…).

## Animación de arranque

El ajolote real del fondo entra caminando en la oscuridad con su propia luz
(cada pie apoyado no resbala), frena, da un coletazo, abre el ojo y un iris de
luz enciende el mundo. Dura 1,9 s (lo que tarda KSplash en este equipo: 2,1 s)
y su último fotograma es exactamente tu escritorio, así que el corte no se ve.

- Código: `packages/axolos-themes/splash/` (`film.js` tiempos, `Axolote.qml`
  personaje, `Splash.qml` escena, `rig/` piezas, `shaders/mundo.frag` luz).
  Decisiones y medidas en [BRIEF.md](packages/axolos-themes/splash/BRIEF.md).
- Instalarla y activarla en tu usuario: `tools/activar-animacion.sh`
- Verla sin reiniciar: `ksplashqml --test --window com.noel.axolos`
- Rehacer el rig si cambias el fondo:
  `python3 tools/rig_axolote.py <fondo.jpg> tools/silueta-ajolote.png packages/axolos-themes/splash/rig`
- Renders (KWin invisible, no toca tu pantalla): `tools/splash-dev/render.sh hoja|storyboard|draft|final <salida>`

## Avisos

- **Fuentes SF Pro (`apple-fonts`)**: tienen licencia de Apple. Úsalas en tu
  ISO personal, pero **no publiques la ISO** con ellas. Para una versión
  pública, quítalas de `iso/packages.add` y de `axolos-desktop`, y cambia la
  fuente en `kdeglobals` (por ejemplo a *Inter*).
- `ID=axolos` en `os-release`, con `ID_LIKE="cachyos arch"`. Si alguna herramienta
  de CachyOS deja de reconocer el sistema, vuelve a poner `ID=cachyos` en
  `packages/axolos-branding/static/os-release`.
- El sistema actual usa SDDM (fondo configurado). La ISO de CachyOS trae
  *Plasma Login Manager*, que todavía no tiene el fondo de AxolOS.

## Siguientes pasos posibles
- Publicación automática desde GitHub Actions (necesita el código del proyecto en el repositorio
  público y la clave privada de firma como secreto: decisión de Noel).

## Cómo llega AxolOS a un equipo nuevo

```
ISO AxolOS ──arranca──► se descarga el instalador de CachyOS más reciente
                         └─► capa AxolOS (iso/instalador/aplicar-axolos.sh)
                              · añade [axolos] al pacman.conf del sistema nuevo
                              · en Plasma instala axolos-desktop (no cachyos-kde-settings)
                              · pantalla de arranque AxolOS, inicio de sesión SDDM con tema AxolOS
                              · Limine con un solo grupo «AxolOS», sus colores y su fondo
                              · marca del instalador: textos, logos, colores y diapositivas
                              · página «Escritorio» con solo AxolOS · KDE Plasma
instalación online ──► base de CachyOS al día + repos optimizados según el procesador
                       (x86-64-v3 / v4 / znver4) + controladores de la gráfica (chwd)
                       + AxolOS al día desde el repositorio firmado
primer inicio ───────► Bienvenida: lenguajes, Git/GitHub, IA según la VRAM
después ─────────────► Centro de AxolOS: actualizaciones, lenguajes, modelos, búsqueda, apariencia
```

- **Sin internet**: el lanzador del live ofrece «Instalar sin conexión» (copia el sistema de la ISO,
  modo offline de CachyOS + `iso/instalador/offline/`): repos con `[axolos]`, llavero, SDDM y Limine
  desde paquetes que lleva la ISO (`iso/paquetes-offline.sh`), y sin restos del live.
- **Equipos ya instalados**: `pkexec /usr/lib/axolos/axolos-root limine --prueba` enseña los cambios
  del menú de arranque; sin `--prueba` los aplica (con copia en `/var/lib/axolos/`). También desde el
  Centro de AxolOS → Apariencia.
- **Probar**: `tools/probar-vm.sh nueva` (con red) y `tools/probar-vm.sh nueva sinred` (sin red).

- **Al día, no una copia**: todo se descarga al instalar; la ISO solo arranca el instalador.
- **Hardware**: lo decide el instalador de CachyOS (repos por CPU, chwd para la gráfica). Los
  paquetes AxolOS son `any`; la IA elige CUDA / ROCm / Vulkan en la Bienvenida.
- **Actualizaciones**: repositorio `[axolos]` firmado en
  `https://github.com/SrNoelll/axolos/releases/download/x86_64` → `sudo pacman -Syu`.
- **Clave de firma**: `3F7DA47A1271EB49F17F573F992DB143AB099E91` (paquete `axolos-keyring`).
  La privada solo está en el equipo de Noel (`~/.gnupg`): **haz copia de seguridad**
  (`gpg --export-secret-keys --armor 3F7DA47A… > axolos-clave-privada.asc`, guárdala fuera del equipo).

### Publicar una versión nueva de los paquetes
Con el código en GitHub basta con `git push`: el flujo `.github/workflows/publicar.yml` hace lo de
abajo en un contenedor de Arch (secreto `AXOLOS_GPG_KEY` = clave privada de firma) y guarda en git los
`pkgrel` que suba. A mano (o para probar sin publicar, con `AXOLOS_SIN_SUBIR=1`):

`tools/publicar-repo.sh`: compila cada paquete y lo compara por contenido con el publicado
(`tools/comparar_paquetes.py`). Si cambió, sube `pkgrel` solo; si no, reutiliza el publicado (una
versión publicada nunca cambia). Firma, verifica y sube a GitHub.

### Pasar un equipo ya instalado al repositorio online
`tools/activar-repo.sh`
