FROM debian:bookworm-slim

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/mumble-rest

# Install system dependencies, ca-certificates, curl, and gpg for modern Debian keyring management
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    python3 \
    python3-pip \
    python3-venv \
    libevent-dev \
    software-properties-common \
    build-essential \
    libssl-dev \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://zeroc.com/download/GPG-KEY-zeroc-release | gpg --dearmor -o /etc/apt/keyrings/zeroc.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/zeroc.gpg] https://zeroc.com/download/ice/3.7/debian12 stable main" > /etc/apt/sources.list.d/zeroc-ice.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       python3-zeroc-ice \
       zeroc-ice-compilers \
    && apt-get autoremove -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements inside a venv with system-site-packages to access python3-zeroc-ice
COPY requirements.txt /opt/mumble-rest/requirements.txt
RUN python3 -m venv --system-site-packages /opt/mumble-rest/venv && \
    /opt/mumble-rest/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /opt/mumble-rest

# Expose API port
EXPOSE 2332

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:2332/healthz || exit 1

CMD ["/opt/mumble-rest/venv/bin/uvicorn", "main:mumble_rest", "--host", "0.0.0.0", "--port", "2332"]
