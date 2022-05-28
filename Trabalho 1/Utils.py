
def constroi_mensagem(string_msg):
    byte_msg = string_msg.encode("utf-8")
    msg = len(byte_msg).to_bytes(2, 'big')
    msg.append(byte_msg)
    return msg

def reconstroi_mensagem(socket):
    msg = socket.recv(1024)
    length = int.from_bytes(msg[:2], 'big')
    
    full_msg = msg[2:]
    length -= 1024
    while length > 0:
        msg = socket.recv(1024)
        length -= 1024
        full_msg.append(msg)
    
    return full_msg.decode("utf-8")
    