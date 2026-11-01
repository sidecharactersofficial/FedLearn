# syntax=docker/dockerfile:1
# Not yet built or tested. Pin base image digests before publishing an artifact.
FROM rust:1.82 AS orchestrator
WORKDIR /src
COPY proto proto
COPY orchestrator orchestrator
RUN cargo build --release --manifest-path orchestrator/Cargo.toml

FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip r-base make ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=orchestrator /src/orchestrator/target/release/fedids-orchestrator /usr/local/bin/
COPY proto proto
COPY worker worker
COPY analysis analysis
COPY orchestrator/sweeps orchestrator/sweeps
COPY .env.example .env.example

RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir grpcio-tools \
 && /opt/venv/bin/python -m grpc_tools.protoc -I proto \
      --python_out=worker/src/fedids_worker/gen $(find proto -name '*.proto') \
 && /opt/venv/bin/pip install --no-cache-dir ./worker
# R packages: replace with `renv::restore()` once renv.lock exists.
RUN Rscript -e 'install.packages(c("arrow","dplyr","ggplot2"), repos="https://cloud.r-project.org")'

ENV PATH="/opt/venv/bin:${PATH}"
ENTRYPOINT ["fedids-orchestrator"]
