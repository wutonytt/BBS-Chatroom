import sys
import socket
import threading
import select
import datetime
import time as t
from collections import deque

host = sys.argv[1]
port = int(sys.argv[2])
addr = (host, port)

# tcp
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_client.connect(addr)

# udp
udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# welcome message
welcome_message = tcp_client.recv(1024).decode('utf-8')
print(welcome_message)
client_id = 0

#################### Chatroom ########################
list_of_clients = []
history = deque(maxlen=3)
close_chatroom_server = 0

# chatroom job
def chatroom(chatroom_addr, owner):
    global close_chatroom_server
    chatroom_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chatroom_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    chatroom_server.bind(chatroom_addr)
    chatroom_server.settimeout(0.1)
    chatroom_server.listen(10)

    while close_chatroom_server == 0:
        try:
            ac_conn, ac_addr = chatroom_server.accept()
            list_of_clients.append(ac_conn)

            client_threads = threading.Thread(target=client_thread, args=(ac_conn, ac_addr, owner, chatroom_server))
            client_threads.start()

        except socket.timeout:
            pass

    # ac_conn.close()
    chatroom_server.close()
    close_chatroom_server = 0

# chatroom client thread
def client_thread(conn, addr, owner, chatroom_server):
    global close_chatroom_server
    welcome_join = '*****************************\n**​ Welcome to the chatroom ​**\n*****************************'
    welcome_join += '|' + owner
    for his in history:
        welcome_join += '|' + his

    conn.sendall(welcome_join.encode())

    while True:
        try:
            message = conn.recv(1024).decode('utf-8')
            message = message.split('|')
            if message[0]:
                # Calls broadcast function to send message to all
                message_to_send = message[1] + '[' + message[2] + ']' + ': ' + message[0]
                
                if (message[1] != 'sys'):
                    history.append(message_to_send)
                
                broadcast(message_to_send, conn)
                
                # client leave-chatroom
                if message[0].split()[1] == 'leave':
                    conn.close()
                    break

                # owner leave-chatroom
                if message[0] == 'the chatroom is close.':
                    close_chatroom_server = 1
                    conn.close()                
                    break

            else:
                """message may have no content if the connection  
                is broken, in this case we remove the connection"""
                remove(conn)
                break

        except:
            continue


def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.sendall(message.encode())
            except:
                clients.close()

                # if the link is broken, we remove the client
                remove(clients)


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


def join_chatroom(join_port):
    chatroom_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t.sleep(0.1)
    chatroom_client.connect((host,join_port))

    welcome_join = chatroom_client.recv(1024).decode('utf-8').split('|')
    print(welcome_join[0])
    for his in welcome_join[2:]:
        print(his)

    owner = welcome_join[1]

    udp_client.sendto(('whoami ' + str(client_id)).encode(), (host, port))
    my_name, addr = udp_client.recvfrom(1024)
    my_name = my_name.decode('utf-8')

    x = datetime.datetime.now()
    time = x.strftime('%H:%I')
    chatroom_client.sendall((my_name + ' join us.|sys|' + time).encode())

    detach = 0
    leave = 0

    while True:
        sockets_list = [sys.stdin, chatroom_client]
        read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

        for socks in read_sockets:
            if socks == chatroom_client:
                message = socks.recv(1024).decode('utf-8')
                print(message)
                if message.split(':')[2] == ' the chatroom is close.':
                    leave = 1
                    chatroom_client.close()
                    break

            else:
                message = sys.stdin.readline().strip('\n')
                # print(message)
                if message == 'detach':
                    detach = 1
                    break

                if message == 'leave-chatroom':
                    if my_name != owner:
                        leave = 1
                        x = datetime.datetime.now()
                        time = x.strftime('%H:%I')
                        chatroom_client.sendall((my_name + ' leave us.|sys|' + time).encode())
                        chatroom_client.close()
                        break
                    else:
                        leave = 1
                        x = datetime.datetime.now()
                        time = x.strftime('%H:%I')
                        chatroom_client.sendall(('the chatroom is close.|sys|' + time).encode())
                        chatroom_client.close()

                        tcp_client.sendall((message + ' ' + str(client_id)).encode())
                        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
                        break

                x = datetime.datetime.now()
                time = x.strftime('%H:%I')
                chatroom_client.sendall((message + '|' + my_name + '|' + time).encode())
                # sys.stdout.write(message)
                # sys.stdout.flush()
        if detach == 1 or leave == 1:
            break
    chatroom_client.close()
    print('Welcome back to BBS.')


def attach(attach_port):
    chatroom_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chatroom_client.connect((host,attach_port))

    welcome_join = chatroom_client.recv(1024).decode('utf-8').split('|')
    print(welcome_join[0])
    for his in welcome_join[2:]:
        print(his)

    owner = welcome_join[1]

    udp_client.sendto(('whoami ' + str(client_id)).encode(), (host, port))
    my_name, addr = udp_client.recvfrom(1024)
    my_name = my_name.decode('utf-8')
    
    detach = 0
    leave = 0

    while True:
        sockets_list = [sys.stdin, chatroom_client]
        read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

        for socks in read_sockets:
            if socks == chatroom_client:
                message = socks.recv(1024).decode('utf-8')
                print(message)
                if message.split(':')[2] == ' the chatroom is close.':
                    leave = 1
                    break
            else:
                message = sys.stdin.readline().strip('\n')
                # print(message)
                if message == 'detach':
                    detach = 1
                    break
                
                if message == 'leave-chatroom':
                    if my_name != owner:
                        leave = 1
                        x = datetime.datetime.now()
                        time = x.strftime('%H:%I')
                        chatroom_client.sendall((my_name + ' leave us.|sys|' + time).encode())
                        chatroom_client.close()
                        break
                    else:
                        leave = 1
                        x = datetime.datetime.now()
                        time = x.strftime('%H:%I')
                        chatroom_client.sendall(('the chatroom is close.' + '|sys|' + time).encode())
                        chatroom_client.close()
                        
                        tcp_client.sendall((message + ' ' + str(client_id)).encode())
                        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
                        break

                x = datetime.datetime.now()
                time = x.strftime('%H:%I')
                chatroom_client.sendall((message + '|' + my_name + '|' + time).encode())
                # sys.stdout.write(message)
                # sys.stdout.flush()
        if detach == 1 or leave == 1:
            break
    chatroom_client.close()
    print('Welcome back to BBS.')


while True:
    client_message = input('% ')
    if client_message == '':
        continue
    command = client_message.split()[0]

    if command == 'register':  # udp
        udp_client.sendto(client_message.encode(), addr)
        udp_server_message, addr = udp_client.recvfrom(1024)
        udp_server_message = udp_server_message.decode('utf-8')
        print(udp_server_message)

    elif command == 'whoami':
        udp_client.sendto((client_message + ' ' + str(client_id)).encode(), addr)
        udp_server_message, addr = udp_client.recvfrom(1024)
        udp_server_message = udp_server_message.decode('utf-8')
        print(udp_server_message)

    elif command == 'login':
        tcp_client.sendall(client_message.encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        if '|' in tcp_server_message:
            client_id = tcp_server_message.split('|')[1]
            tcp_server_message = tcp_server_message.split('|')[0]
        print(tcp_server_message)

    elif command == 'logout':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'list-user':
        tcp_client.sendall(client_message.encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'exit':
        if len(client_message.split()) != 1:
            tcp_client.sendall(
                (client_message + ' ' + str(client_id)).encode())
            tcp_server_message = tcp_client.recv(1024).decode('utf-8')
            print(tcp_server_message)
        else:
            tcp_client.sendall(
                (client_message + ' ' + str(client_id)).encode())
            tcp_server_message = tcp_client.recv(1024).decode('utf-8')
            tcp_client.close()
            udp_client.close()
            break

    # board & post

    elif command == 'create-board':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'create-post':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'list-board':
        tcp_client.sendall(client_message.encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'list-post':
        tcp_client.sendall(client_message.encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'read':
        tcp_client.sendall(client_message.encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'delete-post':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'update-post':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    elif command == 'comment':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    # chatroom

    elif command == 'create-chatroom':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

        if tcp_server_message == 'start to create chatroom...':
            chatroom_port = int(client_message.split()[1])
            chatroom_addr = (host, chatroom_port)

            udp_client.sendto(('whoami ' + str(client_id)).encode(), (host, port))
            owner, addr = udp_client.recvfrom(1024)
            owner = owner.decode('utf-8')

            chatrooms = threading.Thread(target=chatroom, args=(chatroom_addr,owner))
            chatrooms.start()

            join_chatroom(chatroom_port)
            
    elif command == 'list-chatroom':
        udp_client.sendto((client_message + ' ' + str(client_id)).encode(), addr)
        udp_server_message, addr = udp_client.recvfrom(1024)
        udp_server_message = udp_server_message.decode('utf-8')
        print(udp_server_message)

    elif command == 'join-chatroom':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        if tcp_server_message in ['Please login first.', 'The chatroom does not exist or the chatroom is close.', 'Usage: join-chatroom <chatroom_name>']:
            print(tcp_server_message)
        else:
            join_port = int(tcp_server_message)
            # print(join_port)
            join_chatroom(join_port)

    elif command == 'attach':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        if tcp_server_message in ['Please login first.', 'Please create-chatroom first.', 'Please restart-chatroom first.', 'Usage: attach']:
            print(tcp_server_message)
        else:
            attach_port = int(tcp_server_message)
            attach(attach_port)

    elif command == 'restart-chatroom':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        if tcp_server_message.split('|')[0] != 'start to create chatroom...':
            print(tcp_server_message)
        else:
            print('start to create chatroom...')
            chatroom_port = int(tcp_server_message.split('|')[2])
            chatroom_addr = (host, chatroom_port)

            owner = tcp_server_message.split('|')[1]

            chatrooms = threading.Thread(target=chatroom, args=(chatroom_addr,owner))
            chatrooms.start()

            join_chatroom(chatroom_port)


    elif command == 'leave-chatroom':
        tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
        tcp_server_message = tcp_client.recv(1024).decode('utf-8')
        print(tcp_server_message)

    else:
        print('Command not found.')
        continue
