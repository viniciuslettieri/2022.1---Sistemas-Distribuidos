import string
import threading
import json
import os

import Estrutura
from Utils import constroi_mensagem, reconstroi_mensagem, printLog
from ModuloCliente import ModuloCliente
from ModuloServidor import ModuloServidor, ModuloCoordenadorServidores

# Guarantees that the user can only use the commands allowed in their current log status
def checkLoginStatus(operation):
    printLog(f"checkLoginStatus")
    needsLogin = False if operation == "login" else True
    if needsLogin and not Estrutura.isLogged:
        raise Exception("Você precisa fazer login antes de realizar essa operação!")
    elif not needsLogin and Estrutura.isLogged:
        raise Exception("Voce já fez login. Não é possível fazer novamente!")

def handleLoginInitializations():
    printLog(f"handleLoginInitializations")
    try:
        Estrutura.coordenadorServidores = ModuloCoordenadorServidores('', Estrutura.userport)
        thread_coordenador = threading.Thread(target=Estrutura.coordenadorServidores.trata_novos_servidores)   
        thread_coordenador.start()
        printLog(f"Nova Thread {thread_coordenador.name} {thread_coordenador.ident}")
    except:
        raise Exception("Erro criando o servidor na porta escolhida!")

# Parses a command made by the user so the server can understand it    
def parseUserCommand(userInput):
    printLog(f"parseUserCommand")
    parsedCommand = ''
    secoes = userInput.split(" ")
    operation = secoes[0]

    checkLoginStatus(operation)

    if operation == "get_lista":            # /get_lista
        if len(secoes) == 1:
            parsedCommand = '{"operacao": "get_lista"}'
        else:
            raise Exception("O comando 'get_lista' requer 0 parâmetros.")

    elif operation == "login":              # /login [username] [porta]
        if len(secoes) == 3:
            parsed_username = secoes[1]
            parsed_port = secoes[2]
            parsedCommand = '{"operacao": "login", "username": "' + parsed_username + '" ,"porta": "' + parsed_port + '"}'
            Estrutura.userport = parsed_port
        else:
            raise Exception("O comando 'login' requer 2 parâmetros: [username] [porta]")

    elif operation == "logoff":             # /logoff
        if len(secoes) == 1:                
            parsedCommand = '{"operacao": "logoff", "username": "' + Estrutura.username + '"}'
        else:
            raise Exception("O comando 'logoff' requer 0 parâmetros.")
    
    return parsedCommand

def printListaClientes():
    clearTerminal()
    print("\u001b[31mA qualquer momento, digite :r para refrescar a lista de usuários e mensagens\u001b[0m")
    print("Escolha um usuário para começar uma conversa: ")
    print("\nClientes Ativos: \n")
    for usuario in Estrutura.lista_usuarios:
        dados = Estrutura.lista_usuarios[usuario]
        print(f"{usuario}: ({dados['Endereco']}, {dados['Porta']})")
    print()

# Handle responses from get_lista type requests
def handleGetListaResponse(response):
    printLog(f"handleGetListaResponse")
    status = response["status"]
    if status == "200":
        Estrutura.lista_usuarios = response["clientes"]
        printListaClientes()
    else:
        exceptionMessage = "Comando get_lista mal-sucedido erro {erro}".format(erro = status)
        raise Exception(exceptionMessage)

# Handle responses from login type requests
def handleLoginResponse(response, userInput):
    printLog(f"handleLoginResponse")
    status = response["status"]
    parsed_username = userInput.split(" ")[1]

    if status == "200":
        print("Bem vindo " + parsed_username + "!")
        Estrutura.isLogged = True
        Estrutura.username = parsed_username
    else:
        exceptionMessage = f"O username {parsed_username} já existe :(\n Tente outro ;)"
        raise Exception(exceptionMessage)

# Handle response from logoff type requests
def handleLogoffResponse(response, userInput):
    printLog(f"handleLogoffResponse")

    status = response["status"]

    if status =="200":
        Estrutura.coordenadorServidores.encerra()

        for username in Estrutura.clientes:
            Estrutura.clientes[username].encerra()
        Estrutura.clientes.clear()

        print("Você foi desconectado com sucesso\n Até a próxima :)")
        Estrutura.isLogged = False
    else:
        exceptionMessage = f"Algo de errado aconteceu ao tentar deslogar. Tente novamente."
        raise Exception(exceptionMessage)

# Central function when dealing with server Commands
def handleServerRequest(userInput):
    printLog(f"handleServerRequest")
    try:
        parsedInput = parseUserCommand(userInput)
        secoes = userInput.split(" ")
        operationType = secoes[0]

        # Verifica se o servidor pode ser criado na porta
        if operationType == "login":
            handleLoginInitializations()
        
        Estrutura.clienteServidorCentral.enviaMensagem(parsedInput)
        response_message = Estrutura.clienteServidorCentral.recebeMensagem()
        response = json.loads(response_message)

        printLog(f"reponse login - {response}")

        operationType = response["operacao"]

        if operationType == "get_lista":
            handleGetListaResponse(response)
        elif operationType =="login":
            handleLoginResponse(response,userInput)
        elif operationType=="logoff":
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
            elif parsed_username in Estrutura.lista_usuarios:
                HOST = Estrutura.lista_usuarios[parsed_username]["Endereco"]
                PORT = Estrutura.lista_usuarios[parsed_username]["Porta"]
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

def handleDebugCommand():
    print("\nActive threads:")
    for thread in threading.enumerate(): 
        if thread.name == "MainThread":
            print(thread.name)
        else:
            print(thread.name, thread.ident)
    print("\nClientes: ", Estrutura.clientes)
    print("\nLista Clientes: ", Estrutura.lista_usuarios)
    print("\nEstá logado: ", Estrutura.isLogged)
    if Estrutura.isLogged:
        print("\nServidores Ativos: ", Estrutura.coordenadorServidores.servidores)
    print()

# Deals with the different possible inputs passed by the user
def handleUserInput(userInput):
    printLog(f"[Log: handleUserInput]")
    if userInput[0] == '/':
        command = userInput.split(" ")[0][1:]
        if command in Estrutura.serverCommands:
            handleServerRequest(userInput[1:])
        elif command in Estrutura.chatCommands:
            handleChatRequest(userInput[1:])
        elif command == "debug":
            handleDebugCommand()
    else:
        printLog(f"nao eh comando")
        pass # aqui vamos adicionar o envio de mensagem mas por enquanto usa \message

def atende_stdin():
    clearTerminal()
    while not Estrutura.isLogged:
        loginInterface()
    while True:
        getList()
        usuario = startChat()
        print("Mande as suas mensagens: \n")
        while True:
            close = sendMessage(usuario)
            if close: break

def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def loginInterface():
    print("Para entrar no bate-papo, primeiro precisamos que você se conecte.")
    usuario = input("Usuario: ")
    porta = input("Porta: ")
    comando = f"/login {usuario} {porta}"
    handleUserInput(comando)
    print()

def getList():
    comando = f"/get_lista"
    handleUserInput(comando)

def startChat():
    mensagem = input("Digite o usuario que deseja conversar com: ")
    if mensagem == ":r": 
        getList()
        return startChat()
    comando = f"/chat {mensagem}"
    handleUserInput(comando)
    return mensagem

def sendMessage(usuario):
    message = input()
    if message == ":q": return True
    showMessages(usuario)
    comando = f"/message {usuario} {message}"
    handleUserInput(comando)
    return False

def showMessages(usuario):
    if not usuario in Estrutura.messages: Estrutura.messages[usuario] = []
    messages = Estrutura.messages[usuario]
    for message in messages:
        print(f"{usuario}:\t {message}")