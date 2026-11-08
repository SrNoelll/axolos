"""AxolOS · contexto para la IA: el equipo de quien la usa (leído en vivo) + el manual de AxolOS.

Nada está escrito a mano para un equipo concreto: todo se lee al momento de /proc, /sys,
os-release, pacman, KDE (atajos reales vía kglobalaccel, pantallas vía kscreen-doctor)…
y el manual solo incluye los apartados de lo que está instalado.
"""
import datetime as dt
import json
import os
import platform
import pwd
import re
import shutil
import subprocess
from pathlib import Path

MANUAL = Path(os.environ.get("AXOLOS_MANUAL", "/usr/share/axolos/ia/manual.md"))
PERFILES = Path(os.environ.get("AXOLOS_PERFILES", "/usr/share/axolos/perfiles.json"))


def _sh(*cmd, timeout=3):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _leer(p):
    try:
        return Path(p).read_text(errors="replace").strip()
    except OSError:
        return ""


def _os_release():
    d = {}
    for linea in _leer("/etc/os-release").splitlines() or _leer("/usr/lib/os-release").splitlines():
        if "=" in linea:
            k, v = linea.split("=", 1)
            d[k] = v.strip('"')
    return d


def _gb(n):
    return f"{n / 2**30:.0f} GB"


# --- piezas -------------------------------------------------------------------------------------
def _usuario():
    pw = pwd.getpwuid(os.getuid())
    real = pw.pw_gecos.split(",")[0].strip()
    if real and real != pw.pw_name:
        quien = f"Usuario: {real} (cuenta «{pw.pw_name}»)"
    else:
        quien = f"Usuario: {pw.pw_name} (es el nombre de la cuenta; puede no ser su nombre real)"
    return [quien,
            f"Carpeta personal: {pw.pw_dir}",
            f"Terminal: {Path(pw.pw_shell).name}" + (", con Konsole" if shutil.which("konsole") else ""),
            f"Idioma: {os.environ.get('LANG', '?')}"]


def _sistema():
    osr = _os_release()
    nombre = osr.get("PRETTY_NAME") or osr.get("NAME", "Linux")
    base = osr.get("ID_LIKE", "")
    ver = _sh("pacman", "-Q", "axolos-desktop") or _sh("pacman", "-Q", "axolos-branding")
    lineas = [f"Sistema: {nombre}" + (f" (basado en {base})" if base else "")
              + (f", paquete {ver}" if ver else "")]
    plasma = _sh("plasmashell", "--version").replace("plasmashell", "").strip()
    sesion = os.environ.get("XDG_SESSION_TYPE", "")
    lineas.append(f"Kernel: {platform.release()}"
                  + (f" · KDE Plasma {plasma}" if plasma else "")
                  + (f" · sesión {sesion.capitalize()}" if sesion else ""))
    return lineas


def _hardware():
    lineas = []
    fab, modelo = _leer("/sys/class/dmi/id/sys_vendor"), _leer("/sys/class/dmi/id/product_name")
    if modelo and "filled" not in modelo.lower():
        lineas.append(f"Equipo: {fab} {modelo}".replace("  ", " ") + f" (nombre de red «{platform.node()}»)")
    cpu = ""
    for linea in _leer("/proc/cpuinfo").splitlines():
        if linea.startswith("model name"):
            cpu = re.sub(r"\s+", " ", linea.split(":", 1)[1]).strip()
            break
    hilos = os.cpu_count() or 0
    nucleos = len({ln for ln in _leer("/proc/cpuinfo").splitlines() if ln.startswith("core id")}) or hilos
    if cpu:
        lineas.append(f"Procesador: {cpu} ({hilos} hilos)")
    try:
        ram = int(_leer("/proc/meminfo").split()[1]) * 1024
        lineas.append(f"Memoria RAM: {_gb(ram)}")
    except (ValueError, IndexError):
        pass
    gpus = []
    for linea in _sh("lspci", "-mm").splitlines():
        if re.search(r'"(VGA|3D|Display)', linea):
            partes = re.findall(r'"([^"]*)"', linea)
            if len(partes) >= 3:
                gpus.append(f"{partes[1].replace(' Corporation', '')} {partes[2]}")
    vram = _sh("nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits")
    if vram:
        n, m = vram.splitlines()[0].rsplit(",", 1)
        gpus = [g for g in gpus if "NVIDIA" not in g] + [f"{n.strip()} con {int(m) / 1024:.0f} GB de VRAM"]
    if gpus:
        lineas.append("Gráficas: " + "; ".join(gpus))
    pantallas = []
    try:
        j = json.loads(_sh("kscreen-doctor", "-j") or "{}")
        for o in j.get("outputs", []):
            if not o.get("enabled"):
                continue
            modo = next((m for m in o.get("modes", []) if m.get("id") == o.get("currentModeId")), {})
            tam = modo.get("size", {})
            txt = f"{o.get('name')}"
            if tam:
                txt += f" {tam.get('width')}×{tam.get('height')} a {modo.get('refreshRate', 0):.0f} Hz"
            if o.get("scale", 1) != 1:
                txt += f", escala {o['scale'] * 100:.0f} %"
            if o.get("priority") == 1:
                txt += " (principal)"
            pantallas.append(txt)
    except ValueError:
        pass
    if pantallas:
        lineas.append("Pantallas: " + "; ".join(pantallas))
    try:
        st = os.statvfs("/")
        fs = _sh("findmnt", "-no", "FSTYPE", "/")
        lineas.append(f"Disco del sistema: {_gb(st.f_blocks * st.f_frsize)} en total, "
                      f"{_gb(st.f_bavail * st.f_frsize)} libres" + (f" ({fs})" if fs else ""))
    except OSError:
        pass
    for bat in sorted(Path("/sys/class/power_supply").glob("BAT*")):
        cap, est = _leer(bat / "capacity"), _leer(bat / "status")
        if cap:
            lineas.append(f"Batería: {cap} % ({ {'Charging': 'cargando', 'Discharging': 'descargando', 'Full': 'llena', 'Not charging': 'conectado, sin cargar'}.get(est, est.lower())})")
    return lineas


def _software(instalados):
    lineas = []
    nav = _sh("xdg-settings", "get", "default-web-browser")
    if nav:
        nombre = nav
        for d in (Path.home() / ".local/share/applications", Path("/usr/share/applications")):
            f = d / nav
            if f.exists():
                m = re.search(r"^Name=(.+)$", _leer(f), re.M)
                nombre = m.group(1) if m else nav
                break
        lineas.append(f"Navegador por defecto: {nombre}")
    aur = [h for h in ("paru", "yay") if shutil.which(h)]
    lineas.append("Instalar programas: pacman" + (f"; AUR con {' o '.join(aur)}" if aur else "; sin ayudante de AUR")
                  + ("; Flatpak disponible" if shutil.which("flatpak") else ""))
    ax = sorted(p for p in instalados if p.startswith("axolos-"))
    if ax:
        lineas.append("Componentes de AxolOS instalados: " + ", ".join(ax))
    herramientas = {"python3": "Python", "node": "Node.js", "bun": "Bun", "deno": "Deno", "go": "Go",
                    "rustc": "Rust", "cargo": "Cargo", "java": "Java", "gcc": "GCC", "clang": "Clang",
                    "docker": "Docker", "podman": "Podman", "distrobox": "distrobox", "kubectl": "kubectl",
                    "code": "VS Code", "codium": "VSCodium", "nvim": "Neovim", "kate": "Kate",
                    "idea": "IntelliJ IDEA", "android-studio": "Android Studio", "git": "git", "gh": "GitHub CLI"}
    hay = [n for c, n in herramientas.items() if shutil.which(c)]
    if hay:
        lineas.append("Herramientas de desarrollo presentes: " + ", ".join(hay))
    try:
        perf = json.loads(PERFILES.read_text(encoding="utf-8"))
        nv = "0x10de" in {_leer(p) for p in Path("/sys/class/drm").glob("card*/device/vendor")}
        ok, no = [], []
        for k, p in perf.items():
            pk = p["paquetes"] + p.get("paquetes_nvidia" if nv else "paquetes_otros", [])
            falta = subprocess.run(["pacman", "-T", *pk], capture_output=True).returncode != 0
            (no if falta else ok).append(p["nombre"])
        lineas.append("Perfiles de axolos-dev instalados: " + (", ".join(ok) or "ninguno")
                      + (f". Sin instalar: {', '.join(no)}" if no else ""))
    except (OSError, ValueError, KeyError):
        pass
    if shutil.which("docker"):
        grupos = _sh("id", "-nG").split()
        lineas.append("Docker: " + ("el usuario puede usarlo sin sudo" if "docker" in grupos
                                    else "el usuario NO está en el grupo docker (necesita sudo)"))
    return lineas


def _ia():
    try:
        import axolos_ia as ia
    except ImportError:
        return []
    hw = ia.hardware()
    v = ia.servidor_ok()
    ms = [m["name"] for m in ia.modelos()] if v else []
    return [f"IA local: Ollama {v or 'apagado'} en {ia.URL}"
            + (f", acelerada por gráfica ({hw['backend']})" if hw["backend_ok"] else ", sin aceleración por gráfica"),
            "Modelos instalados: " + (", ".join(ms) or "ninguno"),
            "Índice de archivos para «ia busco …»: " + _indice()]


def _indice():
    try:
        import axolos_buscar
        return axolos_buscar.estado()
    except Exception:  # noqa: BLE001
        return "no disponible"


def _atajos():
    """Atajos globales tal y como están AHORA en KDE (incluye los que el usuario haya cambiado)."""
    try:
        import dbus
        from PyQt6.QtCore import QKeyCombination
        from PyQt6.QtGui import QKeySequence
    except ImportError:
        return []
    try:
        bus = dbus.SessionBus()
        comps = bus.get_object("org.kde.kglobalaccel", "/kglobalaccel").allComponents(
            dbus_interface="org.kde.KGlobalAccel")
    except dbus.DBusException:
        return []
    agrupados, salida = {}, []
    for c in comps:
        try:
            infos = bus.get_object("org.kde.kglobalaccel", c).allShortcutInfos(
                dbus_interface="org.kde.kglobalaccel.Component")
        except dbus.DBusException:
            continue
        for s in infos:
            teclas = [QKeySequence(QKeyCombination.fromCombined(int(k))).toString() for k in s[6] if int(k)]
            # fuera las teclas especiales (volumen, brillo, multimedia, panel táctil…)
            teclas = [t for t in teclas if re.search(r"Meta|Ctrl|Alt|Shift|^F\d+$|Print", t)
                      and " " not in t.split("+")[-1]]
            if not teclas:
                continue
            accion = str(s[1])
            m = re.match(r"(.*?)\s(\d+)(.*)$", accion)
            if m and re.search(r"(escritorio|entrada)", accion, re.I):   # «… escritorio 1/2/3» → una línea
                agrupados.setdefault((str(s[3]), m.group(1) + " N" + m.group(3)), []).append(
                    (int(m.group(2)), " o ".join(teclas)))
                continue
            salida.append(f"{s[3]} · {accion}: {' o '.join(teclas)}")
    for (comp, accion), teclas in agrupados.items():
        salida.append(f"{comp} · {accion}: " + "; ".join(f"{n} = {t}" for n, t in sorted(teclas)))
    return sorted(salida)


def manual(instalados):
    """Manual de AxolOS con solo los apartados de lo que está instalado.
    Bloques: <!-- si: paquete1|paquete2 --> … <!-- fin -->."""
    texto = _leer(MANUAL)

    def bloque(m):
        req = [p.strip() for p in m.group(1).split("|")]
        return m.group(2) if any(p in instalados for p in req) else ""
    texto = re.sub(r"<!-- si: ([^>]+?) -->\n?(.*?)<!-- fin -->\n?", bloque, texto, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def contexto():
    instalados = set(_sh("pacman", "-Qq", timeout=5).split())
    ahora = dt.datetime.now()
    dia = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"][ahora.weekday()]
    partes = ["## El equipo del usuario (datos leídos ahora mismo)",
              f"Fecha y hora: {dia} {ahora.strftime('%d/%m/%Y %H:%M')}"]
    for f in (_usuario, _sistema, _hardware, lambda: _software(instalados), _ia):
        try:
            partes += f()
        except Exception:  # noqa: BLE001  un dato que falle no debe dejar a Axo sin el resto
            continue
    at = _atajos()
    if at:
        partes += ["", "## Atajos de teclado activos ahora en KDE (pueden cambiarse en Preferencias del "
                       "sistema → Teclado → Atajos de teclado)"] + at
    texto = "\n".join(p if p.startswith("#") or not p else f"- {p}" for p in partes)
    m = manual(instalados)
    return texto + ("\n\n" + m if m else "")


if __name__ == "__main__":
    print(contexto())
