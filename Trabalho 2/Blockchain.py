from datetime import datetime
import json
import hashlib
import os
import sys
import random

import rpyc
from State import state

# Determina a quantidade de zeros que o hash precisa ter no início
DESAFIO_ZEROS = 5

datetime_format = "%m/%d/%Y, %H:%M:%S"

class Block:
    def __init__(self, index:int, timestamp:datetime, previous_hash: str, transactions:list, nonce: int):
        self.block_data = {
            "index": index,
            "timestamp": timestamp.strftime(datetime_format),
            "previous_hash": previous_hash,
            "nonce": nonce,
            "transaction_counter": len(transactions),
            "transactions": transactions
        }

    @classmethod
    def replicate_block(self, other_block):
        """ Gera um objeto de bloco a partir da referencia do RPyC pois ele não retorna objetos locais.
            Precisamos fazer algumas conversões para funcionar. """
            
        return Block(
            other_block.get_index(), 
            datetime.strptime(other_block.get_timestamp(), datetime_format), 
            other_block.get_previous_hash(), 
            list(other_block.get_transactions()),
            other_block.get_nonce()
        )
    
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

    print("Proof of Work Iniciado...", end=" ")

    new_block = None
    while True:
        nonce = random.randint(0, sys.maxsize)
        new_block = Block(index, timestamp, previous_hash, transactions, nonce)
        if new_block.validate_proof_of_work(): break

    print(new_block.generate_hash())

    return new_block

def send_new_block_to_neighbors(block):
        global state

        neighbors = state["neighbors"]
        for neighbor in neighbors:
            server = rpyc.connect(neighbor[0], neighbor[1], config={"allow_public_attrs": True})
            server.root.add_new_block(block)
            server.close()

class Blockchain:
    def __init__(self, added_blocks={}):
        self.transactions_pool = []
        
        self.blocks = {}
        for block in added_blocks:
            new_block = Block.replicate_block(block)
            hash_block = new_block.generate_hash()
            self.blocks[hash_block] = new_block
        
        if not self.validate_blockchain():
            raise ValueError("Conjunto Inválido de Blocos")

    def restart_blockchain(self):
        """ Reinicia as propriedades do blockchain """

        self.blocks = {}
        self.transactions_pool = []

    def start_blockchain(self):
        """ Inicia a blockchain com o bloco genesis """

        self.restart_blockchain
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

    def get_previous_block(self, current_block:Block):
        """ Obtém o bloco anterior a partir de outro """

        previous_hash = current_block.get_previous_hash()
        return self.blocos[previous_hash]
    
    def get_kth_block(self, k):
        """ Obtém o bloco de índice k """

        block = self.get_latest_block()
        while block and block.get_index() != k:
            previous_hash = block.get_previous_hash()
            block = self.blocks.get(previous_hash)
        
        return block

    def print_blockchain(self):
        """ Imprime todos os blocos da blockchain atual """

        block = self.get_latest_block()
        while block:
            block.print_data()
            previous_hash = block.get_previous_hash()
            block = self.blocks.get(previous_hash)
    
    def print_blocks(self):
        """ Imprime todos os blocos no set de blocos """

        for block in self.blocks.values():
            block.print_data()

    def validate_new_block(self, new_block:Block):
        """ Valida se novo bloco é válido para a blockchain.
            Precisa que a ordem dos index seja seguida.
            Precisa que cada bloco anterior seja válido.
            Precisa chegar ao bloco genesis ao fim. """

        block = new_block
        current_index = block.get_index()

        while block:
            block_index = block.get_index()

            if current_index != block_index or not block.validate_proof_of_work():
                return False

            previous_hash = block.get_previous_hash()
            block = self.blocks.get(previous_hash)
            current_index -= 1
        
        return True

    def validate_blockchain(self):
        """ Valida se a blockchain atual está válida """

        block = self.get_latest_block()
        if block is None:
            return True
        
        return self.validate_new_block(block)

    def mine(self):
        """ Tenta minerar um novo bloco para as novas transacoes """

        while(True):
            quantidade_blocos = len(self.blocks)

            last_block = self.get_latest_block()
            last_block_hash = last_block.generate_hash()
            last_block_index = last_block.get_index()

            new_block = generate_proof_of_work(last_block_index+1, datetime.now(), last_block_hash, self.transactions_pool.copy())
            new_block_hash = new_block.generate_hash()

            if quantidade_blocos == len(self.blocks) and self.add_block(new_block) == True:
                break

        self.transactions_pool.clear()

        send_new_block_to_neighbors(new_block)

    def add_transaction(self, transaction:str):
        """ Adiciona uma nova transacao na pool """

        self.transactions_pool.append(transaction)
        if len(self.transactions_pool) == 2:
            self.mine()

    def add_block(self, new_block:Block):
        """ Adiciona um novo bloco na cadeia atual """

        new_block = Block.replicate_block(new_block)

        validated = self.validate_new_block(new_block)
        if validated:
            block_hash = new_block.generate_hash()
            self.blocks[block_hash] = new_block
            return True
        else:
            return False
    
    def remove_until_index_reached(self, index):
        blocks_to_remove = []
        for _, block in self.blocks.items():
            if block.get_index() >= index:
                blocks_to_remove.append(block.generate_hash())
        
        for block_hash in blocks_to_remove:
            del self.blocks[block_hash]

    def return_blocks(self):
        """ Retorna o Set de blocos """

        return self.blocks.values()


if __name__ == "__main__":
    """ O arquivo blockchain é auxiliar para os demais, mas segue um roteiro de execução para testagem """

    print("\nPARTE 1: INICIO DA BLOCKCHAIN", "="*60, "\n")

    bc1 = Blockchain()
    bc1.start_blockchain()  

    print("\nImprimindo a Blockchain Inicial", "-"*60, "\n")
    bc1.print_blockchain()


    print("\nPARTE 2: ADICAO DE NOVAS TRANSACOES E FORMACAO DE BLOCO", "="*60, "\n")

    bc1.add_transaction("Primeira Mensagem")
    bc1.add_transaction("Segunda Mensagem")
    bc1.add_transaction("Terceira Mensagem")
    bc1.add_transaction("Quarta Mensagem")
    bc1.add_transaction("Quinta Mensagem")

    print("\nImprimindo a Blockchain com Novos Blocos", "-"*60, "\n")
    bc1.print_blockchain()


    print("\nPARTE 3: RECEBIMENTO EXTERNO DE BLOCO", "="*60, "\n")

    print("\nÚltimo Bloco Inserido", "-"*60, "\n")
    last_block = bc1.get_latest_block()
    last_block.print_data()

    last_index = last_block.get_index()
    last_hash = last_block.generate_hash()
    new_block = generate_proof_of_work(last_index+1, datetime.now(), last_hash, ["Bloco Externo!"])

    bc1.add_block(new_block)

    print("\nImprimindo a Blockchain com Bloco Externo", "-"*60, "\n")
    bc1.print_blockchain()


    print("\nPARTE 4: INSERÇÃO DE BLOCO DESATUALIZADO", "="*60, "\n")

    print("\nBloco Atual #0 Inserido", "-"*60, "\n")
    kth_block = bc1.get_kth_block(0)
    kth_block.print_data()

    kth_index = kth_block.get_index()
    kth_hash = kth_block.generate_hash()
    new_block = generate_proof_of_work(kth_index+1, datetime.now(), kth_hash, ["Bloco Fora da Ordem!"])

    bc1.add_block(new_block)

    print("\nImprimindo a Blockchain após Inserção Fora da Ordem - Se Mantém", "-"*60, "\n")
    bc1.print_blockchain()


    print("\nPARTE 5: INSERÇÃO DE OUTROS BLOCOS DESATUALIZADO", "="*60, "\n")

    # usando o bloco anterior gerado
    kth_index = new_block.get_index()
    kth_hash = new_block.generate_hash()
    new_block = generate_proof_of_work(kth_index+1, datetime.now(), kth_hash, ["Outro Bloco Fora da Ordem!"])
    bc1.add_block(new_block)

    kth_index = new_block.get_index()
    kth_hash = new_block.generate_hash()
    new_block = generate_proof_of_work(kth_index+1, datetime.now(), kth_hash, ["Mais Bloco Fora da Ordem!"])
    bc1.add_block(new_block)

    print("\nImprimindo a Blockchain após Inserção Fora da Ordem", "-"*60, "\n")
    bc1.print_blockchain()


    print("\nPARTE 6: INICIALIZACAO DE BLOCKCHAIN A PARTIR DE OUTRA", "="*60, "\n")

    bc2 = Blockchain(bc1.return_blocks())

    print("\nImprimindo a Blockchain Copiada", "-"*60, "\n")
    bc2.print_blockchain()