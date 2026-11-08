"""AxolOS · búsqueda de archivos por significado con la IA local.

Índice (en ~/.local/share/axolos/indice/archivos.db, solo en este equipo):
  - fotos y vídeos: los describe el modelo de visión instalado (qwen3.5) → «playa con sombrillas…»
  - PDF, Office (docx/pptx/xlsx/odt/odp/ods) y texto: su contenido
  - de todo: nombre, carpeta y fecha (EXIF en fotos)
Cada entrada se convierte en un vector con embeddinggemma (multilingüe). Buscar = vector de la frase
+ coseno, con ajustes por tipo («foto», «pdf»…) y fecha («último», «de ayer», «2025»…).
"""
import base64
import datetime as dt
import fcntl
import io
import json
import os
import re
import sqlite3
import subprocess
import time
import zipfile
from html import unescape
from pathlib import Path

import numpy as np

import axolos_ia as ia

DATOS = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "axolos/indice"
DB = DATOS / "archivos.db"
CONF = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "axolos/indice.conf"
EMBED = "embeddinggemma"
Q_PREF = "task: search result | query: "
D_PREF = "title: {t} | text: "
VISION_PREF = ["qwen3.5:9b", "qwen3.5:4b", "qwen3.5:27b", "qwen3.5:2b", "qwen3.5:0.8b"]

IMG = {"jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff"}
VID = {"mp4", "mkv", "webm", "mov", "avi", "m4v"}
PDF = {"pdf"}
OFFICE = {"docx", "pptx", "xlsx", "odt", "odp", "ods"}
TXT = {"txt", "md", "markdown", "rst", "csv", "tex", "org", "json", "yaml", "yml", "html", "htm"}
SALTAR = {".git", "node_modules", ".venv", "venv", "__pycache__", ".cache", "build", "dist", "target",
          ".idea", ".vscode", "site-packages"}
MAX_MB = {"img": 60, "vid": 4000, "pdf": 200, "office": 100, "txt": 5}

PROMPT_FOTO = ("Describe esta imagen en español en una o dos frases, para poder encontrarla después con una "
               "búsqueda: qué tipo es (foto, captura de pantalla, dibujo, documento escaneado…), qué se ve, el "
               "lugar, personas, animales, objetos y cualquier texto visible importante. Sin introducción.")


def tipo_de(p: Path):
    e = p.suffix.lower().lstrip(".")
    for t, ex in (("img", IMG), ("vid", VID), ("pdf", PDF), ("office", OFFICE), ("txt", TXT)):
        if e in ex:
            return t
    return None


NOMBRE_TIPO = {"img": "Imagen", "vid": "Vídeo", "pdf": "PDF", "office": "Documento", "txt": "Texto"}


def carpetas():
    """Carpetas a indexar: ~/.config/axolos/indice.conf (una por línea) o las de usuario habituales."""
    if CONF.exists():
        rutas = [Path(os.path.expanduser(x.strip())) for x in CONF.read_text().splitlines()
                 if x.strip() and not x.lstrip().startswith("#")]
    else:
        rutas = []
        for clave in ("DESKTOP", "DOCUMENTS", "DOWNLOAD", "PICTURES", "VIDEOS"):
            try:
                r = subprocess.run(["xdg-user-dir", clave], capture_output=True, text=True).stdout.strip()
            except OSError:
                r = ""
            if r and Path(r) != Path.home():
                rutas.append(Path(r))
    return [r for r in dict.fromkeys(rutas) if r.is_dir()]


# --- base de datos ---------------------------------------------------------------------------------
def conectar():
    DATOS.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=30)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE TABLE IF NOT EXISTS archivos(
        ruta TEXT PRIMARY KEY, mtime REAL, tam INTEGER, tipo TEXT, fecha REAL,
        desc TEXT, texto TEXT, vec BLOB, mini BLOB, visto REAL)""")
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    return c


# --- extracción -------------------------------------------------------------------------------------
def _xml_texto(data, etiqueta):
    return " ".join(unescape(m) for m in re.findall(rf"<{etiqueta}[^>]*>([^<]*)</{etiqueta}>", data))


def texto_office(p: Path):
    try:
        with zipfile.ZipFile(p) as z:
            nombres = z.namelist()
            if p.suffix.lower() == ".docx":
                partes = [_xml_texto(z.read("word/document.xml").decode(errors="ignore"), "w:t")]
            elif p.suffix.lower() == ".pptx":
                sl = sorted((n for n in nombres if re.match(r"ppt/slides/slide\d+\.xml", n)),
                            key=lambda n: int(re.findall(r"\d+", n)[0]))
                partes = [_xml_texto(z.read(n).decode(errors="ignore"), "a:t") for n in sl]
            elif p.suffix.lower() == ".xlsx":
                partes = [_xml_texto(z.read("xl/sharedStrings.xml").decode(errors="ignore"), "t")] \
                    if "xl/sharedStrings.xml" in nombres else []
            else:   # OpenDocument
                c = z.read("content.xml").decode(errors="ignore")
                partes = [re.sub(r"<[^>]+>", " ", c)]
        return re.sub(r"\s+", " ", " ".join(partes)).strip()
    except (zipfile.BadZipFile, KeyError, OSError):
        return ""


def texto_pdf(p: Path):
    try:
        r = subprocess.run(["pdftotext", "-q", "-l", "6", "-enc", "UTF-8", str(p), "-"],
                           capture_output=True, text=True, timeout=60)
        return re.sub(r"\s+", " ", r.stdout).strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def texto_plano(p: Path):
    try:
        t = p.read_text(errors="ignore")[:20000]
    except OSError:
        return ""
    if p.suffix.lower() in (".html", ".htm"):
        t = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", t))
    return re.sub(r"\s+", " ", unescape(t)).strip()


def _imagen(p_o_bytes):
    from PIL import Image, ImageOps
    im = Image.open(io.BytesIO(p_o_bytes) if isinstance(p_o_bytes, bytes) else p_o_bytes)
    im = ImageOps.exif_transpose(im)
    return im


def fecha_exif(p: Path):
    try:
        from PIL import Image
        ex = Image.open(p).getexif()
        v = ex.get_ifd(0x8769).get(36867) or ex.get(306)      # DateTimeOriginal / DateTime
        return dt.datetime.strptime(str(v)[:19], "%Y:%m:%d %H:%M:%S").timestamp() if v else None
    except Exception:  # noqa: BLE001  EXIF roto o ausente
        return None


def primera_pagina(p: Path):
    """Primera página de un PDF como JPEG (para miniatura y para leer PDF escaneados)."""
    try:
        r = subprocess.run(["pdftoppm", "-q", "-f", "1", "-l", "1", "-r", "70", "-jpeg", str(p)],
                           capture_output=True, timeout=60)
        return r.stdout or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def fotograma(p: Path):
    """Un fotograma del vídeo (al 15 % de su duración) en JPEG."""
    try:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                    "csv=p=0", str(p)], capture_output=True, text=True, timeout=30).stdout or 0)
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(dur * 0.15, 0):.2f}", "-i", str(p),
                            "-frames:v", "1", "-vf", "scale=768:-2", "-f", "image2", "-c:v", "mjpeg", "-"],
                           capture_output=True, timeout=60)
        return r.stdout or None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def jpeg_b64(origen, lado=768):
    im = _imagen(origen).convert("RGB")
    im.thumbnail((lado, lado))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=85)
    return base64.b64encode(b.getvalue()).decode()


def miniatura(origen, lado=64):
    """PNG cuadrado pequeño para enseñar en KRunner/Bento."""
    from PIL import ImageOps
    im = _imagen(origen).convert("RGBA")
    im = ImageOps.fit(im, (lado, lado))
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def describir(modelo, b64):
    with ia._req("/api/chat", {"model": modelo, "stream": False, "think": False,
                               "messages": [{"role": "user", "content": PROMPT_FOTO, "images": [b64]}],
                               "options": {"num_predict": 110, "temperature": 0.2}}, timeout=300) as r:
        return json.load(r)["message"]["content"].strip().replace("\n", " ")


def embeber(textos):
    with ia._req("/api/embed", {"model": EMBED, "input": textos}, timeout=300) as r:
        v = np.array(json.load(r)["embeddings"], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def modelo_vision():
    instalados = {m["name"].removesuffix(":latest") for m in ia.modelos()}
    for m in VISION_PREF:
        if m in instalados and "vision" in ia.capacidades(m):
            return m
    return None


# --- indexar -----------------------------------------------------------------------------------------
def candidatos():
    for raiz in carpetas():
        for dirpath, dirnames, ficheros in os.walk(raiz):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SALTAR]
            for f in ficheros:
                if f.startswith("."):
                    continue
                p = Path(dirpath) / f
                t = tipo_de(p)
                if not t:
                    continue
                try:
                    st = p.stat()
                except OSError:
                    continue
                if st.st_size == 0 or st.st_size > MAX_MB[t] * 2**20:
                    continue
                yield p, t, st


def en_bateria():
    """True si hay cargador posible (portátil) y no está enchufado."""
    red = [p for p in Path("/sys/class/power_supply").glob("*")
           if (p / "type").exists() and (p / "type").read_text().strip() in ("Mains", "USB")]
    return bool(red) and not any((p / "online").exists() and (p / "online").read_text().strip() == "1"
                                 for p in red)


def indexar(aviso=print, parar=lambda: False, max_bateria=None):
    """Añade lo nuevo/cambiado y quita lo borrado. Solo un indexador a la vez (el resto espera).
    max_bateria: si el portátil va con batería y hay más pendientes que esto, se deja para luego."""
    DATOS.mkdir(parents=True, exist_ok=True)
    with open(DATOS / "indexando.lock", "w") as cerrojo:
        fcntl.flock(cerrojo, fcntl.LOCK_EX)
        return _indexar(aviso, parar, max_bateria)


def _indexar(aviso, parar, max_bateria):
    if not ia.servidor_ok():
        aviso("La IA local está apagada: no se puede indexar.")
        return 1
    if EMBED not in {m["name"].removesuffix(":latest") for m in ia.modelos()}:
        aviso(f"Falta el modelo de búsqueda: axolos-ia descargar {EMBED}")
        return 1
    vision = modelo_vision()
    if not vision:
        aviso("Sin modelo de visión: las fotos se buscarán solo por nombre y fecha.")
    db = conectar()
    vistos, pendientes = set(), []
    hechos = {r[0]: (r[1], r[2]) for r in db.execute("SELECT ruta, mtime, tam FROM archivos")}
    for p, t, st in candidatos():
        k = str(p)
        vistos.add(k)
        if hechos.get(k) != (st.st_mtime, st.st_size):
            pendientes.append((p, t, st))
    borrados = [k for k in hechos if k not in vistos]
    db.executemany("DELETE FROM archivos WHERE ruta = ?", [(k,) for k in borrados])
    db.commit()
    total = len(pendientes)
    if max_bateria is not None and total > max_bateria and en_bateria():
        aviso(f"{total} archivos nuevos: se indexarán al enchufar el portátil (describir fotos usa la gráfica)")
        return 0
    aviso(f"{len(vistos)} archivos en {', '.join(str(c) for c in carpetas())}: {total} por indexar"
          + (f", {len(borrados)} quitados" if borrados else ""))
    lote = []
    for i, (p, t, st) in enumerate(pendientes, 1):
        if parar():
            break
        desc, texto, mini, fecha = "", "", None, st.st_mtime
        try:
            if t in ("img", "vid"):
                origen = p if t == "img" else fotograma(p)
                if origen:
                    mini = miniatura(origen)
                    if vision:
                        desc = describir(vision, jpeg_b64(origen))
                if t == "img":
                    fecha = fecha_exif(p) or st.st_mtime
            elif t == "pdf":
                texto = texto_pdf(p)
                pagina = primera_pagina(p)
                if pagina:
                    mini = miniatura(pagina)
                    if vision and len(texto) < 80:          # PDF escaneado: que lo lea la visión
                        desc = describir(vision, jpeg_b64(pagina, 1024))
            elif t == "office":
                texto = texto_office(p)
            else:
                texto = texto_plano(p)
        except Exception as e:  # noqa: BLE001  un archivo raro no para el índice
            aviso(f"   ! {p.name}: {e}")
        if not desc:
            desc = texto[:240]
        carpeta = str(p.parent).replace(str(Path.home()), "~")
        cuando = dt.datetime.fromtimestamp(fecha).strftime("%d/%m/%Y")
        contenido = f"{NOMBRE_TIPO[t]} «{p.name}» en {carpeta}, del {cuando}. {desc} {texto[:2500]}"
        lote.append((str(p), st.st_mtime, st.st_size, t, fecha, desc, texto[:4000], mini,
                     D_PREF.format(t=p.stem) + contenido))
        aviso(f"   [{i}/{total}] {p.name}")
        if len(lote) >= 16 or i == total:
            vecs = embeber([x[-1] for x in lote])
            db.executemany("INSERT OR REPLACE INTO archivos VALUES (?,?,?,?,?,?,?,?,?,?)",
                           [(*x[:7], v.tobytes(), x[7], time.time()) for x, v in zip(lote, vecs)])
            db.commit()
            lote = []
    if lote:
        vecs = embeber([x[-1] for x in lote])
        db.executemany("INSERT OR REPLACE INTO archivos VALUES (?,?,?,?,?,?,?,?,?,?)",
                       [(*x[:7], v.tobytes(), x[7], time.time()) for x, v in zip(lote, vecs)])
        db.commit()
    db.execute("INSERT OR REPLACE INTO meta VALUES ('ultima', ?)", (str(time.time()),))
    db.commit()
    aviso("Índice al día.")
    return 0


# --- buscar ------------------------------------------------------------------------------------------
TIPOS_CONSULTA = [   # palabra de la frase → extensiones que se aceptan
    (r"\b(fotos?|im[aá]genes|imagen|capturas?|pantallazos?|selfies?)\b", IMG),
    (r"\b(v[ií]deos?|grabaci[oó]n(es)?|pel[ií]culas?)\b", VID),
    (r"\bpdfs?\b", PDF),
    (r"\b(presentaci[oó]n(es)?|diapositivas|pptx?|powerpoint)\b", {"pptx", "odp"}),
    (r"\b(excel|hojas? de c[aá]lculo|xlsx)\b", {"xlsx", "ods", "csv"}),
    (r"\b(word|docx)\b", {"docx", "odt"}),
    (r"\b(documentos?|apuntes|notas|textos?)\b", PDF | OFFICE | TXT),
]
# Por debajo: «lo más parecido», no una coincidencia clara (medido con embeddinggemma en archivos reales:
# las descripciones de fotos son cortas y puntúan más alto que documentos largos)
UMBRAL_CLARO = {"img": 0.38, "vid": 0.38}
UMBRAL_DOC = 0.22
VACIAS = {"una", "uno", "unos", "unas", "los", "las", "del", "mis", "que", "con", "por", "para", "busco",
          "buscar", "busca", "archivo", "archivos", "fichero", "ficheros", "foto", "fotos", "imagen",
          "documento", "pdf", "video", "vídeo", "donde", "dónde", "está", "esta", "tengo", "algo"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]


def _fechas(q, ahora):
    """(desde, hasta, preferir_reciente) a partir de la frase."""
    hoy = dt.datetime.combine(ahora.date(), dt.time())
    if re.search(r"\bhoy\b", q):
        return hoy.timestamp(), None, False
    if re.search(r"\bayer\b", q):
        return (hoy - dt.timedelta(days=1)).timestamp(), hoy.timestamp(), False
    if re.search(r"\besta semana\b", q):
        return (hoy - dt.timedelta(days=hoy.weekday())).timestamp(), None, False
    if re.search(r"\b(este mes)\b", q):
        return hoy.replace(day=1).timestamp(), None, False
    if re.search(r"\bmes pasado\b", q):
        fin = hoy.replace(day=1)
        return (fin - dt.timedelta(days=1)).replace(day=1).timestamp(), fin.timestamp(), False
    m = re.search(r"\b(19|20)\d\d\b", q)
    if m:
        a = int(m.group(0))
        return dt.datetime(a, 1, 1).timestamp(), dt.datetime(a + 1, 1, 1).timestamp(), False
    for i, mes in enumerate(MESES, 1):
        if re.search(rf"\b{mes}\b", q):
            a = ahora.year if i <= ahora.month else ahora.year - 1
            ini = dt.datetime(a, i, 1)
            fin = dt.datetime(a + (i == 12), i % 12 + 1, 1)
            return ini.timestamp(), fin.timestamp(), False
    reciente = bool(re.search(r"\b([uú]ltim[oa]s?|recientes?|nuev[oa]s?|actual)\b", q))
    return None, None, reciente


class Buscador:
    """Mantiene el índice en memoria y lo recarga si cambia."""

    def __init__(self):
        self._mtime, self.filas, self.mat = 0, [], None

    def _cargar(self):
        try:
            m = max(DB.stat().st_mtime, Path(str(DB) + "-wal").stat().st_mtime
                    if Path(str(DB) + "-wal").exists() else 0)
        except OSError:
            return False
        if m != self._mtime:
            db = conectar()
            filas = db.execute("SELECT ruta, tipo, fecha, desc, vec, mini FROM archivos WHERE vec IS NOT NULL")\
                .fetchall()
            db.close()
            self.filas = [f for f in filas if Path(f[0]).exists()]
            self.mat = np.vstack([np.frombuffer(f[4], dtype=np.float32) for f in self.filas]) \
                if self.filas else None
            self._mtime = m
        return self.mat is not None

    def buscar(self, consulta, n=8):
        if not self._cargar():
            return []
        q = consulta.lower().strip()
        exts = set()
        for patron, es in TIPOS_CONSULTA:
            if re.search(patron, q):
                exts = set(es)
                break                    # el primero que aparece manda («foto de mis apuntes» = foto)
        desde, hasta, reciente = _fechas(q, dt.datetime.now())
        qv = embeber([Q_PREF + consulta])[0]
        sim = self.mat @ qv
        palabras = [w for w in re.findall(r"\w{3,}", q) if w not in VACIAS]
        out = []
        ahora = time.time()
        for (ruta, tipo, fecha, desc, _v, mini), s in zip(self.filas, sim):
            if exts and Path(ruta).suffix.lower().lstrip(".") not in exts:
                continue
            if desde and (fecha or 0) < desde or hasta and (fecha or 0) >= hasta:
                continue
            nombre = Path(ruta).name.lower()
            d = (desc or "").lower()
            s = float(s) + sum(0.15 if re.search(rf"\b{re.escape(w)}", nombre) else 0.02 if w in d else 0
                               for w in palabras)
            if reciente:
                s += 0.06 * max(0.0, 1 - (ahora - (fecha or 0)) / (365 * 86400))
            out.append((s, ruta, tipo, fecha, desc, mini))
        out.sort(key=lambda x: -x[0])
        if not out:
            return []
        # ¿queda algo que buscar además del tipo y las palabras de relleno? («presentación» → solo tipo)
        resto = re.sub(r"\b(un|una|unos|unas|el|la|los|las|de|del|mi|mis|que|en|con|busco|buscar|"
                       r"archivo|archivos|fichero|ficheros)\b", " ", q)
        for patron, _ts in TIPOS_CONSULTA:
            resto = re.sub(patron, " ", resto)
        solo_tipo = not resto.strip()
        if solo_tipo:                              # sin tema: lo más reciente de ese tipo
            out.sort(key=lambda x: -(x[3] or 0))
            res = out[:n]
            debil = False
        else:
            mejor = out[0][0]
            if mejor < 0.2:                        # nada se parece de verdad
                return []
            res = [o for o in out if o[0] >= max(mejor - 0.1, 0.18)][:n]
            debil = mejor < UMBRAL_CLARO.get(out[0][2], UMBRAL_DOC)
        return [dict(score=round(s, 3), ruta=r, tipo=t, fecha=f, desc=d, mini=m, parecido=debil)
                for s, r, t, f, d, m in res]


def estado():
    if not DB.exists():
        return "sin índice todavía"
    db = conectar()
    n = dict(db.execute("SELECT tipo, COUNT(*) FROM archivos GROUP BY tipo").fetchall())
    ult = db.execute("SELECT v FROM meta WHERE k='ultima'").fetchone()
    db.close()
    plural = {"img": "imágenes", "vid": "vídeos", "pdf": "PDF", "office": "documentos", "txt": "textos"}
    partes = [f"{v} {plural.get(k, k)}" for k, v in sorted(n.items(), key=lambda x: -x[1])]
    cuando = dt.datetime.fromtimestamp(float(ult[0])).strftime("%d/%m %H:%M") if ult else "nunca"
    return f"{sum(n.values())} archivos ({', '.join(partes)}), actualizado {cuando}"
