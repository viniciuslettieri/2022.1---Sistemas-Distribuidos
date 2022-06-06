import string
import threading
import socket
import json

import Estrutura
from Utils import constroi_mensagem, reconstroi_mensagem, printLog


class ModuloServidor:
    def __init__(self, sock):
        printLog("[Log: Novo ModuloServidor]")
        self.sock = sock

    def atende_comunicacao(self, data):
        """ Realiza a comunicação com o cliente, atendendo a requisicao """

        (address, port) = data

        while True:
            printLog("[Log: reconstruindo mensagem]")
            mensagem_json_string = reconstroi_mensagem(self.sock)
            if not mensagem_json_string: break
            
            mensagem_json = json.loads(mensagem_json_string)
            username = mensagem_json["username"]
            mensagem = mensagem_json["mensagem"]
            
            key = (min(username, Estrutura.username), max(username, Estrutura.username))
            if key not in Estrutura.messages: Estrutura.messages[key] = []
            Estrutura.messages[key] += [(username, mensagem)]

            if key not in Estrutura.newMessages: Estrutura.newMessages[key] = 0
            Estrutura.newMessages[key] += 1


        printLog(f"[Log: O usuario { self.sock } encerrou a conexão]")
        self.sock.close()

        Estrutura.coordenadorServidores.removeServidor(self)
    
    def encerra(self):
        self.sock.close()
        printLog(f"[Log: Logoff ModuloServidor com sucesso]")

class ModuloCoordenadorServidores:
    def __init__(self, HOST, PORT):
        printLog("[Log: Novo ModuloCoordenadorServidores]", HOST, PORT)
        self.HOST = HOST
        self.PORT = int(PORT)
        self.inicializa()
        self.servidores = []    # Guarda os ModuloServidor

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
        printLog(f"[Log: O servidor aceitou a conexão de { client_addr }]")
        return client_sock, client_addr

    def trata_novos_servidores(self):
        printLog("[Log: trata novos servidores]")
        while True:
            printLog("[Log: Aguardando nova conexao]")
            client_sock, client_addr = self.aceita_conexao()
            printLog("[Log: Conexao aceita]")
            novo_servidor = ModuloServidor(client_sock)
            nova_thread_servidor = threading.Thread(target=novo_servidor.atende_comunicacao, args=(client_addr,))   
            nova_thread_servidor.start()
            printLog(f"[Log: Nova Thread {nova_thread_servidor.name} {nova_thread_servidor.ident}]")
            self.servidores.append(novo_servidor) 
        printLog("[Log: Coordenador Finalizou Tratamento de Novos Servidores]")
    
    def encerra(self):
        printLog(f"[Log: Logoff ModuloCoordenadorServidores]")
        self.sock.close()
        for servidor in self.servidores:
            servidor.encerra()
        self.servidores = []
        printLog(f"[Log: Logoff ModuloCoordenadorServidores com Sucesso]")

    def removeServidor(self, servidor):
        self.servidores.remove(servidor)
        printLog(f"[Log: removeServidor - Lista {self.servidores}]")