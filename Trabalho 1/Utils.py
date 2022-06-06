
TAM_MENSAGEM = 1024

def constroi_mensagem(string_msg):
    byte_msg = string_msg.encode("utf-8")
    print(byte_msg)
    msg = len(byte_msg).to_bytes(2, 'big')
    print(int.from_bytes(msg,'big'))
    msg += byte_msg
    return msg

def reconstroi_mensagem(socket):
    msg = socket.recv(2)
    length = int.from_bytes(msg, 'big')
    
    full_msg = b''
    while length > 0:
        msg = socket.recv(TAM_MENSAGEM)
        length -= TAM_MENSAGEM
        full_msg += msg
    
    return full_msg.decode("utf-8")

log = False

def activateLog():
    global log
    log = True

def printLog(message, *args):
    global log
    if log: 
        print(f"[Log: ${message}]", *args)
