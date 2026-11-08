#!/usr/bin/env python3
"""AxolOS · iconos de las apps propias (Axo, Bienvenida, Instalar AxolOS).

Apps: Axo, Bienvenida, Centro e Instalar. Una familia: baldosa redondeada con el ajolote blanco y, en la esquina, un emblema que dice qué
hace cada app. Cada una tiene su color. El ajolote suelto («axolos») se queda para el sistema
(logo, Bento).

Solo degradados y formas: KDE pinta los iconos con QtSvg (SVG Tiny), sin filtros ni máscaras.

  iconos_apps_axolos.py            escribe los SVG en su paquete
  iconos_apps_axolos.py --vista D  además, PNG de muestra en D
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SILUETA = ROOT / "packages/axolos-branding/files/ajolote-silueta.svg"   # potrace del logo

# Caja del ajolote dentro del SVG de potrace (unidades de su viewBox 1977)
CAJA = (33, 261, 1926, 1746)

APPS = {
    # nombre del icono: (destino, degradado arriba, abajo, emblema, color del emblema, fondo del emblema)
    "axolos-axo": (ROOT / "packages/axolos-ia/static/axolos-axo.svg",
                   "#a093ff", "#5a46c4", "chispa", "#5a46c4", "#ffffff"),
    "axolos-bienvenida": (ROOT / "packages/axolos-bienvenida/static/axolos-bienvenida.svg",
                          "#ffa0b4", "#dc5378", "corazon", "#dc5378", "#ffffff"),
    "axolos-centro": (ROOT / "packages/axolos-bienvenida/static/axolos-centro.svg",
                      "#8fe0ee", "#2f8ea6", "ajustes", "#2f8ea6", "#ffffff"),
    "axolos-instalar": (ROOT / "iso/airootfs/usr/share/icons/hicolor/scalable/apps/axolos-instalar.svg",
                        "#3a3946", "#17171e", "instalar", "#ffffff", "#a69afe"),
}

EMBLEMAS = {
    # dibujados sobre un círculo de radio 1 centrado en 0,0 (se escalan al emblema)
    "chispa": '<path d="M0,-0.62 C0.06,-0.2 0.2,-0.06 0.62,0 C0.2,0.06 0.06,0.2 0,0.62 '
              'C-0.06,0.2 -0.2,0.06 -0.62,0 C-0.2,-0.06 -0.06,-0.2 0,-0.62 Z" transform="translate(-0.08,0.08)"/>'
              '<path d="M0,-0.24 C0.025,-0.08 0.08,-0.025 0.24,0 C0.08,0.025 0.025,0.08 0,0.24 '
              'C-0.025,0.08 -0.08,0.025 -0.24,0 C-0.08,-0.025 -0.025,-0.08 0,-0.24 Z" transform="translate(0.36,-0.36)"/>',
    "corazon": '<path d="M0,0.52 C-0.18,0.36 -0.56,0.1 -0.56,-0.17 C-0.56,-0.38 -0.4,-0.52 -0.22,-0.52 '
               'C-0.1,-0.52 -0.02,-0.45 0,-0.38 C0.02,-0.45 0.1,-0.52 0.22,-0.52 C0.4,-0.52 0.56,-0.38 '
               '0.56,-0.17 C0.56,0.1 0.18,0.36 0,0.52 Z"/>',
    "ajustes": '<rect x="-0.52" y="-0.36" width="1.04" height="0.12" rx="0.06"/>'
               '<rect x="-0.52" y="0.24" width="1.04" height="0.12" rx="0.06"/>'
               '<circle cx="0.2" cy="-0.3" r="0.17"/><circle cx="-0.22" cy="0.3" r="0.17"/>',
    "instalar": '<path d="M-0.09,-0.56 L0.09,-0.56 L0.09,0.02 L0.29,-0.18 L0.42,-0.05 L0,0.37 '
                'L-0.42,-0.05 L-0.29,-0.18 L-0.09,0.02 Z"/>'
                '<path d="M-0.5,0.3 L-0.32,0.3 L-0.32,0.42 L0.32,0.42 L0.32,0.3 L0.5,0.3 L0.5,0.6 L-0.5,0.6 Z"/>',
}


def silueta():
    texto = SILUETA.read_text(encoding="utf-8")
    g = re.search(r'<g transform="([^"]+)"', texto).group(1)
    caminos = "".join(re.findall(r"<path[^>]*/>", texto, re.S))
    return g, re.sub(r"\s+", " ", caminos)


def icono(arriba, abajo, emblema, c_emb, f_emb):
    g, caminos = silueta()
    # ajolote: 284 px de ancho, algo arriba a la izquierda para dejar sitio al emblema
    ancho = 284
    s = ancho / (CAJA[2] - CAJA[0])
    alto = (CAJA[3] - CAJA[1]) * s
    cx, cy = 240, 238
    tx, ty = cx - ancho / 2 - CAJA[0] * s, cy - alto / 2 - CAJA[1] * s
    ex, ey, er = 364, 364, 64          # emblema
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="baldosa" x1="0" y1="56" x2="0" y2="456" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{arriba}"/><stop offset="1" stop-color="{abajo}"/>
    </linearGradient>
    <linearGradient id="brillo" x1="0" y1="56" x2="0" y2="256" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.16"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="56" y="62" width="400" height="400" rx="96" fill="#000000" opacity="0.22"/>
  <rect x="56" y="56" width="400" height="400" rx="96" fill="url(#baldosa)"/>
  <rect x="56" y="56" width="400" height="400" rx="96" fill="url(#brillo)"/>
  <rect x="57.5" y="57.5" width="397" height="397" rx="94.5" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="3"/>
  <g transform="translate({tx:.2f},{ty:.2f}) scale({s:.6f})">
    <g transform="{g}" fill="#ffffff">{caminos}</g>
  </g>
  <circle cx="{ex}" cy="{ey}" r="{er + 12}" fill="{abajo}"/>
  <circle cx="{ex}" cy="{ey}" r="{er}" fill="{f_emb}"/>
  <g transform="translate({ex},{ey}) scale({er})" fill="{c_emb}">{EMBLEMAS[emblema]}</g>
</svg>
'''


def main():
    vista = Path(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[1] == "--vista" else None
    for nombre, (destino, arriba, abajo, emb, c_emb, f_emb) in APPS.items():
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(icono(arriba, abajo, emb, c_emb, f_emb), encoding="utf-8")
        print(f"{nombre}: {destino.relative_to(ROOT)}")
        if vista:
            vista.mkdir(parents=True, exist_ok=True)
            (vista / f"{nombre}.svg").write_text(destino.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
