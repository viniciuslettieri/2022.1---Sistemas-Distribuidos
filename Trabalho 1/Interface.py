import string
import threading
import json
import argparse

import Estrutura
from Utils import constroi_mensagem, reconstroi_mensagem, printLog
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
    printLog(f"[Log: checkLoginStatus]")
    needsLogin = False if operation == "login" else True
    if(needsLogin and not Estrutura.isLogged):
        raise Exception("Você precisa fazer login antes de realizar essa operação")
    elif(not needsLogin and Estrutura.isLogged):
        raise Exception("Voce já fez login. Não é possível fazer novamente")

def handleLoginInitializations():
    printLog(f"[Log: handleLoginInitializations]")
    try:
        coordenador = ModuloCoordenadorServidores('', Estrutura.userport)
        thread_coordenador = threading.Thread(target=coordenador.trata_novos_servidores)   
        thread_coordenador.start()
    except:
        print("Erro Criando ")

# Parses a command made by the user so the server can understand it    
def parseUserCommand(userInput):
    printLog(f"[Log: parseUserCommand]")
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
    print()

# Handle responses from get_lista type requests
def handleGetListaResponse(response):
    printLog(f"[Log: handleGetListaResponse]")
    status = response["status"]
    if(status == "200"):
        Estrutura.lista_clientes = response["clientes"]
        printListaClientes()
    else:
        exceptionMessage = "Comando get_lista mal-sucedido erro {erro}".format(erro = status)
        raise Exception(exceptionMessage)

# Handle responses from login type requests
def handleLoginResponse(response, userInput):
    printLog(f"[Log: handleLoginResponse]")
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
    printLog(f"[Log: handleChatRequest]")
    
    try:
        secoes = userInput.split(" ")
        operation = secoes[0]

        checkLoginStatus(operation)

        if operation == "chat":
            parsed_username = secoes[1]
            printLog(f"[Log: chat com {parsed_username}]")

            if parsed_username in Estrutura.clientes.keys():
                print(f"Você já iniciou um chat com '{parsed_username}'")
            elif parsed_username == Estrutura.username:
                print("Não é possível iniciar um chat com o seu próprio usuário, tente uma pessoa diferente!")
            elif parsed_username in Estrutura.lista_clientes:
                HOST = Estrutura.lista_clientes[parsed_username]["Endereco"]
                PORT = Estrutura.lista_clientes[parsed_username]["Porta"]
                printLog(f"[Log: chat created {HOST} {PORT}]")
                novo_cliente = ModuloCliente(HOST, PORT)
                Estrutura.clientes[parsed_username] = novo_cliente     
            else:
                print("Não foi possível encontrar o usuário.")
                print("Tente usar o comando '/get_lista' para recuperar os usuários ativos.")

        elif operation == "message":
            parsed_username = secoes[1]
            mensagem = " ".join(secoes[2:])

            printLog(f"[Log: message para {parsed_username}]")

            if parsed_username in Estrutura.clientes.keys():
                cliente = Estrutura.clientes[parsed_username]
                cliente.enviaMensagem(mensagem)
            else:
                raise Exception("ERRO: Primeiro use o comando de chat para iniciar uma conversa!")

    except Exception as error:
        print(error)

# Deals with the different possible inputs passed by the user
def handleUserInput(userInput):
    printLog(f"[Log: handleUserInput]")
    if userInput[0] == '/':
        command = userInput.split(" ")[0][1:]
        if command in Estrutura.serverCommands:
            handleServerRequest(userInput[1:])
        elif command in Estrutura.chatCommands:
            handleChatRequest(userInput[1:])
    else:
        printLog(f"[Log: nao eh comando]")
        pass # aqui vamos adicionar o envio de mensagem mas por enquanto usa \message

def atende_stdin():
    while True:
        comando = input()
        printLog(f"[Log: comando {comando}]")
        handleUserInput(comando)
