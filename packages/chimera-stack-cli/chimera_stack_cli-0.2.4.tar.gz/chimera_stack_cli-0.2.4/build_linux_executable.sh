#!/bin/bash

# Build executable for Linux

# Create releases directory if it doesn't exist
mkdir -p releases

# Build the Docker image
docker build -t chimera-build -f Dockerfile.build .

# Create a temporary container
CONTAINER_ID=$(docker create chimera-build)

# Copy the executable from the container
docker cp $CONTAINER_ID:/app/dist/chimera-stack-cli ./releases/chimera-stack-cli-linux

# Remove the temporary container
docker rm $CONTAINER_ID

# Make the Linux executable executable
chmod +x ./releases/chimera-stack-cli-linux

# Generate checksum and append to SHA256SUMS.txt
cd releases || exit 1
# Remove any existing entry for this file
if [ -f SHA256SUMS.txt ]; then
  grep -v "chimera-stack-cli-linux$" SHA256SUMS.txt > SHA256SUMS.txt.new
  mv SHA256SUMS.txt.new SHA256SUMS.txt
fi
sha256sum chimera-stack-cli-linux >> SHA256SUMS.txt

echo "Linux executable built and placed in releases/chimera-stack-cli-linux"
