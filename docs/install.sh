#!/usr/bin/env bash
# AuxFlow installer: installs auxflow via pipx/pip and configures PATH.
set -euo pipefail

echo "Installing AuxFlow..."

# 1. Prefer pipx if available
if command -v pipx >/dev/null 2>&1; then
  pipx install auxflow --force
  pipx ensurepath
  echo "AuxFlow installed with pipx."
  exit 0
fi

# 2. Fall back to pip with user directory
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install --user auxflow

  BIN_DIR="$(python3 -m site --user-base)/bin"

  # Add to PATH in shell profile if not already present
  add_to_profile() {
    local profile="$1"
    if [ -f "$profile" ] && ! grep -q "$BIN_DIR" "$profile"; then
      echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$profile"
      echo "Added $BIN_DIR to $profile"
    fi
  }

  add_to_profile "$HOME/.bashrc"
  add_to_profile "$HOME/.zshrc"

  echo "AuxFlow installed to $BIN_DIR."
  echo "Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
  exit 0
fi

echo "Error: Neither pipx nor python3 was found. Install Python 3.12+ first." >&2
exit 1
