FROM python:3.13.0a4-slim

WORKDIR /api

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -p ./data/logs
COPY src/ ./src/
COPY main.py .
COPY release.txt .

EXPOSE 8000

ENTRYPOINT [ "python3", "main.py" ]