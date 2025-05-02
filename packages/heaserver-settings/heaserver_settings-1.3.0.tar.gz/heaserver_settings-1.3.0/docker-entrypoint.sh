#!/bin/sh
set -e

cat > .hea-config.cfg <<EOF
[DEFAULT]
Registry=${HEASERVER_REGISTRY_URL:-http://heaserver-registry:8080}

[MongoDB]
ConnectionString=mongodb://${MONGO_HEA_USERNAME}:${MONGO_HEA_PASSWORD}@${MONGO_HOSTNAME}:27017/${MONGO_HEA_DATABASE}?authSource=${MONGO_HEA_AUTH_SOURCE:-admin}
EOF

exec heaserver-settings -f .hea-config.cfg -b ${HEASERVER_SETTINGS_URL:-http://heaserver-settings:8080}


