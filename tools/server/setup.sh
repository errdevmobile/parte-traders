#!/usr/bin/env bash
# Instala en un servidor Ubuntu (Google Cloud e2-micro gratuito, Oracle, etc.) todo lo
# necesario para enviar «El Parte de las 7» al grupo de WhatsApp sin depender
# de ningún ordenador personal.
#
# Uso (en el servidor, como el usuario normal, NO como root):
#   curl -fsSL https://raw.githubusercontent.com/errdevmobile/parte-traders/main/tools/server/setup.sh -o setup.sh
#   bash setup.sh
set -euo pipefail

RAW="https://raw.githubusercontent.com/errdevmobile/parte-traders/main/tools/server"
APP="$HOME/mcp-whatsapp"
STORE="$HOME/wa-store"
PARTE="$HOME/parte"

echo "==> 1/6 Paquetes del sistema y zona horaria"
sudo apt-get update -y
sudo apt-get install -y git make curl ca-certificates python3 tzdata build-essential
sudo timedatectl set-timezone Europe/Madrid || true

# Máquinas pequeñas (1 GB de RAM, como la gratuita de Google Cloud): añadir
# 2 GB de memoria de intercambio para que la compilación no se quede sin memoria.
if [ "$(awk '/MemTotal/ {print $2}' /proc/meminfo)" -lt 2000000 ] && ! swapon --show | grep -q /swapfile; then
  echo "==> Memoria pequeña: creando 2 GB de swap"
  sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

echo "==> 2/6 Go (versión estable más reciente)"
GOVER="$(curl -fsSL 'https://go.dev/VERSION?m=text' | head -1)"
ARCH="$(dpkg --print-architecture)"   # arm64 o amd64
if ! /usr/local/go/bin/go version 2>/dev/null | grep -q "$GOVER"; then
  curl -fsSL "https://go.dev/dl/${GOVER}.linux-${ARCH}.tar.gz" -o /tmp/go.tgz
  sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf /tmp/go.tgz
fi
export PATH="/usr/local/go/bin:$PATH"
go version

echo "==> 3/6 Servicio de WhatsApp (mcp-whatsapp)"
if [ -d "$APP/.git" ]; then git -C "$APP" pull --ff-only; else git clone https://github.com/Sealjay/mcp-whatsapp.git "$APP"; fi
( cd "$APP" && CGO_ENABLED=1 GOTOOLCHAIN=auto make build )   # SQLite necesita cgo (compilador C)
mkdir -p "$STORE/uploads"

echo "==> 4/6 Script del parte"
mkdir -p "$PARTE"
curl -fsSL "$RAW/parte_send.py" -o "$PARTE/parte_send.py"
if [ ! -f "$PARTE/parte.env" ]; then
  read -rp "ID del grupo de WhatsApp (termina en @g.us): " GROUP_JID
  read -rp "Tu número para avisos de error (con prefijo, sin +, ej. 34600111222): " OWNER_PHONE
  cat > "$PARTE/parte.env" <<EOF
GROUP_JID=$GROUP_JID
OWNER_PHONE=$OWNER_PHONE
PAGE_URL=https://errdevmobile.github.io/parte-traders/
EOF
fi

echo "==> 5/6 Vincular WhatsApp"
if [ ! -f "$STORE/.paired" ]; then
  systemctl --user stop whatsapp-mcp 2>/dev/null || true
  echo "Se mostrará un código QR. En el móvil: WhatsApp > Ajustes > Dispositivos vinculados > Vincular dispositivo."
  if "$APP/bin/whatsapp-mcp" -store "$STORE" login; then
    touch "$STORE/.paired"
  else
    echo "!! No se ha podido vincular WhatsApp. Revisa el error de arriba y vuelve a ejecutar: bash setup.sh"
    exit 1
  fi
fi

echo "==> 6/6 Servicios automáticos (systemd)"
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/whatsapp-mcp.service" <<EOF
[Unit]
Description=whatsapp-mcp (servicio de WhatsApp)
After=network-online.target

[Service]
Type=exec
ExecStart=$APP/bin/whatsapp-mcp -store $STORE serve
Environment=WHATSAPP_MCP_ADDR=127.0.0.1:8765
Environment=WHATSAPP_MCP_MEDIA_ROOT=$STORE/uploads
Restart=always
RestartSec=10s

[Install]
WantedBy=default.target
EOF
cat > "$HOME/.config/systemd/user/parte.service" <<EOF
[Unit]
Description=Enviar El Parte de las 7 al grupo
After=whatsapp-mcp.service

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 -I $PARTE/parte_send.py --env $PARTE/parte.env
EOF
cat > "$HOME/.config/systemd/user/parte.timer" <<EOF
[Unit]
Description=El Parte de las 7, de lunes a viernes a las 7:00 (Madrid)

[Timer]
OnCalendar=Mon..Fri *-*-* 07:00:00 Europe/Madrid
Persistent=false

[Install]
WantedBy=timers.target
EOF
sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable whatsapp-mcp.service && systemctl --user restart whatsapp-mcp.service
systemctl --user enable --now parte.timer

echo
echo "Listo. Comprobaciones útiles:"
echo "  systemctl --user status whatsapp-mcp     # el servicio de WhatsApp"
echo "  systemctl --user list-timers parte.timer  # próxima ejecución"
echo "  python3 $PARTE/parte_send.py --dry-run --any-date   # ver el mensaje sin enviarlo"
echo "  python3 $PARTE/parte_send.py --any-date --to <tu número>   # prueba real a ti mismo"
echo "  journalctl --user -u parte.service        # registro de envíos"
