import socket
import string
import threading

import Estrutura
from ModuloCliente import ModuloCliente
from ModuloServidor import ModuloServidor, ModuloCoordenadorServidores
from Interface import *

def main():  
    # global interface, clienteServidorCentral, HOST_SERVIDOR_CENTRAL, PORT_SERVIDOR_CENTRAL
    
    print(Estrutura.clienteServidorCentral)
    Estrutura.clienteServidorCentral = ModuloCliente(
        Estrutura.HOST_SERVIDOR_CENTRAL, Estrutura.PORT_SERVIDOR_CENTRAL
    )

    # interface = Interface()
    thread_interface = threading.Thread(target=atende_stdin)   
    thread_interface.start()

    thread_interface.join()


if __name__ == "__main__":
    main()
