# content2.py
def Diffie_Hellman():
    code = """
import random

def generate_shared_key(prime, generator, private_key):
    # Calculate public key as (generator ^ private_key) % prime
    public_key = pow(generator, private_key, prime)
    return public_key

def compute_shared_secret(public_key, private_key, prime):
    # Calculate shared secret as (public_key ^ private_key) % prime
    shared_secret = pow(public_key, private_key, prime)
    return shared_secret

# Example Usage:

# Select a prime number and a generator (these are typically public values)
prime = 23  # A small prime for simplicity
generator = 5  # A primitive root modulo 23

# Alice's private key and Bob's private key
alice_private_key = random.randint(1, 100)
bob_private_key = random.randint(1, 100)

# Alice computes her public key
alice_public_key = generate_shared_key(prime, generator, alice_private_key)

# Bob computes his public key
bob_public_key = generate_shared_key(prime, generator, bob_private_key)

# Alice and Bob exchange their public keys
print(f"Alice's Public Key: {alice_public_key}")
print(f"Bob's Public Key: {bob_public_key}")

# Alice computes the shared secret using Bob's public key
alice_shared_secret = compute_shared_secret(bob_public_key, alice_private_key, prime)

# Bob computes the shared secret using Alice's public key
bob_shared_secret = compute_shared_secret(alice_public_key, bob_private_key, prime)

# Verify that both Alice and Bob have the same shared secret
print(f"Alice's Shared Secret: {alice_shared_secret}")
print(f"Bob's Shared Secret: {bob_shared_secret}")
    """
    print(code)


def SHA1():
    code = """
import hashlib

def sha1_hash(message):
    # Create a new sha1 hash object
    sha1 = hashlib.sha1()
    
    # Update the hash object with the message (in bytes)
    sha1.update(message.encode())
    
    # Get the hexadecimal representation of the hash
    return sha1.hexdigest()

# Example Usage:
message = "Hello, this is a message to be hashed using SHA-1."
hashed_message = sha1_hash(message)

print(f"Original Message: {message}")
print(f"SHA-1 Hash: {hashed_message}")
    """
    print(code)



def MD5():
    code = """
import hashlib

def md5_hash(message):
    # Create a new md5 hash object
    md5 = hashlib.md5()
    
    # Update the hash object with the message (in bytes)
    md5.update(message.encode())
    
    # Get the hexadecimal representation of the hash
    return md5.hexdigest()

# Example Usage:
message = "Hello, this is a message to be hashed using MD5."
hashed_message = md5_hash(message)

print(f"Original Message: {message}")
print(f"MD5 Hash: {hashed_message}")
    """
    print(code)





