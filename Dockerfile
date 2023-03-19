FROM python:3-alpine
RUN apk add --virtual .build-dependencies \
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre-dev
RUN apk add --no-cache pcre
WORKDIR /app
COPY ./server /app
COPY ./server/templates /app/templates
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apk del .build-dependencies && rm -rf /var/cache/apk/*
ENV FLASK_DEBUG=1
EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/wsgi.ini"]