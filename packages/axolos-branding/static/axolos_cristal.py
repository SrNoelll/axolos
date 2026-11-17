"""AxolOS · colores y cristal líquido para las apps PyQt de AxolOS (Bienvenida, Centro, Axo, instalador).

  colores()            paleta del modo activo (AxolOS Cristal oscuro o claro), con las mismas claves
                       que usan las apps («bg», «surface», «accent»…)
  translucido(qss, C)  con el cristal de KWin activo, los fondos de ventana pasan a ser translúcidos
  preparar(ventana)    ventana con fondo translúcido (KWin pone detrás desenfoque y refracción)

El modo sale del esquema de color de KDE (kdeglobals), sin Qt: las apps montan su estilo antes de
crear la aplicación. Si el efecto Glass no está cargado, todo queda opaco: nunca una ventana
transparente sin desenfoque detrás. AXOLOS_MODO=claro|oscuro lo fuerza (pruebas).
"""
import configparser
import os
import subprocess
from pathlib import Path

OSCURO = dict(bg="#121218", bg_dark="#0e0e13", side="#0f0f14", surface="#1b1b24", border="#2a2a36",
              fg="#ececf3", muted="#8a8a99", faint="#4b4b57", accent="#a69afe", accent_hi="#cdc6ff",
              accent_lo="#7662ce", pink="#ff7a93", green="#7ddfb4", yellow="#f3cf7a", cyan="#7fd4e4",
              lilac="#b4acff", indigo="#8f85f2", user="#2a2540", code_head="#18181f",
              decorador="#fbe2a6", numero="#ff9fb0", comentario="#6e6c80", sobre_acento="#1f1a3d")
CLARO = dict(bg="#eef2f7", bg_dark="#e3e9f1", side="#e7ecf3", surface="#f8fafc", border="#d3dbe6",
             fg="#1c2230", muted="#5b6478", faint="#9aa3b5", accent="#7662ce", accent_hi="#5a46c4",
             accent_lo="#a69afe", pink="#d6365a", green="#1e9e6a", yellow="#9a6c00", cyan="#1f7f94",
             lilac="#6a5fd6", indigo="#5f55d0", user="#e6e1ff", code_head="#e3e9f1",
             decorador="#9a6c00", numero="#d6365a", comentario="#7a8295", sobre_acento="#ffffff")
# opacidad de los fondos de ventana con el cristal activo (el resto del contenido es opaco)
ALFA = {"bg": 0.80, "side": 0.70, "bg_dark": 0.84}


def modo():
    forzado = os.environ.get("AXOLOS_MODO")
    if forzado in ("claro", "oscuro"):
        return forzado
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    try:
        cfg.read(base / "kdeglobals", encoding="utf-8")
        r, g, b = (int(x) for x in cfg["Colors:Window"]["BackgroundNormal"].split(",")[:3])
    except (KeyError, ValueError, OSError, configparser.Error):
        return "oscuro"
    return "claro" if (0.299 * r + 0.587 * g + 0.114 * b) > 140 else "oscuro"


def colores():
    return dict(CLARO if modo() == "claro" else OSCURO)


_activo = None


def cristal_activo():
    """¿KWin tiene cargado el efecto Glass? (sin él, fondos opacos)."""
    global _activo
    if _activo is None:
        try:
            r = subprocess.run(["qdbus6", "org.kde.KWin", "/Effects", "org.kde.kwin.Effects.isEffectLoaded", "glass"],
                               capture_output=True, text=True, timeout=2)
            _activo = r.stdout.strip() == "true"
        except (OSError, subprocess.TimeoutExpired):
            _activo = False
    return _activo


def translucido(qss, C):
    if not cristal_activo():
        return qss
    for clave, alfa in ALFA.items():
        h = C[clave].lstrip("#")
        rgba = "rgba({},{},{},{})".format(*(int(h[i:i + 2], 16) for i in (0, 2, 4)), round(alfa * 255))
        for prop in ("background", "background-color"):
            qss = qss.replace(f"{prop}: {C[clave]};", f"{prop}: {rgba};")
    return qss


def preparar(ventana):
    if cristal_activo():
        from PyQt6.QtCore import Qt
        ventana.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
