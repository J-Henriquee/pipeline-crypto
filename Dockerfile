FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
COPY src/ src

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "src/extract_data.py"]