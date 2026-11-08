#!/usr/bin/env python3
"""Pequeño editor de ficheros de configuración KDE (formato INI con grupos [A][B]).

Uso:
  kini.py FICHERO [--drop-section REGEX]... [--drop-key 'GRUPO|CLAVE']...
                  [--set 'GRUPO|CLAVE=VALOR']... [--sub VIEJO NUEVO]...
                  [--drop-value-regex REGEX]...

GRUPO se escribe sin el corchete exterior: p.ej. 'Containments][236][General'.
Edita el fichero en sitio y conserva el orden original.
"""
import argparse
import re
import sys


def parse(text):
    sections = []  # [(name|None, [lines])]
    cur = [None, []]
    sections.append(cur)
    for line in text.splitlines():
        m = re.match(r"^\[(.*)\]\s*$", line)
        if m:
            cur = [m.group(1), []]
            sections.append(cur)
        else:
            cur[1].append(line)
    return sections


def dump(sections):
    out = []
    for name, lines in sections:
        if name is None and not any(l.strip() for l in lines):
            continue
        if name is not None:
            out.append(f"[{name}]")
        # quita líneas vacías finales y deja una sola de separación
        while lines and not lines[-1].strip():
            lines.pop()
        out.extend(lines)
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--drop-section", action="append", default=[])
    ap.add_argument("--drop-key", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--sub", nargs=2, action="append", default=[])
    ap.add_argument("--drop-value-regex", action="append", default=[],
                    help="borra cualquier línea clave=valor cuyo valor case con REGEX")
    a = ap.parse_args()

    with open(a.file, encoding="utf-8") as f:
        text = f.read()
    for old, new in a.sub:
        text = text.replace(old, new)
    secs = parse(text)

    for rx in a.drop_section:
        r = re.compile(rx)
        secs = [s for s in secs if s[0] is None or not r.search(s[0])]

    for spec in a.drop_key:
        grp, key = spec.split("|", 1)
        for s in secs:
            if s[0] == grp:
                s[1] = [l for l in s[1] if l.split("=", 1)[0] != key]

    for rx in a.drop_value_regex:
        r = re.compile(rx)
        for s in secs:
            s[1] = [l for l in s[1] if "=" not in l or not r.search(l.split("=", 1)[1])]

    for spec in a.set:
        grp, kv = spec.split("|", 1)
        key, val = kv.split("=", 1)
        target = next((s for s in secs if s[0] == grp), None)
        if target is None:
            target = [grp, []]
            secs.append(target)
        for i, l in enumerate(target[1]):
            if l.split("=", 1)[0] == key:
                target[1][i] = f"{key}={val}"
                break
        else:
            # inserta antes de las líneas vacías finales
            target[1].append(f"{key}={val}")

    # quita grupos que se hayan quedado vacíos
    secs = [s for s in secs if s[0] is None or any(l.strip() for l in s[1])]

    with open(a.file, "w", encoding="utf-8") as f:
        f.write(dump(secs))


if __name__ == "__main__":
    sys.exit(main())
