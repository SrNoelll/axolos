#!/usr/bin/env python3
"""AxolOS · añade traducciones nuevas a los catálogos de los programas (dominio «axolos»).

  tools/i18n_rellenar.py LOTE.py

LOTE.py define  N = [(texto original en español, en, fr, ru, zh_CN, ja), ...]. Comprueba que cada
texto esté en la plantilla y que las traducciones conserven los marcadores {…}; después las mezcla
en po/{en,fr,ru,zh_CN,ja}.po con msgmerge (como compendio). Ejecuta antes tools/i18n.sh.
"""
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))
import po  # noqa: E402

D = RAIZ / "packages/axolos-branding/po"
IDIOMAS = ("en", "fr", "ru", "zh_CN", "ja")
LLAVES = re.compile(r"\{[^{}]*\}")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = importlib.util.spec_from_file_location("lote", sys.argv[1])
    lote = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lote)
    plantilla = {e[0] for e in po.leer(D / "axolos.pot")}
    errores = []
    for n in lote.N:
        if len(n) != 1 + len(IDIOMAS):
            errores.append(f"faltan idiomas: {n[0]!r}")
        if n[0] not in plantilla:
            errores.append(f"no está en la plantilla: {n[0]!r}")
        for s in n[1:]:
            if sorted(LLAVES.findall(s)) != sorted(LLAVES.findall(n[0])):
                errores.append(f"marcadores distintos: {s!r}")
    if errores:
        sys.exit("\n".join(errores))
    for i, l in enumerate(IDIOMAS, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".po", delete=False, encoding="utf-8") as c:
            c.write('msgid ""\nmsgstr "Content-Type: text/plain; charset=UTF-8\\n"\n\n')
            for n in lote.N:
                c.write(f"msgid {po.cadena(n[0])}\nmsgstr {po.cadena(n[i])}\n\n")
        subprocess.run(["msgmerge", "--quiet", "--update", "--backup=none", "--no-wrap", "--no-fuzzy-matching",
                        f"--compendium={c.name}", str(D / f"{l}.po"), str(D / "axolos.pot")], check=True)
        Path(c.name).unlink()
    print(f"{len(lote.N)} textos añadidos en {len(IDIOMAS)} idiomas")


if __name__ == "__main__":
    main()
