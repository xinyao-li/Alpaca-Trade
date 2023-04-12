FROM python:3.7-slim-buster

MAINTAINER li651854292@gmail.com

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY main.py /app

COPY inputs/config.py /app

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "/app/main.py"]