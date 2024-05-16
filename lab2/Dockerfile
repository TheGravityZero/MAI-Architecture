FROM python:3.12
WORKDIR /lab2

COPY ./ /lab2
RUN pip install -r /lab2/requirements.txt

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]