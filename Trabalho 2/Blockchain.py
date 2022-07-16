from datetime import datetime
import json
import hashlib
import os
import sys
import random

# Determina a quantidade de zeros que o hash precisa ter no início
DESAFIO_ZEROS = 4

class Block:
    def __init__(self, index:int, timestamp:datetime, previous_hash: str, transactions:list, nonce: int):
        self.block_data = {
            "index": index,
            "timestamp": timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
            "previous_hash": previous_hash,
            "nonce": nonce,
            "transaction_counter": len(transactions),
            "transactions": transactions
        }
    
    def generate_hash(self):
        json_block = json.dumps(self.block_data)
        return hashlib.sha256(json_block.encode("utf-8")).hexdigest()

    def get_index(self):
        return self.block_data["index"]
    
    def get_timestamp(self):
        return self.block_data["timestamp"]
    
    def get_previous_hash(self):
        return self.block_data["previous_hash"]
    
    def get_nonce(self):
        return self.block_data["nonce"]
    
    def get_transaction_counter(self):
        return self.block_data["transaction_counter"]

    def get_transactions(self):
        return self.block_data["transactions"]

    def print_data(self):
        """ Imprime os dados desse Block """

        index = self.block_data["index"]
        timestamp = self.block_data["timestamp"]
        previous_hash = self.block_data["previous_hash"]
        nonce = self.block_data["nonce"]
        transaction_counter = self.block_data["transaction_counter"]
        transactions = self.block_data["transactions"]

        print(f"Bloco {index} minerado em {timestamp}")
        print(f"Possui nonce: {nonce}")
        print(f"Possui hash: {self.generate_hash()}")
        print(f"Bloco anterior com hash: {previous_hash}")
        print(f"Possui as seguintes transações:", transactions, "\n")
    
    def validate_proof_of_work(self):
        """ Verifica se o bloco atual, com o nonce gerado, respeita o desafio de zeros """

        hash_result = self.generate_hash()
        return hash_result.startswith("0" * DESAFIO_ZEROS)


def generate_proof_of_work(index:int, timestamp:datetime, previous_hash: str, transactions:list):
    """ Gera nonces aleatórios até o hash resultante do bloco passe no desafio de zeros iniciais """

    print("Proof of Work Iniciado...")

    new_block = None
    while True:
        nonce = random.randint(0, sys.maxsize)
        new_block = Block(index, timestamp, previous_hash, transactions, nonce)
        if new_block.validate_proof_of_work(): break

    return new_block


class Blockchain:
    def __init__(self):
        self.blocks = {}
        self.transactions_pool = []

    def start_blockchain(self):
        """ Inicia a blockchain com o bloco genesis """

        self.blocks.clear()
        genesis_block = generate_proof_of_work(0, datetime.now(), None, [])
        genesis_hash = genesis_block.generate_hash()
        self.blocks[genesis_hash] = genesis_block

    def get_latest_block(self):
        """ Obtém o bloco de maior index """

        highest_index = -1
        highest_block = None
        for block_hash, block in self.blocks.items():
            if block.get_index() > highest_index:
                highest_block = block
                highest_index = block.get_index()
        
        return highest_block

    def print_blockchain(self):
        """ Imprime todos os blocos da blockchain atual """

        block = self.get_latest_block()
        while block:
            block.print_data()
            previous_hash = block.get_previous_hash()
            index_block = block.get_index()
            block = self.blocks.get(previous_hash)

    def mine(self):
        """ Tenta minerar um novo bloco para as novas transacoes """

        last_block = self.get_latest_block()
        last_block_hash = last_block.generate_hash()
        last_block_index = last_block.get_index()
        
        new_block = generate_proof_of_work(last_block_index+1, datetime.now(), last_block_hash, self.transactions_pool.copy())
        new_block_hash = new_block.generate_hash()
        self.blocks[new_block_hash] = new_block

        self.transactions_pool.clear()

    def add_transaction(self, transaction:str):
        """ Adiciona uma nova transacao na pool """

        self.transactions_pool.append(transaction)
        if len(self.transactions_pool) == 5:
            self.mine()


if __name__ == "__main__":
    """ O arquivo blockchain é auxiliar para os demais, mas segue um roteiro de execução para testagem """

    bc = Blockchain()
    bc.start_blockchain()  

    bc.print_blockchain()

    bc.add_transaction("Primeira Mensagem")
    bc.add_transaction("Segunda Mensagem")
    bc.add_transaction("Terceira Mensagem")
    bc.add_transaction("Quarta Mensagem")
    bc.add_transaction("Quinta Mensagem")

    bc.print_blockchain()

    bc.add_transaction("Sexta Mensagem")
    bc.add_transaction("Sétima Mensagem")
    bc.add_transaction("Oitava Mensagem")
    bc.add_transaction("Nona Mensagem")
    bc.add_transaction("Décima Mensagem")

    bc.print_blockchain()