import hashlib
import random
import hmac

# OPRF-related functions
def generate_key():
    return random.getrandbits(256)

def oprf(key, value):
    return hmac.new(key, value.encode(), hashlib.sha256).digest()

def hash_element(element, key):
    return hashlib.sha256(oprf(key, str(element))).hexdigest()

# Batch processing function
def process_batch(batch, key):
    return {hash_element(elem, key): elem for elem in batch}


class OPRF:

    @staticmethod
    def get_key():
        return generate_key()

    @staticmethod
    def get_hash(element, server_key):
        server_key = server_key.to_bytes(32, byteorder='big')
        return hash_element(element, server_key)
    
    @staticmethod
    def get_batch_hash(X, batch_size, server_key):
        server_key = server_key.to_bytes(32, byteorder='big')
        elements = list(set(X))
        batches_a = [elements[i:i + batch_size] for i in range(0, len(elements), batch_size)]

        hashed_a_batches = [process_batch(batch, server_key) for batch in batches_a]
        hashed_a = {k: v for batch in hashed_a_batches for k, v in batch.items()}
        return hashed_a

    @staticmethod
    def get_intersect(hashed_a, hashed_b):
        intersection_hashes = set(hashed_a).intersection(set(hashed_b))
        return intersection_hashes
