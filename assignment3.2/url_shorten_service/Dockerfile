FROM python:3.10-slim

WORKDIR /url_shorten_service

COPY requirements.txt /url_shorten_service/
COPY run_url.py /url_shorten_service/
COPY url_db.py /url_shorten_service/
COPY services /url_shorten_service/services

RUN pip install --no-cache-dir -r requirements.txt

# Install Redis and Nginx
RUN apt-get update && apt-get install -y nginx redis

EXPOSE 8000

# Start Redis and Nginx before running the app
CMD service nginx start && /etc/init.d/redis-server start && exec python3 run_url.py