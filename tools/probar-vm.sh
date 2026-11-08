#!/usr/bin/env bash
# =============================================================================
#  AxolOS · probar-vm.sh   Prueba la ISO en una máquina virtual (QEMU + KVM, UEFI)
#
#    tools/probar-vm.sh            arranca la ISO para instalar (disco virtual de 60 GB)
#    tools/probar-vm.sh sistema    arranca el sistema ya instalado, sin la ISO
#    tools/probar-vm.sh nueva      borra el disco virtual y empieza de cero
#    tools/probar-vm.sh sinred     como instalar, pero sin red (prueba la instalación sin conexión)
#    tools/probar-vm.sh nueva sinred   las dos cosas: disco limpio y sin red
#
#  Necesita:  sudo pacman -S --needed qemu-desktop edk2-ovmf
#  Todo queda en build/vm/ (el disco crece solo según se usa, unos 15 GB tras instalar).
#  Para soltar el ratón de la ventana: Ctrl+Alt+G.
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VM="$ROOT/build/vm"
DISCO="$VM/axolos.qcow2"
VARS="$VM/uefi-vars.fd"
FW=/usr/share/edk2/x64
say() { printf '\e[1;35m==>\e[0m %s\n' "$*"; }
die() { printf '\e[1;31m!!\e[0m %s\n' "$*"; exit 1; }

command -v qemu-system-x86_64 >/dev/null || die "Falta QEMU:  sudo pacman -S --needed qemu-desktop edk2-ovmf"
[[ -f $FW/OVMF_CODE.4m.fd && -f $FW/OVMF_VARS.4m.fd ]] || die "Falta el firmware UEFI:  sudo pacman -S --needed edk2-ovmf"
[[ -r /dev/kvm && -w /dev/kvm ]] || die "No tengo acceso a /dev/kvm (activa la virtualización en la BIOS)"

modo=${1:-instalar}
case $modo in
  instalar|sistema) ;;
  sinred) ;;
  nueva)
    if [[ -e $DISCO ]]; then
      mkdir -p "$HOME/.axolos-limpieza"
      mv "$DISCO" "$HOME/.axolos-limpieza/axolos-vm-$(date +%Y%m%d-%H%M%S).qcow2"
      say "Disco anterior movido a ~/.axolos-limpieza (bórralo cuando quieras: ocupa espacio)"
    fi
    rm -f "$VARS"; modo=instalar; [[ ${2:-} == sinred ]] && modo=sinred ;;
  *) die "uso: $0 [instalar|sistema|nueva|sinred]" ;;
esac

mkdir -p "$VM"
[[ -f $DISCO ]] || { say "Creando disco virtual de 60 GB"; qemu-img create -q -f qcow2 "$DISCO" 60G; }
[[ -f $VARS ]]  || cp "$FW/OVMF_VARS.4m.fd" "$VARS"     # la NVRAM de la VM (entradas de arranque UEFI)

# Memoria y procesadores: la mitad del equipo, con tope razonable
ram_gb=$(( $(awk '/MemTotal/ {print int($2/1048576)}' /proc/meminfo) / 2 )); (( ram_gb > 8 )) && ram_gb=8; (( ram_gb < 4 )) && ram_gb=4
cpus=$(( $(nproc) / 2 )); (( cpus > 8 )) && cpus=8; (( cpus < 2 )) && cpus=2

args=(
  -name "AxolOS (prueba)"
  -machine q35,accel=kvm -cpu host -smp "$cpus" -m "${ram_gb}G"
  -drive if=pflash,format=raw,readonly=on,file="$FW/OVMF_CODE.4m.fd"
  -drive if=pflash,format=raw,file="$VARS"
  # Disco primero y la ISO después, como un PC con el USB puesto: con el disco vacío arranca la ISO;
  # tras instalar, «Reiniciar ahora» entra en el sistema instalado
  -drive file="$DISCO",if=none,id=disco,cache=writeback,discard=unmap -device virtio-blk-pci,drive=disco,bootindex=0
  -nic user,model=virtio-net-pci            # internet: el instalador de CachyOS instala online
  -device virtio-tablet-pci -device virtio-keyboard-pci
  -audiodev pipewire,id=snd -device ich9-intel-hda -device hda-duplex,audiodev=snd
  -device virtio-rng-pci
)
# Gráficos con aceleración 3D (Plasma va fluido); si la GPU no lo permite, sin ella
if qemu-system-x86_64 -device help 2>/dev/null | grep -q '"virtio-vga-gl"'; then
  args+=(-device virtio-vga-gl -display gtk,gl=on,zoom-to-fit=on)
else
  args+=(-device virtio-vga -display gtk,zoom-to-fit=on)
fi

if [[ $modo == sinred ]]; then
  for i in "${!args[@]}"; do [[ ${args[$i]} == user,model=virtio-net-pci ]] && args[$i]=none; done
  modo=instalar
  say "Sin red: el lanzador ofrecerá «Instalar sin conexión»"
fi
if [[ $modo == instalar ]]; then
  ISO=$(ls -1t "$ROOT"/out/*.iso 2>/dev/null | head -1) || true
  [[ -n $ISO ]] || die "No hay ISO en out/: constrúyela con ./build-iso.sh"
  if [[ -f $ISO.sig ]] && ! gpg --verify "$ISO.sig" "$ISO" >/dev/null 2>&1; then die "La firma de $(basename "$ISO") no es válida"; fi
  args+=(-drive file="$ISO",media=cdrom,readonly=on,if=none,id=iso -device ide-cd,drive=iso,bootindex=1)
  say "Arrancando $(basename "$ISO") · ${ram_gb} GB de RAM · ${cpus} núcleos"
  cat <<'EOF'
   Qué comprobar:
     1. En el live: escritorio AxolOS, sin la Bienvenida encima; abre el instalador.
     2. Instala con Plasma (en «Paquetes» debe aparecer axolos-desktop en vez de cachyos-kde-settings).
        Log del instalador en el live: /home/liveuser/cachy-install.log  (busca «[AxolOS]»).
     3. Al terminar, «Reiniciar ahora» arranca ya el sistema instalado (la ISO sigue puesta, como un USB).
        Sin la ISO:  tools/probar-vm.sh sistema
EOF
else
  say "Arrancando el sistema instalado · ${ram_gb} GB de RAM · ${cpus} núcleos"
  cat <<'EOF'
   Qué comprobar en el sistema instalado:
     · pantalla de arranque y entrada AxolOS, aparece la Bienvenida
     · en una terminal:  fastfetch  ·  cat /etc/os-release  ·  pacman -Sl axolos | head
     · sudo pacman -Syu  (las actualizaciones de AxolOS llegan del repositorio de GitHub)
EOF
fi
exec qemu-system-x86_64 "${args[@]}"
