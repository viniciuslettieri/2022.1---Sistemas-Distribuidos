import socket

HOST = ''
PORT = 5000

sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(5)
novo_sock, endereco = sock.accept()

while True:
    msg = novo_sock.recv(1024)
    
    if not msg: 
        break
    else:
        print(str(msg, encoding='utf-8'))

    novo_sock.send(msg)

novo_sock.close()
sock.close()