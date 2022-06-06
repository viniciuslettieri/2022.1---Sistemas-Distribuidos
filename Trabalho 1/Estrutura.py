
# Esse arquivo guarda todas as estruturas do simulador

HOST_SERVIDOR_CENTRAL = 'localhost'
PORT_SERVIDOR_CENTRAL = 5000

username = None
userport = None
clientes = {}               # Guarda os ModuloCliente
lista_usuarios = {}         # Guarda a lista dos usuarios ativos
messages = {}               # Guarda todas as mensagens por par de usuários
newMessages = {}            # Guarda a quantidade de mensagens novas por par de usuários

clienteServidorCentral = None
coordenadorServidores = None

isLogged = False      # Logged state of the user

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