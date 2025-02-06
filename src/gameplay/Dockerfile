FROM python:3.13.0-slim-bookworm

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py migrate

# CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "PongBackend.asgi:application"]
