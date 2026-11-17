#!/usr/bin/env python3
"""AxolOS · comprueba que ningún programa tapa la función de traducción «_».

Si una función usa «_» como variable (for _ in…, a, _ = …, *_, lambda _=…) y además llama a _("…"),
Python la trata como variable local y la traducción falla al ejecutarse (UnboundLocalError o
«'bool' object is not callable»). Uso: tools/i18n_sombras.py ARCHIVO...  (sale con 1 si encuentra alguno)
"""
import ast
import sys


def sombras(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read(), ruta)
    malos = []

    def visitar(ambito, nombre):
        asigna, llama = [], []
        pila = list(ast.iter_child_nodes(ambito))
        while pila:
            n = pila.pop()
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,
                              ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp)):
                visitar(n, getattr(n, "name", type(n).__name__))     # ámbito propio
                continue
            if isinstance(n, ast.Name) and n.id == "_" and isinstance(n.ctx, ast.Store):
                asigna.append(n.lineno)
            elif isinstance(n, ast.arg) and n.arg == "_":
                asigna.append(n.lineno)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_":
                llama.append(n.lineno)
            pila.extend(ast.iter_child_nodes(n))
        if isinstance(ambito, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            asigna += [a.lineno for a in ast.walk(ambito.args) if isinstance(a, ast.arg) and a.arg == "_"]
        if asigna and (llama or isinstance(ambito, ast.Module)):
            malos.append(f"{ruta}:{min(asigna)}: «_» usada como variable en {nombre} "
                         f"(llamadas a _() en {sorted(set(llama))[:6]})")

    visitar(arbol, "el módulo")
    return malos


if __name__ == "__main__":
    todos = [m for r in sys.argv[1:] for m in sombras(r)]
    print("\n".join(todos) or f"Sin sombras de _() en {len(sys.argv) - 1} programas")
    sys.exit(1 if todos else 0)
