import string
import threading
import socket
import json

import Estrutura
from Utils import constroi_mensagem, reconstroi_mensagem, printLog
from Interface import showMessages, printListaClientes


class ModuloServidor:
    def __init__(self, sock, address):
        printLog("Novo ModuloServidor")
        self.sock = sock
        self.address = address

    def atende_comunicacao(self):
        """ Realiza a comunicação com o cliente, recebendo as mensagens """

        (address, port) = self.address

        printLog("reconstruindo mensagem")
        mensagem_json_string = reconstroi_mensagem(self.sock)

        if not mensagem_json_string:
            mensagem_json = json.loads(mensagem_json_string)
            username = mensagem_json["username"]
            mensagem = mensagem_json["mensagem"]
            
            key = (min(username, Estrutura.username), max(username, Estrutura.username))
            Estrutura.mutexMessages.acquire()
            if key not in Estrutura.messages: Estrutura.messages[key] = []
            Estrutura.messages[key] += [(username, mensagem)]
            if key not in Estrutura.newMessages: Estrutura.newMessages[key] = 0
            Estrutura.newMessages[key] += 1
            Estrutura.mutexMessages.release()
            if Estrutura.estadoTela == "chat":
                showMessages(Estrutura.usuarioChat)
            elif Estrutura.estadoTela == "menu":
                printListaClientes()
        else:
            printLog(f"O usuario { self.sock } encerrou a conexão")
            self.sock.close()

            # Se remove da lista do Coordenador
            Estrutura.coordenadorServidores.removeServidor(self)
    
    def encerra(self):
        """ Encerra o socket atual """
        self.sock.close()
        printLog(f"Logoff ModuloServidor com sucesso")

class ModuloCoordenadorServidores:
    def __init__(self, HOST, PORT):
        printLog("Novo ModuloCoordenadorServidores", HOST, PORT)
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

            Estrutura.select_inputs.append(sock)

            printLog(f"O servidor foi inicializado na porta { self.PORT }.")
            self.sock = sock

    def aceita_conexao(self):
        """ Realiza a conexão com o cliente e devolve o novo socket direto """
        client_sock, client_addr = self.sock.accept()
        printLog(f"O servidor aceitou a conexão de { client_addr }")
        return client_sock, client_addr

    def trata_novos_servidores(self):
        """ Aguarda a conexao de um novo cliente do usuario para iniciar conversa """
        printLog("Trata novos servidores")
        
        # while True:
        #     printLog("Aguardando nova conexao")
        client_sock, client_addr = self.aceita_conexao()
        printLog("Conexao aceita")
        novo_servidor = ModuloServidor(client_sock, client_addr)
        # nova_thread_servidor = threading.Thread(target=novo_servidor.atende_comunicacao, args=(client_addr,))   
        # nova_thread_servidor.start()
        # printLog(f"Nova Thread {nova_thread_servidor.name} {nova_thread_servidor.ident}")
        self.servidores.append(novo_servidor)
        Estrutura.select_inputs.append(client_sock)
        Estrutura.socket_servidores[client_sock] = novo_servidor

        printLog("Coordenador Finalizou Tratamento de Novos Servidores")
    
    def encerra(self):
        """ Encerra seu socket e todos os servidores em questao """
        printLog(f"Logoff ModuloCoordenadorServidores")
        self.sock.close()
        for servidor in self.servidores:
            servidor.encerra()
        self.servidores = []
        printLog(f"Logoff ModuloCoordenadorServidores com Sucesso")

    def removeServidor(self, servidor):
        """ Remove um servidor da sua lista """
        self.servidores.remove(servidor)
        Estrutura.select_inputs.remove(servidor.sock)
        del Estrutura.socket_servidores[servidor.sock]
        printLog(f"removeServidor - Lista {self.servidores}")