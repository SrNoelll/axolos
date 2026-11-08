#!/usr/bin/env bash
# =============================================================================
#  AxolOS · publicar-repo.sh
#  Compila los paquetes AxolOS firmados (desde una carpeta neutra, para que no
#  queden rutas de tu disco dentro) y publica el repositorio de pacman en GitHub:
#      https://github.com/SrNoelll/axolos/releases/tag/x86_64
#  Los equipos con AxolOS lo usan con:
#      [axolos]
#      Server = https://github.com/SrNoelll/axolos/releases/download/x86_64
#
#  Necesita: la clave de firma de AxolOS en tu gpg y `gh` con sesión iniciada.
#  No hace falta subir pkgrel a mano: compara cada paquete con el publicado y lo sube si cambió.
#
#  Lo ejecuta también GitHub Actions (.github/workflows/publicar.yml) al subir cambios:
#    AXOLOS_CI=1          guarda en git (y sube) los pkgrel que haya subido, antes de publicar
#    AXOLOS_SIN_SUBIR=1   compila, firma y comprueba, pero no publica nada (pruebas)
#    AXOLOS_FPR=…         otra clave de firma (pruebas)
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GH_REPO="${AXOLOS_GH_REPO:-SrNoelll/axolos}"
TAG=x86_64
STAGE="${TMPDIR:-/tmp}/axolos-publicar"
FPR=${AXOLOS_FPR:-$(<"$ROOT/iso/instalador/axolos.fpr")}
say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
die() { printf '\e[1;31m!!\e[0m %s\n' "$*"; exit 1; }

gpg --list-secret-keys "$FPR" >/dev/null 2>&1 || die "Falta la clave de firma de AxolOS ($FPR) en este equipo."
[[ ${AXOLOS_SIN_SUBIR:-} == 1 ]] || gh auth status >/dev/null 2>&1 || die "Inicia sesión en GitHub:  gh auth login"

say "1/4 Copiando el proyecto a una carpeta neutra"
rm -rf "$STAGE"; mkdir -p "$STAGE/AxolOS/repo"
tar -C "$ROOT" --exclude=./build --exclude=./repo --exclude=./out --exclude=./.git -cf - . | tar -C "$STAGE/AxolOS" -xf -
# Paquetes del AUR ya compilados (con su firma): se reutilizan
for p in yaru-icon-theme whitesur-cursor-theme-git ttf-ia-writer; do
  f=$(ls -1 "$ROOT"/repo/"$p"-[0-9r]*.pkg.tar.zst 2>/dev/null | sort -V | tail -1) || true
  [[ -n $f ]] || die "Falta $p en repo/ (compílalo con ./build-packages.sh)"
  cp "$f" "$STAGE/AxolOS/repo/"
  [[ -f $f.sig ]] && cp "$f.sig" "$STAGE/AxolOS/repo/"
done

# Una versión publicada no cambia nunca: si cambiara con el mismo nombre, pacman la daría por
# corrupta en cualquier equipo que ya la tenga en caché. Así que cada paquete se compila de prueba y
# se compara por contenido con el publicado (tools/comparar_paquetes.py):
#   igual           → se reutiliza el publicado tal cual
#   distinto        → se sube pkgrel en su PKGBUILD (aquí y en tu carpeta) y se publica la nueva
#   versión nueva   → se publica
version_de() { (cd "$1" && startdir=$PWD bash -c 'source PKGBUILD; echo "$pkgname-$pkgver-$pkgrel-${arch[0]}.pkg.tar.zst"'); }
compilar=(); subidos=()
PRUEBA="$STAGE/prueba"; mkdir -p "$PRUEBA"
for d in "$STAGE"/AxolOS/packages/axolos-*/; do
  p=$(basename "$d"); f=$(version_de "$d")
  if [[ ! -f $ROOT/repo/$f || ! -f $ROOT/repo/$f.sig ]]; then
    compilar+=("$p"); continue
  fi
  (cd "$d" && PKGDEST="$PRUEBA" BUILDDIR="$STAGE/b" makepkg -f -d --noconfirm >"$STAGE/prueba-$p.log" 2>&1) \
    || { tail -15 "$STAGE/prueba-$p.log"; die "No compila $p (log: $STAGE/prueba-$p.log)"; }
  if python3 -I "$ROOT/tools/comparar_paquetes.py" "$ROOT/repo/$f" "$PRUEBA/$f" > "$STAGE/cambios-$p.txt"; then
    cp "$ROOT/repo/$f" "$ROOT/repo/$f.sig" "$STAGE/AxolOS/repo/"
  else
    rel=$(sed -n 's/^pkgrel=\([0-9]\+\)$/\1/p' "$d/PKGBUILD")
    [[ -n $rel ]] || die "$p: no entiendo su pkgrel"
    sed -i "s/^pkgrel=$rel\$/pkgrel=$((rel + 1))/" "$d/PKGBUILD"
    # en la prueba solo cambia la copia; de verdad, también tu carpeta
    [[ ${AXOLOS_SIN_SUBIR:-} == 1 ]] || sed -i "s/^pkgrel=$rel\$/pkgrel=$((rel + 1))/" "$ROOT/packages/$p/PKGBUILD"
    say "$p cambió desde la $rel publicada: pasa a pkgrel $((rel + 1))"
    sed 's/^/     /' "$STAGE/cambios-$p.txt"
    compilar+=("$p"); subidos+=("$p")
  fi
done
echo "   versiones nuevas: ${compilar[*]:-ninguna}"

say "2/4 Compilando y firmando"
(cd "$STAGE/AxolOS" && AXOLOS_SOLO="${compilar[*]}" ./build-packages.sh --no-aur) >"$STAGE/compilacion.log" 2>&1 \
  || { tail -20 "$STAGE/compilacion.log"; die "Falló la compilación (log: $STAGE/compilacion.log)"; }
for f in "$STAGE"/AxolOS/repo/*.pkg.tar.zst "$STAGE"/AxolOS/repo/axolos.db; do
  gpg --verify "$f.sig" "$f" >/dev/null 2>&1 || die "Firma incorrecta: $(basename "$f")"
done
say "3/4 Preparando la publicación"
NUEVO="$STAGE/AxolOS/repo"
SUBIR="$STAGE/subir"; mkdir -p "$SUBIR"
for f in "$NUEVO"/*.pkg.tar.zst "$NUEVO"/*.pkg.tar.zst.sig; do cp "$f" "$SUBIR/"; done
cp -L "$NUEVO/axolos.db" "$SUBIR/axolos.db";       cp -L "$NUEVO/axolos.db.sig" "$SUBIR/axolos.db.sig"
cp -L "$NUEVO/axolos.files" "$SUBIR/axolos.files"; cp -L "$NUEVO/axolos.files.sig" "$SUBIR/axolos.files.sig"

if [[ ${AXOLOS_SIN_SUBIR:-} == 1 ]]; then
  say "Prueba terminada (AXOLOS_SIN_SUBIR=1): $(ls -1 "$SUBIR"/*.pkg.tar.zst | wc -l) paquetes firmados en $SUBIR"
  exit 0
fi

# Los pkgrel subidos se guardan en git ANTES de publicar: si no, la siguiente vez no encontraría
# publicada la versión que dice su PKGBUILD y volvería a publicar la anterior
if ((${#subidos[@]})); then
  if [[ ${AXOLOS_CI:-} == 1 ]]; then
    git -C "$ROOT" add packages/*/PKGBUILD
    git -C "$ROOT" commit -q -m "AxolOS: pkgrel automático (${subidos[*]}) [skip ci]" \
      -m "Su contenido cambió desde la versión publicada (tools/comparar_paquetes.py)."
    git -C "$ROOT" push -q || die "No pude guardar en git los pkgrel nuevos: no publico nada"
  else
    say "Recuerda guardar en git los PKGBUILD con pkgrel nuevo: ${subidos[*]}"
  fi
fi

say "4/4 Subiendo a https://github.com/$GH_REPO/releases/tag/$TAG"
gh repo view "$GH_REPO" >/dev/null 2>&1 || die "No existe el repositorio $GH_REPO"
if ! gh release view "$TAG" -R "$GH_REPO" >/dev/null 2>&1; then
  gh release create "$TAG" -R "$GH_REPO" --latest=false \
    --title "Repositorio de paquetes AxolOS (x86_64)" \
    --notes "Repositorio de pacman de AxolOS. No descargues nada a mano: añade el repositorio a pacman (ver el README)."
fi
gh release upload "$TAG" -R "$GH_REPO" --clobber "$SUBIR"/*
# Quitar de la release lo que ya no está en el repositorio (versiones viejas)
mapfile -t locales < <(cd "$SUBIR" && ls -1)
gh release view "$TAG" -R "$GH_REPO" --json assets --jq '.assets[].name' | while read -r a; do
  printf '%s\n' "${locales[@]}" | grep -qxF "$a" || { gh release delete-asset "$TAG" "$a" -R "$GH_REPO" -y >/dev/null; echo "   quitado: $a"; }
done
# El repo local queda igual que el publicado
rm -f "$ROOT"/repo/*
cp -a "$NUEVO/." "$ROOT/repo/"
say "Publicado: $(ls -1 "$SUBIR"/*.pkg.tar.zst | wc -l) paquetes firmados"
