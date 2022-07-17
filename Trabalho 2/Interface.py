import rpyc
import threading
import os
import socket    
import requests

from Node import inicializa_servidor, state
from Blockchain import Blockchain

class bcolors:
    colors = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKCYAN': '\033[96m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    @staticmethod
    def print_color(str, color):
        print(bcolors.colors[color] + str + bcolors.colors["ENDC"])


def conectar_com_novos(novos_nodes: set):
    """ Conecta recursivamente com os vizinhos dos novos Nodes """

    global state
    
    novos_vizinhos = set()
    for novo_node in novos_nodes:
        try:
            server = rpyc.connect(novo_node[0], novo_node[1], config={"allow_public_attrs": True})

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
            bcolors.print_color(f"Nova Conexão: {novo_node}.", "OKGREEN")

        except:
            bcolors.print_color(f"Erro: Não foi possível conectar com {novo_node}.", "FAIL")
    
    if len(novos_vizinhos) > 0:
        conectar_com_novos(novos_vizinhos)

def iniciar_blockchain():
    global state

    state["blockchain"] = Blockchain()

    bcolors.print_color("\nIniciando Blockchain com o Bloco Genesis:\n", "HEADER")
    state["blockchain"].start_blockchain()
    state["blockchain"].print_blockchain()

def extrair_blockchain(node_ip, node_port):
    """ Obtem de outro Node sua blockchain """

    global state

    try:
        server = rpyc.connect(node_ip, node_port, config={"allow_public_attrs": True})
        blocks = server.root.return_blockchain()

        if len(blocks) == 0:
            raise ValueError

        new_blockchain = Blockchain(blocks)
        state["blockchain"] = new_blockchain
        server.close()

        bcolors.print_color(f"\nBlockchain com { len(state['blockchain'].blocks) } blocos obtida com sucesso.\n", "OKGREEN")

    except ValueError:
        bcolors.print_color("\nErro: A Blockchain da Origem não é válida.\n", "FAIL")

    except:
        bcolors.print_color("\nErro: Não foi possível recuperar a blockchain da Origem.\n", "FAIL")

def conectar_com_blockchain():
    """ Conecta o Node atual recursivamente com toda a vizinhança de outro Node.
        Obtem o bloco mais recente de todos os vizinhos.
        Solicita a blockchain completa daquele com o bloco mais recente. """

    global state

    outro_node_ip = '127.0.1.1'
    # outro_node_ip = input("Insira o IP do Node de Origem: ")
    outro_node_porta = int(input("Insira a Porta do Node de Origem: "))
    
    print("")
    conectar_com_novos({(outro_node_ip, outro_node_porta)})
    extrair_blockchain(outro_node_ip, outro_node_porta)

def listar_nodes_vizinhos():
    global state

    bcolors.print_color("\nLista dos Nós Vizinhos:\n", "HEADER")
    if len(state["neighbors"]) == 0:
        print("Não há vizinhos conectados.\n")
    else:
        print(state["neighbors"], "\n")

def mostrar_blockchain():
    global state

    bcolors.print_color("\nBlockchain Atual:\n", "HEADER")
    state["blockchain"].print_blockchain()

def mostrar_blocos():
    global state

    bcolors.print_color("\nBlocos Atuais neste Node:\n", "HEADER")
    state["blockchain"].print_blocks()

def mostra_opcoes():
    global state
    has_blockchain = state["blockchain"]
    
    print("\n", "-" * 50)
    bcolors.print_color("\n- Opções Disponíveis -\n", "HEADER")
    print("1. Iniciar Blockchain com Genesis")
    print("2. Entrar em Blockchain de outro Node")
    print("3. Listar Nodes Vizinhos")
    if has_blockchain: print("4. Mostrar Blockchain Atual")
    if has_blockchain: print("5. Mostrar Todos os Blocos")
    if has_blockchain: print("6. Criar Transação")
    if has_blockchain: print("7. Criar fork malicioso")
    print("F. Finalizar o Programa. \n")

def criar_transacao():
    global state
    transacao = input("Escreva qual será sua transação: ")
    state["blockchain"].add_transaction(str(transacao))

def iniciar_fork_malicioso():
    global state
    blockchain_index = len(state["blockchain"].blocks) - 1
    index = int(input("Escreva o indice do fork malicioso (atualmente " + str(blockchain_index) + "): "))
    if (index >= 1 and index <= blockchain_index):
        state["blockchain"].remove_until_index_reached(index)
    else:
        print("Valor Inválido: Insira um índice menor para iniciar o fork malicioso")

def menu():
    global state

    while True:
        has_blockchain = state["blockchain"]
        mostra_opcoes()

        opcao = input("Selecione a Opção: ")
        os.system('cls' if os.name == 'nt' else 'clear')
        if opcao == "1":
            iniciar_blockchain()
        elif opcao == "2":
            conectar_com_blockchain()
        elif opcao == "3":
            listar_nodes_vizinhos()
        elif opcao == "4" and  has_blockchain:
            mostrar_blockchain()
        elif opcao == "5" and  has_blockchain:
            mostrar_blocos()
        elif opcao == "6" and  has_blockchain:
            criar_transacao()
        elif opcao == "7" and has_blockchain:
            iniciar_fork_malicioso()
        elif opcao.upper() == "F":
            server = rpyc.connect('localhost', state["porta_server"], config={"allow_public_attrs": True})
            server.close()
            print("\nPrograma Finalizado!\n")
            os._exit(0)


if __name__ == "__main__":
    # state["endereco_server"] = requests.get('https://checkip.amazonaws.com').text.strip()
    state["endereco_server"] = socket.gethostbyname(socket.gethostname())

    print("Seu Endereço de IP: " + state["endereco_server"])  
    state["porta_server"] = int(input("Insira sua Porta de Servidor: "))
    
    try:
        node = threading.Thread(target=inicializa_servidor, args=(state["porta_server"],))
        node.start()

        menu()
    except:
       bcolors.print_color("\nErro: Erro interno.", "FAIL")
     
