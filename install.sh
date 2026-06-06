#!/bin/bash
# FileStation One-Click Installer for Debian/Ubuntu

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}       FileStation Installer           ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (use sudo)."
  exit 1
fi

# Ask for configuration
read -p "Enter a name for this instance/service [fileserver]: " FS_SVC
FS_SVC=${FS_SVC:-fileserver}

read -p "Enter your admin username [admin]: " FS_USER
FS_USER=${FS_USER:-admin}

read -p "Enter your admin password [secret]: " FS_PASS
FS_PASS=${FS_PASS:-secret}

read -p "Enter the base directory to serve [/home]: " FS_DIR
FS_DIR=${FS_DIR:-/home}

read -p "Enter the HTTP port [80]: " FS_PORT
FS_PORT=${FS_PORT:-80}

read -p "Enter the HTTPS port [443]: " FS_HTTPS_PORT
FS_HTTPS_PORT=${FS_HTTPS_PORT:-443}

read -p "Do you want to enable public mode? (y/n) [n]: " FS_PUBLIC
if [[ "$FS_PUBLIC" =~ ^[Yy]$ ]]; then
    PUB_FLAG="--public"
else
    PUB_FLAG=""
fi

read -p "Enter your domain for HTTPS (leave blank for HTTP only): " FS_DOMAIN

echo -e "\n${GREEN}Updating system and installing dependencies...${NC}"
apt update
apt install -y python3 certbot

# Download server.py if not in current directory
if [ ! -f "/root/server.py" ]; then
    echo -e "\n${GREEN}Downloading FileStation...${NC}"
    if [ -f "server.py" ]; then
        cp server.py /root/server.py
    else
        echo "Please place server.py in the same directory as this script, or in /root/server.py"
        exit 1
    fi
fi

SSL_FLAGS=""
if [ -n "$FS_DOMAIN" ]; then
    echo -e "\n${GREEN}Acquiring Let's Encrypt Certificates for $FS_DOMAIN...${NC}"
    systemctl stop nginx 2>/dev/null || true
    systemctl stop apache2 2>/dev/null || true
    
    certbot certonly --standalone -d "$FS_DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email
    
    SSL_FLAGS="--force-https --cert /etc/letsencrypt/live/$FS_DOMAIN/fullchain.pem --key /etc/letsencrypt/live/$FS_DOMAIN/privkey.pem"
fi

echo -e "\n${GREEN}Setting up Systemd Service...${NC}"
cat <<EOF > /etc/systemd/system/${FS_SVC}.service
[Unit]
Description=FileStation Server ($FS_SVC)
After=network.target

[Service]
User=root
WorkingDirectory=/root/
ExecStart=/usr/bin/python3 /root/server.py -p $FS_PORT --https-port $FS_HTTPS_PORT -d $FS_DIR -u $FS_USER --password $FS_PASS $PUB_FLAG $SSL_FLAGS
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${FS_SVC}.service
systemctl restart ${FS_SVC}.service

echo -e "\n${BLUE}=======================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
if [ -n "$FS_DOMAIN" ]; then
    echo -e "Access your server at: https://$FS_DOMAIN"
else
    echo -e "Access your server at: http://$(hostname -I | awk '{print $1}'):$FS_PORT"
fi
echo -e "Check logs with: sudo journalctl -u ${FS_SVC}.service -f"
echo -e "${BLUE}=======================================${NC}"
