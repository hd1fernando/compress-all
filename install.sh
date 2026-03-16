#!/bin/bash

set -e

INSTALL_DIR="$HOME/.local/bin"
SCRIPT_NAME="compress-all"
SCRIPT_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/src/main.py"

install_compress_all() {
    mkdir -p "$INSTALL_DIR"
    
    cat > "$INSTALL_DIR/$SCRIPT_NAME" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../share/compress-all" && pwd)"
python3 "$SCRIPT_DIR/src/main.py" "$@"
EOF
    
    chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    
    SHARE_DIR="$HOME/.local/share/compress-all"
    mkdir -p "$SHARE_DIR"
    cp -r "$(dirname "${BASH_SOURCE[0]}")/src" "$SHARE_DIR/"
    
    echo "Installed to $INSTALL_DIR/$SCRIPT_NAME"
    echo ""
    echo "Make sure $INSTALL_DIR is in your PATH."
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
}

update_compress_all() {
    SHARE_DIR="$HOME/.local/share/compress-all"
    if [ -d "$SHARE_DIR" ]; then
        rm -rf "$SHARE_DIR/src"
        cp -r "$(dirname "${BASH_SOURCE[0]}")/src" "$SHARE_DIR/"
        echo "Updated compress-all successfully"
    else
        echo "compress-all is not installed. Installing..."
        install_compress_all
    fi
}

if [ -f "$HOME/.local/share/compress-all/src/main.py" ]; then
    update_compress_all
else
    install_compress_all
fi
