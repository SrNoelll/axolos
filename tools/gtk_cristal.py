#!/usr/bin/env python3
"""AxolOS · cristal en las apps GTK (Archivos/Nautilus y demás libadwaita, y GTK3).

Las apps GTK no siguen Kvantum: pintaban su fondo gris opaco de Adwaita y el efecto Glass de KWin
(que pone cristal detrás de todo lo que una ventana no declara opaco) no tenía dónde verse. Estas hojas
dejan su fondo translúcido con el MISMO color y la misma transparencia que las ventanas Qt
(tools/kvantum_axolos.py), así Archivos se ve como la terminal. Claro y oscuro: GTK4 con
«prefers-color-scheme» (libadwaita sigue el modo del escritorio); GTK3 con los colores que KDE escribe
en colors.css al cambiar de esquema.

Salida: packages/axolos-themes/assets/axolos/gtk/cristal-gtk4.css y cristal-gtk3.css
(/usr/share/axolos/gtk/); las importa el gtk.css de cada cuenta (skel y axolos-aspecto --migrar).

Uso: tools/gtk_cristal.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kvantum_axolos  # noqa: E402

SALIDA = Path(__file__).resolve().parent.parent / "packages/axolos-themes/assets/axolos/gtk"
RADIO = 14   # = esquinas del efecto Glass y de las barras de título


def rgba(hexa, alfa):
    h = hexa.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgb({r} {g} {b} / {round(alfa * 100)}%)"


def modo(variante, oscuro):
    _, acento, _, transparencia, c = kvantum_axolos.VARIANTES[variante]
    a = 1 - transparencia / 100
    ventana, texto = c["window.color"], c["text.color"]
    claro_o_blanco = "255 255 255"
    capa = (lambda x: f"rgb({claro_o_blanco} / {x}%)")
    return f"""  :root {{
    /* el cristal: fondo de ventana translúcido; cabecera, vista y barra lateral sobre él */
    --window-bg-color: {rgba(ventana, a)};
    --window-fg-color: {texto};
    /* la vista (lista o cuadrícula) lleva otra capa, como el texto de la terminal sobre su ventana */
    --view-bg-color: {rgba(c["base.color"], 0.62 if oscuro else 0.55)};
    --view-fg-color: {texto};
    --headerbar-bg-color: transparent;
    --headerbar-backdrop-color: transparent;
    --headerbar-fg-color: {texto};
    --headerbar-border-color: transparent;
    --headerbar-shade-color: transparent;
    --headerbar-darker-shade-color: transparent;
    --sidebar-bg-color: {capa(4 if oscuro else 28)};
    --sidebar-backdrop-color: {capa(3 if oscuro else 22)};
    --sidebar-fg-color: {texto};
    --sidebar-border-color: transparent;
    --sidebar-shade-color: transparent;
    --secondary-sidebar-bg-color: {capa(3 if oscuro else 20)};
    --secondary-sidebar-backdrop-color: {capa(2 if oscuro else 16)};
    --secondary-sidebar-border-color: transparent;
    --secondary-sidebar-shade-color: transparent;
    --card-bg-color: {capa(6 if oscuro else 45)};
    --card-shade-color: transparent;
    --overview-bg-color: {rgba(ventana, a)};
    --thumbnail-bg-color: {capa(8 if oscuro else 55)};
    --dialog-bg-color: {rgba(ventana, min(1, a + 0.22))};
    --popover-bg-color: {rgba(ventana, min(1, a + 0.24))};
    --popover-shade-color: transparent;
    --accent-bg-color: #7662ce;
    --accent-fg-color: #ffffff;
    --accent-color: {acento if oscuro else "#6a55d8"};
    --window-radius: {RADIO}px;
  }}"""


def gtk4():
    return f"""/* AxolOS · cristal en GTK4/libadwaita (generado por tools/gtk_cristal.py; no editar a mano) */
@media (prefers-color-scheme: dark) {{
{modo("AxolOSDark", True)}
}}
@media (prefers-color-scheme: light) {{
{modo("AxolOS", False)}
}}
/* esquinas iguales a las del resto de ventanas (y a las del cristal de KWin) */
window.csd, window.csd > .titlebar:not(headerbar) {{ border-radius: {RADIO}px; }}
window.csd.maximized, window.csd.fullscreen, window.csd.tiled {{ border-radius: 0; }}
"""


def gtk3():
    _, _, _, t_osc, _ = kvantum_axolos.VARIANTES["AxolOSDark"]
    a = round(1 - t_osc / 100, 2)
    return f"""/* AxolOS · cristal en GTK3 (generado por tools/gtk_cristal.py; no editar a mano)
   Los colores salen de colors.css (los escribe KDE al cambiar de esquema, claro u oscuro). */
window.background:not(.popup):not(.tooltip) {{ background-color: alpha(@theme_bg_color, {a}); }}
window.csd headerbar, window.csd .titlebar, headerbar {{ background-color: transparent; background-image: none;
  box-shadow: none; border-color: transparent; }}
.sidebar, placessidebar, placessidebar list {{ background-color: transparent; }}
"""


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "cristal-gtk4.css").write_text(gtk4(), encoding="utf-8")
    (SALIDA / "cristal-gtk3.css").write_text(gtk3(), encoding="utf-8")
    print(SALIDA / "cristal-gtk4.css")
    print(SALIDA / "cristal-gtk3.css")


if __name__ == "__main__":
    main()
