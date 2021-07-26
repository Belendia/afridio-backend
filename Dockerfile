FROM python:3.9-alpine
LABEL maintainer="Belendia Serda"

ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk update

RUN apk add --update --no-cache --virtual .tmp-build-deps libffi-dev \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

RUN apk del musl-dev zlib zlib-dev

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D webuser
RUN chown -R webuser:webuser /vol/
RUN chmod -R 755 /vol/web
USER webuser
