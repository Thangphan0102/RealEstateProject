FROM python:3.9-slim

RUN apt-get update
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY deployment/requirements.txt .
RUN pip install -r requirements.txt

COPY . /data_pipeline
WORKDIR /data_pipeline