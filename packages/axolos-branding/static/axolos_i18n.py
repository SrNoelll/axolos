"""AxolOS · idioma de las aplicaciones.

Todas las apps de AxolOS (Axo, Bienvenida, Centro, axolos-ia, axolos-dev…) hablan el idioma del
sistema: español, inglés, francés, ruso, chino o japonés; con cualquier otro, inglés.
Los textos se escriben en español en el código y se traducen con gettext (dominio «axolos»,
catálogos en /usr/share/locale/<idioma>/LC_MESSAGES/axolos.mo, fuentes en
packages/axolos-branding/po/).

    from axolos_i18n import _, ngettext, idioma, nombre_idioma
    _("Instalar AxolOS")                     → «Install AxolOS» con LANG=en_US.UTF-8
    _("{n} archivos").format(n=3)            (los textos con datos usan marcadores {…})
"""
import gettext
import os

DOMINIO = "axolos"
LOCALEDIR = os.environ.get("AXOLOS_LOCALEDIR", "/usr/share/locale")
IDIOMAS = ("es", "en", "fr", "ru", "zh", "ja")
NOMBRES = {"es": "español", "en": "English", "fr": "français", "ru": "русский", "zh": "中文", "ja": "日本語"}
# nombre del idioma tal y como se lo pedimos a la IA («responde en …»)
PARA_LA_IA = {"es": "español", "en": "English", "fr": "French", "ru": "Russian",
              "zh": "Simplified Chinese", "ja": "Japanese"}


def idioma():
    """Idioma de la interfaz: 'es', 'en', 'fr', 'ru', 'zh' o 'ja' (inglés si el sistema usa otro)."""
    # la primera variable con valor manda (como gettext); LANGUAGE puede ser una lista «de:es»
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        codigos = [p.split(".")[0].split("@")[0].split("_")[0].lower()
                   for p in os.environ.get(var, "").split(":")]
        codigos = [c for c in codigos if c and c not in ("c", "posix")]
        if codigos:
            return next((c for c in codigos if c in IDIOMAS), "en")
    return "en"


def nombre_idioma(codigo=None):
    return NOMBRES[codigo or idioma()]


def _catalogo():
    codigo = idioma()
    if codigo == "es":          # los textos originales ya están en español
        return gettext.NullTranslations()
    nombres = {"zh": ["zh_CN", "zh"]}.get(codigo, [codigo])
    return gettext.translation(DOMINIO, LOCALEDIR, languages=nombres, fallback=True)


_cat = _catalogo()
_ = _cat.gettext
ngettext = _cat.ngettext


def elegir(textos):
    """De un diccionario {'es': …, 'en': …} (datos con traducción propia), el del idioma actual."""
    if not isinstance(textos, dict):
        return textos
    return textos.get(idioma()) or textos.get("en") or textos.get("es") or next(iter(textos.values()), "")
