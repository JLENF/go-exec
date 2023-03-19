## Running server in Docker

First build a image from Dockerfile:

```bash
docker build -t flask-uwsgi . --no-cache --force-rm
```

Running  a container "go-exec-server" with expose port 5000:

```bash
docker run --rm -d --name go-exec-server -p 5000:5000 flask-uwsgi
```

If you want to debug python app on container, run in interactive mode:

```bash
docker run --rm --name go-exec-server -p 5000:5000 -it flask-uwsgi sh
```

```bash
/app # python3 server.py
```


