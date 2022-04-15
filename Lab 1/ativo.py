import socket

HOST = 'localhost'
PORT = 5000

sock = socket.socket()
sock.connect((HOST, PORT))

mensagem = ""
while mensagem != "fim":
    mensagem = input("Digite a mensagem: ")
    sock.send(mensagem.encode("ascii"))
    msg = sock.recv(1024)
    print(str(msg, encoding='utf-8'))

sock.close()