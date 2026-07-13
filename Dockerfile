# matching-container -- AWS ECS/Fargate task image.
#
# Stage 1 compiles the C++ fingerprinting engine (FFTW3 + pybind11) into a
# Python extension module. Stage 2 ships only the runtime: no compilers,
# no CMake, no headers.
#
# linux/amd64 is pinned because Fargate task definitions declare a CPU
# architecture, and a mismatched image fails at task start rather than at
# build time. Override with --platform for arm64 Fargate.

# ---------- Stage 1: build the C++ extension ----------
FROM --platform=linux/amd64 python:3.11-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        libfftw3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY fingerprinting_engine/ ./fingerprinting_engine/

# Build a wheel so stage 2 installs a self-contained artifact instead of
# copying loose .so files around. Build isolation is left on so pip resolves
# scikit-build-core/pybind11 from the engine's own [build-system] requires,
# and scikit-build-core puts pybind11's CMake dir on CMAKE_PREFIX_PATH for
# the find_package(pybind11) call in CMakeLists.txt.
RUN pip wheel --no-cache-dir --no-deps -w /wheels ./fingerprinting_engine

# ---------- Stage 2: runtime ----------
FROM --platform=linux/amd64 python:3.11-slim-bookworm AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ffmpeg for audio normalization; libfftw3-3 is the runtime half of
# libfftw3-dev, needed by the compiled extension.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libfftw3-3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

# Non-root: ECS does not enforce this, but a compromised worker with write
# access to its own code is a worse day than one without.
RUN useradd --create-home --uid 10001 matcher \
    && chown -R matcher:matcher /app
USER matcher

# No EXPOSE / healthcheck port: this task is an SQS consumer, not a server.
# ECS health is inferred from the task staying alive; the worker exits
# non-zero if it cannot reach its queue.
ENTRYPOINT ["python", "-m", "backend.services.worker"]
