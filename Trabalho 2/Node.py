import rpyc
from rpyc.utils.server import ThreadedServer
from Blockchain import Blockchain

# Todos os Estados Globais
# neighbors - lista de tuplas (ip, porta)

state = {
    "neighbors": set(),
    "porta_server": None,
    "endereco_server": None,
    "blockchain": Blockchain()
}


class Node(rpyc.Service):
    global state

    def on_connect(self, conx):
        pass
        # print("connect")

    def on_disconnect(self, conx):
        pass
        # print("disconnect")

    def exposed_notify_new(self, new_ip, new_port):
        state["neighbors"].add( (new_ip, new_port) )

    def exposed_return_neighbors(self):
        return state["neighbors"]

    def exposed_return_blockchain(self):
        return state["blockchain"].return_blocks()
        

    
def inicializa_servidor(port):
    global state
    
    state["porta_server"] = port

    try:
        node = ThreadedServer(Node, port=port, protocol_config={"allow_public_attrs": True})
        node.start()
    except:
        print('\033[91m' + "\nErro: Erro ao tentar inicializar o servidor." + '\033[0m')
        exit(0)
