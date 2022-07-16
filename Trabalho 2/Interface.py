import rpyc
import threading
import os
import socket    

from Node import inicializa_servidor, state

def conectar_com_novos(novos_nodes: set):
    """ Conecta recursivamente com os vizinhos dos novos Nodes """

    global state
    
    novos_vizinhos = set()
    for novo_node in novos_nodes:
        try:
            server = rpyc.connect(novo_node[0], novo_node[1])

            server.root.notify_new(state["endereco_server"], state["porta_server"])

            myself = (state["endereco_server"], state["porta_server"])

            outros_vizinhos = set()
            for k in server.root.return_neighbors():
                outros_vizinhos.add(k)
            
            outros_vizinhos.discard(myself)

            novos = outros_vizinhos.difference(state["neighbors"])
            novos_vizinhos = novos_vizinhos.union(novos)

            server.close()

            state["neighbors"].add(novo_node)
            print(f"Nova Conexão: {novo_node}.")

        except:
            print(f"Erro: Não foi possível conectar com {novo_node}.")
    
    if len(novos_vizinhos) > 0:
        conectar_com_novos(novos_vizinhos)

def extrair_blockchain(node_ip, node_port):
    """ ... """

    global state

    for vizinho in state["neighbors"]:
        print(vizinho)


def conectar_com_blockchain():
    """ Conecta o Node atual recursivamente com toda a vizinhança de outro Node.
        Obtem o bloco mais recente de todos os vizinhos.
        Solicita a blockchain completa daquele com o bloco mais recente. """

    global state

    # outro_node_ip = input("Insira o IP do Node de Origem: ")
    outro_node_ip = '127.0.1.1'
    outro_node_porta = int(input("Insira a Porta do Node de Origem: "))

    conectar_com_novos({(outro_node_ip, outro_node_porta)})
    extrair_blockchain(outro_node_ip, outro_node_porta)

def listar_nodes_vizinhos():
    global state

    print("Vizinhos: ")
    print(state["neighbors"])

def mostra_opcoes():
    print("-" * 50)
    print("Opções Disponíveis:")
    print("1. Iniciar Blockchain")
    print("2. Conectar com Blockchain")
    print("3. Listar Nodes Vizinhos")
    print("F. finalizar o programa. \n")

def menu():
    global state
    
    while True:
        mostra_opcoes()

        opcao = input("Selecione a Opção: ")
        if opcao == "1":
            pass
        elif opcao == "2":
            conectar_com_blockchain()
        elif opcao == "3":
            listar_nodes_vizinhos()
        elif opcao.upper() == "F":
            server = rpyc.connect('localhost', state["porta_server"])
            server.close()
            print("\nPrograma Finalizado!\n")
            os._exit(0)


if __name__ == "__main__":
    # state["endereco_server"] = requests.get('https://checkip.amazonaws.com').text.strip()
    state["endereco_server"] = socket.gethostbyname(socket.gethostname())


    print("Seu Endereço de IP: " + state["endereco_server"])  
    state["porta_server"] = int(input("Insira sua Porta de Servidor: "))
    
    node = threading.Thread(target=inicializa_servidor, args=(state["porta_server"],))
    node.start()

    menu()
