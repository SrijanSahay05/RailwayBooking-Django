FROM python:3.11.0a7-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
Copy ./requirements.txt .  
RUN pip install -r requirements.txt

COPY . .
