FROM python:3.12
WORKDIR /deliveries

RUN pip install fastapi[all] pymongo

COPY . /deliveries

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]