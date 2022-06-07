import socket
import json
import os

# multiprocessing
import select
import threading
import sys

import Utils

# window interface imports
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


HOST = ""          # Any address will be able to reach server side
DOOR = 5000      # Door used by both client/server

MAX_CONNECTIONS = 30

inputs = [sys.stdin]

connections = {}

connections_changed = False

# Convert data to ListStore (lists that TreeViews can display)
connections_list_store = Gtk.ListStore(str, str, str)

def createServerConnection():
    # create socket (instantiation)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind door and interface to communicate with clients
    sock.bind((HOST, DOOR))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set max number of connections and wait for at least one connection
    sock.listen(MAX_CONNECTIONS)

    sock.setblocking(False)

    inputs.append(sock)

    return sock

def interface():

    threads = []
    passiveSock = createServerConnection()

    newThread = threading.Thread(target=drawConnections)
    newThread.start()
    threads.append(newThread)

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
    
    try:
        command = json_req["operacao"]
        json_string = {"operacao": command, "status": 200, "clientes": connections, "Usuario": {"Endereco": str(address), "Porta": int(DOOR)}}
    except Exception as error:
        json_string = {"operacao": command, "status": 400, "mensagem": "Erro ao obter a lista"}

    answer = json.dumps(json_string)
    return answer

def login(json_req, address):
    command = json_req["operacao"]
    username = json_req["username"]
    userdoor = json_req["porta"]
    json_string = {}
    
    if not (username in connections):
        connections[username] = {"Endereco": str(address), "Porta": int(userdoor)}
        connections_list_store.append(list((
                username, 
                connections[username]["Endereco"], 
                connections[username]["Porta"]
                )))
        connections_changed = True
        json_string = {"operacao": command, "status": 200, "mensagem": "Login com sucesso"}
    else:
        json_string = {"operacao": command, "status": 400, "mensagem": "Username em Uso"}
    
    answer = json.dumps(json_string)
    return answer

def logoff(json_req):
    try:
        command = json_req["operacao"]
        username = json_req["username"]

        if not (username in connections):
            raise Exception()

        del connections[username]

        for row in connections_list_store:
            if (row[0] == username):
                connections_list_store.remove(row.iter)
                break

        json_string = {"operacao": command, "status": 200, "mensagem": "Logoff com sucesso"}
        connections_changed = True
    except Exception:
        json_string = {"operacao": command, "status": 400, "mensagem": "Erro no Logoff"}

    answer = json.dumps(json_string)
    return answer

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Central Server Connections")
        Gtk.Window.set_default_size(self, 640, 480)
        layout = Gtk.Box()
        self.add(layout)

        for connection in connections:

            connections_list_store.append(list((
                connection, 
                connections[connection]["Endereco"], 
                connections[connection]["Porta"]
                )))

        # TreeView is the item that is displayed
        connections_tree_view = Gtk.TreeView(connections_list_store)

        for i, col_title in enumerate(["Username", "Address", "Door"]):

            # Render means how to draw the data
            renderer = Gtk.CellRendererText()

            # Create colmns (title is column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)

            # Add column to TreeView
            connections_tree_view.append_column(column)

        # Add TreeView to main layout
        layout.pack_start(connections_tree_view, True, True, 0)

        os.system("clear")
        print("Central Server Online - Accepting Connections...")

def drawConnections():

    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

    print("Central Server Offline - Not Receiving Connections...")
    return

def main():
    interface()

if __name__ == "__main__":
    main()
