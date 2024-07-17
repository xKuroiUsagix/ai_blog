FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y git
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./docker/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/start-server /start-server
RUN sed -i 's/\r$//g' /start-server
RUN chmod +x /start-server

COPY ./docker/celery/worker/start-worker /start-worker
RUN sed -i 's/\r$//g' /start-worker
RUN chmod +x /start-worker

COPY ./docker/celery/beat/start-beat /start-beat
RUN sed -i 's/\r$//g' /start-beat
RUN chmod +x /start-beat

ENTRYPOINT ["/entrypoint"]
