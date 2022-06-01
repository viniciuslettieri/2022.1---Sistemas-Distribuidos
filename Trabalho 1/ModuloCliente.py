import socket

from Utils import constroi_mensagem, reconstroi_mensagem

class ModuloCliente:
    def __init__(self, HOST, PORT):
        print("[Novo ModuloCliente]", HOST, PORT)
        self.HOST = HOST
        self.PORT = PORT
        self.inicializa()

    def inicializa(self):
        """ Cria e retorna o socket passivo para o servidor """
        if not hasattr(self, "sock"):
            sock = socket.socket()
            sock.connect((self.HOST, self.PORT))
            self.sock = sock    
    
    def enviaMensagem(self, msg):
        print("[enviaMensagem]")
        byte_msg = constroi_mensagem(msg)
        self.sock.send(byte_msg)

    def recebeMensagem(self):
        response = reconstroi_mensagem(self.sock)
        return response