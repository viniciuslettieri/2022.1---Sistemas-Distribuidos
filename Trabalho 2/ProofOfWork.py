import json
import hashlib
import glob
import os

for i in range(100000000000000000):
    test_block = {
        "header": {
            "previous_hash": "1",
            "nonce": i,
            "hash_merkle": "3", 
            "timestamp": "4"
        },
        "transaction_counter": "5",
        "transactions": "6"
    }

    json_block = json.dumps(test_block)
    hash_result = hashlib.sha256(json_block.encode("utf-8")).hexdigest()

    quantidade_zeros = 5
    if hash_result[:quantidade_zeros] == "0"*quantidade_zeros:
        print("\nBloco em JSON:", json_block.encode("utf-8"))
        print("\nHash do Bloco:", hash_result)
        break