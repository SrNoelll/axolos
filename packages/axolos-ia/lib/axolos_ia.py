"""AxolOS · IA local: lo común a axolos-ia, el chat Axo, KRunner y la Bienvenida.

El motor es Ollama (servicio ollama.service, http://127.0.0.1:11434): usa llama.cpp
por dentro, libera la gráfica cuando no se usa y descarga modelos con un comando.
"""
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

URL = os.environ.get("AXOLOS_IA_URL", "http://127.0.0.1:11434").rstrip("/")
ROOT_HELPER = "/usr/lib/axolos/axolos-root"

# Catálogo. vram/ram = lo mínimo para que vaya fluido (GB).  Velocidades medidas en AxolOS con
# una RTX 4060 Laptop (8 GB) + 32 GB de RAM, Ollama 0.40 con CUDA:
#   qwen3.5:9b       41 tokens/s  (6,4 GB de VRAM)
#   qwen3-coder:30b  38 tokens/s  (MoE: 6,8 GB en gráfica y el resto en RAM)
#   sin gráfica (CPU) qwen3:8b va a 9,6 tokens/s
CATALOGO = [
    dict(id="qwen3.5:4b", nombre="Qwen 3.5 · 4B", uso="Chat, código e imágenes (equipos modestos)",
         gb=3.3, vram=4.5, ram=8),
    dict(id="qwen3.5:9b", nombre="Qwen 3.5 · 9B", uso="Chat, código e imágenes",
         gb=6.6, vram=7.5, ram=16),
    dict(id="qwen3.5:27b", nombre="Qwen 3.5 · 27B", uso="Chat, código e imágenes (máxima calidad)",
         gb=17.5, vram=20, ram=32),
    dict(id="qwen3-coder:30b", nombre="Qwen3 Coder · 30B", uso="Programación avanzada (agentes, proyectos grandes)",
         gb=18.6, vram=6, ram=28),
    dict(id="qwen2.5-coder:1.5b", nombre="Qwen2.5 Coder · 1.5B", uso="Autocompletado de código en el editor",
         gb=1.0, vram=1.5, ram=8),
    dict(id="qwen2.5-coder:7b", nombre="Qwen2.5 Coder · 7B", uso="Autocompletado de código (más preciso)",
         gb=4.7, vram=6, ram=16),
    # Elegido midiendo búsquedas en español: 12/12 aciertos frente a 7/12 de nomic-embed-text
    dict(id="embeddinggemma", nombre="EmbeddingGemma", uso="Buscar tus archivos por lo que contienen",
         gb=0.6, vram=1, ram=4),
]
POR_ID = {m["id"]: m for m in CATALOGO}


def cabe(model, hw):
    m = POR_ID.get(model)
    return bool(m) and hw["vram_gb"] >= m["vram"] and hw["ram_gb"] >= m["ram"] * 0.9


# --- Hardware --------------------------------------------------------------------
def _vendor():
    vend = set()
    for p in Path("/sys/class/drm").glob("card*/device/vendor"):
        try:
            vend.add(p.read_text().strip())
        except OSError:
            pass
    return "nvidia" if "0x10de" in vend else "amd" if "0x1002" in vend else "otra"


def hardware():
    """{'vendor', 'gpu', 'vram_gb', 'ram_gb', 'backend', 'backend_ok'}"""
    hw = {"vendor": _vendor(), "gpu": "", "vram_gb": 0.0}
    try:
        hw["ram_gb"] = round(int(open("/proc/meminfo").read().split()[1]) / 1048576, 1)
    except (OSError, ValueError, IndexError):
        hw["ram_gb"] = 0.0
    if hw["vendor"] == "nvidia" and shutil.which("nvidia-smi"):
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            name, mem = r.stdout.strip().splitlines()[0].rsplit(",", 1)
            hw["gpu"], hw["vram_gb"] = name.strip(), round(int(mem) / 1024, 1)
    elif hw["vendor"] == "amd":
        for p in Path("/sys/class/drm").glob("card*/device/mem_info_vram_total"):
            hw["vram_gb"] = max(hw["vram_gb"], round(int(p.read_text()) / 2**30, 1))
        hw["gpu"] = "AMD Radeon"
    need = {"nvidia": "ollama-cuda", "amd": "ollama-rocm", "otra": "ollama-vulkan"}[hw["vendor"]]
    hw["backend"] = need
    hw["backend_ok"] = subprocess.run(["pacman", "-T", need], capture_output=True).returncode == 0
    return hw


def recomendados(hw=None):
    """Ids del catálogo que conviene instalar en este equipo."""
    hw = hw or hardware()
    v = hw["vram_gb"] if hw["backend_ok"] or hw["vendor"] != "otra" else 0
    if v >= 20:
        return ["qwen3.5:27b", "qwen2.5-coder:7b", "embeddinggemma"]
    if v >= 12:
        return ["qwen3.5:9b", "qwen2.5-coder:7b", "embeddinggemma"]
    if v >= 7:
        return ["qwen3.5:9b", "qwen2.5-coder:1.5b", "embeddinggemma"]
    return ["qwen3.5:4b", "qwen2.5-coder:1.5b", "embeddinggemma"]


def opcionales(hw=None):
    """Modelos grandes que este equipo mueve bien pero no se descargan solos (pesan mucho)."""
    hw = hw or hardware()
    rec = set(recomendados(hw))
    return [m["id"] for m in CATALOGO if m["id"] not in rec and m["gb"] > 8 and cabe(m["id"], hw)]


# --- Servidor ----------------------------------------------------------------------
def _req(path, data=None, timeout=10):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(URL + path, body, {"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout)


def servidor_ok():
    try:
        with _req("/api/version", timeout=2) as r:
            return json.load(r).get("version", "?")
    except (OSError, ValueError):
        return None


def modelos():
    """[{'name', 'size_gb', 'family'}] instalados."""
    try:
        with _req("/api/tags") as r:
            return [{"name": m["name"], "size_gb": round(m.get("size", 0) / 1e9, 1),
                     "family": m.get("details", {}).get("family", "")} for m in json.load(r)["models"]]
    except (OSError, ValueError, KeyError):
        return []


def capacidades(model):
    try:
        with _req("/api/show", {"model": model}) as r:
            return json.load(r).get("capabilities", [])
    except (OSError, ValueError):
        return []


def es_chat(model, caps=None):
    caps = caps if caps is not None else capacidades(model)
    return "completion" in caps and "embedding" not in caps and not re.search(r"embed", model)


def en_memoria():
    """[{'name', 'vram_gb', 'size_gb'}] cargados ahora mismo."""
    try:
        with _req("/api/ps") as r:
            return [{"name": m["name"], "vram_gb": round(m.get("size_vram", 0) / 2**30, 1),
                     "size_gb": round(m.get("size", 0) / 2**30, 1)} for m in json.load(r)["models"]]
    except (OSError, ValueError, KeyError):
        return []


# Contexto de Axo: el sistema (equipo + manual) ocupa ~4.500 tokens y Ollama trae 4.096 por defecto,
# así que recortaría el principio. 16k cuesta ~0,2 GB más de VRAM con qwen3.5:9b (medido).
CTX_CHAT = 16384


def chat(model, messages, think=False, stop=None, num_ctx=CTX_CHAT):
    """Genera la respuesta en streaming: ('thinking'|'content', texto) y al final ('stats', dict)."""
    data = {"model": model, "messages": messages, "stream": True, "think": bool(think),
            "options": {"num_ctx": num_ctx}}
    with _req("/api/chat", data, timeout=600) as r:
        for line in r:
            if stop is not None and stop():
                return
            if not line.strip():
                continue
            d = json.loads(line)
            if "error" in d:
                raise RuntimeError(d["error"])
            msg = d.get("message", {})
            if msg.get("thinking"):
                yield "thinking", msg["thinking"]
            if msg.get("content"):
                yield "content", msg["content"]
            if d.get("done"):
                ev, dur = d.get("eval_count", 0), d.get("eval_duration", 0) or 1
                yield "stats", {"tokens": ev, "tok_s": round(ev / (dur / 1e9), 1)}


def titulo(model, pregunta, respuesta):
    """Título corto (3-6 palabras) para una conversación, en el idioma de la pregunta."""
    msgs = [{"role": "system", "content": "Devuelves solo un título de 3 a 6 palabras, sin comillas ni "
                                          "punto final, en el mismo idioma que el usuario."},
            {"role": "user", "content": f"Pregunta: {pregunta[:1500]}\n\nRespuesta: {respuesta[:1500]}\n\n"
                                        "Título de esta conversación:"}]
    with _req("/api/chat", {"model": model, "messages": msgs, "stream": False, "think": False,
                            "options": {"num_predict": 24, "temperature": 0.2}}, timeout=120) as r:
        t = json.load(r).get("message", {}).get("content", "")
    t = re.sub(r"[\"'«»*#`]", "", t.strip().splitlines()[0] if t.strip() else "").strip(" .:")
    return t[:60]


def descargar(model):
    """Descarga un modelo: genera (completado_bytes, total_bytes, estado)."""
    with _req("/api/pull", {"model": model, "stream": True}, timeout=3600) as r:
        for line in r:
            d = json.loads(line)
            if "error" in d:
                raise RuntimeError(d["error"])
            yield d.get("completed", 0), d.get("total", 0), d.get("status", "")


def nombre_bonito(model):
    m = POR_ID.get(model) or POR_ID.get(model.removesuffix(":latest"))
    return m["nombre"] if m else model
