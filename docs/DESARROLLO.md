# AxolOS · desarrollo

AxolOS es CachyOS + KDE Plasma con un escritorio de cristal líquido propio, IA local y herramientas
para programar, repartido en paquetes de pacman firmados. Este documento explica cómo está hecho y
cómo se trabaja en él. (El [README](../README.es.md) es la presentación para quien lo usa.)

## Estructura

```
AxolOS/
├── packages/            # un PKGBUILD por paquete (+ sus archivos)
│   ├── axolos-glass/        efecto Glass de KWin, ajustes de cristal y salvaguarda de versión
│   ├── axolos-themes/       temas globales, Plasma, Kvantum, decoraciones, colores, fondos,
│   │                        iconos, inicio de sesión (SDDM), arranque (Plymouth, Limine)
│   ├── axolos-menu/         Bento (QML) y sus traducciones
│   ├── axolos-kde-settings/ /etc/skel, axolos-aspecto, axolos-navegadores
│   ├── axolos-branding/     identidad, axolos-root (pkexec), axolos_i18n, axolos_cristal, traducciones
│   ├── axolos-ia/           Ollama afinado, Axo (chat), búsqueda, KRunner, VS Code
│   ├── axolos-dev/          perfiles de lenguajes y herramientas
│   ├── axolos-bienvenida/   Bienvenida y Centro de AxolOS
│   ├── axolos-keyring/      clave de firma
│   └── axolos-desktop/      metapaquete
├── iso/                 # capa sobre la ISO y el instalador de CachyOS
├── build-iso.sh         # crea la ISO de AxolOS
├── build-packages.sh    # compila los paquetes en repo/ (local)
├── install.sh           # convierte un CachyOS ya instalado en AxolOS
├── tools/               # generadores del aspecto, traducciones, publicación y pruebas
└── .github/workflows/   # comprobar.yml (cada cambio) y publicar.yml (paquetes)
```

## El aspecto: cristal líquido

Todo lo visual se **genera** con herramientas de `tools/`; se cambia el generador, se ejecuta y se
guardan en git el generador y su resultado.

| Qué | Herramienta | Notas |
|---|---|---|
| Fondos oscuro y claro, logo de arranque | `fondo_cristal.py` (Blender) | `blender -b --factory-startup --python tools/fondo_cristal.py -- --modo oscuro --salida X.png`; `--solo-ajolote` para el logo. El ajolote se infla resolviendo ∇²u = −1 sobre la silueta (alisada: el trazado de potrace trae ondas de un píxel que la refracción convierte en dientes) y se extrae como superficie implícita con OpenVDB, con los vértices sobre la superficie exacta y normales analíticas: canto redondo y continuo. Dispersión con tres vidrios (R, G, B) |
| Iconos de cristal | `iconos_cristal.py` + `iconos_cristal_blender.py` | Qt dibuja placa y símbolo; Blender renderiza; escribe el tema `AxolOS` y los iconos de las apps |
| Índices de los temas de iconos | `iconos_tema.py` | `AxolOS` (hereda Yaru morado oscuro) y `AxolOS-Claro` (los mismos iconos por enlaces; hereda variantes claras para que los de las barras se vean en modo claro) |
| Marcos de Plasma (paneles, menús, avisos) | `plasma_cristal.py` | 9 piezas con máscara y sombra; color `ColorScheme-Background` (claro u oscuro). Plasma usa `translucent/` cuando hay desenfoque detrás (relleno muy ligero) y la normal cuando no |
| Esquemas de color | `colores_cristal.py` | AxolOS Cristal oscuro y claro |
| Kvantum | `kvantum_axolos.py` | desde MacTahoe: `AxolOS` (claro) y `AxolOSDark` |
| Barras de título | `decoracion_cristal.py` | Aurorae `AxolOS` y `AxolOS-Claro`, dibujadas desde cero: la barra es el mismo cristal que la ventana (color y opacidad de Kvantum), sin contorno, esquinas de 14 px y sombra gaussiana redondeada; los botones son de `botones_axolos.py` |
| Disposición del escritorio | `diseno_axolos.py` | guion `contents/layouts/` de los dos temas globales a partir de la disposición de skel (barra, dock con Bento, reloj): aplicar el tema con «Diseño del escritorio» deja el escritorio de AxolOS |
| Menú de arranque (Limine) | `arranque_cristal.py` | a partir del fondo oscuro |
| Marca del instalador | `instalador_marca_axolos.py` + `instalador_textos.py` | diapositivas en los 6 idiomas |
| Terminal | `terminal_axolos.py` | Konsole translúcido |

- **KWin**: `axolos-glass` empaqueta el efecto [Glass](https://github.com/4v3ngR/kwin-effects-glass)
  (commit fijado) y su configuración en `/etc/xdg/kwinrc` (`Effect-blurplus`). Un efecto de KWin solo
  carga con la KWin para la que se compiló: KWin lo comprueba («built for a different version») y el
  gancho `zz-axolos-glass.hook` vuelve entonces al desenfoque normal hasta que llega la recompilación.
  La publicación corre en la imagen de CachyOS cada 3 horas para recompilarlo cuando cambia KWin.
- **Cómo se ve el cristal** (como el Liquid Glass de Apple): poco desenfoque, refracción en el canto,
  irisado y filo de luz, y tinte adaptable (`UseWindowPaletteTint` + `AutoTintAlpha`: el cristal toma
  el color del tema y solo se espesa cuando el fondo contrasta). Barra y dock en «translúcido» (un panel
  opaco hace sólidos también sus menús). Se afina viéndolo en un KWin virtual con el efecto cargado.
- **Claro y oscuro**: temas globales `com.noel.axolos` (oscuro) y `com.noel.axolos.claro`; Plasma
  puede alternarlos solo (`DefaultLightLookAndFeel`/`DefaultDarkLookAndFeel`). `axolos-aspecto` lo
  hace desde la terminal y desde el Centro; `axolos-aspecto --migrar` pone al día una cuenta que ya
  existía (una vez por versión, al iniciar sesión).
- **Apps PyQt**: `axolos_cristal.py` da la paleta del modo activo y, si el cristal está cargado,
  fondos translúcidos (si no, opacos).
- **Inicio de sesión**: `sddm/AxolOS/Cristal.qml` + `cristal.frag` (refracción, dispersión y brillo en
  QML). Recompilar el shader: `/usr/lib/qt6/bin/qsb --glsl "100 es,120,150" --hlsl 50 --msl 12 -o cristal.frag.qsb cristal.frag`.
- **Pendiente**: animación de arranque del ajolote de cristal (la anterior terminaba en la pose del
  fondo metálico; ahora la pantalla de inicio muestra el fondo tal cual).

## Idiomas

Español, inglés, francés, ruso, chino simplificado y japonés; cualquier otro idioma usa el inglés.

- Programas (Python y shell): textos en español marcados con `_()` / `t`; dominio `axolos`
  (`packages/axolos-branding/po`). Bento (QML): textos en inglés con `i18n()`; dominio
  `plasma_applet_org.axolos.bento` (`packages/axolos-menu/po`).
- `tools/i18n.sh` regenera plantillas y catálogos; `--comprobar` falla si falta algo o si un programa
  usa `_` como variable (`tools/i18n_sombras.py`). Añadir traducciones: `tools/i18n_rellenar.py LOTE.py`.
- Lanzadores, metadatos, esquemas de color y temas globales llevan sus traducciones dentro.

## Publicar

`git push` y GitHub Actions hace el resto ([publicar.yml](../.github/workflows/publicar.yml)): compila
cada paquete en la imagen de CachyOS, lo compara con el publicado (`tools/comparar_paquetes.py`; los
binarios se comparan por nombre y manda la receta `compilado-para`), sube `pkgrel` solo si cambió (y
lo guarda en git), firma y sube a la release [`x86_64`](https://github.com/SrNoelll/axolos/releases/tag/x86_64).
Secreto `AXOLOS_GPG_KEY` = clave privada de firma. A mano: `tools/publicar-repo.sh`
(`AXOLOS_SIN_SUBIR=1` para probar sin publicar).

- **Clave de firma**: `3F7DA47A1271EB49F17F573F992DB143AB099E91` (paquete `axolos-keyring`). Guarda una
  copia de la privada fuera del equipo.
- **No subas `pkgrel` a mano.**

## La ISO

```bash
sudo pacman -S --needed archiso git
./build-iso.sh
```

La ISO arranca el instalador de CachyOS más reciente con la capa de AxolOS (`iso/instalador/aplicar-axolos.sh`):
repositorio `[axolos]`, `axolos-desktop` en vez de `cachyos-kde-settings`, SDDM y Plymouth de AxolOS,
Limine con un grupo «AxolOS», marca del instalador y página «Escritorio». Con red instala todo al día
(repos de CachyOS optimizados por CPU y controladores con chwd); sin red, «Instalar sin conexión»
copia el sistema de la ISO (`iso/instalador/offline/`). Probar: `tools/probar-vm.sh nueva` y
`tools/probar-vm.sh nueva sinred`.

## Probar sin tocar el sistema

- Menú Bento real en varios idiomas: `tools/bento-dev/capturar.sh SALIDA es en fr ru zh_CN ja`.
- Escritorio completo con el cristal: `tools/escritorio-prueba.sh captura.png [oscuro|claro]` (KWin virtual,
  usuario limpio con skel y temas del repositorio; `DISENO=1` aplica el tema global con su disposición,
  `MENU=1` abre Bento, `VENTANAS="konsole dolphin"`). El efecto Glass solo carga con la versión exacta de
  KWin del equipo.
- `axolos-glass` lleva un parche propio (`ventanas-sin-filo.patch`): sin filo de luz en las ventanas.

## Avisos

- Las fuentes de Apple (`apple-fonts`) no se pueden redistribuir: nunca en la ISO pública ni en el
  repositorio; AxolOS usa Inter y Source Serif 4 si no están.
- `ID=axolos` en `os-release` con `ID_LIKE="cachyos arch"`.
- `collect.sh` (la «foto» del escritorio de Noel) se retiró: el aspecto ya no se copia de un
  escritorio, se genera.
