from datetime import datetime
import json
import hashlib
import os
import sys
import random

# Determina a quantidade de zeros que o hash precisa ter no início
DESAFIO_ZEROS = 5

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


bc = Blockchain()
bc.start_blockchain()  
bc.print_blockchain()
