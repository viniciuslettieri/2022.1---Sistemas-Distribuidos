import rpyc
from rpyc.utils.server import ThreadedServer, ThreadPoolServer
import argparse
from random import randint
from datetime import datetime
import multiprocessing


vizinhos = []
identificador = None
porta_server = None
id_lider = None


# Variaveis de estado para uma eleicao
last_election = None
received_echo = 0
received_ack = 0
best_id = None
curent_parent_port = None


class Elemento(rpyc.Service):
    global porta_server

    def on_connect(self, conx):
        global identificador

    def on_disconnect(self, conx):
        global identificador

    def exposed_return_id(self):
        global identificador
        return identificador

    def exposed_return_id_lider(self):
        global id_lider
        return id_lider

    def exposed_list_neighbors(self):
        global vizinhos
        return vizinhos

    def exposed_start_election(self):
        global identificador, porta_server
        print(f"Eleição Iniciada em {porta_server} [id: {identificador}]")
        self.exposed_probe(None, datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

    def treat_returns(self):
        global vizinhos, identificador, received_echo, received_ack, best_id, curent_parent_port
        
        if curent_parent_port == None:
            num_vizinhos = len(vizinhos)
        else:
            num_vizinhos = len(vizinhos) - 1

        # Checa se recebeu todas as respostas
        if received_echo + received_ack == num_vizinhos:
            # Checa se ele é o Iniciador da Eleicao
            if curent_parent_port == None:   
                print("Eleição Finalizada:", best_id)

                # Emite para os vizinhos o eleito      
                for porta_viz in vizinhos:
                    server = rpyc.connect('localhost', porta_viz)
                    if porta_viz != curent_parent_port:
                        server.root.eleito(identificador, best_id)
            else:
                server = rpyc.connect('localhost', curent_parent_port)
                server.root.echo(best_id)

    def exposed_probe(self, parent, origin):
        global vizinhos, identificador, last_election, received_echo, received_ack, best_id, curent_parent_port
        
        # Checa se recebeu um probe da mesma eleicao que esta participando
        if last_election != None and last_election == origin:
            server = rpyc.connect('localhost', parent[1])
            server.root.ack()
            return

        # Participando de uma nova eleicao - reinicia estados
        last_election = origin
        received_echo = 0
        received_ack = 0
        best_id = identificador
        curent_parent_port = parent[1] if parent != None else None

        for porta_viz in vizinhos:
            server = rpyc.connect('localhost', porta_viz)
            if parent == None or porta_viz != curent_parent_port:
                server.root.probe((identificador, porta_server), origin)

        # Tratamento para folhas
        if parent != None and len(vizinhos) <= 1:
            self.treat_returns()

    def exposed_echo(self, received_id):
        global identificador, received_echo, best_id
        received_echo += 1

        # Guarda o melhor id ate o momento
        best_id = max(best_id, received_id)
        self.treat_returns()
    
    def exposed_ack(self):
        global identificador, received_ack
        received_ack += 1
        self.treat_returns()
    
    def exposed_eleito(self, parent, id_lider_recebido):
        global vizinhos, identificador, id_lider
        
        # Se for igual ja propagou anteriormente
        if id_lider_recebido == id_lider:
            return

        id_lider = id_lider_recebido

        for porta_viz in vizinhos:
            server = rpyc.connect('localhost', porta_viz)
            if server.root.return_id() == parent: continue
            server.root.eleito(identificador, id_lider)

    def exposed_connect_to(self, port):
        global vizinhos
        vizinhos.append(port)

    def exposed_disconnect_from(self, port):
        global vizinhos
        vizinhos.remove(port)


def inicializa_servidor(port):
    global identificador, porta_server
    identificador = randint(100, 999)
    porta_server = port
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