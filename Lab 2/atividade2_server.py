import socket
import re
import string
from collections import Counter

# configuracao inicial dos sockets do servidor
HOST = ''
PORT = 5000

sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(5)

# executaremos indefinidamente
while True:
    novo_sock, endereco = sock.accept()

    filename = novo_sock.recv(1024)
    try:
        with open(filename, 'r') as file:
            text = file.read().replace('\n', ' ')

            # tratativa para obter as 5 palavras que mais aparecem no arquivo
            cleaned_text = text.translate(str.maketrans('','', string.punctuation))
            cleaned_text = re.sub(' +', ' ', cleaned_text).split(' ')
            common_words = [ palavra for palavra, _ in Counter(cleaned_text).most_common(5) ]
            response = '\n'.join(common_words)

            # respondendo a requisicao
            novo_sock.send(response.encode("ascii"))
    except:
        erro = f"ERRO: Arquivo '{filename}' não encontrado!".encode("ascii")
        novo_sock.send(erro)

    novo_sock.close()

sock.close()
