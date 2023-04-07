FROM python:3.9-slim

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r ./requirements.txt --no-cache-dir

COPY . .

# WORKDIR source

# CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

# RUN chmod a+x docker/*.sh
#CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000