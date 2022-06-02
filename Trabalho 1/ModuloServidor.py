import string
import threading
import socket

import Estrutura
from Utils import constroi_mensagem, reconstroi_mensagem, printLog


class ModuloServidor:
    def __init__(self, sock):
        printLog("[Novo ModuloServidor]")
        self.sock = sock

    def atende_comunicacao(self):
        """ Realiza a comunicação com o cliente, atendendo a requisicao """

        while True:
            print("[reconstruindo mensagem]")
            mensagem = reconstroi_mensagem(self.sock)
            if not mensagem: break
            print(mensagem)

        print(f"(Servidor) O usuario { self.sock } encerrou a conexão.")
        self.sock.close()

class ModuloCoordenadorServidores:
    def __init__(self, HOST, PORT):
        printLog("[Log: Novo ModuloCoordenadorServidores]", HOST, PORT)
        self.HOST = HOST
        self.PORT = int(PORT)
        self.inicializa()

    def inicializa(self):
        """ Cria e retorna o socket passivo para o servidor """
        if not hasattr(self, "sock"):
            sock = socket.socket()   # default: socket.AF_INET, socket.SOCK_STREAM
            # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.HOST, self.PORT))
            sock.listen(5) 
            # sock.setblocking(False)

            printLog(f"[Log: O servidor foi inicializado na porta { self.PORT }.")
            self.sock = sock

    def aceita_conexao(self):
        """ Realiza a conexão com o cliente e devolve o novo socket direto """
        client_sock, client_addr = self.sock.accept()
        print(f"(Servidor) O servidor aceitou a conexão de { client_addr }.")
        return client_sock, client_addr

    def trata_novos_servidores(self):
        printLog("[Log: trata novos servidores]")
        while True:
            printLog("[Log: Aguardando nova conexao]")
            client_sock, client_addr = self.aceita_conexao()
            printLog("[Log: Conexao aceita]")
            novo_servidor = ModuloServidor(client_sock)
            nova_thread_servidor = threading.Thread(target=novo_servidor.atende_comunicacao)   
            nova_thread_servidor.start()
            Estrutura.servidores.append(novo_servidor) 
        print("[Coordenador Finalizou Tratamento de Novos Servidores]")