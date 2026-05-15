FROM python:3.11-slim

WORKDIR /app

# -----------------------------
# SYSTEM DEPENDENCIES
# -----------------------------

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libxcb1 \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# PYTHON DEPENDENCIES
# -----------------------------

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --default-timeout=1000 -r requirements.txt

# -----------------------------
# APP SOURCE
# -----------------------------

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]