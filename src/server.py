import sys
import sqlite3
import socket
from random import randint
import threading
import datetime

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

# shared global vars & mutex locks
mutex_boards = threading.Lock()
boards = []

mutex_posts = threading.Lock()
posts = []

mutex_comments = threading.Lock()
comments = []

chatroom_ports = []   # [name, port, status]

###### tcp ######

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

        # board & post
        
        elif split_client_message[0] == 'create-board':
            if len(split_client_message) != 3:
                tcp_server_message = 'Usage: create-board <name>'
            else:
                tcp_server_message = create_board(split_client_message[1], split_client_message[2])

        elif split_client_message[0] == 'create-post':
            if split_client_message[2] == '--title' and split_client_message.index('--content') >= 4:
                b_name = split_client_message[1]

                c_index = split_client_message.index('--content')
                i = 3
                title = ''
                while i < c_index:
                    title += split_client_message[i] + ' '
                    i += 1
                j = c_index + 1
                content = ''
                while j < len(split_client_message) - 1:
                    content += split_client_message[j] + ' '
                    j += 1
                tcp_server_message = create_post(b_name, title, content, split_client_message[-1])
            else:
                tcp_server_message = 'Usage: create-post <board-name> --title <title> --content <content>'

        elif split_client_message[0] == 'list-board':
            if len(split_client_message) != 1:
                tcp_server_message = 'Usage: list-board'
            else:
                tcp_server_message = list_board()

        elif split_client_message[0] == 'list-post':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: list-post <board-name>'
            else:
                tcp_server_message = list_post(split_client_message[1])

        elif split_client_message[0] == 'read':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: read <post-S/N>'
            else:
                tcp_server_message = read(int(split_client_message[1]))

        elif split_client_message[0] == 'delete-post':
            if len(split_client_message) != 3:
                tcp_server_message = 'Usage: delete-post <post-S/N>'
            else:
                tcp_server_message = delete_post(int(split_client_message[1]), split_client_message[2])

        elif split_client_message[0] == 'update-post':
            if len(split_client_message) < 5 or split_client_message[2] not in {'--title', '--content'}:
                tcp_server_message = 'Usage: update-post <post-S/N> --title/content <new>'
            else:
                i = 3
                new = ''
                while i < len(split_client_message) - 1:
                    new += split_client_message[i] + ' '
                    i += 1
                tcp_server_message = update_post(int(split_client_message[1]), split_client_message[2], new,
                                                 split_client_message[-1])

        elif split_client_message[0] == 'comment':
            if len(split_client_message) < 4:
                tcp_server_message = 'Usage: comment <post-S/N> <comment>'
            else:
                i = 2
                message = ''
                while i < len(split_client_message) - 1:
                    message += split_client_message[i] + ' '
                    i += 1
                tcp_server_message = comment(int(split_client_message[1]), message, split_client_message[-1])

        # chatroom

        elif split_client_message[0] == 'create-chatroom':
            if len(split_client_message) != 3:
                tcp_server_message = 'Usage: create-chatroom <port>'
            else:
                tcp_server_message = create_chatroom(int(split_client_message[1]), split_client_message[2])

        elif split_client_message[0] == 'join-chatroom':
            if len(split_client_message) != 3:
                tcp_server_message = 'Usage: join-chatroom <chatroom_name>'
            else:
                tcp_server_message = join_chatroom(split_client_message[1], split_client_message[2])

        elif split_client_message[0] == 'leave-chatroom':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: leave-chatroom'
            else:
                tcp_server_message = leave_chatroom(split_client_message[1])
        
        elif split_client_message[0] == 'restart-chatroom':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: restart-chatroom'
            else:
                tcp_server_message = restart_chatroom(split_client_message[1])
        
        elif split_client_message[0] == 'attach':
            if len(split_client_message) != 2:
                tcp_server_message = 'Usage: attach'
            else:
                tcp_server_message = attach(split_client_message[1])
        
        read_tcp_client.sendall(tcp_server_message.encode())


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
        for cha in chatroom_ports:
            if cha[0] == return_str and cha[2] == 'open':
                return 'Please do "attach" and "leave-chatroom" first.'

        cursor.execute('''
        DELETE FROM logininfo WHERE clientID = ?
        ''', (client_id,))
        db.commit()
        current_user = return_str
        return 'Bye, ' + current_user + '.'


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


def create_board(b_name, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        mutex_boards.acquire()
        if any(b_name in i for i in boards) is False:
            boards.append([b_name, return_str])
            mutex_boards.release()
            return 'Create board successfully.'
        else:
            mutex_boards.release()
            return 'Board already exists.'


def create_post(b_name, title, content, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        if any(b_name in i for i in boards):
            mutex_posts.acquire()
            x = datetime.datetime.now()
            date = str(x.month) + '/' + str(x.day)
            content = content.replace('<br>', '\n')
            posts.append([b_name, title, content, return_str, date])
            mutex_posts.release()
            return 'Create post successfully.'
        else:
            return 'Board does not exist.'


def list_board():
    return_message = '{:<12s}'.format('Index') + '{:<15s}'.format('Name') + 'Moderator'
    for i in range(len(boards)):
        return_message += '\n' + '{:<12s}'.format(str(i + 1)) + '{:<15s}'.format(boards[i][0]) + boards[i][1]
    return return_message


def list_post(b_name):
    return_message = '{:<12s}'.format('S/N') + '{:<20s}'.format('Title') + '{:<12s}'.format('Author') + 'Date'
    if any(b_name in i for i in boards):
        for i in range(len(posts)):
            if posts[i][0] == b_name:
                return_message += '\n' + '{:<12s}'.format(str(i + 1)) + '{:<20s}'.format(posts[i][1]) + \
                                  '{:<12s}'.format(posts[i][3]) + posts[i][4]
        return return_message
    else:
        return 'Board does not exist.'


def read(post_sn):
    i = post_sn - 1
    if i < len(posts) and (posts[i] != [0, 0, 0, 0, 0]):
        return_message = 'Author: ' + posts[i][3] + '\nTitle: ' + posts[i][1] + '\nDate: ' + posts[i][4] + '\n--\n' + \
                         posts[i][2] + '\n--'
        for com in comments:
            if com[0] == post_sn:
                return_message += '\n' + com[1] + ': ' + com[2]
        return return_message
    else:
        return 'Post does not exist.'


def delete_post(post_sn, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        i = post_sn - 1
        mutex_posts.acquire()
        if i < len(posts) and (posts[i] != [0, 0, 0, 0, 0]):
            if posts[i][3] == return_str:
                posts[i] = [0, 0, 0, 0, 0]
                mutex_posts.release()
                return 'Delete successfully.'
            else:
                mutex_posts.release()
                return 'Not the post owner.'
        else:
            mutex_posts.release()
            return 'Post does not exist.'


def update_post(post_sn, mode, new, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        i = post_sn - 1
        mutex_posts.acquire()
        if i < len(posts) and (posts[i] != [0, 0, 0, 0, 0]):
            if posts[i][3] == return_str:
                if mode == '--title':
                    posts[i][1] = new
                if mode == '--content':
                    posts[i][2] = new.replace('<br>', '\n')
                mutex_posts.release()
                return 'Update successfully.'
            else:
                mutex_posts.release()
                return 'Not the post owner.'
        else:
            mutex_posts.release()
            return 'Post does not exist.'


def comment(post_sn, message, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        i = post_sn - 1
        if i < len(posts) and (posts[i] != [0, 0, 0, 0, 0]):
            mutex_comments.acquire()
            comments.append([post_sn, return_str, message])
            mutex_comments.release()
            return 'Comment successfully.'
        else:
            return 'Post does not exist.'


def create_chatroom(port, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        name = return_str
        if any(name in i for i in chatroom_ports):
            return 'User has already created the chatroom.'
        else:
            chatroom_ports.append([return_str, port, 'open'])
            return 'start to create chatroom...'


def join_chatroom(chatroom_name, client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        for cha in chatroom_ports:
            if cha[0] == chatroom_name and cha[2] == 'open':
                return str(cha[1])
        return 'The chatroom does not exist or the chatroom is close.'


def leave_chatroom(client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        for cha in chatroom_ports:
            if cha[0] == return_str:
                cha[2] = 'close'
                return 'modify status successfully'
        return 'fail'


def restart_chatroom(client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        for cha in chatroom_ports:
            if cha[0] == return_str:
                if cha[2] == 'close':
                    cha[2] = 'open'
                    return 'start to create chatroom...|' + cha[0] + '|' + str(cha[1])
                elif cha[2] == 'open':
                    return 'Your chatroom is still running.'
        return 'Please create-chatroom first.'


def attach(client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        name = return_str
        for cha in chatroom_ports:
            if cha[0] == name and cha[2] == 'open':
                return str(cha[1])
            if cha[0] == name and cha[2] == 'close':
                return 'Please restart-chatroom first.'
        return 'Please create-chatroom first.'


###### udp ######

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

        elif split_client_message[0] == 'list-chatroom':
            if len(split_client_message) != 2:
                udp_server_message = 'Usage: list-chatroom'
            else:
                udp_server_message = list_chatroom(split_client_message[1])

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


def list_chatroom(client_id):
    return_str = whoami(client_id)
    if return_str == 'Please login first.':
        return return_str
    else:
        return_message = '{:<20s}'.format('Chatroom_name') + 'Status'
        for cha in chatroom_ports:
            return_message += '\n' + '{:<20s}'.format(cha[0]) + cha[2]
        return return_message


def job():
    # create threads if new clients connect
    while True:
        client_id = randint(1, 1000000)
        # Welcome Message Section
        tcp_client, wel_addr = tcp_server.accept()
        print('New Connection.')
        welcome_message = '********************************\n** Welcome to the BBS server. ' \
                          '**\n******************************** '

        tcp_client.sendall(welcome_message.encode())
        tcp_thread_run = threading.Thread(target=read_tcp, args=(tcp_client, client_id))
        tcp_thread_run.start()


# tcp create
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
