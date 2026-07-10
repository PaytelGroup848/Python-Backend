FROM python:3.11-slim

WORKDIR /app

# -----------------------------
# SYSTEM DEPENDENCIES
# -----------------------------

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libxcb1 \
    binutils \
    pax-utils \
    patchelf \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# PYTHON DEPENDENCIES
# -----------------------------

COPY requirements.txt .

ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
ARG TORCH_VERSION=2.5.1
ARG TORCHVISION_VERSION=0.20.1
ARG TORCHAUDIO_VERSION=2.5.1

RUN pip install \
    --upgrade \
    pip \
    setuptools \
    wheel && \
    pip install \
    --no-cache-dir \
    --index-url "${TORCH_INDEX_URL}" \
    "torch==${TORCH_VERSION}" \
    "torchvision==${TORCHVISION_VERSION}" \
    "torchaudio==${TORCHAUDIO_VERSION}" && \
    pip install \
    --prefer-binary \
    --retries 30 \
    --timeout 300 \
    --no-cache-dir \
    -r requirements.txt

RUN find \
    /usr/local/lib/python3.11/site-packages/ \
    -name "*.so*" \
    -exec patchelf --clear-execstack {} \; \
    || true

# -----------------------------
# APP SOURCE
# -----------------------------

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port","8000"]