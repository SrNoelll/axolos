# AxolOS

Distribución Linux basada en **CachyOS** (Arch) con **KDE Plasma**, pensada para programar y usar
**IA en local**. El ajolote es su mascota.

- Escritorio propio: tema AxolOS, menú **Bento**, botones de ventana finos, animaciones de arranque.
- **Axo**: chat con IA que funciona sin internet, búsqueda de archivos por su contenido
  («ia busco una foto de la playa») desde el menú y KRunner.
- Para desarrolladores: perfiles de lenguajes, Git con delta, terminal fish con fzf, zoxide, atuin…
- Asistente de bienvenida: lenguajes, Git/GitHub y modelos de IA según tu gráfica.

Este repositorio publica los **paquetes de AxolOS** para pacman, firmados.

## Repositorio de paquetes

Los paquetes están en la release [`x86_64`](https://github.com/SrNoelll/axolos/releases/tag/x86_64).
Son `any` (sirven en cualquier variante de CachyOS: x86-64-v3, v4 o znver4).

### Añadirlo a un CachyOS ya instalado

```bash
# 1. Confiar en la clave de firma de AxolOS
curl -fsSL https://raw.githubusercontent.com/SrNoelll/axolos/main/axolos.gpg | sudo pacman-key --add -
sudo pacman-key --lsign-key 3F7DA47A1271EB49F17F573F992DB143AB099E91

# 2. Añadir el repositorio al final de /etc/pacman.conf
printf '\n[axolos]\nServer = https://github.com/SrNoelll/axolos/releases/download/x86_64\n' | sudo tee -a /etc/pacman.conf

# 3. Instalar AxolOS completo (sustituye a cachyos-kde-settings)
sudo pacman -Syu axolos-desktop
```

A partir de ahí, `sudo pacman -Syu` actualiza AxolOS junto con el resto del sistema.

Huella de la clave: `3F7D A47A 1271 EB49 F17F  573F 992D B143 AB09 9E91`

### Paquetes

| Paquete | Qué trae |
|---|---|
| `axolos-desktop` | Todo AxolOS de una vez |
| `axolos-keyring` | La clave de firma del repositorio |
| `axolos-branding` | Identidad del sistema, logo, fastfetch |
| `axolos-themes` | Tema global, colores, iconos, sonidos, inicio de sesión y arranque |
| `axolos-menu` | Bento, el menú de aplicaciones |
| `axolos-kde-settings` | Ajustes de Plasma para usuarios nuevos |
| `axolos-dev` | Herramientas de desarrollo y perfiles de lenguajes |
| `axolos-ia` | IA local: Ollama afinado, chat Axo, búsqueda en KRunner/Bento |
| `axolos-bienvenida` | Asistente del primer inicio y Centro de AxolOS (ajustes) |

También se publican `yaru-icon-theme`, `whitesur-cursor-theme-git` y `ttf-ia-writer` (del AUR),
que usa el tema. Las fuentes de Apple (SF Pro, New York) **no** se publican porque su licencia no
lo permite: son opcionales (`paru -S apple-fonts`) y, si no están, AxolOS usa Inter y Source Serif 4.

## Instalar AxolOS desde cero

La ISO de AxolOS arranca un sistema de prueba con el lanzador «Instalar AxolOS». Con conexión instala
la versión más reciente de todo (CachyOS optimizado para tu procesador y tu gráfica, y AxolOS desde
este repositorio); sin conexión, la versión de la ISO, que se pone al día al conectarte.

## Desarrollo

Este repositorio es también el código de AxolOS: los paquetes (`packages/`), la capa sobre el
instalador de CachyOS y la ISO (`iso/`, `build-iso.sh`) y las herramientas (`tools/`). La
documentación técnica está en [`docs/DESARROLLO.md`](docs/DESARROLLO.md).

Los paquetes se publican solos: al subir cambios a `packages/`, GitHub Actions
([`.github/workflows/publicar.yml`](.github/workflows/publicar.yml)) compila cada paquete, lo compara
con el publicado, sube su versión si cambió, lo firma con la clave de AxolOS y actualiza la release
[`x86_64`](https://github.com/SrNoelll/axolos/releases/tag/x86_64).

El tema parte de MacTahoe de Vince Liuice (GPL-3.0). El fondo, el logo, los iconos y la animación de
arranque son de AxolOS.
