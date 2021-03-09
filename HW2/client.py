import sys
import socket

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
            tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
            tcp_server_message = tcp_client.recv(1024).decode('utf-8')
            print(tcp_server_message)
        else:
            tcp_client.sendall((client_message + ' ' + str(client_id)).encode())
            tcp_server_message = tcp_client.recv(1024).decode('utf-8')
            tcp_client.close()
            udp_client.close()
            break

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

    else:
        print('Command not found.')
        continue
