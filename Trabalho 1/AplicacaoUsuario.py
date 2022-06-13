import socket
import string
import threading
import select
import argparse
import sys

import Estrutura
from ModuloCliente import ModuloCliente
from ModuloServidor import ModuloServidor, ModuloCoordenadorServidores
from Interface import *
from Utils import printLog, activateLog, log


def main():     
    # cliente para comunicar com o servidor central
    Estrutura.clienteServidorCentral = ModuloCliente(
        Estrutura.HOST_SERVIDOR_CENTRAL, Estrutura.PORT_SERVIDOR_CENTRAL
    )

    # responsavel pelas componentes de interface e interacao
    # thread_interface = threading.Thread(target=atende_stdin)   
    # thread_interface.start()
    Estrutura.select_inputs.append(sys.stdin)

    # voce pode passar argumentos de log para prints de log
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', help="Activate log")
    args = parser.parse_args()

    if args.log: activateLog()
    # printLog(f"Thread Interface {thread_interface.name} {thread_interface.ident}")

    # aguarda inputs
    r, escrita, excecao = select.select(Estrutura.select_inputs, [], [])
    for ready in r:
        if ready == sys.stdin:
            atende_stdin()
        elif ready == Estrutura.coordenadorServidores.sock:
            Estrutura.coordenadorServidores.trata_novos_servidores()
        else:
            servidor = Estrutura.socket_servidores[ready]
            servidor.atende_comunicacao()

    thread_interface.join()


if __name__ == "__main__":
    main()
