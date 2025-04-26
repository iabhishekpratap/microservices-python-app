FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev python3-dev gcc \
    && pip install --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement requirements.txt

COPY . /app

EXPOSE 8080

CMD ["python", "server.py"]
