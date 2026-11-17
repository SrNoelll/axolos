#!/usr/bin/env python3
"""AxolOS · fondo del menú de arranque (Limine) a partir del fondo oscuro de cristal líquido.

Oscurecido y con viñeta para que el menú de Limine se lea encima; arriba, «AxolOS». Sin más texto:
el arranque ocurre antes de conocer el idioma del sistema.
Uso: QT_QPA_PLATFORM=offscreen tools/arranque_cristal.py
"""
from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QRadialGradient, QBrush

RAIZ = Path(__file__).resolve().parent.parent
FONDO = RAIZ / "packages/axolos-themes/assets/wallpapers/AxolOS/contents/images_dark/3840x2160.jpg"
SALIDA = RAIZ / "packages/axolos-themes/arranque/limine.png"


def main():
    app = QGuiApplication(["arranque"])  # noqa: F841  (debe vivir mientras se dibuja)
    w, h = 1920, 1080
    img = QImage(w, h, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
                     | QPainter.RenderHint.TextAntialiasing)
    p.drawImage(QRectF(0, 0, w, h), QImage(str(FONDO)))
    p.fillRect(0, 0, w, h, QColor(0, 0, 0, 120))                  # más oscuro: el menú se lee encima
    g = QRadialGradient(w / 2, h * 0.55, w * 0.62)                # viñeta
    g.setColorAt(0.45, QColor(0, 0, 0, 0))
    g.setColorAt(1.0, QColor(0, 0, 0, 170))
    p.fillRect(0, 0, w, h, QBrush(g))
    f = QFont("Source Serif 4")
    f.setPixelSize(64)
    f.setWeight(QFont.Weight.DemiBold)
    p.setFont(f)
    p.setPen(QColor("#ececf3"))
    p.drawText(QRectF(0, 52, w, 90), int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter), "AxolOS")
    p.end()
    img.save(str(SALIDA))
    print(SALIDA)


if __name__ == "__main__":
    main()
