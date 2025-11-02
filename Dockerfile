FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system deps if needed (e.g., for Kerberos, build tools)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     krb5-user \
#  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Ensure runtime dirs exist
RUN mkdir -p backend/uploads backend/logs

ENV FLASK_ENV=production
EXPOSE 8000

CMD ["gunicorn", "-w", "3", "-k", "gthread", "--threads", "8", "-b", "0.0.0.0:8000", "backend.wsgi:application"]






