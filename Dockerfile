FROM python:3.9-alpine
MAINTAINER Belendia Abdissa

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev alpine-sdk openssl-dev libffi-dev \
      linux-headers postgresql-dev musl-dev zlib zlib-dev cargo

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
RUN apk add  --no-cache ffmpeg

# BENTO4 INSTALLATION
ENV BENTO4_VERSION 1-6-0-637
ENV BENTO4_INSTALL_DIR=/opt/bento4
ENV PATH=/opt/bento4/bin:${PATH}

# Install dependencies.
RUN apk update \
  && apk add --no-cache \
  ca-certificates bash wget libgcc make g++ tar

# Fetch source.
RUN cd /tmp/ \
  && wget -O Bento4-SRC-${BENTO4_VERSION}.zip http://zebulon.bok.net/Bento4/source/Bento4-SRC-${BENTO4_VERSION}.zip \
  && mkdir Bento4-SRC-${BENTO4_VERSION} && unzip -d Bento4-SRC-${BENTO4_VERSION} Bento4-SRC-${BENTO4_VERSION}.zip \
  && rm Bento4-SRC-${BENTO4_VERSION}.zip

# Create installation directories.
RUN mkdir -p \
  ${BENTO4_INSTALL_DIR}/bin \
  ${BENTO4_INSTALL_DIR}/scripts \
  ${BENTO4_INSTALL_DIR}/include

# Build.
RUN cd /tmp/Bento4-SRC-${BENTO4_VERSION}/Build/Targets/x86-unknown-linux \
  && make AP4_BUILD_CONFIG=Release

# Install.
RUN cd /tmp \
  && cp -r Bento4-SRC-${BENTO4_VERSION}/Build/Targets/x86-unknown-linux/Release/. ${BENTO4_INSTALL_DIR}/bin \
  && cp -r Bento4-SRC-${BENTO4_VERSION}/Source/Python/utils/. ${BENTO4_INSTALL_DIR}/utils \
  && cp -r Bento4-SRC-${BENTO4_VERSION}/Source/Python/wrappers/. ${BENTO4_INSTALL_DIR}/bin \
  && cp -r Bento4-SRC-${BENTO4_VERSION}/Source/C++/**/*.h . ${BENTO4_INSTALL_DIR}/include

# Cleanup.
RUN rm -rf /var/cache/apk/* /tmp/*
# END OF BENTO4 INSTALLATION

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D webuser
RUN chown -R webuser:webuser /vol/
RUN chmod -R 755 /vol/web
USER webuser

