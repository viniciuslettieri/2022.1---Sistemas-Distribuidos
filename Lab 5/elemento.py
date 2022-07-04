import rpyc
from rpyc.utils.server import ThreadedServer
from random import randint
import multiprocessing
import threading
import os


# lista das portas - os identificadores sao os index na lista
replicas = [7048, 1476, 7037]

variavel = 0
historico = []
foi_propagado = True              # diz se os updates foram propagados
copia_primaria = False
porta_server = None
identificador = None
mutex_variavel = threading.Lock()

ack_update_quant = 0


class Elemento(rpyc.Service):
    global porta_server

    def on_connect(self, conx):
        global identificador

    def on_disconnect(self, conx):
        global identificador

    def exposed_list_neighbors(self):
        global replicas
        return replicas

    def exposed_return_id(self):
        global identificador
        return identificador

    def exposed_return_variable(self):
        global variavel
        return variavel

    def exposed_return_historic(self):
        global historico
        return historico

    def exposed_write_variable(self, value):
        global replicas, variavel, historico, copia_primaria, porta_server, mutex_variavel, foi_propagado

        # Obtem a posse da copia primaria
        if copia_primaria == False:
            for replica in replicas:
                if replica != porta_server:
                    server = rpyc.connect('localhost', replica)
                    response = server.root.request_copia_primaria()
                    if response == True:
                        copia_primaria = True 
                        break
            else:
                raise Exception("Error: Could not find primary copy.")

        mutex_variavel.acquire()
        variavel = value
        historico.append((porta_server, value))
        foi_propagado = False
        mutex_variavel.release()

    def exposed_propagar_outros(self):
        global ack_update_quant, porta_server, mutex_variavel, historico, foi_propagado
        
        if foi_propagado:
            return

        mutex_variavel.acquire()
        ack_update_quant = 0
        for replica in replicas:
            if replica != porta_server:
                server = rpyc.connect('localhost', replica)
                server.root.copy_update(historico[-1], porta_server)
        
        mutex_variavel.acquire()
        mutex_variavel.release()
        foi_propagado = True

    def exposed_request_copia_primaria(self):
        global copia_primaria

        if copia_primaria == True:
            self.exposed_propagar_outros()
            copia_primaria = False
            return True
        
        else:
            return False

    def exposed_copy_update(self, last_update, original_port):
        global variavel, historico, mutex_variavel
        
        mutex_variavel.acquire()
        historico.append(last_update) 
        variavel = last_update[1]
        mutex_variavel.release()   

        server = rpyc.connect('localhost', original_port)
        server.root.ack_update()

    def exposed_ack_update(self):
        global replicas, historico, mutex_variavel, ack_update_quant

        ack_update_quant += 1
        if ack_update_quant == len(replicas) - 1:
            mutex_variavel.release()   
        

def inicializa_servidor(port):
    global porta_server, replicas, identificador, copia_primaria
    
    porta_server = port
    identificador = replicas.index(porta_server) + 1
    if identificador == 1:
        copia_primaria = True

    k = ThreadedServer(Elemento, port=port)
    k.start()

def menu():
    global porta_server
    
    server = rpyc.connect('localhost', porta_server)
    while True:
        print("\nOpções Disponíveis:")
        print("1. ler o valor atual de X na replica.")
        print("2. ler o historico de alterações do valor de X.")
        print("3. alterar o valor de X.")
        print("4. propagar as mudanças locais.")
        print("5. finalizar o programa. \n")

        opcao = int(input("Selecione a Opção: "))
        if opcao == 1:
            print(server.root.return_variable())
        elif opcao == 2:
            print(server.root.return_historic())
        elif opcao == 3:
            value = int(input("Qual valor será escrito: "))
            server.root.write_variable(value)
        elif opcao == 4:
            server.root.propagar_outros()
        elif opcao == 5:
            server.close()
            print("\nPrograma Finalizado!\n")
            os._exit(0)

if __name__ == "__main__":
    print("Portas disponíveis:", replicas)
    
    porta = int(input("Selecione uma das portas: "))
    while porta not in replicas:
        porta = int(input("Selecione uma das portas: "))
    
    k = threading.Thread(target=inicializa_servidor, args=(porta,))
    k.start()

    menu()
