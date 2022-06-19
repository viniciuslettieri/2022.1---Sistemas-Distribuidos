# Laboratório 4

Nesse laboratório, implementamos o algoritmo de eleição de líder utilizando RPC.

Para isso, o código `principal.py` se torna responsável por gerar os servidores, através dos métodos e classes de `elemento.py`.

As portas são geradas aleatoriamente e as conexões entre servidores também. Mas para evitar grafos não conexos, a geração das arestas é feita com pelo menos uma saindo de cada elemento.

O código deve ser executado a partir do arquivo `principal.py` e será pedida a porta por onde começar a eleição.

Ao fim, todos os elementos devem possuir o mesmo eleito.