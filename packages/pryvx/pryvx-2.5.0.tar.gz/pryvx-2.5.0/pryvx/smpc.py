import random
import hashlib

def getAdditiveShares(secret, N, fieldSize):
    shares = [random.randrange(fieldSize) for _ in range(N-1)]
    shares.append((secret - sum(shares)) % fieldSize )
    return shares

class SMPC:
    def __init__(self) -> None:
        self.fieldSize = 293973345475167247070445277780365744413

    def encode(self, secret, scale_factor=1000):
        return int(secret * scale_factor)
    
    def decode(self, upscaled, scale_factor=1000):
        return upscaled / scale_factor
    
    def get_field_size(self):
        return self.fieldSize
    
    def get_secret_shares(self, secret, N):
        shares = getAdditiveShares(secret, N, self.fieldSize)
        return shares
    
    def hash_to_bigint(self, data: str) -> int:
        digest = hashlib.sha256(data.encode()).hexdigest()
        return int(digest, 16)
    
    def reconstruct(self, share):
        return share % self.fieldSize
    
    def additive_reconstruct(self, shares):
        return sum(shares) % self.fieldSize