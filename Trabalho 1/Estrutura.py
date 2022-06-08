import threading
# Esse arquivo guarda todas as estruturas do simulador

HOST_SERVIDOR_CENTRAL = 'localhost'
PORT_SERVIDOR_CENTRAL = 5000

mutexMessages = threading.Lock()

username = None
userport = None
clientes = {}               # Guarda os ModuloCliente
lista_usuarios = {}         # Guarda a lista dos usuarios ativos
messages = {}               # Guarda todas as mensagens por par de usuários
newMessages = {}            # Guarda a quantidade de mensagens novas por par de usuários

clienteServidorCentral = None
coordenadorServidores = None

isLogged = False            # Estado de Log dos Prints

estadoTela = "login"        # login, menu, chat
usuarioChat = None          # usuario em chat no momento

# Possible user commands
serverCommands = [
    "get_lista",
    "login",
    "logoff"
]      
chatCommands = [
    "chat",
    "message"
]