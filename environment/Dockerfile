# Reproducible CPU Environment for FedLearn Artifact Evaluation
#
# Build:
#   docker build -f environment/Dockerfile -t fedlearn-artifact .
#
# Run Verification:
#   docker run --rm fedlearn-artifact make verify
#
# Run Fast Smoke Suite:
#   docker run --rm fedlearn-artifact make smoke
#
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system utilities, build tools, and protobuf compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    git \
    curl \
    build-essential \
    protobuf-compiler \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

# Install Python dependencies
COPY requirements.txt requirements.txt
COPY environment/requirements.lock environment/requirements.lock
RUN pip install -r requirements.txt

# Copy source repository
COPY . .

# Install worker package in editable mode
RUN pip install -e worker --no-deps

# Default command runs the fast smoke test suite
CMD ["make", "smoke"]
