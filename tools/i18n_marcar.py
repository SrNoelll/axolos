#!/usr/bin/env python3
"""AxolOS · marca para traducir los textos de un programa en Python (gettext).

  i18n_marcar.py [--prueba] ARCHIVO...

Recorre el árbol sintáctico (no el texto) y envuelve en _() los textos de la interfaz:
  - los que se pasan a widgets y funciones de mensajes (QLabel, setText, say, print…)
  - cualquier frase en español de varias palabras
Las f-strings pasan a  _("Hay {n} archivos").format(n=n)  para que el traductor vea la frase entera.
No toca docstrings, comparaciones, claves de diccionario, expresiones regulares, órdenes de
subprocess ni lo que ya esté marcado. Con --prueba solo lista lo que haría.
Después hay que revisar el resultado: lo que no deba traducirse se desmarca a mano.
"""
import ast
import re
import sys

UI = {  # funciones y métodos cuyos argumentos de texto se ven en pantalla
    "QLabel", "QPushButton", "QCheckBox", "QRadioButton", "QToolButton", "QAction", "QGroupBox",
    "setText", "setToolTip", "setWindowTitle", "setPlaceholderText", "setStatusTip", "addItem",
    "addTab", "setTitle", "information", "question", "warning", "critical", "about",
    "say", "die", "print", "exit", "aviso", "registro", "poner_estado", "fila", "boton", "etiqueta",
    "titulo", "tarea", "terminal", "Tarjeta", "showMessage", "appendPlainText", "log", "error", "nota",
}
NO = {  # funciones cuyos argumentos son código o datos, nunca texto para traducir
    "compile", "search", "match", "fullmatch", "sub", "split", "findall", "finditer",
    "run", "Popen", "check_output", "check_call", "call", "sh", "start", "startDetached", "get",
    "getenv", "setdefault", "fromTheme", "setObjectName", "setProperty", "property", "startswith",
    "endswith", "replace", "strip", "join", "format", "_", "ngettext", "Path", "open", "which",
    "setStyleSheet", "execute", "setApplicationName", "setDesktopFileName", "QIcon", "QFont",
    "QColor", "connect", "loads", "dumps", "encode", "decode", "lower", "upper",
}
ES = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]{2,}[ ,.:;!?][ ¿¡A-Za-zÁÉÍÓÚáéíóúÑñ]{2,}|[áéíóúñÁÉÍÓÚÑ¿¡]")
PALABRA = re.compile(r"^[A-ZÁÉÍÓÚÑ¿¡][a-záéíóúñ]+(?:\s\S+)*[.…!?]*$")
CSS = re.compile(r"[{}]|:\s*[^;\n]+;")                    # hojas de estilo (QSS)
CODIGO = re.compile(r"^\s*(SELECT|INSERT|DELETE|UPDATE|CREATE|DROP|PRAGMA)\b"   # SQL
                    r"|\\[bdswBDSW]|\(\?[:=!<]|^(task|title): ")             # regex y prefijos de modelos


def es_nombre(s):
    """«New York Medium», «Qwen 3.5 · 9B»: nombres propios (todas las palabras con mayúscula)."""
    palabras = [w for w in re.findall(r"[^\W\d_]+", s)]
    return bool(palabras) and all(w[0].isupper() for w in palabras) and not re.search("[áéíóúñ]", s)


def nombre_llamada(n):
    f = n.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def literal(s):
    """Cadena de Python entre comillas dobles, con los caracteres de control escapados."""
    out = []
    for c in s:
        if c == "\\":
            out.append("\\\\")
        elif c == '"':
            out.append('\\"')
        elif c == "\n":
            out.append("\\n")
        elif c == "\t":
            out.append("\\t")
        elif ord(c) < 32 or ord(c) == 127:
            out.append(f"\\x{ord(c):02x}")
        else:
            out.append(c)
    return '"' + "".join(out) + '"'


class Marcador:
    def __init__(self, fuente):
        self.fuente = fuente
        self.b = fuente.encode("utf-8")
        self.lineas = [0]
        for ln in self.b.splitlines(keepends=True):
            self.lineas.append(self.lineas[-1] + len(ln))
        self.arbol = ast.parse(fuente)
        for padre in ast.walk(self.arbol):
            for hijo in ast.iter_child_nodes(padre):
                hijo.padre = padre
        self.cambios, self.lista = [], []

    def pos(self, n):
        return self.lineas[n.lineno - 1] + n.col_offset, self.lineas[n.end_lineno - 1] + n.end_col_offset

    def segmento(self, n):
        a, z = self.pos(n)
        return self.b[a:z].decode("utf-8")

    def contexto(self, n):
        """('ui'|'no'|'docstring'|None) según dónde está el texto."""
        p = getattr(n, "padre", None)
        while isinstance(p, (ast.BinOp, ast.IfExp, ast.Tuple, ast.List, ast.BoolOp, ast.keyword)):
            if isinstance(p, ast.keyword) and p.arg in ("objectName", "fallback"):
                return "no"
            n, p = p, getattr(p, "padre", None)
        if isinstance(p, ast.Expr) and isinstance(getattr(p, "padre", None), (ast.Module, ast.FunctionDef, ast.ClassDef)):
            if p.padre.body and p.padre.body[0] is p:
                return "docstring"
        if isinstance(p, (ast.Compare, ast.Subscript, ast.JoinedStr, ast.FormattedValue)):
            return "no"
        if isinstance(p, ast.Dict) and any(k is n for k in p.keys):
            return "no"
        if isinstance(p, ast.Call):
            nombre = nombre_llamada(p)
            if nombre in NO:
                return "no"
            if nombre in UI:
                return "ui"
        return None

    def marcar_constante(self, n):
        ctx = self.contexto(n)
        s = n.value
        if ctx in ("no", "docstring") or not s.strip() or CSS.search(s) or CODIGO.search(s):
            return
        if ctx is None and es_nombre(s):
            return
        if ctx == "ui" and (ES.search(s) or PALABRA.match(s.strip())):
            pass
        elif ctx is None and ES.search(s) and " " in s.strip():
            pass
        else:
            return
        a, z = self.pos(n)
        self.cambios.append((a, z, f"_({self.segmento(n)})"))
        self.lista.append((n.lineno, s))

    def marcar_fstring(self, n):
        texto = "".join(v.value for v in n.values if isinstance(v, ast.Constant))
        if not (ES.search(texto) and len(texto.strip()) > 1) or self.contexto(n) in ("no", "docstring"):
            return
        if CSS.search(texto) or CODIGO.search(texto):
            return
        plantilla, posic, nombres, num = "", [], {}, 0
        for v in n.values:
            if isinstance(v, ast.Constant):
                plantilla += v.value.replace("{", "{{").replace("}", "}}")
                continue
            if v.format_spec is not None and any(not isinstance(x, ast.Constant) for x in v.format_spec.values):
                return                                          # formato dinámico: a mano
            expr = self.segmento(v.value)
            if isinstance(v.value, ast.Name):
                clave = v.value.id
                nombres[clave] = expr
            else:
                clave = str(num)
                posic.append(expr)
                num += 1
            conv = {-1: "", 115: "!s", 114: "!r", 97: "!a"}[v.conversion]
            spec = (":" + "".join(x.value for x in v.format_spec.values)) if v.format_spec else ""
            plantilla += "{" + clave + conv + spec + "}"
        args = posic + [f"{k}={e}" for k, e in nombres.items()]
        a, z = self.pos(n)
        self.cambios.append((a, z, f"_({literal(plantilla)}).format({', '.join(args)})"))
        self.lista.append((n.lineno, plantilla))

    def ejecutar(self):
        dentro = set()
        for n in ast.walk(self.arbol):
            if isinstance(n, ast.JoinedStr):
                for x in ast.walk(n):
                    if x is not n:
                        dentro.add(id(x))
        for n in ast.walk(self.arbol):
            if id(n) in dentro:
                continue
            if isinstance(n, ast.Call) and nombre_llamada(n) in ("_", "ngettext"):
                for x in ast.walk(n):
                    dentro.add(id(x))
                continue
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                self.marcar_constante(n)
            elif isinstance(n, ast.JoinedStr):
                self.marcar_fstring(n)
        b = self.b
        for a, z, nuevo in sorted(self.cambios, reverse=True):
            b = b[:a] + nuevo.encode("utf-8") + b[z:]
        resultado = b.decode("utf-8")
        ast.parse(resultado)                                   # sigue siendo Python válido
        return resultado


def main():
    prueba = "--prueba" in sys.argv
    for ruta in [a for a in sys.argv[1:] if not a.startswith("--")]:
        m = Marcador(open(ruta, encoding="utf-8").read())
        nuevo = m.ejecutar()
        print(f"== {ruta}: {len(m.lista)} textos")
        for ln, s in sorted(m.lista):
            print(f"   {ln:5d}  {s[:110]!r}")
        if not prueba:
            open(ruta, "w", encoding="utf-8").write(nuevo)


if __name__ == "__main__":
    main()
