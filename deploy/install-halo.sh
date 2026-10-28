#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/2231499412/acg-resource-site.git}"
REPO_ROOT="${REPO_ROOT:-/opt/acg-resource-site/repo}"
HALO_ROOT="${HALO_ROOT:-/opt/halo}"
DATA_ROOT="${DATA_ROOT:-/opt/halo-data}"
HALO_VERSION="${HALO_VERSION:-2.27.1}"
HALO_DB_HOST="${HALO_DB_HOST:-127.0.0.1}"
HALO_DB_PORT="${HALO_DB_PORT:-3306}"
HALO_DB_NAME="${HALO_DB_NAME:-halo_resource}"
HALO_DB_USER="${HALO_DB_USER:-halo_resource}"
HALO_EXTERNAL_URL="${HALO_EXTERNAL_URL:?Set HALO_EXTERNAL_URL, for example https://resource.example.com}"
HALO_DB_PASSWORD="${HALO_DB_PASSWORD:?Set HALO_DB_PASSWORD before running this script}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root or with sudo."
  exit 1
fi

id halo >/dev/null 2>&1 || useradd --system --home-dir "$HALO_ROOT" --shell /usr/sbin/nologin halo
mkdir -p "$(dirname "$REPO_ROOT")" "$HALO_ROOT" "$DATA_ROOT/plugins" /etc/halo

if [ -d "$REPO_ROOT/.git" ]; then
  git -C "$REPO_ROOT" pull --ff-only
else
  git clone "$REPO_URL" "$REPO_ROOT"
fi

if [ ! -f "$HALO_ROOT/halo-${HALO_VERSION}.jar" ]; then
  curl -fL --retry 3 -o "$HALO_ROOT/halo-${HALO_VERSION}.jar" \
    "https://github.com/halo-dev/halo/releases/download/v${HALO_VERSION}/halo-${HALO_VERSION}.jar"
fi

cat > "$HALO_ROOT/application.yaml" <<'YAML'
server:
  port: 8090
spring:
  r2dbc:
    url: r2dbc:pool:mysql://${HALO_DB_HOST}:${HALO_DB_PORT}/${HALO_DB_NAME}
    username: ${HALO_DB_USER}
    password: ${HALO_DB_PASSWORD}
  sql:
    init:
      mode: always
      platform: mysql
halo:
  work-dir: ${DATA_ROOT}
  external-url: ${HALO_EXTERNAL_URL}
YAML

cat > /etc/halo/halo.env <<EOF
HALO_DB_HOST=$HALO_DB_HOST
HALO_DB_PORT=$HALO_DB_PORT
HALO_DB_NAME=$HALO_DB_NAME
HALO_DB_USER=$HALO_DB_USER
HALO_DB_PASSWORD=$HALO_DB_PASSWORD
DATA_ROOT=$DATA_ROOT
HALO_EXTERNAL_URL=$HALO_EXTERNAL_URL
EOF
chmod 600 /etc/halo/halo.env

# This stages the plugin. A new Halo installation must install it once from the Console.
cp "$REPO_ROOT/deploy/plugins/PluginImgBedTelegram-1.0.0.jar" "$DATA_ROOT/plugins/PluginImgBedTelegram-1.0.0.jar"
chown -R halo:halo "$HALO_ROOT" "$DATA_ROOT"

cat > /etc/systemd/system/halo.service <<EOF
[Unit]
Description=Halo resource site
After=network.target mysql.service

[Service]
User=halo
WorkingDirectory=$HALO_ROOT
EnvironmentFile=/etc/halo/halo.env
ExecStart=/usr/bin/java -Dfile.encoding=UTF-8 -server -Xms256m -Xmx512m -jar $HALO_ROOT/halo-${HALO_VERSION}.jar --spring.config.additional-location=optional:file:$HALO_ROOT/
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now halo
systemctl --no-pager --full status halo
