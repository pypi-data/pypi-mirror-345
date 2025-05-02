import random
from sympy import mod_inverse, isprime, nextprime
import math
import hashlib

def generate_prime(bits=512):
    while True:
        p = nextprime(random.getrandbits(bits))
        if isprime(p):
            return p

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)


class PHE:

    @staticmethod
    def keygen(bits=64):
        p = generate_prime(bits)
        q = generate_prime(bits)
        n = p * q
        lambda_n = lcm(p - 1, q - 1)
        g = n + 1
        mu = mod_inverse((pow(g, lambda_n, n * n) - 1) // n, n)
        public_key = (n, g)
        private_key = (lambda_n, mu)
        return public_key, private_key

    @staticmethod
    def encode(value, scale_factor=1000):
        return int(round(value * scale_factor))
    
    @staticmethod
    def hash_to_bigint(data: str) -> int:
        digest = hashlib.sha256(data.encode()).hexdigest()
        return int(digest, 16)

    @staticmethod
    def decode(value, scale_factor=1000):
        return value / scale_factor

    @staticmethod
    def encrypt(public_key, plaintext, r=None):
        n, g = public_key
        if r is None:
            r = random.randint(1, n-1)
        n2 = n * n
        c = (pow(g, plaintext, n2) * pow(r, n, n2)) % n2
        return c

    @staticmethod
    def decrypt(public_key, private_key, ciphertext):
        n, g = public_key
        lambda_n, mu = private_key
        n2 = n * n
        x = pow(ciphertext, lambda_n, n2)
        Lx = (x - 1) // n
        plaintext = (Lx * mu) % n

        # Adjust for negative results
        if plaintext > n // 2:  # If the result is greater than n/2, it's negative
            plaintext -= n
            
        return plaintext

    @staticmethod
    def homomorphic_add(c1, c2, public_key):
        n, _ = public_key
        n2 = n * n
        return (c1 * c2) % n2
    
    @staticmethod
    def homomorphic_add_plaintext(ciphertext, plaintext, public_key):
        n, g = public_key
        n2 = n * n
        c_plain = pow(g, plaintext, n2)
        return (ciphertext * c_plain) % n2
    
    @staticmethod
    def homomorphic_sub_plaintext(ciphertext, plaintext, public_key):
        n, g = public_key
        n2 = n * n
        
        # Encrypt the plaintext as its negative (-plaintext) mod n
        c_plain_neg = pow(g, -plaintext % n, n2)  # Modular inverse for subtraction
        return (ciphertext * c_plain_neg) % n2
    
    @staticmethod
    def homomorphic_sub(c1, c2, public_key):
        n, _ = public_key
        n2 = n * n
        c2_inv = mod_inverse(c2, n2)
        return (c1 * c2_inv) % n2
    
    @staticmethod
    def homomorphic_scalar_mult(ciphertext, scalar, public_key):
        n, g = public_key
        n2 = n * n
        return pow(ciphertext, scalar, n2)

    @staticmethod
    def homomorphic_div(ciphertext, divisor, public_key):
        n, g = public_key
        divisor_inv = mod_inverse(divisor, n)  # Find the modular inverse of the divisor modulo n
        return PHE.homomorphic_scalar_mult(ciphertext, divisor_inv, public_key)