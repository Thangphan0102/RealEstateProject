FROM python:3.9-slim as build

RUN apt-get update
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY deployment/requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/ven/bin:$PATH"

COPY . /real_estate/code/data_pipeline
WORKDIR /real_estate/code/data_pipeline