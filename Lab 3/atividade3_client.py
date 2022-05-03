import socket

# configuracao inicial dos sockets do cliente
HOST = 'localhost'
PORT = 5000

sock = socket.socket()
sock.connect((HOST, PORT))

# pediremos as palavras que mais aparecem no arquivo passado
filename = input("Digite o nome do arquivo: ")
sock.send(filename.encode("ascii"))
msg = sock.recv(1024)
print(str(msg, encoding='utf-8'))

sock.close()