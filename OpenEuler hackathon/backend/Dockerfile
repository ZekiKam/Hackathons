# Didn't manage to use docker; run front and back-end separately!

FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
VOLUME ["/data"]
COPY metrics.py ws_app.py ./
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "metrics.py"]
