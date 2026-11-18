#!/usr/bin/env python3
"""AxolOS · iconos de cristal líquido (Qt dibuja las formas, Blender las renderiza).

Cada icono = una placa de color brillante (cuadrado redondeado o carpeta) + el símbolo hecho de
cristal real encima, que refracta la placa y separa los colores en sus bordes (como los iconos de
«liquid glass»). Formas y símbolos dibujados aquí (sin recursos de otros temas de iconos).

  QT_QPA_PLATFORM=offscreen tools/iconos_cristal.py [--solo nombre,nombre] [--vista CARPETA]

Escribe PNG en el tema de iconos AxolOS (16…256 px y @2x) y los iconos de las apps de AxolOS.
"""
import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPainterPath, QPen, QTransform
from PyQt6.QtSvg import QSvgRenderer

RAIZ = Path(__file__).resolve().parent.parent
SILUETA = RAIZ / "packages/axolos-branding/files/ajolote-silueta.svg"
TEMA = RAIZ / "packages/axolos-themes/assets/icons/AxolOS"
N = 512                                   # lienzo de trabajo


# ---- formas (placas) ---------------------------------------------------------------------------
def cuadrado(p):
    r = QPainterPath()
    r.addRoundedRect(QRectF(56, 56, 400, 400), 104, 104)
    return r


def carpeta(p):
    r = QPainterPath()
    r.addRoundedRect(QRectF(44, 120, 424, 316), 46, 46)
    pestana = QPainterPath()
    pestana.addRoundedRect(QRectF(44, 88, 186, 90), 36, 36)
    return r.united(pestana)


def papelera(p):
    r = QPainterPath()
    r.addRoundedRect(QRectF(118, 150, 276, 314), 54, 54)
    tapa = QPainterPath()
    tapa.addRoundedRect(QRectF(88, 100, 336, 62), 30, 30)
    asa = QPainterPath()
    asa.addRoundedRect(QRectF(204, 66, 104, 52), 24, 24)
    return r.united(tapa).united(asa)


# ---- símbolos ----------------------------------------------------------------------------------
def trazo(path, ancho):
    """Contorno grueso de un trazo como forma rellena (para símbolos de línea)."""
    from PyQt6.QtGui import QPainterPathStroker
    s = QPainterPathStroker()
    s.setWidth(ancho)
    s.setCapStyle(Qt.PenCapStyle.RoundCap)
    s.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return s.createStroke(path).simplified()


def ajolote(caja):
    """Silueta del ajolote encajada en caja (QRectF)."""
    img = QImage(N, N, QImage.Format.Format_Grayscale8)
    img.fill(QColor("white"))
    pt = QPainter(img)
    pt.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(str(SILUETA)).render(pt, caja)
    pt.end()
    return img


def chispa(cx, cy, r):
    """Destello de cuatro puntas con lados cóncavos."""
    k = 0.18 * r
    p = QPainterPath(QPointF(cx, cy - r))
    p.cubicTo(cx + k * 0.5, cy - k, cx + k, cy - k * 0.5, cx + r, cy)
    p.cubicTo(cx + k, cy + k * 0.5, cx + k * 0.5, cy + k, cx, cy + r)
    p.cubicTo(cx - k * 0.5, cy + k, cx - k, cy + k * 0.5, cx - r, cy)
    p.cubicTo(cx - k, cy - k * 0.5, cx - k * 0.5, cy - k, cx, cy - r)
    return p


def corazon(cx, cy, r):
    p = QPainterPath(QPointF(cx, cy + r * 0.9))
    p.cubicTo(cx - r * 1.5, cy - r * 0.1, cx - r * 0.75, cy - r * 1.2, cx, cy - r * 0.45)
    p.cubicTo(cx + r * 0.75, cy - r * 1.2, cx + r * 1.5, cy - r * 0.1, cx, cy + r * 0.9)
    return p


def deslizadores(cx, cy, r):
    p = QPainterPath()
    for i, x in enumerate((-0.55, 0.0, 0.55)):
        linea = QPainterPath(QPointF(cx + x * r, cy - r))
        linea.lineTo(cx + x * r, cy + r)
        p = p.united(trazo(linea, r * 0.16))
        y = cy + (-0.35, 0.45, -0.05)[i] * r
        bola = QPainterPath()
        bola.addEllipse(QPointF(cx + x * r, y), r * 0.24, r * 0.24)
        p = p.united(bola)
    return p


def flecha_abajo(cx, cy, r, bandeja=True):
    p = QPainterPath(QPointF(cx, cy - r))
    p.lineTo(cx, cy + r * 0.45)
    p.moveTo(cx - r * 0.55, cy - r * 0.05)
    p.lineTo(cx, cy + r * 0.5)
    p.lineTo(cx + r * 0.55, cy - r * 0.05)
    if bandeja:
        p.moveTo(cx - r * 0.85, cy + r * 0.55)
        p.lineTo(cx - r * 0.85, cy + r)
        p.lineTo(cx + r * 0.85, cy + r)
        p.lineTo(cx + r * 0.85, cy + r * 0.55)
    return trazo(p, r * 0.24)


def documento(cx, cy, r):
    hoja = QPainterPath()
    hoja.addRoundedRect(QRectF(cx - r * 0.7, cy - r, r * 1.4, r * 2), r * 0.18, r * 0.18)
    rayas = QPainterPath()
    for y in (-0.45, -0.05, 0.35):
        rayas.moveTo(cx - r * 0.38, cy + y * r)
        rayas.lineTo(cx + r * 0.38, cy + y * r)
    return hoja.subtracted(trazo(rayas, r * 0.14))


def nota(cx, cy, r):
    p = QPainterPath()
    cab = QPainterPath()
    cab.addEllipse(QPointF(cx - r * 0.35, cy + r * 0.62), r * 0.38, r * 0.3)
    palo = QPainterPath(QPointF(cx - r * 0.02, cy + r * 0.6))
    palo.lineTo(cx - r * 0.02, cy - r * 0.9)
    palo.lineTo(cx + r * 0.62, cy - r * 0.62)
    return p.united(cab).united(trazo(palo, r * 0.2))


def imagen(cx, cy, r):
    marco = QPainterPath()
    marco.addRoundedRect(QRectF(cx - r, cy - r * 0.78, r * 2, r * 1.56), r * 0.22, r * 0.22)
    hueco = QPainterPath()
    hueco.addRoundedRect(QRectF(cx - r * 0.78, cy - r * 0.56, r * 1.56, r * 1.12), r * 0.1, r * 0.1)
    monte = QPainterPath(QPointF(cx - r * 0.78, cy + r * 0.56))
    monte.lineTo(cx - r * 0.2, cy - r * 0.05)
    monte.lineTo(cx + r * 0.2, cy + r * 0.3)
    monte.lineTo(cx + r * 0.45, cy + r * 0.12)
    monte.lineTo(cx + r * 0.78, cy + r * 0.56)
    monte.closeSubpath()
    sol = QPainterPath()
    sol.addEllipse(QPointF(cx + r * 0.38, cy - r * 0.22), r * 0.15, r * 0.15)
    return marco.subtracted(hueco).united(monte).united(sol)


def video(cx, cy, r):
    p = QPainterPath(QPointF(cx - r * 0.55, cy - r * 0.8))
    p.lineTo(cx + r * 0.85, cy)
    p.lineTo(cx - r * 0.55, cy + r * 0.8)
    p.closeSubpath()
    return trazo(p, r * 0.22).united(p)


def monitor(cx, cy, r):
    pant = QPainterPath()
    pant.addRoundedRect(QRectF(cx - r, cy - r * 0.8, r * 2, r * 1.3), r * 0.18, r * 0.18)
    pie = QPainterPath(QPointF(cx - r * 0.45, cy + r * 0.95))
    pie.lineTo(cx + r * 0.45, cy + r * 0.95)
    pie.moveTo(cx, cy + r * 0.5)
    pie.lineTo(cx, cy + r * 0.95)
    return pant.united(trazo(pie, r * 0.18))


def casa(cx, cy, r):
    p = QPainterPath(QPointF(cx - r * 0.85, cy - r * 0.05))
    p.lineTo(cx, cy - r * 0.85)
    p.lineTo(cx + r * 0.85, cy - r * 0.05)
    p.lineTo(cx + r * 0.85, cy + r * 0.85)
    p.lineTo(cx - r * 0.85, cy + r * 0.85)
    p.closeSubpath()
    puerta = QPainterPath()
    puerta.addRoundedRect(QRectF(cx - r * 0.22, cy + r * 0.25, r * 0.44, r * 0.62), r * 0.08, r * 0.08)
    return trazo(p, r * 0.12).united(p).subtracted(puerta)


def terminal(cx, cy, r):
    p = QPainterPath(QPointF(cx - r * 0.8, cy - r * 0.55))
    p.lineTo(cx - r * 0.2, cy)
    p.lineTo(cx - r * 0.8, cy + r * 0.55)
    p.moveTo(cx + r * 0.05, cy + r * 0.62)
    p.lineTo(cx + r * 0.85, cy + r * 0.62)
    return trazo(p, r * 0.24)


def ranuras(cx, cy, r):
    p = QPainterPath()
    for x in (-0.42, 0.0, 0.42):
        p.moveTo(cx + x * r, cy - r * 0.62)
        p.lineTo(cx + x * r, cy + r * 0.72)
    return trazo(p, r * 0.17)


def engranaje(cx, cy, r):
    p = QPainterPath()
    dientes = 8
    pts = []
    for i in range(dientes * 4):
        a = 2 * math.pi * i / (dientes * 4)
        rr = r if (i % 4) in (0, 1) else r * 0.74
        pts.append(QPointF(cx + rr * math.cos(a), cy + rr * math.sin(a)))
    p.moveTo(pts[0])
    for q in pts[1:]:
        p.lineTo(q)
    p.closeSubpath()
    hueco = QPainterPath()
    hueco.addEllipse(QPointF(cx, cy), r * 0.32, r * 0.32)
    return p.subtracted(hueco)


# ---- catálogo ----------------------------------------------------------------------------------
# nombre: (forma, colores de la placa (arriba, abajo), símbolo, nombres del icono en el tema)
MORADO = ("#b3a8ff", "#6b57d6")
ICONOS = {
    "axolos-axo": (cuadrado, ("#a093ff", "#5a46c4"), "ajolote+chispa", []),
    "axolos-bienvenida": (cuadrado, ("#ffa0b4", "#dc5378"), "ajolote+corazon", []),
    "axolos-centro": (cuadrado, ("#8fe0ee", "#2f8ea6"), "ajolote+deslizadores", []),
    "axolos-instalar": (cuadrado, ("#4a4858", "#18171f"), "ajolote+flecha", []),
    "carpeta": (carpeta, MORADO, None, ["folder", "inode-directory", "folder-open"]),
    "carpeta-documentos": (carpeta, MORADO, "documento", ["folder-documents", "folder-text"]),
    "carpeta-descargas": (carpeta, MORADO, "descargas", ["folder-download", "folder-downloads"]),
    "carpeta-musica": (carpeta, MORADO, "nota", ["folder-music", "folder-sound"]),
    "carpeta-imagenes": (carpeta, MORADO, "imagen", ["folder-pictures", "folder-images"]),
    "carpeta-videos": (carpeta, MORADO, "video", ["folder-videos", "folder-video"]),
    "carpeta-escritorio": (carpeta, MORADO, "monitor", ["user-desktop", "folder-desktop"]),
    "carpeta-personal": (carpeta, MORADO, "casa", ["user-home", "folder-home"]),
    # con los nombres de KDE y los de GNOME (Archivos/Nautilus, Consola, Configuración), que también se usan
    "archivos": (carpeta, ("#c6bdff", "#7a66e0"), "ajolote", ["system-file-manager", "org.kde.dolphin",
                                                              "org.gnome.Nautilus", "nautilus", "file-manager"]),
    "terminal": (cuadrado, ("#3b3a4a", "#121218"), "terminal", ["utilities-terminal", "org.kde.konsole", "konsole",
                                                                "org.gnome.Console", "org.gnome.Terminal",
                                                                "gnome-terminal", "terminal"]),
    "ajustes": (cuadrado, ("#a9aec2", "#4c5164"), "engranaje", ["preferences-system", "systemsettings",
                                                                "org.gnome.Settings", "gnome-control-center"]),
    "papelera": (papelera, ("#55546a", "#1d1c25"), "ranuras", ["user-trash", "trashcan_empty", "user-trash-full",
                                                              "trashcan_full"]),
}
SIMBOLOS = {"chispa": chispa, "corazon": corazon, "deslizadores": deslizadores, "flecha": flecha_abajo,
            "documento": documento, "descargas": flecha_abajo, "nota": nota, "imagen": imagen, "video": video,
            "monitor": monitor, "casa": casa, "terminal": terminal, "engranaje": engranaje, "ranuras": ranuras}


def mascara_de(path_o_img):
    if isinstance(path_o_img, QImage):
        img = path_o_img
        b = img.constBits()
        b.setsize(img.sizeInBytes())
        return np.frombuffer(b, np.uint8).reshape(N, img.bytesPerLine())[:, :N] < 128
    img = QImage(N, N, QImage.Format.Format_Grayscale8)
    img.fill(QColor("white"))
    pt = QPainter(img)
    pt.setRenderHint(QPainter.RenderHint.Antialiasing)
    pt.fillPath(path_o_img, QColor("black"))
    pt.end()
    return mascara_de(img)


def mascaras(nombre):
    forma, colores, simbolo, _ = ICONOS[nombre]
    placa = mascara_de(forma(None))
    # caja interior del símbolo (en la carpeta, sobre el cuerpo)
    cx, cy, r = (256, 284, 104) if forma is carpeta else (256, 256, 120) if forma is cuadrado else (256, 300, 84)
    capa = np.zeros((N, N), bool)
    if simbolo:
        partes = simbolo.split("+")
        if partes[0] == "ajolote":
            grande = len(partes) == 1
            caja = QRectF(cx - r * 1.25, cy - r * 1.2, r * 2.5, r * 2.5) if grande else QRectF(cx - r * 1.3, cy - r * 1.3, r * 2.35, r * 2.35)
            capa |= mascara_de(ajolote(caja))
            partes = partes[1:]
            if partes:   # emblema en la esquina inferior derecha, con un hueco alrededor
                ex, ey, er = cx + r * 0.92, cy + r * 0.92, r * 0.46
                hueco = QPainterPath()
                hueco.addEllipse(QPointF(ex, ey), er * 1.35, er * 1.35)
                capa &= ~mascara_de(hueco)
                capa |= mascara_de(SIMBOLOS[partes[0]](ex, ey, er))
        else:
            capa |= mascara_de(SIMBOLOS[partes[0]](cx, cy, r * 0.82))
    capa &= placa
    return placa, capa, colores


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--solo", default="")
    a.add_argument("--vista", default="")
    a.add_argument("--muestras", type=int, default=256)
    a.add_argument("--solo-vista", action="store_true", help="no escribe en el tema (pruebas)")
    a.add_argument("--reinstalar", action="store_true",
                   help="sin Blender: vuelve a escribir todos los tamaños y nombres desde los renders ya hechos "
                        "(p. ej. al añadir nombres a ICONOS)")
    args = a.parse_args()
    app = QGuiApplication(["iconos"])  # noqa: F841
    if args.reinstalar:
        for nombre, (_, _, _, temas) in ICONOS.items():
            if nombre.startswith("axolos-") or not temas:
                continue
            ctx = "apps" if nombre in ("archivos", "terminal", "ajustes") else "places"
            maestro = TEMA / "256x256@2x" / ctx / f"{temas[0]}.png"
            instalar(nombre, QImage(str(maestro)), "", False)
            print(nombre, "→", ", ".join(temas))
        return 0
    nombres = [n for n in ICONOS if not args.solo or n in args.solo.split(",")]
    with tempfile.TemporaryDirectory() as tmp:
        trabajos = []
        for n in nombres:
            placa, capa, colores = mascaras(n)
            np.save(f"{tmp}/{n}-placa.npy", placa)
            np.save(f"{tmp}/{n}-simbolo.npy", capa)
            trabajos.append({"nombre": n, "placa": f"{tmp}/{n}-placa.npy", "simbolo": f"{tmp}/{n}-simbolo.npy",
                             "colores": list(colores), "salida": f"{tmp}/{n}.png"})
        (Path(tmp) / "trabajos.json").write_text(json.dumps(trabajos))
        subprocess.run(["blender", "-b", "--factory-startup", "--python", str(RAIZ / "tools/iconos_cristal_blender.py"),
                        "--", f"{tmp}/trabajos.json", str(args.muestras)], check=True,
                       stdout=subprocess.DEVNULL)
        for t in trabajos:
            instalar(t["nombre"], QImage(t["salida"]), args.vista, args.solo_vista)


TAMANOS = (16, 24, 32, 48, 256)


def instalar(nombre, img, vista, solo_vista=False):
    from PyQt6.QtCore import QSize
    _, _, _, temas = ICONOS[nombre]
    def a(t):
        return img.scaled(QSize(t, t), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    if vista:
        Path(vista).mkdir(parents=True, exist_ok=True)
        img.save(f"{vista}/{nombre}.png")
    if solo_vista:
        return
    if nombre.startswith("axolos-"):     # iconos de las apps de AxolOS: hicolor de cada paquete
        destino = {"axolos-axo": RAIZ / "packages/axolos-ia/static/iconos",
                   "axolos-bienvenida": RAIZ / "packages/axolos-bienvenida/static/iconos",
                   "axolos-centro": RAIZ / "packages/axolos-bienvenida/static/iconos",
                   "axolos-instalar": RAIZ / "iso/airootfs/usr/share/icons/hicolor"}[nombre]
        for t in (16, 22, 24, 32, 48, 64, 128, 256, 512):
            d = destino / f"{t}x{t}/apps"
            d.mkdir(parents=True, exist_ok=True)
            a(t).save(str(d / f"{nombre}.png"))
        return
    for t in TAMANOS:
        for escala in (1, 2):
            sub = f"{t}x{t}" + ("@2x" if escala == 2 else "")
            d = TEMA / sub / ("apps" if nombre in ("archivos", "terminal", "ajustes") else "places")
            d.mkdir(parents=True, exist_ok=True)
            im = a(t * escala)
            for icono in temas:
                im.save(str(d / f"{icono}.png"))


if __name__ == "__main__":
    sys.exit(main())
