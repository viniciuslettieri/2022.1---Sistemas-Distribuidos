import socket
import json

# multiprocessing
import select
import threading
import sys

import Utils

HOST = ""          # Any address will be able to reach server side
DOOR = 5000      # Door used by both client/server

MAX_CONNECTIONS = 30

inputs = [sys.stdin]

connections = {}


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
                if (command == "exit"):
                    for t in threads:
                        t.join()
                    passiveSock.close()
                    sys.exit()

def requisition(newSock, address):
    while True:
        # Keep blocked until receives message from client side
        message = Utils.reconstroi_mensagem(newSock)
        # If client side doesn"t send a message end communication
        if not message:
            print(str(address) + "-> ended")
            newSock.close()  # encerra a conexao com o cliente
            return
        else:
            print("Message received from (" + str(address[1]) + "): " + message)

            json_string = message
            json_req = json.loads(json_string)

            try:
                answer = data_acess(json_req, address[0])

                if (answer):
                    # Send the same message received to client side
                    answer = Utils.constroi_mensagem(answer)
                    newSock.sendall(answer)
            except Exception as error:
                newSock.sendall(Utils.constroi_mensagem(str(error)))

def data_acess(json_req, address):
    command = json_req["operacao"]
    print(command)
    if (command == "get_lista"):
        return get_lista(json_req, address) 
    elif (command == "login"):
        return login(json_req, address)
    elif (command == "logoff"):
        return logoff(json_req)
    else:
        raise ModuleNotFoundError()    

def get_lista(json_req, address):
    command = json_req["operacao"]
    json_string = {"operacao": command, "status": str(200), "clientes": connections, "Usuario": {"Endereco": str(address), "Porta": str(DOOR)}}
    answer = json.dumps(json_string)
    return answer

def login(json_req, address):
    command = json_req["operacao"]
    username = json_req["username"]
    json_string = {}

    if not (username in connections):
        userdoor = json_req["porta"]
        connections[username] = {"Endereco": str(address), "Porta": str(userdoor)}
        json_string = {"operacao": command, "status": str(200), "mensagem": "Login com sucesso"}

    else:
        json_string = {"operacao": command, "status": str(400), "mensagem": "Username em Uso"}
    
    answer = json.dumps(json_string)
    return answer

def logoff(json_req):
    command = json_req["operacao"]
    username = json_req["username"]
    print(json_req)
    del connections[username]
    print(json_req)

    json_string = {"operacao": command, "status": str(200), "mensagem": "Logoff com sucesso"}
    answer = json.dumps(json_string)
    return answer

def main():
    interface()

if __name__ == "__main__":
    main()
