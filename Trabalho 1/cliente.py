import socket
from traceback import print_tb
import Utils
HOST = 'localhost'  # ip/server to send messages. If it's in another computer, input the ip
DOOR = 5000        # Door used by both client/server

MESSAGE_SIZE = 256 # We will use one unsigned byte to represent size of message. 1 byte for length of message, and 2^8 - 1 for message.
conections = []#array with the current open connectios

def createConnection(host, door):

    # create socket (instantiation)
    activeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect with client server side
    activeSock.connect((host, door))
    return activeSock
#Parses a command made by the user so the server can understand it
socketServidor = createConnection(HOST,DOOR) #initialize a connection with the central server    
def parseUserCommand(userInput):
    parsedCommand = ''
    
    if(userInput == "get_lista"):
        
        parsedCommand = "{'operacao':'get_lista'}"
    elif(userInput == "login"):
        username  = userInput.split(" ")[1]
        port = input.split(" ")[2]
        parsedCommand = "{'operacao':'login','username':{user},'porta':{porta}}".format(user = username, porta = port)
    else:
        username  = userInput.split(" ")[1]
        parsedCommand = "{'operacao':'login','username':{user}}".format(user = username)
    return parsedCommand
def handleServerRequest(userInput):
    parsedInput = parseUserCommand(userInput)
    menssage = Utils.constroi_mensagem( parsedInput)
    socketServidor.sendall(menssage)
    message = Utils.reconstroi_mensagem(socketServidor)
    print(message)
    


#Deals with the different possible inputs passed by the user
def handleUserInput(userInput):
    isForServer = 1 if (userInput =="get_lista" or userInput =="login" or userInput =="logoff") else 0
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