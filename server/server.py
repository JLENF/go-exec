from flask import Flask, jsonify, request, abort, render_template, redirect
import hashlib
import pymysql
from datetime import datetime
import random
import string
from config import Config

app = Flask(__name__)
app.config.from_object('config.Config')

# variables
auto_discovery_enabled = True

def connect_db():
    # connect to database
    conexao = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    return conexao

def close_db(cursor,conexao):
    # close connection to database
    conexao.commit()
    cursor.close()
    conexao.close()

def check_auth_key(client_hostname,client_auth_key):
    # check if auth_key is valid
    conexao = connect_db()
    cursor = conexao.cursor()
    cursor.execute('SELECT id,auth_key FROM servers WHERE active = 1 AND deleted_at IS NULL AND hostname = %s LIMIT 1', client_hostname,)
    resultado = cursor.fetchone()
    close_db(cursor,conexao)
    if resultado is None:
        return False
    id_server = resultado[0]
    auth_key_db = resultado[1]
    if auth_key_db != client_auth_key:
        return False
    return id_server

def get_hash(input_str):
    encoded_string = input_str + 'shablau123'
    hash_object = hashlib.md5(encoded_string.encode('utf-8'))
    return hash_object.hexdigest()

def update_monitor(id_server,api_version):
    # update monitor
    conexao = connect_db()
    cursor = conexao.cursor()
    cursor.execute('UPDATE monitor SET last_seen = %s, api_version = %s WHERE id_server = %s', (datetime.now(),api_version,id_server,))
    close_db(cursor,conexao)

def auto_discovery(client_hostname,client_auth_key):
    # auto discovery
    conexao = connect_db()
    cursor = conexao.cursor()
    # ignore check if is active and if deleted_at is null - for auto discovery only new servers
    cursor.execute('SELECT id FROM servers WHERE hostname = %s AND auth_key = %s LIMIT 1', (client_hostname,client_auth_key,))
    resultado = cursor.fetchone()
    if resultado is None:
        # insert new server
        cursor.execute('INSERT INTO servers (hostname,auth_key,created_at,active,registered_by) VALUES (%s,%s,%s,%s,%s)', (client_hostname,client_auth_key,datetime.now(),1,'auto_discovery'))
        id_server = cursor.lastrowid
        cursor.execute('INSERT INTO monitor (id_server,api_version) VALUES (%s,%s)', (id_server,'v1.0'))
        close_db(cursor,conexao)
        return id_server
    else:
        close_db(cursor,conexao)
        return False
    
@app.route('/api/v1.0/list_cmd', methods=['POST'])
def api():
    # check if is active and auth_key is valid
    id_server = check_auth_key(request.form['hostname'],request.form.get('auth_key'))
    if id_server is False:
        # check if auto_discovery is enabled
        if auto_discovery_enabled:
            # if is a new server, insert it and return id_server
            id_server = auto_discovery(request.form['hostname'],request.form.get('auth_key'))
            if id_server is False:
                return abort(401)
        else:
            return abort(401)

    # update monitor with last_seen and api_version
    update_monitor(id_server,'v1.0')

    conexao = connect_db()
    cursor = conexao.cursor()    
    cursor.execute('SELECT id FROM commands WHERE id_server = %s AND downloaded_at IS NULL', id_server,)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()        
    if resultado is None:
        return abort(401)
    id_commands = []
    for row in resultado:
        # create json with id_commands
        id_commands.append({
            'id': row[0],
        })
    return jsonify(id_commands)

@app.route('/api/v1.0/get_cmd', methods=['POST'])
def get_cmd():
    # check if is active and auth_key is valid
    id_server = check_auth_key(request.form['hostname'],request.form.get('auth_key'))
    if id_server is False:
        return abort(401)

    # get command
    conexao = connect_db()
    cursor = conexao.cursor()   
    id_command = request.form['cmd_id']
    cursor.execute('SELECT id,command,md5,timeout,bash,process,relative_exec FROM commands WHERE relative_retried < relative_retry AND id = %s LIMIT 1', id_command,)
    query_cmd = cursor.fetchone()
    # if query_cmd is None, the relative_cmd is not found or the relative_cmd exitcode is not 0
    if query_cmd is not None:
        # check if relative command exists and exitcode is 0
        relative_exec = query_cmd[6]
        if relative_exec is not None:
            cursor.execute('SELECT id,exitcode,downloaded_at,executed_at FROM commands WHERE id = %s AND executed_at IS NOT NULL LIMIT 1', relative_exec,)
            query_relative = cursor.fetchone()
            if query_relative is None:
                # update retried tentatives
                cursor.execute('UPDATE commands SET relative_retried = relative_retried + 1 WHERE id = %s', id_command,)
                close_db(cursor,conexao)
                #print("Relative command not found")
                return abort(412)
            else:
                # check if downloaded_at is not null
                if query_relative[2] is None:
                    close_db(cursor,conexao)
                    #print("Relative command not executed")
                    return abort(412)
                else:
                    # check if exitcode is 0
                    #print(query_relative[1])
                    if int(query_relative[1]) != 0:
                        eror_msg = f"Relative command: {relative_exec} exitcode is not 0"
                        cursor.execute('UPDATE commands SET downloaded_at = %s, stdout = %s WHERE id = %s', (datetime.now(),eror_msg,id_command,))
                        close_db(cursor,conexao)
                        #print("Relative command exitcode is not 0")
                        return abort(412)

        # if not exists relative command
        # update command status where donloaded = 1
        cursor.execute('UPDATE commands SET downloaded_at = %s WHERE id = %s', (datetime.now(),id_command,))
        conexao.commit()
        cursor.close()
        conexao.close()
        if query_cmd is None:
            return abort(401)
        id_command = query_cmd[0]
        command = query_cmd[1]
        hash = query_cmd[2]
        timeout = query_cmd[3]
        bash = True if query_cmd[4] == 1 else False
        process = True if query_cmd[5] == 1 else False
        response_items = []
        response_items.append({
            'id': id_command,
            'comando': command,
            'hash': hash,
            'timeout': timeout,
            'bash': bash,
            'process': process,
        })
        return jsonify(response_items)
    else:
        eror_msg = "relative_retried as reached the limit of relative_retry"
        cursor.execute('UPDATE commands SET downloaded_at = %s, stdout = %s WHERE id = %s', (datetime.now(),eror_msg,id_command,))        
        close_db(cursor,conexao)
        return abort(406)
    
@app.route('/api/v1.0/cmd_result', methods=['POST'])
def result():
    # check if is active and auth_key is valid
    id_server = check_auth_key(request.form['hostname'],request.form.get('auth_key'))
    if id_server is False:
        return abort(401)

    # receive result from client
    hostname = request.form['hostname']
    cmd_id = request.form['cmd_id']
    cmd_stdout = request.form['cmd_stdout']
    cmd_stderr = request.form['cmd_stderr']
    cmd_exitCode = request.form['cmd_exitCode']
    cmd_duration = request.form['cmd_duration']

    conexao = connect_db()
    cursor = conexao.cursor()
    cursor.execute('UPDATE commands SET executed_at = %s, stdout = %s, stderr = %s, exitcode = %s, duration = %s WHERE id = %s', (datetime.now(), cmd_stdout, cmd_stderr, cmd_exitCode, cmd_duration, cmd_id,))
    conexao.commit()
    cursor.close()
    conexao.close()     
    # return OK  
    response_items = []
    response_items.append({
        'status': 'OK',
    })   
    return jsonify(response_items)

@app.route('/server/<string:action>', methods=['GET', 'POST'])
@app.route('/server/<string:action>/<int:id>', methods=['GET','POST'])
def server(action, id = None):

    if action == 'add':
        if request.method == 'POST':
            # receive data from form
            hostname = request.form['hostname']
            # if auth_key is empty, generate a random string
            if request.form['auth_key'] == '':
                auth_key = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
            else:
                auth_key = request.form['auth_key']
            created_at = datetime.now()
            group = None if request.form['group'] == '' else request.form['group']
            subgroup = None if request.form['subgroup'] == '' else request.form['subgroup']

            # save to database
            conexao = connect_db()
            cursor = conexao.cursor()   
            # check if hostname already exists
            #cursor.execute('SELECT id FROM servers WHERE hostname = %s AND deleted_at IS NULL', (hostname,))
            #query = cursor.fetchone()
            #if query is not None:
            #    close_db(cursor,conexao)
            #    # return a message of error
            #    mensagem = 'Hostname já cadastrado!'
            #    return render_template('message.html', mensagem=mensagem)
            #else:
            cursor.execute('INSERT INTO servers (hostname, auth_key, created_at, id_group, id_subgroup,registered_by) VALUES (%s, %s, %s, %s, %s,%s)', (hostname, auth_key, created_at, group, subgroup,'form_add_server'))
            id_server = cursor.lastrowid
            cursor.execute('INSERT INTO monitor (id_server,api_version) VALUES (%s,%s)', (id_server,'v1.0'))
            close_db(cursor,conexao)    

            # return a message of success
            mensagem = 'Server registered successfully!'
            return render_template('message.html', mensagem=mensagem)
        else:
            # render form
            return render_template('server_add.html')

    # if action is list, render template
    elif action == 'list':
        # query all servers
        conexao = connect_db()
        cursor = conexao.cursor()   
        cursor.execute('SELECT id, hostname, auth_key, name, created_at, updated_at, id_group, id_subgroup, registered_by, active FROM servers WHERE deleted_at IS NULL ORDER BY hostname ASC')
        query_servers = cursor.fetchall()
        
        # if query is empty, redirect to home
        if not query_servers:
                mensagem = 'Servers not found! Please register a server first.'
                return render_template('message.html', mensagem=mensagem)

        result = []
        for row in query_servers:
            # create json with id_commands
            result.append({
                'id': row[0],
                'hostname': row[1],
                'auth_key': row[2],
                'name': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'group': row[6],
                'subgroup': row[7],
                'registered_by': row[8],
                'active': row[9]
            })
        # for debug
        #print(result) 
        close_db(cursor,conexao)
        return render_template('server_list.html', result=result)

    elif action == 'disable':
        if id is not None:
            conexao = connect_db()
            cursor = conexao.cursor()   
            cursor.execute("UPDATE servers SET active = 0 WHERE id = %s", (id))
            close_db(cursor,conexao)
            return redirect('/server/list')

    elif action == 'enable':
        if id is not None:
            conexao = connect_db()
            cursor = conexao.cursor()   
            cursor.execute("UPDATE servers SET active = 1 WHERE id = %s", (id))
            close_db(cursor,conexao)
            return redirect('/server/list')
        
    elif action == 'edit':
        # if form is submitted, update database
        if request.method == 'POST':
            id = request.form['id']
            hostname = request.form['hostname']
            auth_key = request.form['auth_key']
            name = request.form['name']
            group = request.form['group']
            subgroup = request.form['subgroup']
            active = request.form['active']

            conexao = connect_db()
            cursor = conexao.cursor()
            # check if hostname and auth_key already exists
            cursor.execute('SELECT id FROM servers WHERE hostname = %s AND auth_key = %s AND deleted_at IS NULL', (hostname, auth_key))
            query = cursor.fetchall()
            # if query is upper than 1, return a message of error
            if len(query) > 1:
                close_db(cursor,conexao)
                # return a message of error
                mensagem = 'Hostname and auth_key already exists!'
                return render_template('message.html', mensagem=mensagem)
            else:
                cursor.execute("UPDATE servers SET hostname = %s, auth_key = %s, name = %s, updated_at = NOW(), active = %s, id_group = %s, id_subgroup = %s WHERE id = %s", (hostname, auth_key, name, active, group, subgroup, id))
                close_db(cursor,conexao)
                return redirect('/server/list')
        # if form is not submitted, render template
        conexao = connect_db()
        cursor = conexao.cursor()   
        cursor.execute('SELECT id, hostname, auth_key, name, id_group, id_subgroup, active FROM servers WHERE id = %s LIMIT 1', (int(id)))
        query_servers = cursor.fetchone()
        close_db(cursor,conexao)
        if not query_servers:
            return redirect('/server/list')
        result = {
            'id': query_servers[0],
            'hostname': query_servers[1],
            'auth_key': query_servers[2],
            'name': query_servers[3],
            'group': query_servers[4],
            'subgroup': query_servers[5],
            'active': query_servers[6]
        }
        return render_template('server_edit.html', result=result)
    
    elif action == 'delete':
        if id is not None:
            conexao = connect_db()
            cursor = conexao.cursor()   
            cursor.execute("UPDATE servers SET deleted_at = NOW() WHERE id = %s", (id))
            close_db(cursor,conexao)
            return redirect('/server/list')
    else:
        redirect('/server/list')

@app.route('/command/<string:action>', methods=['GET', 'POST'])
@app.route('/command/<string:action>/<int:id>', methods=['GET','POST'])
def command(action, id = None):

    # if action is add, render template
    if action == 'add':
        # if form is submitted, insert data to database
        if request.method == 'POST':
            # receive data from form
            id_server = request.form['id_server']
            command = request.form['command']
            md5 = get_hash(command)
            timeout = request.form.get('timeout', 30)
            bash = 1 if request.form.get('bash', False) else 0
            process = 1 if request.form.get('process', False) else 0
            relative_exec = None if request.form['relative_exec'] == '' else request.form['relative_exec']

            conexao = connect_db()
            cursor = conexao.cursor()   
            # insert command to database
            cursor = conexao.cursor()
            cursor.execute('INSERT INTO commands (id_server, command, md5, timeout, bash, process, relative_exec, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (id_server, command, md5, timeout, bash, process, relative_exec, datetime.now(),))
            close_db(cursor,conexao)    

            # return a message of success
            #mensagem = 'Command registered successfully!'
            #return render_template('message.html', mensagem=mensagem)
            return redirect('/command/list')
        else:
            conexao = connect_db()
            cursor = conexao.cursor()   
            cursor.execute('SELECT id, hostname FROM servers WHERE active = 1 AND deleted_at IS NULL ORDER BY hostname ASC')
            servidores = cursor.fetchall()
            close_db(cursor,conexao)

            # render form
            return render_template('command_add.html', servidores=servidores)
    elif action == 'list':
        conexao = connect_db()
        cursor = conexao.cursor()
        # select last 5 commands
        cursor.execute('SELECT c.id, s.name, s.hostname, c.command, c.timeout, c.bash, c.process, c.relative_exec, c.relative_retry, c.relative_retried, c.created_at, c.downloaded_at, c.executed_at, c.stdout, c.stderr, c.exitcode, c.duration FROM commands c JOIN servers s ON c.id_server = s.id ORDER BY c.id DESC LIMIT 5')
        #cursor.execute('SELECT c.id, c.id_server, c.command, c.md5, c.timeout, c.bash, c.process, c.relative_exec, c.created_at, c.updated_at, s.hostname FROM commands c INNER JOIN servers s ON c.id_server = s.id WHERE c.deleted_at IS NULL ORDER BY c.created_at DESC')
        query_commands = cursor.fetchall()
        
        # if query is empty, redirect to home
        if not query_commands:
                mensagem = 'Commands not found! Please register a command first.'
                return render_template('message.html', mensagem=mensagem)

        # create a list of commands to render
        result = []
        for row in query_commands:
            # create json with id_commands
            result.append({
                'id': row[0],
                'name': row[1],
                'hostname': row[2],
                'command': row[3],
                'timeout': row[4],
                'bash': row[5],
                'process': row[6],
                'relative_exec': row[7],
                'relative_retry': row[8],
                'relative_retried': row[9],
                'created_at': row[10],
                'downloaded_at': row[11],
                'executed_at': row[12],
                'stdout': row[13],
                'stderr': row[14],
                'exitcode': row[15],
                'duration': row[16]
            })
        # for debug
        #print(result) 
        close_db(cursor,conexao)
        return render_template('command_list.html', result=result)

if __name__ == '__main__':
    # listen on all IPs
    app.run(host='0.0.0.0', debug=True)
