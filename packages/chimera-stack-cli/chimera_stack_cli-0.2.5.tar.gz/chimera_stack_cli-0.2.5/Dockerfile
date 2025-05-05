FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    docker.io \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Create and set up a non-root user with specific UID/GID
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} developer && \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash developer && \
    # Add to docker group without creating it (it already exists)
    usermod -aG docker developer

# Create and configure virtual environment
ENV VIRTUAL_ENV=/home/developer/venv
RUN python -m venv $VIRTUAL_ENV && \
    chown -R developer:developer $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY --chown=developer:developer requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set up working directory
WORKDIR /app

# Ensure /app is writable by developer
RUN chown developer:developer /app

# Switch to non-root user
USER developer

# Keep container running
CMD ["/bin/sh", "-c", "while true; do sleep 1; done"]
