#!/usr/bin/env python3
"""Quita del layout de /etc/skel los relojes analógicos del escritorio y sus posiciones.

El reloj lo crea axolos-reloj-escritorio.js al primer inicio, medido sobre la pantalla de cada
usuario (las posiciones copiadas son píxeles de la pantalla de quien lo empaqueta).
uso: quitar_reloj_skel.py plasma-org.kde.plasma.desktop-appletsrc
"""
import re
import sys

ruta = sys.argv[1]
texto = open(ruta, encoding="utf-8").read()
bloques = re.split(r"(?m)^(?=\[)", texto)
# applets de reloj: [Containments][C][Applets][A] con plugin=org.kde.plasma.analogclock
relojes = set()
for b in bloques:
    m = re.match(r"\[Containments\]\[(\d+)\]\[Applets\]\[(\d+)\]\n", b)
    if m and re.search(r"(?m)^plugin=org\.kde\.plasma\.analogclock$", b):
        relojes.add(m.groups())
salida = []
for b in bloques:
    m = re.match(r"\[Containments\]\[(\d+)\]\[Applets\]\[(\d+)\]", b)
    if m and m.groups() in relojes:
        continue                                    # el applet y todas sus subsecciones
    for c, a in relojes:                            # su posición en el contenedor del escritorio
        if b.startswith(f"[Containments][{c}]\n"):
            b = re.sub(rf"Applet-{a}:[^;\n]*;", "", b)
            b = re.sub(r"(?m)^ItemGeometries[^=\n]*=\n", "", b)
    salida.append(b)
open(ruta, "w", encoding="utf-8").write("".join(salida))
print(f"relojes quitados: {len(relojes)}")
