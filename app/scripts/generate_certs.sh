#!/bin/bash
# Generate self-signed TLS certificates for local development.
# Creates certificate and key files in /etc/wfs/ssl/ directory.

set -e

CERT_DIR="/etc/wfs/ssl/certs"
KEY_DIR="/etc/wfs/ssl/private"
CERT_FILE="$CERT_DIR/server.crt"
KEY_FILE="$KEY_DIR/server.key"

# Create directories if they don't exist
mkdir -p "$CERT_DIR"
mkdir -p "$KEY_DIR"

# Check if cert and key already exist
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "TLS certificates already exist at $CERT_FILE and $KEY_FILE"
    exit 0
fi

# Generate self-signed certificate and key
# Valid for 365 days
# CN (Common Name) set to localhost for local development
openssl req -x509 -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 365 \
    -nodes \
    -subj "/CN=localhost/O=Weather Forecast Service/C=US" \
    2>/dev/null || {
    echo "Error: Failed to generate TLS certificates"
    exit 1
}

# Verify certificate was created
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Error: Certificate generation failed - files not created"
    exit 1
fi

echo "TLS certificates generated successfully"
echo "  Certificate: $CERT_FILE"
echo "  Key: $KEY_FILE"
