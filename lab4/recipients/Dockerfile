FROM python:3.12
WORKDIR /rest_api

RUN pip install sqlalchemy psycopg2-binary "fastapi["all"]" pyjwt

COPY . /rest_api

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]