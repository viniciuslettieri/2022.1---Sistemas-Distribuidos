import rpyc
from utils import generate_pairs
from elemento import inicializa_servidores

# Gera os servidores para cada elemento na devida porta
quantidade_servidores = 10
portas, processos = inicializa_servidores(quantidade_servidores)

# Obtenção dos elementos
print("Conectando com os servidores:")
elementos = {}
for porta in portas:
    elementos[porta] = rpyc.connect('localhost', porta)
    print("Conectado com", porta)

# Criacao da rede
print("\nCriando as arestas entre servidores:")
conexoes = 0
gera_pares = generate_pairs(portas)
while conexoes < len(elementos):
    (a, b) = next(gera_pares)
    print(a, "<->", b)
    conexoes += 1
    elementos[a].root.connect_to(b)
    elementos[b].root.connect_to(a)

# Verificando a rede de vizinhos
print("\nRede de vizinhança:")
for k in elementos:
    print("Vizinhos de", k, "com identificador", elementos[k].root.return_id(), "=>", elementos[k].root.list_neighbors())

# Processo de lideranca
porta_input = input(f"\nSelecione uma das portas: {portas}\n> ")
while porta_input:
    porta_input = int(porta_input)
    if porta_input not in portas: 
        porta_input = input(f"\nA porta não está na lista. \nSelecione uma das portas: {portas}\n> ")
        continue

    # Envia probe
    print("Retorno do Probe:", elementos[porta_input].root.probe())

    # Verificando os lideres
    for k in elementos:
        print("Lider de", k, ":", elementos[k].root.return_id_lider())
    
    porta_input = input(f"\nSelecione uma das portas: {portas}\n> ")


for k in elementos:
    elementos[k].close()

for processo in processos:
    processo.terminate()