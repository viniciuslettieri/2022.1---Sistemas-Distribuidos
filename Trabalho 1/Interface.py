import string
import threading
import json
import argparse

import Estrutura
from Utils import constroi_mensagem, reconstroi_mensagem
from ModuloCliente import ModuloCliente
from ModuloServidor import ModuloServidor, ModuloCoordenadorServidores

# Makes a log if the -l (--log) flag is active
#def printLog(message):
#    # Gets flag from command line
#    parser = argparse.ArgumentParser()
#
#   parser.add_argument("-l", "--log", help="Log", type=bool)
#   if () print(f"[Log: ${message}]")

# Guarantees that the user can only use the commands allowed in their current log status
def checkLoginStatus(operation):
    print(f"[Log: checkLoginStatus]")
    needsLogin = False if operation == "login" else True
    if(needsLogin and not Estrutura.isLogged):
        raise Exception("Você precisa fazer login antes de realizar essa operação")
    elif(not needsLogin and Estrutura.isLogged):
        raise Exception("Voce já fez login. Não é possível fazer novamente")

def handleLoginInitializations():
    print(f"[Log: handleLoginInitializations]")
    coordenador = ModuloCoordenadorServidores('', Estrutura.userport)
    thread_coordenador = threading.Thread(target=coordenador.trata_novos_servidores)   
    thread_coordenador.start()

# Parses a command made by the user so the server can understand it    
def parseUserCommand(userInput):
    print(f"[Log: parseUserCommand]")
    parsedCommand = ''
    secoes = userInput.split(" ")
    operation = secoes[0]

    checkLoginStatus(operation)

    if operation == "get_lista":
        parsedCommand = '{"operacao": "get_lista"}'

    elif operation == "login":
        parsed_username = secoes[1]
        parsed_port = secoes[2]
        parsedCommand = '{"operacao": "login", "username": "' + parsed_username + '" ,"porta": "' + parsed_port + '"}'
        Estrutura.userport = parsed_port

    elif operation == "logoff":
        parsed_username  = secoes[1]
        parsedCommand = '{"operacao": "logoff", "username": "' + parsed_username + '"}'

    return parsedCommand

def printListaClientes():
    print("\n> Clientes Ativos:")
    for usuario in Estrutura.lista_clientes:
        dados = Estrutura.lista_clientes[usuario]
        print(f"{usuario}: ({dados['Endereco']}, {dados['Porta']})")

# Handle responses from get_lista type requests
def handleGetListaResponse(response):
    print(f"[Log: handleGetListaResponse]")
    status = response["status"]
    if(status == "200"):
        Estrutura.lista_clientes = response["clientes"]
        printListaClientes()
    else:
        exceptionMessage = "Comando get_lista mal-sucedido erro {erro}".format(erro = status)
        raise Exception(exceptionMessage)

# Handle responses from login type requests
def handleLoginResponse(response, userInput):
    print(f"[Log: handleLoginResponse]")
    status = response["status"]
    parsed_username = userInput.split(" ")[1]

    if(status == "200"):
        print("Bem vindo " + parsed_username + "!")
        Estrutura.isLogged = True
        Estrutura.username = parsed_username
        handleLoginInitializations()

    else:
        exceptionMessage = f"O username {parsed_username} já existe :(\n Tente outro ;)"
        raise Exception(exceptionMessage)

# Handle response from logoff type requests
def handleLogoffResponse(response, userInput):
    print(f"[Log: handleLogoffResponse]")

    status = response["status"]
    parsed_username = userInput.split(" ")[1]

    if(status =="200"):
        for connection in conections:#End all peer to peer conections
            connection.close()
        print("Você foi desconectado com sucesso\n Até a próxima :)")
        Estrutura.isLogged = False
    else:
        exceptionMessage = f"Algo de errado aconteceu ao tentar deslogar {parsed_username}. Tente novamente."
        raise Exception(exceptionMessage)

# Central function when dealing with server Commands
def handleServerRequest(userInput):
    print(f"[Log: handleServerRequest]")
    try:
        parsedInput = parseUserCommand(userInput)
        
        print(Estrutura.clienteServidorCentral)
        Estrutura.clienteServidorCentral.enviaMensagem(parsedInput)
        response_message = Estrutura.clienteServidorCentral.recebeMensagem()
        response = json.loads(response_message)

        print(f"[Log: reponse login - {response}]")

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

# Central function when dealing with user chatting Commands
def handleChatRequest(userInput):
    print(f"[Log: handleChatRequest]")
    # try:
    secoes = userInput.split(" ")
    operation = secoes[0]

    checkLoginStatus(operation)

    print(Estrutura.lista_clientes)

    if operation == "chat":
        parsed_username = secoes[1]
        print(f"[Log: chat com {parsed_username}]")

        if parsed_username in Estrutura.clientes.keys() or parsed_username == Estrutura.username:
            print("[Log: passed]")
            pass
        else:
            HOST = Estrutura.lista_clientes[parsed_username]["Endereco"]
            PORT = Estrutura.lista_clientes[parsed_username]["Porta"]
            print(f"[Log: chat created {HOST} {PORT}]")
            novo_cliente = ModuloCliente(HOST, PORT)
            Estrutura.clientes[parsed_username] = novo_cliente     

    elif operation == "message":
        parsed_username = secoes[1]
        mensagem = " ".join(secoes[2:])

        print(f"[Log: message para {parsed_username}]")

        if parsed_username in Estrutura.clientes.keys():
            cliente = Estrutura.clientes[parsed_username]
            cliente.enviaMensagem(mensagem)
        else:
            raise Exception("ERRO: Primeiro use o comando de chat para iniciar uma conversa!")

    # except Exception as error:
        # print(error)

# Deals with the different possible inputs passed by the user
def handleUserInput(userInput):
    print(f"[Log: handleUserInput]")
    if userInput[0] == '/':
        command = userInput.split(" ")[0][1:]
        if command in Estrutura.serverCommands:
            handleServerRequest(userInput[1:])
        elif command in Estrutura.chatCommands:
            handleChatRequest(userInput[1:])
    else:
        print(f"[Log: nao eh comando]")
        pass # aqui vamos adicionar o envio de mensagem mas por enquanto usa \message

def atende_stdin():
    while True:
        comando = input()
        print(f"[Log: comando {comando}]")
        handleUserInput(comando)
