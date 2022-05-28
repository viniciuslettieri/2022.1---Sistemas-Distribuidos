import socket
import operator
import json

# multiprocessing
import select
import threading
import sys

HOST = ''          # Any address will be able to reach server side
DOOR = 5000      # Door used by both client/server

MESSAGE_SIZE = 256 # We will use one unsigned byte to represent size of message. 1 byte for length of message, and 2^8 - 1 for message.
MAX_CONNECTIONS = 5
DICT_RETURN_SIZE = 5

inputs = [sys.stdin]

connections = {'luanzinho32': {'Endereco': '10.10.10.10', 'Porta': '5000'}}


def createServerConnection():
    # create socket (instantiation)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind door and interface to communicate with clients
    sock.bind((HOST, DOOR))

    # Set max number of connections and wait for at least one connection
    sock.listen(MAX_CONNECTIONS)

    sock.setblocking(False)

    inputs.append(sock)

    return sock

def interface():

    threads = []
    passiveSock = createServerConnection()

    print("Accepting Connections...")

    while True:
        r, escrita, excecao = select.select(inputs, [], [])

        for ready in r:
            if ready == passiveSock:
                newSock, address = passiveSock.accept()
                print("On " + str(address[0]) +
                      " connecting with " + str(address[1]))

                newThread = threading.Thread(
                    target=requisition, args=(newSock, address))
                newThread.start()
                threads.append(newThread)
            elif ready == sys.stdin:
                command = input()
                if (command == 'exit'):
                    for t in threads:
                        t.join()
                    passiveSock.close()
                    sys.exit()

def requisition(newSock, address):
    while True:
        # Keep blocked until receives message from client side
        message = newSock.recv(MESSAGE_SIZE)
        print(message)
        print(int.from_bytes(message[0:1], 'little'))
        # If client side doesn't send a message end communication
        if not message:
            print(str(address) + '-> ended')
            newSock.close()  # encerra a conexao com o cliente
            return
        else:
            print("Message received from (" + str(address[1]) + "): " +
                  str(message[1:], encoding='utf-8'))

            command = str(message[1:], encoding='utf-8')

            try:
                answer = data_acess(command, address)

                if (answer):
                    # Send the same message received to client side
                    newSock.send(
                        bytes(answer, encoding='utf-8'))
            except Exception as error:
                newSock.send(bytes(str(error), encoding='utf-8'))


def data_acess(command, address):
    if (command == "get_lista"):
        return get_lista(address) 
    else:
        raise ModuleNotFoundError()    

def get_lista(address):
    json_string = {"operacao": "get_lista", "status": str(200), "clientes": connections, "usuario": {"endereco": str(address[0]), "porta": str(DOOR)}}
    answer = json.dumps(json_string)
    return answer


def main():
    interface()


if __name__ == "__main__":
    main()
