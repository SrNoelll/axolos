# AxolOS · animación de arranque (KSplash)

Hecha siguiendo la skill `motion-videos` de Noel (puertas: hoja de personaje →
storyboard → borrador → final), adaptada a una animación que corre en directo
en Plasma: sin vídeo, sin sonido (KSplash no reproduce audio).

## La idea
> El ajolote real del fondo entra caminando en la oscuridad con su propia luz,
> frena, da un coletazo, abre el ojo y un iris de luz enciende el mundo.
> El último fotograma **es** tu escritorio: el corte no existe.

## Por qué dura 1,9 s
Medido en este equipo: KSplash está en pantalla **2,14 s**
(`journalctl --user -b | grep plasma-ksplash`). La historia completa cabe en
1,9 s a velocidad real. Si un arranque tarda más, el ajolote espera quieto en
su pose (el ojo destella de vez en cuando) y aparece la tarjeta *AxolOS*.

## Guion (film.js es la única fuente de tiempos)
| t | qué pasa |
|---|---|
| 0,00–0,22 | su luz se enciende en la oscuridad; se echa atrás (anticipación) |
| 0,12–1,12 | ~4,5 pasos en pares diagonales; **cada pie apoyado no resbala** |
| 1,12–1,50 | frena, se pasa 24 px y vuelve con muelle; coletazo amortiguado |
| 1,33 | destello en el ojo |
| 1,38–1,82 | iris de luz desde su ojo: enciende los tubos |
| 1,82–1,94 | relevo al fondo dibujado igual que Plasma (imperceptible) |

## Personaje (Axolote.qml + rig/)
- Es el ajolote **del fondo**, recortado en 6 piezas por `tools/rig_axolote.py`:
  cuerpo rígido, 4 patas y cola, con las articulaciones rellenas.
- Nunca se deforma. Solo giran las piezas alrededor de sus pivotes.
- **Pies apoyados**: durante el apoyo, el ángulo de cada pata se calcula para
  que el pie quede quieto en el mundo (`plantedAngle`). Si la pata no llega,
  apoya un poco más atrás (alcance de la articulación, 78 %).

## Dirección de arte
Abismo `#050506` · Obsidiana `#121215` · Grafito `#2a2a30` · Hierro `#5b5b63`
· Plata `#a3a3ab` · Destello `#e8e8ee` · Violeta AxolOS `#926ee4` (solo interfaz).
Tipografías: **New York Extra Large** (marca) + **iA Writer Mono S** (texto).
Luz clave arriba-izquierda, sombra abajo-derecha.

## Medidas de calidad (borrador renderizado con GPU)
- Deslizamiento de los pies apoyados: **0 px/s** en las cuatro patas.
- Pose al terminar el iris: reposo exacto (todas las articulaciones a 0).
- Cambio máximo entre fotogramas en el relevo final: ≥ **40,9 dB** PSNR.
- Último fotograma frente al escritorio de Plasma: **49,9 dB** PSNR.

## Comandos (desde la raíz de AxolOS)
```
tools/splash-dev/render.sh hoja        hoja.png      # puerta 1
tools/splash-dev/render.sh storyboard  story.png     # puerta 2
tools/splash-dev/render.sh draft       borrador.mp4  # puerta 3 (960x540)
tools/splash-dev/render.sh final       final.mp4     # puerta 4 (1080p)
python3 tools/rig_axolote.py FONDO.jpg tools/silueta-ajolote.png packages/axolos-themes/splash/rig
```
Todo se renderiza en un KWin virtual e invisible: no aparece nada en pantalla.
