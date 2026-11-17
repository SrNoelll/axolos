"""AxolOS · leer y escribir catálogos .po sencillos (sin dependencias)."""
import ast
import re


def leer(ruta):
    """[(msgid, msgstr, comentarios)] en orden, sin la cabecera."""
    entradas, actual, campo, coment = [], {}, None, []
    for ln in open(ruta, encoding="utf-8").read().split("\n") + [""]:
        if not ln.strip():
            if "msgid" in actual:
                entradas.append((actual["msgid"], actual.get("msgstr", ""), coment))
            actual, campo, coment = {}, None, []
        elif ln.startswith("#"):
            coment.append(ln)
        elif m := re.match(r"^(msgid|msgstr) (\".*\")$", ln):
            campo = m.group(1)
            actual[campo] = ast.literal_eval(m.group(2))
        elif ln.startswith('"') and campo:
            actual[campo] += ast.literal_eval(ln)
    return [e for e in entradas if e[0] != ""]


def cadena(s):
    """Texto en formato .po (una línea por cada \\n, como hace gettext)."""
    esc = s.replace("\\", "\\\\").replace('"', '\\"').replace("\t", "\\t").replace("\r", "\\r")
    partes = esc.split("\n")
    if len(partes) == 1:
        return f'"{esc}"'
    trozos = [p + "\\n" for p in partes[:-1]] + ([partes[-1]] if partes[-1] else [])
    return '""\n' + "\n".join(f'"{t}"' for t in trozos)
