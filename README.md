# go-exec

go-exec is a client/server utility written in Go and Python to executing commands remotely.

## The goal

I have different servers with different applications and sometimes I needed to run a certain command on several servers, and I had to connect one by one to run the command and analyze the output.

The idea of go-exec is to centralize these commands in an API that the client consults every XX seconds.
Commands are protected with MD5 to ensure that the content received by the client is the same as entered into the database, and an additional word is also inserted into MD5 to ensure that the commands are not entered directly into the database by an attacker.

__This project must be executed in a controlled and restricted environment with authentication and firewall rules. Anyone who has access to this environment will be able to execute commands on the registered servers.__

__It is still in the POC (proof of concept) phase, it needs to create frontend with authentication, etc.__

## Server

Server is written in python using the Flask library to create the API with the routes providing the commands.

The files needed to run the server and the MySQL database are in the "server" directory.

Server has a configuration flag to allow clients to register, if you distribute the application via rpm or deb it will facilitate the client to register.

```python
auto_discovery_enabled = True
```

### Running a server (local with DEBUG enabled)

```bash
pip install -r requirements.txt
```

The command below starts the server in DEBUG mode, for production use I recommend using uwsgi with Nginx and SSL certificate.

```bash
python3 server.py
```

### Add server and commands

These are the routes in the flask for you to list and add servers/commands in your browser (without authentication):

[http://127.0.0.1:5000/server/add](http://127.0.0.1:5000/server/add)

[http://127.0.0.1:5000/server/list](http://127.0.0.1:5000/server/list)

[http://127.0.0.1:5000/command/add](http://127.0.0.1:5000/command/add)

[http://127.0.0.1:5000/command/list](http://127.0.0.1:5000/command/list)


## Client

The client was written in Go and some settings are compiled into the file for security.
As the goal of this project is to execute commands remotely, it is safer to leave the parameters fixed inside the compiled application.

```go
var debug bool = true
var loop_sec time.Duration = 10
var api_url string = "http://127.0.0.1:5000/api/v1.0/"
var md5_shuffles string = "shablau123"
```

### Running a client
```bash
go run go-exec.go
```

### Building a client
```bash
go build .
```

On its first run, if the client does not find the go-exec.json file, it automatically creates it with a random auth key. Very useful with the automatic registration function mentioned above.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to make tests as needed.

## License

[MIT](https://choosealicense.com/licenses/mit/)
