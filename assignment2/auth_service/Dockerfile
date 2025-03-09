FROM python:3.10-slim

WORKDIR /auth_service

COPY requirements.txt /auth_service/
COPY run_auth.py /auth_service/
COPY auth_db.py /auth_service/

RUN pip install --no-cache-dir -r requirements.txt

# Install Redis and Nginx
RUN apt-get update && apt-get install -y nginx redis

# Start Redis and Nginx before running the app
CMD service nginx start && /etc/init.d/redis-server start && exec python3 run_auth.py