#!/bin/bash
# This script generates a locally-trusted SSL certificate for localhost using mkcert.

# Exit immediately if a command exits with a non-zero status.
set -e

# Directory to store certificates, relative to the script's location
CERT_DIR="$(dirname "$0")/certs"
KEY_FILE="$CERT_DIR/localhost.key"
CERT_FILE="$CERT_DIR/localhost.crt"

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo "Error: mkcert is not installed. Please install it to continue."
    echo "See: https://github.com/FiloSottile/mkcert#installation"
    exit 1
fi

# Create certs directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if the certificate already exists. If so, skip generation.
# This prevents regenerating the cert on every rebuild.
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL certificate already exists. Skipping generation."
    exit 0
fi

echo "Generating locally-trusted SSL certificate for localhost using mkcert..."
echo "This will use the system-wide mkcert CA. Ensure you have run 'mkcert -install'."

# Generate the certificate for localhost.
# By not setting CAROOT, this uses the default CA that 'mkcert -install' configured.
mkcert -key-file "$KEY_FILE" -cert-file "$CERT_FILE" localhost 127.0.0.1 ::1

echo "Certificate generated successfully in $CERT_DIR"