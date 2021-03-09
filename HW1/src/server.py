import sys
import sqlite3
import socket
from random import randint
import threading

# create db & table
with sqlite3.connect('userinfo.db', check_same_thread=False) as db:
    cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
userID INTEGER PRIMARY KEY,
username VARCHAR(20) NOT NULL,
email VARCHAR(89) NOT NULL,
password VARCHAR(20) NOT NULL);
''')
db.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS logininfo (
clientID INTEGER PRIMARY KEY,
username VARCHAR(20) NOT NULL);
''')
db.commit()

###
host = '127.0.0.1'
port = int(sys.argv[1])
addr = (host, port)


def read_tcp(read_tcp_client, client_id):
    while True:
        client_message = read_tcp_client.recv(1024).decode('utf-8')
        split_client_message = client_message.split()
        # print(split_client_message)
        tcp_server_message = ''

        if split_client_message[0] == 'exit':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: exit'
            else:
                cursor.execute('''
                DELETE FROM logininfo WHERE clientID = ?
                ''', (split_client_message[1],))
                db.commit()
                read_tcp_client.close()
                break

        elif split_client_message[0] == 'login':
            if len(split_client_message) != 3:
                tcp_server_message = 'Usage: login <username> <password>'
            else:
                tcp_server_message = login(split_client_message[1], split_client_message[2], client_id)

        elif split_client_message[0] == 'logout':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: logout'
            else:
                tcp_server_message = logout(split_client_message[1])

        elif split_client_message[0] == 'list-user':
            if len(split_client_message) != 1:
                tcp_server_message = 'Usage: list-user'
            else:
                tcp_server_message = list_user()

        read_tcp_client.sendall(tcp_server_message.encode())


def read_udp():
    while True:
        client_message, udp_addr = udp_server.recvfrom(1024)
        client_message = client_message.decode('utf-8')
        split_client_message = client_message.split()
        # print(split_client_message)
        udp_server_message = ''

        if split_client_message[0] == 'register':
            if len(split_client_message) != 4:
                udp_server_message = 'Usage: register <username> <email> <password>'
            else:
                udp_server_message = register(split_client_message[1], split_client_message[2], split_client_message[3])
        elif split_client_message[0] == 'whoami':
            if len(split_client_message) != 2:
                udp_server_message = 'Usage: whoami'
            else:
                udp_server_message = whoami(split_client_message[1])

        udp_server.sendto(udp_server_message.encode(), udp_addr)


def register(username, email, password):
    cursor.execute('''
    SELECT EXISTS(SELECT 1 FROM user WHERE username=?);
    ''', (username,))
    db.commit()
    if cursor.fetchall()[0][0] == 1:
        return 'Username is already used.'
    else:
        cursor.execute('''
        INSERT INTO user (username, email, password)
        VALUES (?, ?, ?);
        ''', (username, email, password))
        db.commit()
        return 'Register successfully.'


def login(username, password, client_id):
    # whether the client already login
    cursor.execute('''
    SELECT EXISTS(SELECT 1 FROM logininfo WHERE clientID=?);
    ''', (client_id,))
    db.commit()
    if cursor.fetchall()[0][0] == 0:  # not logging in
        # whether the user exists
        cursor.execute('''
        SELECT EXISTS(SELECT 1 FROM user WHERE username=?);
        ''', (username,))
        db.commit()
        if cursor.fetchall()[0][0] == 0:
            return 'Login failed.'

        cursor.execute('''
        SELECT password FROM user WHERE username=?;
        ''', (username,))
        db.commit()
        if cursor.fetchall()[0][0] == password:
            cursor.execute('''
            INSERT INTO logininfo (clientID, username)
            VALUES (?, ?);
            ''', (client_id, username))
            db.commit()
            return 'Welcome, ' + username + '|' + str(client_id)
        else:
            return 'Login failed.'
    else:
        return 'Please logout first.'


def logout(client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        cursor.execute('''
        DELETE FROM logininfo WHERE clientID = ?
        ''', (client_id,))
        db.commit()
        current_user = return_str
        return 'Bye, ' + current_user


def whoami(client_id):
    cursor.execute('''
    SELECT EXISTS(SELECT 1 FROM logininfo WHERE clientID=?);
    ''', (client_id,))
    db.commit()
    if cursor.fetchall()[0][0] == 0:  # not logging in
        return 'Please login first.'
    else:
        cursor.execute('''
        SELECT username FROM logininfo WHERE clientID = ?;
        ''', (client_id,))
        db.commit()
        return cursor.fetchall()[0][0]


def list_user():
    cursor.execute('''
    SELECT username, email FROM user
    ''')
    db.commit()
    user_list = cursor.fetchall()
    return_message = '{:<15s}'.format('Name') + 'Email'
    for j in range(len(user_list)):
        return_message = return_message + '\n' + '{:<15s}'.format(user_list[j][0]) + user_list[j][1]
    return return_message


def job():
    # create threads if new clients connect
    while True:
        client_id = randint(1, 1000000)
        # Welcome Message Section
        tcp_client, wel_addr = tcp_server.accept()
        print('New Connection.')
        welcome_message = '********************************\n** Welcome to the BBS server. **\n********************************'

        tcp_client.sendall(welcome_message.encode())
        tcp_thread_run = threading.Thread(target=read_tcp, args=(tcp_client, client_id))
        tcp_thread_run.start()


# tcp create
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.bind(addr)
tcp_server.listen(10)

# udp -> keep listening
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind(addr)
udp_thread = threading.Thread(target=read_udp)
udp_thread.start()

# tcp -> create thread to handle multi-clients
tcp_thread = threading.Thread(target=job)
tcp_thread.start()
