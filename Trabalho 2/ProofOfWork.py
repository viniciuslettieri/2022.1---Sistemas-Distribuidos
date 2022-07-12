import json
import hashlib
import os
import random

quantidade_zeros = 5
print(f"Iniciando tentativa para {quantidade_zeros} digitos zeros iniciais.")

json_block = ""
hash_result = ""
while hash_result[:quantidade_zeros] != "0" * quantidade_zeros:
    nonce = random.randint(0, 1000000000000000)

    test_block = {
        "header": {
            "previous_hash": "1",
            "nonce": nonce,
            "hash_merkle": "3", 
            "timestamp": "4"
        },
        "transaction_counter": "5",
        "transactions": "6"
    }

    json_block = json.dumps(test_block)
    hash_result = hashlib.sha256(json_block.encode("utf-8")).hexdigest()

print("\nBloco em JSON:", json_block.encode("utf-8"))
print("\nHash do Bloco:", hash_result)