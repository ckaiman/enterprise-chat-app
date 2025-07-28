#!/bin/bash
# This script generates a locally-trusted SSL certificate for localhost using mkcert.

# Exit immediately if a command exits with a non-zero status.
set -e

# Add common Homebrew binary paths to the script's PATH to find mkcert
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Directory to store certificates, relative to the script's location
CERT_DIR="$(dirname "$0")/certs"
KEY_FILE="$CERT_DIR/localhost.key"
CERT_FILE="$CERT_DIR/localhost.crt"

# Function to provide installation instructions for mkcert
prompt_for_mkcert_installation() {
    echo "Error: mkcert is not installed, but it's required to create a local SSL certificate for Nginx."
    echo "See: https://github.com/FiloSottile/mkcert#installation"
    echo ""

    # Detect OS and provide specific instructions
    os_name=$(uname -s)
    case "$os_name" in
        Darwin*)
            echo "It looks like you are on macOS. You can install mkcert using Homebrew:"
            echo "  brew install mkcert"
            echo "After installing, please re-run './rebuild.sh'."
            ;;
        Linux*)
            echo "It looks like you are on Linux. Please follow the installation instructions at the link above."
            echo "A common method is using Homebrew: https://brew.sh/"
            ;;
        *)
            echo "Please install mkcert for your operating system ($os_name) and then re-run './rebuild.sh'."
            ;;
    esac
    exit 1
}

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    prompt_for_mkcert_installation
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