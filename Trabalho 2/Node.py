import rpyc
from rpyc.utils.server import ThreadedServer

# Todos os Estados Globais
# neighbors - lista de tuplas (ip, porta)

state = {
    "neighbors": set(),
    "porta_server": None,
    "endereco_server": None
}


class Node(rpyc.Service):
    global state

    def on_connect(self, conx):
        print("connect")

    def on_disconnect(self, conx):
        print("disconnect")

    def exposed_notify_new(self, new_ip, new_port):
        state["neighbors"].add( (new_ip, new_port) )

    def exposed_return_neighbors(self):
        return state["neighbors"]
        

    
def inicializa_servidor(port):
    global state
    
    state["porta_server"] = port

    node = ThreadedServer(Node, port=port)
    node.start()
