#!/usr/bin/env bash
# =============================================================
# HNA Flight Monitor — Ubuntu One-Key Deploy Script
# Usage: bash deploy.sh
# Run as a non-root user with sudo privileges (e.g. deploy)
# =============================================================
set -euo pipefail

# ---------- config ----------
APP_NAME="hna-monitor"
APP_DIR="/home/${USER}/apps/${APP_NAME}"
PYTHON="python3"
NODE_MAJOR=20
# ----------------------------

info()  { echo -e "\033[32m[INFO]\033[0m  $*"; }
warn()  { echo -e "\033[33m[WARN]\033[0m  $*"; }
error() { echo -e "\033[31m[ERROR]\033[0m $*" >&2; exit 1; }

# ---- 1. system packages ----
info "Updating system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip git curl nginx

# ---- 2. Node.js (for npx / variflight-mcp) ----
if ! command -v node &>/dev/null; then
  info "Installing Node.js ${NODE_MAJOR}..."
  curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | sudo -E bash - >/dev/null
  sudo apt-get install -y -qq nodejs
else
  info "Node.js already installed: $(node -v)"
fi

# ---- 3. project directory ----
mkdir -p "${APP_DIR}"
mkdir -p "${APP_DIR}/data"

# ---- 4. virtualenv ----
if [ ! -d "${APP_DIR}/.venv" ]; then
  info "Creating virtualenv..."
  ${PYTHON} -m venv "${APP_DIR}/.venv"
fi

# ---- 5. install python deps ----
info "Installing Python dependencies..."
"${APP_DIR}/.venv/bin/pip" install -q --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -q -r "${APP_DIR}/requirements.txt"

# ---- 6. .env file ----
if [ ! -f "${APP_DIR}/.env" ]; then
  info "Creating .env from .env.example — please edit before starting!"
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
  warn ">> Edit ${APP_DIR}/.env and fill in VARIFLIGHT_API_KEY and SERVERCHAN_SENDKEY, then re-run this script or start manually."
else
  info ".env already exists, skipping copy."
fi

# ---- 7. systemd service ----
SERVICE_SRC="${APP_DIR}/systemd/hna-monitor.service"
SERVICE_DST="/etc/systemd/system/hna-monitor.service"

if [ -f "${SERVICE_SRC}" ]; then
  info "Installing systemd service..."
  # patch WorkingDirectory and ExecStart to actual paths
  sed \
    -e "s|/home/deploy/apps/hna-monitor|${APP_DIR}|g" \
    -e "s|User=deploy|User=${USER}|g" \
    -e "s|Group=deploy|Group=${USER}|g" \
    "${SERVICE_SRC}" | sudo tee "${SERVICE_DST}" >/dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable hna-monitor
  sudo systemctl restart hna-monitor
  info "Service status:"
  sudo systemctl status hna-monitor --no-pager || true
else
  warn "systemd service template not found at ${SERVICE_SRC}, skipping."
fi

# ---- 8. Nginx ----
NGINX_CONF="/etc/nginx/sites-available/${APP_NAME}"
NGINX_ENABLED="/etc/nginx/sites-enabled/${APP_NAME}"

if [ ! -f "${NGINX_CONF}" ]; then
  info "Installing Nginx config..."
  sudo cp "${APP_DIR}/systemd/nginx-${APP_NAME}.conf" "${NGINX_CONF}" 2>/dev/null || {
    warn "Nginx config template not found, generating a minimal one..."
    sudo tee "${NGINX_CONF}" >/dev/null <<NGINX
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
NGINX
  }
  sudo ln -sf "${NGINX_CONF}" "${NGINX_ENABLED}"
  sudo nginx -t && sudo systemctl reload nginx
else
  info "Nginx config already exists."
fi

# ---- 9. firewall ----
if command -v ufw &>/dev/null; then
  sudo ufw allow OpenSSH    2>/dev/null || true
  sudo ufw allow 'Nginx Full' 2>/dev/null || true
  sudo ufw --force enable   2>/dev/null || true
  info "UFW rules applied."
fi

info "----------------------------------------------"
info "Deploy complete!"
info "App dir:  ${APP_DIR}"
info "Logs:     journalctl -u ${APP_NAME} -f"
info "Restart:  sudo systemctl restart ${APP_NAME}"
info "Web:      http://$(hostname -I | awk '{print $1}')"
info "----------------------------------------------"
