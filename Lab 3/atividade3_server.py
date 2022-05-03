import socket
import re
import string
from collections import Counter
import sys
import select
import threading

HOST = ''
PORT = 5000

entradas = [sys.stdin]


def inicializaServidor():
    """ Cria o socket passivo para o servidor """

    sock = socket.socket()   # default: socket.AF_INET, socket.SOCK_STREAM
    sock.bind((HOST, PORT))
    sock.listen(5) 
    sock.setblocking(False)

    entradas.append(sock)

    print(f"(Servidor) O servidor foi inicializado na porta {PORT}.")

    return sock


def aceitaConexao(sock):
    """ Realiza a conexão com o cliente e devolve o novo socket direto """

    client_sock, client_addr = sock.accept()
    print(f"(Servidor) O servidor aceitou a conexão de ({client_sock}, {client_addr}).")
    return client_sock, client_addr


def atendeRequisicao(client_sock, client_addr):
    """ Realiza a comunicação com o cliente, atendendo a requisicao """

    while True:
        filename = client_sock.recv(1024)
        
        # checa se o cliente encerrou a conexão
        if not filename:
            break
        
        # responde a requisição
        try:
            with open(filename, 'r') as file:
                text = file.read().replace('\n', ' ')

                # tratativa para obter as 5 palavras que mais aparecem no arquivo
                cleaned_text = text.translate(str.maketrans('','', string.punctuation))
                cleaned_text = re.sub(' +', ' ', cleaned_text).split(' ')
                common_words = [ palavra for palavra, _ in Counter(cleaned_text).most_common(5) ]
                response = '\n'.join(common_words)

                client_sock.send(response.encode("utf-8"))
        except:
            filename = str(filename, encoding="utf-8")
            erro = f"ERRO: Arquivo '{filename}' não encontrado!".encode("utf-8")
            client_sock.send(erro)

        print(f"(Servidor) O servidor atendeu a requisição de ({client_sock}, {client_addr}).")

    print(f"(Servidor) O cliente ({client_sock}, {client_addr}) encerrou a conexão.")
    client_sock.close()


def main():
    clientes = []     

    server_sock = inicializaServidor()
    while True:
        leitura, _, _ = select.select(entradas, [], [])

        for leitura_pronto in leitura:
            if leitura_pronto == server_sock:
                client_sock, client_addr = aceitaConexao(server_sock)
                cliente = threading.Thread(target=atendeRequisicao, args=(client_sock, client_addr))   
                cliente.start()
                clientes.append(cliente) 
                client_sock.close()
            elif leitura_pronto == sys.stdin:
                comando = input()
                if comando == "exit":
                    for client in clientes:
                        client.join()
                    server_sock.close()
                    sys.exit()


main()
