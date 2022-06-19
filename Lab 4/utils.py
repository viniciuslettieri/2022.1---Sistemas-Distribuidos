from random import choice
import random

def generate_pairs(lista):
    seen = set()

    # Primeiro geramos com certeza uma conexao para cada
    for x in lista:
        y = choice(lista)
        while (x, y) in seen or (y, x) in seen or x == y:
            y = choice(lista)

        seen.add((x, y))
        yield (x, y)

    # Depois geramos mais conexoes
    while True:
        x, y = choice(lista), choice(lista)
        while (x, y) in seen or (y, x) in seen or x == y:
            x, y = choice(lista), choice(lista)

        seen.add((x, y))
        yield (x, y)