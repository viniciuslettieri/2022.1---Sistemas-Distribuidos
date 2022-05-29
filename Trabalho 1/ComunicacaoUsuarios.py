import socket
import re
import string
import sys
import select
import threading

from Utils import constroi_mensagem, reconstroi_mensagem


lista_clientes = {
    "user1": {
        "endereco": '',
        "porta": 5000
    },
    "user2": {
        "endereco": '',
        "porta": 7000
    }
}


servidores = []
clientes = {}
username = None


class ModuloServidor:
    def __init__(self, sock):
        print("[Novo ModuloServidor]")
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
        print("[Novo ModuloCoordenadorServidores]", HOST, PORT)
        self.HOST = HOST
        self.PORT = PORT
        self.inicializa()

    def inicializa(self):
        """ Cria e retorna o socket passivo para o servidor """
        sock = socket.socket()   # default: socket.AF_INET, socket.SOCK_STREAM
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.HOST, self.PORT))
        sock.listen(5) 
        # sock.setblocking(False)

        print(f"(Servidor) O servidor foi inicializado na porta { self.PORT }.")
        self.sock = sock

    def aceita_conexao(self):
        """ Realiza a conexão com o cliente e devolve o novo socket direto """
        client_sock, client_addr = self.sock.accept()
        print(f"(Servidor) O servidor aceitou a conexão de { client_addr }.")
        return client_sock, client_addr

    def trata_novos_servidores(self):
        print("[trata novos servidores]")
        while True:
            client_sock, client_addr = self.aceita_conexao()
            print("aceito")
            novo_servidor = ModuloServidor(client_sock)
            nova_thread_servidor = threading.Thread(target=novo_servidor.atende_comunicacao)   
            nova_thread_servidor.start()
            servidores.append(novo_servidor) 


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
        # response = reconstroi_mensagem(self.sock)
        # print(str(msg, encoding='utf-8'))


class Interface:
    def atende_stdin(self):
        while True:
            comando = input()
            print(f"[comando {comando}]")
            
            if comando.startswith("\chat"):   
                secoes = comando.split(" ")
                USERNAME = secoes[1]
                
                print(f"[chat com {USERNAME}]")

                if USERNAME in clientes.keys() or USERNAME == username:
                    pass
                else:
                    HOST = lista_clientes[USERNAME]["endereco"]
                    PORT = lista_clientes[USERNAME]["porta"]
                    novo_cliente = ModuloCliente(HOST, PORT)
                    clientes[USERNAME] = novo_cliente

            elif comando.startswith("\message"):  
                secoes = comando.split(" ")
                USERNAME = secoes[1]
                mensagem = " ".join(secoes[2:])

                print(f"[message para {USERNAME}]")

                if USERNAME in clientes.keys():
                    cliente = clientes[USERNAME]
                    cliente.enviaMensagem(mensagem)
                else:
                    print("\nERRO: primeiro use o comando de chat para iniciar uma conversa!\n")



def main():  
    global username

    username = input("Digite seu username: ")
    coordenador = ModuloCoordenadorServidores(lista_clientes[username]["endereco"], lista_clientes[username]["porta"])
    thread_coordenador = threading.Thread(target=coordenador.trata_novos_servidores)   
    thread_coordenador.start()

    interface = Interface()
    thread_interface = threading.Thread(target=interface.atende_stdin)   
    thread_interface.start()

    thread_coordenador.join()
    thread_interface.join()


if __name__ == "__main__":
    main()
