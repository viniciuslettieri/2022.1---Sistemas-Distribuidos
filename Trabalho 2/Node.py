import rpyc
from rpyc.utils.server import ThreadedServer
from Blockchain import Block, Blockchain
from State import state

class Node(rpyc.Service):
    global state
    
    def exposed_notify_new(self, new_ip, new_port):
        state["neighbors"].add( (new_ip, new_port) )

    def exposed_return_neighbors(self):
        return state["neighbors"]

    def exposed_return_blockchain(self):
        return state["blockchain"].get_blocks()
    
    def exposed_add_new_block(self, block: Block):
        state["blockchain"].add_block(block)
    
def inicializa_servidor(port):
    global state
    
    state["porta_server"] = port

    try:
        node = ThreadedServer(Node, port=port, protocol_config={"allow_public_attrs": True})
        node.start()
    except:
        print('\033[91m' + "\nErro: Erro ao tentar inicializar o servidor." + '\033[0m')
        exit(0)
