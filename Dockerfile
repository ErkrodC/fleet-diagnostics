FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY sample_data ./sample_data

EXPOSE 8000

CMD ["python", "-m", "src.exporter", "sample_data/telemetry.json", "--port", "8000"]
