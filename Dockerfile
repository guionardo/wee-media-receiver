FROM python:3.9-slim

WORKDIR /api

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -p ./data/logs
COPY src/ ./src/
COPY main.py .

EXPOSE 8000

ENTRYPOINT [ "python3", "main.py" ]