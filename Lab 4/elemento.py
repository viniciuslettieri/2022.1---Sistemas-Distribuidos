import rpyc
from rpyc.utils.server import ThreadedServer, ThreadPoolServer
import argparse
from random import randint
from datetime import datetime
import multiprocessing


vizinhos = []
identificador = None
respondido = None
eleito_recebido = None
id_lider = None


class Elemento(rpyc.Service):
    def on_connect(self, conx):
        global identificador
        # print(f"Conexao estabelecida. [{identificador}]")

    def on_disconnect(self, conx):
        global identificador
        # print(f"Conexao encerrada. [{identificador}]")

    def exposed_return_id(self):
        global identificador
        return identificador
    
    def exposed_return_id_lider(self):
        global id_lider
        return id_lider

    def exposed_list_neighbors(self):
        global vizinhos
        return vizinhos

    def exposed_probe(self, parent=None, origin=datetime.now().strftime("%m/%d/%Y %H:%M:%S")):
        global vizinhos, identificador, respondido
        
        if respondido != None and respondido == origin:
            return None

        respondido = origin

        max_response = identificador
        for porta_viz in vizinhos:
            server = rpyc.connect('localhost', porta_viz)
            if server.root.return_id() == parent: continue

            response = server.root.probe(identificador, origin)
            if response:
                max_response = max(max_response, response)

        if parent == None:
            for viz in vizinhos:
                server = rpyc.connect('localhost', viz)
                server.root.eleito(identificador, origin, max_response)

        return max_response
    
    def exposed_echo(self):
        print("echo")
    
    def exposed_eleito(self, parent, origin, id_lider_recebido):
        global vizinhos, identificador, eleito_recebido, id_lider
       
        if eleito_recebido != None and eleito_recebido == origin:
            return None

        eleito_recebido = origin
        id_lider = id_lider_recebido

        for porta_viz in vizinhos:
            server = rpyc.connect('localhost', porta_viz)
            if server.root.return_id() == parent: continue
            server.root.eleito(identificador, origin, id_lider_recebido)
    
    def exposed_connect_to(self, port):
        global vizinhos
        vizinhos.append(port)

    def exposed_disconnect_from(self, port):
        global vizinhos
        vizinhos.remove(port)


def inicializa_servidor(port):
    global identificador
    identificador = randint(100, 999)
    k = ThreadedServer(Elemento, port=port)
    k.start()


def inicializa_servidores(quantidade_servidores):
    portas = []
    processos = []
    while quantidade_servidores > 0:
        porta = randint(1000, 9999)
        if porta in portas: 
            continue

        try:
            t = multiprocessing.Process(target=inicializa_servidor, args=(porta,))
            t.start()
            portas.append(porta)
            processos.append(t)
            quantidade_servidores -= 1
        except:
            pass

    return portas, processos