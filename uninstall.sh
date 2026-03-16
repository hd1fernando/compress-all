#!/bin/bash

set -e

INSTALL_DIR="$HOME/.local/bin"
SHARE_DIR="$HOME/.local/share/compress-all"
SCRIPT_NAME="compress-all"

uninstall_compress_all() {
    if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
        rm -f "$INSTALL_DIR/$SCRIPT_NAME"
        echo "Removed $INSTALL_DIR/$SCRIPT_NAME"
    fi
    
    if [ -d "$SHARE_DIR" ]; then
        rm -rf "$SHARE_DIR"
        echo "Removed $SHARE_DIR"
    fi
    
    echo ""
    echo "compress-all has been uninstalled."
    echo "If you added PATH manually, remove the line from your ~/.bashrc or ~/.zshrc"
}

if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ] || [ -d "$SHARE_DIR" ]; then
    uninstall_compress_all
else
    echo "compress-all is not installed."
fi
