#!/bin/bash

set -e

INSTALL_DIR="$HOME/.local/bin"
SHARE_DIR="$HOME/.local/share/compress-all"
SCRIPT_NAME="compress-all"

install_compress_all() {
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$SHARE_DIR"
    
    cp -r "$(dirname "${BASH_SOURCE[0]}")/src" "$SHARE_DIR/"
    
    python3 -m venv "$SHARE_DIR/venv"
    "$SHARE_DIR/venv/bin/pip" install brotli
    
    cat > "$INSTALL_DIR/$SCRIPT_NAME" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../share/compress-all" && pwd)"
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/src/main.py" "$@"
EOF
    
    chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    
    echo "Installed to $INSTALL_DIR/$SCRIPT_NAME"
    echo ""
    echo "Make sure $INSTALL_DIR is in your PATH."
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
}

update_compress_all() {
    if [ -d "$SHARE_DIR" ]; then
        rm -rf "$SHARE_DIR/src"
        cp -r "$(dirname "${BASH_SOURCE[0]}")/src" "$SHARE_DIR/"
        
        if [ -d "$SHARE_DIR/venv" ]; then
            "$SHARE_DIR/venv/bin/pip" install --upgrade brotli
        else
            python3 -m venv "$SHARE_DIR/venv"
            "$SHARE_DIR/venv/bin/pip" install brotli
        fi
        
        cat > "$INSTALL_DIR/$SCRIPT_NAME" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../share/compress-all" && pwd)"
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/src/main.py" "$@"
EOF
        chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
        
        echo "Updated compress-all successfully"
    else
        echo "compress-all is not installed. Installing..."
        install_compress_all
    fi
}

if [ -f "$SHARE_DIR/src/main.py" ]; then
    update_compress_all
else
    install_compress_all
fi
