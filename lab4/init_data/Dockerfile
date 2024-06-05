FROM python:3.12
WORKDIR /init

RUN pip install sqlalchemy psycopg2-binary

COPY . /init

ENTRYPOINT ["bash", "-c", "python3 main.py"]