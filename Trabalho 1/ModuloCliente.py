import socket

from Utils import constroi_mensagem, reconstroi_mensagem, printLog

class ModuloCliente:
    def __init__(self, HOST, PORT):
        printLog("[Log: Novo ModuloCliente]", HOST, PORT)
        self.HOST = HOST
        self.PORT = int(PORT)
        self.inicializa()

    def inicializa(self):
        """ Cria e retorna o socket passivo para o servidor """
        if not hasattr(self, "sock"):
            sock = socket.socket()
            sock.connect((self.HOST, self.PORT))
            self.sock = sock    
            printLog("[Log: Novo ModuloCliente Inicializado]")
    
    def enviaMensagem(self, msg):
        printLog("[Log: enviaMensagem]")
        byte_msg = constroi_mensagem(msg)
        self.sock.send(byte_msg)
        printLog("[Log: mensagem enviada]")

    def recebeMensagem(self):
        printLog("[Log: recebeMensagem]")
        response = reconstroi_mensagem(self.sock)
        printLog(f"[Log: mensagem recebida {response}]")
        return response

    def encerra(self):
        self.sock.close()
        printLog(f"[Log: Logoff ModuloCliente com Sucesso]")
