import socket
import string
import threading
import argparse

import Estrutura
from ModuloCliente import ModuloCliente
from ModuloServidor import ModuloServidor, ModuloCoordenadorServidores
from Interface import *
from Utils import printLog, activateLog, log

def main():  
    # global interface, clienteServidorCentral, HOST_SERVIDOR_CENTRAL, PORT_SERVIDOR_CENTRAL
    
    Estrutura.clienteServidorCentral = ModuloCliente(
        Estrutura.HOST_SERVIDOR_CENTRAL, Estrutura.PORT_SERVIDOR_CENTRAL
    )

    # interface = Interface()
    thread_interface = threading.Thread(target=atende_stdin)   
    thread_interface.start()

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', help="Activate log")
    args = parser.parse_args()

    if args.log: activateLog()
    printLog(f"[Log: Thread Interface {thread_interface.name} {thread_interface.ident}]")

    thread_interface.join()


if __name__ == "__main__":
    main()
