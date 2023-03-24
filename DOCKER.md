## Running app, mysql and nginx via docker-compose:

## build images

```bash
docker compose build --no-cache
```

## start containers

```bash
docker compose -f "docker-compose.yaml" up -d --build
``` 

## stop containers

```bash
docker compose -f "docker-compose.yaml" down
```

### if you get errors when docker-compose downloading images from docker.io, download manually:

```bash
docker image pull nginx:1.22
docker image pull python:3-alpine
docker image pull mysql:8.0.32
```

## Running only server app in Docker

First build a image from Dockerfile:

```bash
docker build -t flask-uwsgi . --no-cache --force-rm
```

Running  a container "go-exec-server" with expose port 5000:

```bash
docker run --rm -d --name go-exec-server -p 5000:5000 flask-uwsgi
```

## Debug

If you want to debug server app on container, there are two ways:

### running app in interactive mode:

```bash
docker run --rm --name go-exec-server -p 5000:5000 -it flask-uwsgi sh
```

```bash
/app # python3 server.py
```

### inspect logs in container:

```bash
docker container logs go-exec-server
```


