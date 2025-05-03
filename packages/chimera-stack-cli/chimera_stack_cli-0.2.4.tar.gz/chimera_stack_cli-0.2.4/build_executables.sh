#!/bin/bash
# Build executables for macOS

# Ensure PyInstaller is installed
pip install pyinstaller

# Clean previous PyInstaller builds without removing PyPI packages
if [ -d "build" ]; then
  rm -rf build
fi

if [ -d "dist" ]; then
  # Remove only executable files, not wheel (.whl) or source (.tar.gz) packages
  find dist -type f -not -name "*.whl" -not -name "*.tar.gz" -delete
fi

# Build for macOS
echo "Building executable for macOS"
pyinstaller chimera-stack-cli.spec

# Create release directory if it doesn't exist
mkdir -p releases
cp dist/chimera-stack-cli releases/chimera-stack-cli-macos

# Make executable
chmod +x releases/chimera-stack-cli-macos

# Generate checksum and append to SHA256SUMS.txt
cd releases || exit 1
# Remove any existing entry for this file
if [ -f SHA256SUMS.txt ]; then
  grep -v "chimera-stack-cli-macos$" SHA256SUMS.txt > SHA256SUMS.txt.new
  mv SHA256SUMS.txt.new SHA256SUMS.txt
fi
shasum -a 256 chimera-stack-cli-macos >> SHA256SUMS.txt

echo "Build complete! Executable is in the 'releases' directory."
