#!/usr/bin/env python3
"""AxolOS · marca del instalador (Calamares).

Genera iso/instalador/marca/:
  axolos/                   componente de marca de Calamares (textos, logos, colores, diapositivas)
  escritorio-axolos.png     vista previa del escritorio para la página «Escritorio»

Se dibuja con Qt (fuentes libres: Source Serif 4, Inter, JetBrains Mono y Noto CJK para chino y
japonés) para que la ISO pueda redistribuirlo. Las diapositivas salen en cada idioma de IDIOMAS y
show.qml elige la del idioma del instalador con las traducciones de la marca (lang/*.qm).
Uso:  QT_QPA_PLATFORM=offscreen tools/instalador_marca_axolos.py
"""
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QGuiApplication, QImage,
                         QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient)
from PyQt6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
SALIDA = ROOT / "iso/instalador/marca"
MARCA = SALIDA / "axolos"
FONDO = ROOT / "packages/axolos-themes/assets/wallpapers/AxolOS/contents/images/2730x1536.jpg"
LOGO = ROOT / "packages/axolos-branding/files/axolos-logo.png"
ICONOS = {
    "axo": ROOT / "packages/axolos-ia/static/axolos-axo.svg",
    "bienvenida": ROOT / "packages/axolos-bienvenida/static/axolos-bienvenida.svg",
    "instalar": ROOT / "iso/airootfs/usr/share/icons/hicolor/scalable/apps/axolos-instalar.svg",
}
C = dict(bg="#17171d", bg_dark="#0f0f13", surface="#1e1e26", border="#2a2a34", fg="#e6e6ee",
         muted="#a3a3b4", faint="#5b5b68", accent="#a69afe", accent_hi="#cdc6ff", accent_lo="#7662ce",
         pink="#ff7a93", green="#7ddfb4", yellow="#f3cf7a", cyan="#7fd4e4")
SERIF, SANS, MONO = "Source Serif 4", "Inter", "JetBrainsMono Nerd Font"


CJK = []   # familias de respaldo para el idioma que se está dibujando (chino o japonés)


def fuente(familia, px, peso=QFont.Weight.Normal):
    f = QFont(familia)
    f.setFamilies([familia, *CJK])
    f.setPixelSize(int(px))
    f.setWeight(peso)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return f


def lienzo(w, h, transparente=False):
    img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent if transparente else QColor(C["bg_dark"]))
    p = QPainter(img)
    p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
                     | QPainter.RenderHint.SmoothPixmapTransform)
    return img, p


def svg(p, ruta, rect):
    QSvgRenderer(str(ruta)).render(p, rect)


def ajolote(p, rect, opacidad=1.0):
    img = QImage(str(LOGO))
    p.save()
    p.setOpacity(opacidad)
    p.drawImage(rect, img)
    p.restore()


def resplandor(p, centro, radio, color, alfa=110):
    g = QRadialGradient(centro, radio)
    c = QColor(color)
    c.setAlpha(alfa)
    g.setColorAt(0, c)
    c.setAlpha(0)
    g.setColorAt(1, c)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(g))
    p.drawEllipse(centro, radio, radio)


def fondo_axolos(p, w, h, oscuro=0.30):
    """Fondo de pantalla de AxolOS, recortado, oscurecido y con degradado a la izquierda para el texto."""
    img = QImage(str(FONDO))
    esc = max(w / img.width(), h / img.height())
    src_w, src_h = w / esc, h / esc
    p.drawImage(QRectF(0, 0, w, h), img,
                QRectF((img.width() - src_w) / 2, (img.height() - src_h) / 2, src_w, src_h))
    velo = QColor(C["bg_dark"])
    velo.setAlphaF(1 - oscuro)
    p.fillRect(QRectF(0, 0, w, h), velo)
    g = QLinearGradient(0, 0, w * 0.62, 0)
    g.setColorAt(0, QColor(15, 15, 19, 245))
    g.setColorAt(1, QColor(15, 15, 19, 0))
    p.fillRect(QRectF(0, 0, w, h), QBrush(g))


def texto(p, rect, s, f, color, flags=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop):
    p.setFont(f)
    p.setPen(QColor(color))
    return p.drawText(rect, int(flags) | int(Qt.TextFlag.TextWordWrap), s)


def caja(p, rect, radio, relleno, borde=None, ancho=2):
    camino = QPainterPath()
    camino.addRoundedRect(rect, radio, radio)
    p.setPen(QPen(QColor(borde), ancho) if borde else Qt.PenStyle.NoPen)
    p.setBrush(QColor(relleno))
    p.drawPath(camino)


# ---- diapositivas -----------------------------------------------------------------------------
# 1920×1080, con todo lo importante dentro de la franja central (y 200–880): Calamares las recorta
# para llenar su zona (más ancha que 16:9) sin deformarlas.
W, H = 1920, 1080
X0, ANCHO_TXT = 170, 820


def diapositiva(etiqueta, titulo, cuerpo, dibujo, t):
    img, p = lienzo(W, H)
    fondo_axolos(p, W, H)
    y = 300
    texto(p, QRectF(X0, y, ANCHO_TXT, 40), etiqueta.upper(), fuente(SANS, 24, QFont.Weight.DemiBold), C["accent"])
    r = texto(p, QRectF(X0, y + 52, ANCHO_TXT, 300), titulo, fuente(SERIF, 82, QFont.Weight.DemiBold), C["fg"])
    texto(p, QRectF(X0, r.bottom() + 28, ANCHO_TXT - 40, 360), cuerpo, fuente(SANS, 33), C["muted"])
    dibujo(p, t)
    p.end()
    return img


def d_bienvenida(p, t):
    c = QPointF(1420, 540)
    resplandor(p, c, 330, C["accent"], 90)
    ajolote(p, QRectF(c.x() - 300, c.y() - 300, 600, 600))


def d_axo(p, t):
    resplandor(p, QPointF(1430, 540), 360, C["accent_lo"], 80)
    svg(p, ICONOS["axo"], QRectF(1130, 250, 200, 200))
    burbujas = [
        (QRectF(1260, 450, 520, 92), C["accent"], C["bg_dark"], t["pregunta"]),
        (QRectF(1060, 568, 640, 150), "#26262f", C["fg"], t["respuesta"]),
    ]
    for rect, fondo, color, frase in burbujas:
        caja(p, rect, 30, fondo)
        texto(p, rect.adjusted(30, 22, -30, -18), frase, fuente(SANS, 27), color)
    texto(p, QRectF(1060, 740, 640, 40), t["privado"], fuente(SANS, 24), C["faint"])


def d_buscar(p, t):
    resplandor(p, QPointF(1420, 540), 360, C["accent_lo"], 70)
    caja(p, QRectF(1020, 300, 780, 84), 42, C["surface"], C["accent"], 3)
    texto(p, QRectF(1080, 322, 680, 44), t["consulta"], fuente(SANS, 31), C["fg"])
    filas = [("#f3b27a", "#7fd4e4", t["archivos"][0], t["donde"][0]),
             ("#7fd4e4", "#a69afe", t["archivos"][1], t["donde"][1]),
             ("#7ddfb4", "#f3cf7a", "IMG_2041.jpg", t["donde"][2])]
    y = 420
    for a, b, nombre, sub in filas:
        caja(p, QRectF(1020, y, 780, 108), 22, "#20202a")
        g = QLinearGradient(1044, y + 16, 1120, y + 92)
        g.setColorAt(0, QColor(a))
        g.setColorAt(1, QColor(b))
        camino = QPainterPath()
        camino.addRoundedRect(QRectF(1044, y + 16, 76, 76), 14, 14)
        p.fillPath(camino, QBrush(g))
        texto(p, QRectF(1146, y + 20, 600, 40), nombre, fuente(SANS, 29, QFont.Weight.Medium), C["fg"])
        texto(p, QRectF(1146, y + 60, 600, 36), sub, fuente(SANS, 23), C["faint"])
        y += 124


def d_programar(p, t):
    resplandor(p, QPointF(1420, 540), 360, C["accent_lo"], 70)
    marco = QRectF(1000, 260, 820, 560)
    caja(p, marco, 26, "#121217", C["border"], 2)
    for i, col in enumerate(("#5c5b67", "#5c5b67", C["accent"])):
        p.setBrush(QColor(col))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(marco.right() - 108 + i * 34, marco.top() + 34), 9, 9)
    lineas = [
        [(t["carpeta"] + " ", C["cyan"]), ("main ", C["accent"]), ("❯", C["green"])],
        [(t["orden"], C["fg"])],
        [("✓ ", C["green"]), ("Rust · rustup, cargo, rust-analyzer", C["muted"])],
        [("✓ ", C["green"]), (t["python"], C["muted"])],
        [("$ git log --oneline", C["fg"])],
        [("a1f3c2e ", C["yellow"]), (t["commit"], C["muted"])],
    ]
    f = fuente(MONO, 27)
    fm = QFontMetricsF(f)
    y = marco.top() + 96
    for linea in lineas:
        x = marco.left() + 44
        for s, color in linea:
            texto(p, QRectF(x, y, 800, 40), s, f, color)
            x += fm.horizontalAdvance(s)
        y += 66


def d_aldia(p, t):
    resplandor(p, QPointF(1420, 540), 360, C["accent_lo"], 70)
    caja(p, QRectF(1040, 300, 740, 92), 46, C["surface"], C["border"], 2)
    texto(p, QRectF(1040, 322, 740, 48), "sudo pacman -Syu", fuente(MONO, 34), C["fg"], Qt.AlignmentFlag.AlignHCenter)
    puntos = list(zip(("CachyOS", "AxolOS", "Btrfs"), t["puntos"]))
    y = 440
    for nombre, sub in puntos:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(C["accent"]))
        p.drawEllipse(QPointF(1080, y + 26), 14, 14)
        texto(p, QRectF(1114, y, 660, 44), nombre, fuente(SANS, 31, QFont.Weight.DemiBold), C["fg"])
        texto(p, QRectF(1114, y + 42, 660, 40), sub, fuente(SANS, 26), C["muted"])
        y += 110


DIBUJOS = [d_bienvenida, d_axo, d_buscar, d_programar, d_aldia]
from instalador_textos import IDIOMAS, TEXTOS, QM_CJK  # noqa: E402  textos por idioma

SHOW_QML = '''/* AxolOS · presentación durante la instalación (generada por tools/instalador_marca_axolos.py) */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation
    // Idioma de las diapositivas: lo traduce lang/calamares-axolos_<idioma>.qm según el idioma elegido
    // en el instalador (es, fr, ru, zh_CN, ja); con cualquier otro, inglés.
    readonly property string idioma: qsTr("en", "slides language code")
    Rectangle { anchors.fill: parent; color: "#0f0f13"; z: -1 }
    Timer {
        interval: 12000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
%s
}
'''
SLIDE_QML = '''    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "%s." + presentation.idioma + ".jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }'''

BRANDING_DESC = '''---
# AxolOS · marca del instalador (generada por tools/instalador_marca_axolos.py)
componentName:  axolos
welcomeStyleCalamares:   false
welcomeExpandingLogo:   true
windowExpanding:    normal
windowSize: 1100px,600px
windowPlacement: center
sidebar: qml,bottom
navigation: widget
strings:
    productName:         AxolOS
    shortProductName:    AxolOS
    version:             "%(version)s"
    shortVersion:        "%(version)s"
    versionedName:       AxolOS
    shortVersionedName:  AxolOS
    bootloaderEntryName: AxolOS
    productUrl:          https://github.com/SrNoelll/axolos
    supportUrl:          https://github.com/SrNoelll/axolos/issues
images:
    productLogo:         "logo.png"
    productIcon:         "icon.png"
    productWelcome:      "welcome.png"
style:
   SidebarBackground:        "#131318"
   SidebarText:              "#a3a3b4"
   SidebarTextCurrent:       "#17171d"
   SidebarBackgroundCurrent: "#a69afe"
slideshow:               "show.qml"
slideshowAPI: 2
uploadServer :
    type :    "http"
    url :     "https://paste.cachyos.org"
    sizeLimit : -1
'''

SIDEBAR_QML = '''/* AxolOS · barra de pasos del instalador (abajo), con los colores de la marca */
import io.calamares.ui 1.0
import io.calamares.core 1.0
import QtQuick 2.3
import QtQuick.Layouts 1.3

Rectangle {
    id: sideBar
    color: Branding.styleString(Branding.SidebarBackground)
    height: 46
    width: parent ? parent.width : 0      // al crearse aún no tiene padre
    Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: "#2a2a34" }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12; anchors.rightMargin: 12
        spacing: 4
        Image {
            Layout.alignment: Qt.AlignVCenter
            Layout.rightMargin: 8
            width: 28; height: 28
            sourceSize.width: 28; sourceSize.height: 28
            source: "file:/" + Branding.imagePath(Branding.ProductLogo)
        }
        Repeater {
            model: ViewManager
            Rectangle {
                readonly property bool actual: index == ViewManager.currentStepIndex
                readonly property bool hecho: index < ViewManager.currentStepIndex
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
                height: 30
                radius: 15
                color: actual ? Branding.styleString(Branding.SidebarBackgroundCurrent) : "transparent"
                Text {
                    anchors.centerIn: parent
                    width: parent.width - 8
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    text: display
                    color: parent.actual ? Branding.styleString(Branding.SidebarTextCurrent)
                         : (parent.hecho ? "#e6e6ee" : Branding.styleString(Branding.SidebarText))
                    font.weight: parent.actual ? Font.DemiBold : Font.Normal
                    font.pointSize: 9.5
                }
            }
        }
    }
}
'''

STYLESHEET = '''/* AxolOS · estilo del instalador (Calamares) */
QWidget { font: 13px; }
QDialogButtonBox { dialogbuttonbox-buttons-have-icons: 0; }
#debugButton { background-color: none; font: bold 8px; color: #ffffff; height: 32px; padding: 0px; border: none; }
#aboutButton { background-color: none; font: 14px; border: none; }
QProgressBar { border: none; border-radius: 4px; background: #26262f; max-height: 8px; text-align: center; color: transparent; }
QProgressBar::chunk { border-radius: 4px; background: #a69afe; }
'''

CHOOSER = '''# AxolOS · página «Escritorio» del instalador: AxolOS es KDE Plasma con su diseño
# (generado por tools/instalador_marca_axolos.py; sustituye al de CachyOS)
---
mode: required
method: netinstall-select
labels:
    step: "Desktop"
    step[es]: "Escritorio"
    step[fr]: "Bureau"
    step[ru]: "Рабочий стол"
    step[zh_CN]: "桌面"
    step[ja]: "デスクトップ"
default: KDE-Desktop
items:
    - id: KDE-Desktop
      name: "AxolOS · KDE Plasma"
      description: "AxolOS on KDE Plasma: its own theme and Bento menu, Axo (local AI) and tools for developers. This is the AxolOS desktop."
      description[es]: "AxolOS sobre KDE Plasma: tema y menú Bento propios, Axo (IA local) y herramientas para programar. Es el escritorio de AxolOS."
      description[fr]: "AxolOS sur KDE Plasma : thème et menu Bento propres, Axo (IA locale) et outils pour développer. C'est le bureau d'AxolOS."
      description[ru]: "AxolOS на KDE Plasma: собственная тема и меню Bento, Axo (локальный ИИ) и инструменты для разработки. Это рабочий стол AxolOS."
      description[zh_CN]: "基于 KDE Plasma 的 AxolOS：自有主题和 Bento 菜单、Axo（本地 AI）以及开发工具。这就是 AxolOS 桌面。"
      description[ja]: "KDE Plasma ベースの AxolOS：独自のテーマと Bento メニュー、Axo（ローカル AI）、開発ツール。これが AxolOS のデスクトップです。"
      screenshot: "/usr/share/axolos/instalador/marca/escritorio-axolos.jpg"
'''


def escritorio():
    """Vista previa del escritorio AxolOS (barra superior, dock y reloj) para la página «Escritorio»."""
    w, h = 1280, 720
    img, p = lienzo(w, h)
    fondo = QImage(str(FONDO))
    esc = max(w / fondo.width(), h / fondo.height())
    sw, sh = w / esc, h / esc
    p.drawImage(QRectF(0, 0, w, h), fondo, QRectF((fondo.width() - sw) / 2, (fondo.height() - sh) / 2, sw, sh))
    # barra superior
    p.fillRect(QRectF(0, 0, w, 30), QColor(15, 15, 19, 150))
    texto(p, QRectF(w - 150, 6, 130, 20), "12:00", fuente(SANS, 15, QFont.Weight.Medium), C["fg"], Qt.AlignmentFlag.AlignRight)
    bandeja = ["battery-full-symbolic", "audio-volume-high-symbolic", "network-wireless-symbolic",
               "bluetooth-active-symbolic", "notifications-symbolic"]
    x = w - 186
    for nombre in bandeja:
        ruta = next((f for f in (f"/usr/share/icons/breeze-dark/status/22/{nombre}.svg",
                                 f"/usr/share/icons/breeze-dark/devices/22/{nombre}.svg",
                                 f"/usr/share/icons/breeze-dark/actions/22/{nombre}.svg")
                     if Path(f).exists()), None)
        if ruta:
            svg(p, ruta, QRectF(x, 5, 20, 20))
            x -= 30
    # reloj del escritorio (como el analógico de Plasma)
    cx, cy, r = w - 101, 129, 85
    caja(p, QRectF(cx - r, cy - r, 2 * r, 2 * r), 36, "#2c2c33", "#3a3a44", 1)
    import math
    for i in range(60):
        a = math.radians(i * 6)
        largo, grosor = (13, 3) if i % 5 == 0 else (6, 1.2)
        p.setPen(QPen(QColor(C["fg"] if i % 5 == 0 else "#8a8a99"), grosor, cap=Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx + math.sin(a) * (r - 10), cy - math.cos(a) * (r - 10)),
                   QPointF(cx + math.sin(a) * (r - 10 - largo), cy - math.cos(a) * (r - 10 - largo)))
    for n, ang in (("12", 0), ("3", 90), ("6", 180), ("9", 270)):
        a = math.radians(ang)
        texto(p, QRectF(cx + math.sin(a) * (r - 40) - 20, cy - math.cos(a) * (r - 40) - 15, 40, 30), n,
              fuente(SANS, 22, QFont.Weight.DemiBold), C["fg"], Qt.AlignmentFlag.AlignCenter)
    for ang, largo, grosor in ((300, 38, 5), (60, 56, 4)):
        a = math.radians(ang)
        p.setPen(QPen(QColor(C["fg"]), grosor, cap=Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx, cy), QPointF(cx + math.sin(a) * largo, cy - math.cos(a) * largo))
    p.setBrush(QColor(C["fg"]))
    p.drawEllipse(QPointF(cx, cy), 4, 4)
    # dock
    iconos = [("ajolote", None), ("svg", ICONOS["axo"]), ("svg", ICONOS["bienvenida"])]
    extra = [Path(f) for f in ("/usr/share/icons/Yaru-purple/256x256/apps/filemanager-app.png",
                                "/usr/share/icons/hicolor/256x256/apps/firefox.png",
                                "/usr/share/icons/Yaru/256x256/apps/terminal-app.png",
                                "/usr/share/icons/Yaru/256x256/actions/configure.png") if Path(f).exists()]
    elementos = [iconos[0]] + [("png", f) for f in extra[:2]] + [iconos[1]] + [("png", f) for f in extra[2:]]
    t, pad = 58, 14
    ancho = len(elementos) * (t + pad) + pad
    x0, y0 = (w - ancho) / 2, h - t - 2 * pad - 14
    caja(p, QRectF(x0, y0, ancho, t + 2 * pad), 24, "#cc1e1e26", "#2a2a34", 1)
    x = x0 + pad
    for tipo, ruta in elementos:
        r = QRectF(x, y0 + pad, t, t)
        if tipo == "ajolote":
            ajolote(p, r.adjusted(4, 6, -4, -6))
        elif tipo == "svg":
            svg(p, ruta, r)
        else:
            p.drawImage(r, QImage(str(ruta)))
        x += t + pad
    p.end()
    return img


def traducciones_marca():
    """lang/calamares-axolos_<idioma>.qm: Calamares las carga al elegir idioma; traducen qsTr("en")."""
    lang = MARCA / "lang"
    lang.mkdir(exist_ok=True)
    lrelease = next((x for x in ("/usr/lib/qt6/bin/lrelease", "lrelease6", "lrelease") if Path(x).exists()
                     or subprocess.run(["which", x], capture_output=True).returncode == 0), None)
    for idioma in IDIOMAS:
        if idioma == "en":
            continue
        ts = lang / f"calamares-axolos_{idioma}.ts"
        ts.write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="{idioma}">
<context>
    <name>show</name>
    <message>
        <source>en</source>
        <comment>slides language code</comment>
        <translation>{idioma}</translation>
    </message>
</context>
</TS>
''', encoding="utf-8")
        if lrelease:
            subprocess.run([lrelease, "-silent", str(ts), "-qm", str(ts.with_suffix(".qm"))], check=True)
    if not lrelease:
        print("Aviso: sin lrelease (qt6-tools) no se regeneran los .qm de lang/", file=sys.stderr)


def main():
    app = QGuiApplication(sys.argv)  # noqa: F841
    MARCA.mkdir(parents=True, exist_ok=True)
    version = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else "1.0"
    (MARCA / "branding.desc").write_text(BRANDING_DESC % {"version": version}, encoding="utf-8")
    (MARCA / "calamares-sidebar.qml").write_text(SIDEBAR_QML, encoding="utf-8")
    (MARCA / "stylesheet.qss").write_text(STYLESHEET, encoding="utf-8")
    (SALIDA / "packagechooser_desktop.conf").write_text(CHOOSER, encoding="utf-8")

    # logo de la barra (ajolote blanco), icono de la ventana y portada
    img, p = lienzo(128, 128, True)
    ajolote(p, QRectF(0, 0, 128, 128))
    p.end()
    img.save(str(MARCA / "logo.png"))
    img, p = lienzo(256, 256, True)
    svg(p, ICONOS["instalar"], QRectF(0, 0, 256, 256))
    p.end()
    img.save(str(MARCA / "icon.png"))
    img, p = lienzo(900, 516, True)
    resplandor(p, QPointF(450, 258), 250, C["accent"], 70)
    ajolote(p, QRectF(450 - 240, 258 - 240, 480, 480))
    p.end()
    img.save(str(MARCA / "welcome.png"))

    for viejo in MARCA.glob("diapositiva*.jpg"):
        viejo.unlink()
    for idioma in IDIOMAS:
        CJK[:] = QM_CJK.get(idioma, [])
        for i, (t, dib) in enumerate(zip(TEXTOS[idioma], DIBUJOS), 1):
            img = diapositiva(t["etiqueta"], t["titulo"], t["cuerpo"], dib, t)
            img.convertToFormat(QImage.Format.Format_RGB32).save(str(MARCA / f"diapositiva{i}.{idioma}.jpg"), "JPG", 88)
    CJK[:] = []
    slides = [SLIDE_QML % f"diapositiva{i}" for i in range(1, len(DIBUJOS) + 1)]
    (MARCA / "show.qml").write_text(SHOW_QML % "\n".join(slides), encoding="utf-8")
    traducciones_marca()
    escritorio().convertToFormat(QImage.Format.Format_RGB32).save(str(SALIDA / "escritorio-axolos.jpg"), "JPG", 90)
    for f in sorted(SALIDA.rglob("*")):
        if f.is_file():
            print(f"{f.relative_to(ROOT)}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
