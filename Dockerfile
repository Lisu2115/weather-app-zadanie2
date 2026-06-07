# syntax=docker/dockerfile:1
# ETAP 1: Budowanie (builder)
FROM python:3.11-alpine AS builder

LABEL org.opencontainers.image.authors="Mikolaj Lis"

WORKDIR /app

COPY requirements.txt .

# Aktualizacja podstawowych narzędzi Pythona przed instalacją Twoich zależności
RUN pip install --upgrade pip setuptools wheel

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-cache-dir -r requirements.txt

# ETAP 2: Uruchomienie (Finalny obraz)
FROM python:3.11-alpine

WORKDIR /app

# Aktualizacja podstawowych narzędzi Pythona w docelowym obrazie, aby załatać podatności CVE wyłapane przez Trivy
RUN pip install --upgrade pip setuptools wheel

COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5000/ || exit 1

# Start aplikacji
CMD ["python", "app.py"]
