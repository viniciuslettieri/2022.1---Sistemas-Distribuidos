
# Esse arquivo guarda todas as estruturas do simulador

HOST_SERVIDOR_CENTRAL = '10.11.0.16 '
PORT_SERVIDOR_CENTRAL = 5000

servidores = []
clientes = {}
username = None
userport = None
# interface = None
lista_clientes = {}

clienteServidorCentral = "ola"

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
