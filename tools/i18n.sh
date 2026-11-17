#!/usr/bin/env bash
# AxolOS · traducciones (gettext). Dos catálogos:
#   axolos                          programas de AxolOS (Python y shell). Originales en español,
#                                   marcados con _() / t; idiomas: en fr ru zh_CN ja (resto → inglés)
#   plasma_applet_org.axolos.bento  menú Bento (QML). Originales en inglés, como en KDE;
#                                   idiomas: es fr ru zh_CN ja
#
#   tools/i18n.sh               regenera las plantillas (.pot) y actualiza cada idioma con msgmerge
#   tools/i18n.sh --comprobar   falla si una plantilla no está al día o falta alguna traducción
#
# Para añadir un programa en Python: márcalo con tools/i18n_marcar.py y añádelo a PY.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=(
    iso/airootfs/usr/local/bin/axolos-instalar
    packages/axolos-bienvenida/bin/axolos-bienvenida
    packages/axolos-bienvenida/bin/axolos-centro
    packages/axolos-branding/static/axolos-root
    packages/axolos-dev/static/axolos-dev
    packages/axolos-ia/bin/axolos-ia
    packages/axolos-ia/bin/axolos-ia-chat
    packages/axolos-ia/lib/axolos-ia-krunner
    packages/axolos-ia/lib/axolos-indice-vigia
    packages/axolos-ia/lib/axolos_buscar.py
    packages/axolos-ia/lib/axolos_ia.py
    packages/axolos-kde-settings/axolos-navegadores
)
# Scripts de shell: textos con la función «t» (usa /usr/lib/axolos/axolos-texto)
SH=(
    packages/axolos-branding/static/axolos-apps
    packages/axolos-dev/axolos-dev.install
    packages/axolos-ia/axolos-ia.install
    packages/axolos-glass/axolos-glass-comprobar
)
QML=(
    packages/axolos-menu/org.axolos.bento/contents/ui/BentoView.qml
    packages/axolos-menu/org.axolos.bento/contents/ui/main.qml
)
COMUN=(--from-code=UTF-8 --no-wrap --sort-by-file --add-comments=TRANSLATORS:
       --package-name=AxolOS --msgid-bugs-address=https://github.com/SrNoelll/axolos/issues)

# catálogo: carpeta  dominio  idiomas
CATALOGOS=(
    "packages/axolos-branding/po axolos en,fr,ru,zh_CN,ja"
    "packages/axolos-menu/po plasma_applet_org.axolos.bento es,fr,ru,zh_CN,ja"
)

plantilla() {  # plantilla DOMINIO SALIDA
    case $1 in
    axolos)
        xgettext -L Python --keyword=_ --keyword=ngettext:1,2 "${COMUN[@]}" -o "$2" "${PY[@]}"
        xgettext -L Shell --keyword=t --join-existing "${COMUN[@]}" -o "$2" "${SH[@]}" ;;
    plasma_applet_org.axolos.bento)
        # tr()/trp() son los envoltorios de i18n()/i18np() de BentoView.qml
        xgettext -L JavaScript --keyword=i18n --keyword=i18np:1,2 --keyword=tr --keyword=trp:1,2 \
            "${COMUN[@]}" -o "$2" "${QML[@]}" ;;
    esac
}

comprobar=0
[[ ${1:-} == --comprobar ]] && comprobar=1
# ningún programa puede usar «_» como variable: taparía la traducción (tools/i18n_sombras.py)
(( comprobar )) && python3 tools/i18n_sombras.py "${PY[@]}" packages/axolos-branding/static/axolos-texto
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

for c in "${CATALOGOS[@]}"; do
    read -r dir dominio idiomas <<<"$c"
    IFS=, read -ra idiomas <<<"$idiomas"
    if (( comprobar )); then
        plantilla "$dominio" "$tmp/$dominio.pot"
        for l in "${idiomas[@]}"; do
            # msgcmp: cada texto del código tiene que estar traducido en cada idioma
            msgcmp "$dir/$l.po" "$tmp/$dominio.pot" 2>&1 | sed "s|^|$dominio/$l: |" >&2 \
                || { echo "Faltan traducciones en $dir/$l.po (ejecuta tools/i18n.sh)" >&2; exit 1; }
            msgfmt -c --check-format -o /dev/null "$dir/$l.po"
        done
        echo "$dominio: traducciones al día (${idiomas[*]})"
    else
        plantilla "$dominio" "$dir/$dominio.pot"
        for l in "${idiomas[@]}"; do
            msgmerge --quiet --update --backup=none --no-wrap --no-fuzzy-matching "$dir/$l.po" "$dir/$dominio.pot"
            msgattrib --no-obsolete --no-wrap -o "$dir/$l.po" "$dir/$l.po"   # fuera los textos que ya no existen
            msgfmt -c --statistics -o /dev/null "$dir/$l.po" 2>&1 | sed "s|^|$dominio/$l: |"
        done
    fi
done
