
import json
import socket
import threading
import Utils


HOST = 'localhost'      # ip/server to send messages. If it's in another computer, input the ip
DOOR = 5000             # Door used by both client/server

MESSAGE_SIZE = 256      # We will use one unsigned byte to represent size of message. 1 byte for length of message, and 2^8 - 1 for message.
conections = []         # array with the current open connectios
usersOnline = {}        # Local representation of the server's client list
serverCommands = {"get_lista":True,"login":True,"Logoff":True}      # possible actions a user can reques from the server
isLogged = False        # Log state of the user


def createConnection(host, door):
    # create socket (instantiation)
    activeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect with client server side
    activeSock.connect((host, door))
    return activeSock

socketServidor = createConnection(HOST,DOOR) #initialize a connection with the central server   

#garantees that the user can only use the commands alowed in their current log status
def checkLoginStatus(operation):
    needsLogin = False if operation == "login" else True
    if(needsLogin and not isLogged):
        raise Exception("Você precisa fazer login antes de realizar essa operação")
    elif(not needsLogin and isLogged):
        raise Exception("Voce já fez login. Não é possível fazer novamente")


#Parses a command made by the user so the server can understand it    
def parseUserCommand(userInput):
    parsedCommand = ''
    operation = userInput.split(" ")[0]
    checkLoginStatus(operation)
    if(operation == "get_lista"):
        parsedCommand = '{"operacao":"get_lista"}'
    elif(operation == "login"):
        username  = userInput.split(" ")[1]
        port = userInput.split(" ")[2]
        parsedCommand = '{"operacao":"login","username":"'+username+'"  ,"porta":"'+port+'"}'
    elif(operation =="logoff"):
        username  = userInput.split(" ")[1]
        parsedCommand = '{"operacao":"logoff","username":"'+username+'"}'
    return parsedCommand


#Sends a request to the server
def sendServerRequest(request):
    menssage = Utils.constroi_mensagem(request)
    socketServidor.sendall(menssage)


#Receivs the server response
def receivServerResponse():
    response = Utils.reconstroi_mensagem(socketServidor)
    response = json.loads(response)
    
    return response


#Handle responses from get_lista type requests
def handleGetListaResponse(response):
    status = response["status"]
    if(status == "200"):
        usersOnline = response["clientes"]
    else:
        exceptionMessage = "Comando get_lista mal-sucedido erro {erro}".format(erro = status)
        raise Exception(exceptionMessage)


#Handle responses from login type requests
def handleLoginResponse(response,userInput):
    status = response["status"]
    username = userInput.split(" ")[1]
    if(status =="200"):
        print("Bem vindo "+username+"!")
        isLogged = True
    else:
        exceptionMessage = "O username {user} já existe :(\n Tente outro ;)".format(user = username)
        raise Exception(exceptionMessage)


#Handle response from logoff type requests
def handleLogoffResponse(response,userInput):
    status = response["status"]
    username = userInput.split(" ")[1]
    if(status =="200"):
        for connection in conections:#End all peer to peer conections
            connection.close()
        print("Você foi desconectado com sucesso\n Até a próxima:)")
        isLogged = False
    else:
        exceptionMessage = "Algo de errado aconteceu ao tentar deslogar {user}. Tente novament.".format(user = username)
        raise Exception(exceptionMessage)


#Central function when dealing with server Commands
def handleServerRequest(userInput):
    try:
        parsedInput = parseUserCommand(userInput)
        sendServerRequest(parsedInput)
        response = receivServerResponse()
        operationType = response["operacao"]
        if(operationType == "get_lista"):
            handleGetListaResponse(response)
        elif(operationType =="login"):
            handleLoginResponse(response,userInput)
        elif(operationType=="logoff"):
            handleLogoffResponse(response,userInput)
        else:
            raise Exception("Operação desconhecida")
    except Exception as error:
        print(error)



#Deals with the different possible inputs passed by the user
def handleUserInput(userInput):
    isForServer = True if serverCommands[userInput.split(" ")[0]] else False # searches for input in the command list
    if(isForServer):
        handleServerRequest(userInput)
        return
    

def main():
   
    # Keep sending message to server
    userInput = input()

    while (userInput != "exit"):  # exit will close communication
        handleUserInput(userInput)
        # Keep receiving user input
        userInput = input()

    # Close connection
    socketServidor.close()


main()