#!/usr/bin/env python3
"""AxolOS · ¿dos paquetes de pacman tienen el mismo contenido?

  comparar_paquetes.py PUBLICADO NUEVO     sale con 0 si son iguales y con 1 (y qué cambia) si no

Compara lo que el paquete instala (cada archivo con su suma, permisos y destino de los enlaces), su
script de instalación y sus metadatos (.PKGINFO: dependencias, descripción…), sin contar lo que
cambia en cada compilación (fecha, tamaño, quién lo empaqueta, .BUILDINFO y .MTREE).
Lo usa publicar-repo.sh para subir pkgrel solo cuando algo cambió de verdad.
"""
import hashlib
import sys
import tarfile

IGNORAR = {".BUILDINFO", ".MTREE"}
PKGINFO_VARIABLE = ("builddate", "size", "packager", "pkgbuild_sha256sum")


def huella(ruta):
    datos = {}
    with tarfile.open(ruta, "r:*") as tar:
        for m in tar.getmembers():
            if m.name in IGNORAR:
                continue
            if m.name == ".PKGINFO":
                texto = tar.extractfile(m).read().decode("utf-8", "replace")
                lineas = [ln for ln in texto.splitlines()
                          if ln and not ln.startswith("#") and ln.split(" = ")[0] not in PKGINFO_VARIABLE]
                datos[m.name] = ("pkginfo", tuple(sorted(lineas)))
            elif m.isfile():
                datos[m.name] = ("archivo", m.mode & 0o7777, hashlib.sha256(tar.extractfile(m).read()).hexdigest())
            elif m.issym() or m.islnk():
                datos[m.name] = ("enlace", m.linkname)
            elif m.isdir():
                datos[m.name] = ("carpeta", m.mode & 0o7777)
    return datos


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a, b = huella(sys.argv[1]), huella(sys.argv[2])
    if a == b:
        return 0
    cambios = sorted(set(a) ^ set(b)) + sorted(k for k in set(a) & set(b) if a[k] != b[k])
    for k in cambios[:12]:
        estado = "nuevo" if k not in a else "quitado" if k not in b else "cambia"
        print(f"   {estado}: {k}")
    if len(cambios) > 12:
        print(f"   … y {len(cambios) - 12} más")
    return 1


if __name__ == "__main__":
    sys.exit(main())
