# Stage 1: Install Python dependencies
FROM python:3.10-slim AS builder

WORKDIR /build

COPY requirements.txt /build/

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.10-slim

WORKDIR /auth_service

# Copy the installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY run_auth.py /auth_service/
COPY auth_db.py /auth_service/

RUN apt-get update && apt-get install -y nginx redis &&    \
    # Clean up apt cache
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD service nginx start && /etc/init.d/redis-server start && exec python3 run_auth.py