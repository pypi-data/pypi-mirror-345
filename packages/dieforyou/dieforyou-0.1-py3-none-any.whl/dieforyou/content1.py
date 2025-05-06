# content1.py
def Caesar():
    caesar_code = """
def caesar_cipher_encode(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            result += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            result += char
    return result

def caesar_cipher_decode(text, shift):
    return caesar_cipher_encode(text, -shift)  # Reverse the shift for decoding

# Example Usage:
plaintext = "Hello World"
shift = 3
encoded_text = caesar_cipher_encode(plaintext, shift)
decoded_text = caesar_cipher_decode(encoded_text, shift)

print(f"Encoded: {encoded_text}")
print(f"Decoded: {decoded_text}")
    """
    print(caesar_code)




def Playfair():
    playfair_code = """
# Playfair Cipher Encoding and Decoding
def create_playfair_matrix(key):
    matrix = []
    key = ''.join(sorted(set(key), key=lambda x: key.index(x)))  # Remove duplicates, preserve order
    key = key.upper().replace('J', 'I')  # Combine I/J into one slot
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # No J in Playfair matrix
    for char in key + alphabet:
        if char not in matrix:
            matrix.append(char)
    return matrix

def playfair_cipher_process(text, key, mode='encrypt'):
    matrix = create_playfair_matrix(key)
    text = text.upper().replace('J', 'I').replace(' ', '')
    
    if len(text) % 2 != 0:
        text += 'X'  # Add padding if needed

    result = ""
    for i in range(0, len(text), 2):
        first_char = text[i]
        second_char = text[i + 1]

        row1, col1 = divmod(matrix.index(first_char), 5)
        row2, col2 = divmod(matrix.index(second_char), 5)

        if row1 == row2:
            if mode == 'encrypt':
                result += matrix[row1 * 5 + (col1 + 1) % 5]
                result += matrix[row2 * 5 + (col2 + 1) % 5]
            else:  # Decryption
                result += matrix[row1 * 5 + (col1 - 1) % 5]
                result += matrix[row2 * 5 + (col2 - 1) % 5]
        elif col1 == col2:
            if mode == 'encrypt':
                result += matrix[((row1 + 1) % 5) * 5 + col1]
                result += matrix[((row2 + 1) % 5) * 5 + col2]
            else:  # Decryption
                result += matrix[((row1 - 1) % 5) * 5 + col1]
                result += matrix[((row2 - 1) % 5) * 5 + col2]
        else:
            if mode == 'encrypt':
                result += matrix[row1 * 5 + col2]
                result += matrix[row2 * 5 + col1]
            else:  # Decryption
                result += matrix[row1 * 5 + col2]
                result += matrix[row2 * 5 + col1]

    return result

# Example Usage:
plaintext = "HELLO WORLD"
key = "KEYWORD"
encoded_text = playfair_cipher_process(plaintext, key, mode='encrypt')
decoded_text = playfair_cipher_process(encoded_text, key, mode='decrypt')

print(f"Encoded: {encoded_text}")
print(f"Decoded: {decoded_text}")
    """
    print(playfair_code)



import numpy as np

def Hill():
    hill_code = """
import numpy as np

# Hill Cipher Encoding and Decoding
def matrix_inverse(matrix, mod=26):
    det = int(np.round(np.linalg.det(matrix)))  # Determinant of the matrix
    det_inv = pow(det, -1, mod)  # Modular inverse of determinant
    matrix_mod = matrix % mod
    matrix_adj = np.round(det * np.linalg.inv(matrix)).astype(int) % mod  # Adjugate matrix
    return (det_inv * matrix_adj) % mod  # Inverse of matrix modulo mod

def hill_cipher_process(text, key, mode='encrypt'):
    # Convert text to numbers, A=0, B=1, ..., Z=25
    text = text.upper().replace(' ', '')
    text_nums = [ord(char) - 65 for char in text]

    # Prepare the key matrix (assuming the key is 2x2 or 3x3, for simplicity)
    key_matrix = np.array(key).reshape(int(len(key)**0.5), int(len(key)**0.5))

    # Check if the key matrix is invertible
    if np.linalg.det(key_matrix) == 0:
        raise ValueError("Key matrix is not invertible")

    # Encryption or Decryption
    if mode == 'encrypt':
        result_nums = np.dot(np.array(text_nums).reshape(-1, len(key_matrix)), key_matrix) % 26
    else:  # Decryption
        inverse_key_matrix = matrix_inverse(key_matrix)
        result_nums = np.dot(np.array(text_nums).reshape(-1, len(key_matrix)), inverse_key_matrix) % 26

    result_text = ''.join([chr(num + 65) for num in result_nums.flatten()])
    return result_text

# Example Usage:
plaintext = "HELLO"
key = [6, 24, 1, 13, 16, 10, 20, 17, 15]  # 3x3 Key matrix as a flat list
encoded_text = hill_cipher_process(plaintext, key, mode='encrypt')
decoded_text = hill_cipher_process(encoded_text, key, mode='decrypt')

print(f"Encoded: {encoded_text}")
print(f"Decoded: {decoded_text}")
    """
    print(hill_code)


def RailFenceColumnMajor():
    code = """
def RailFence_ColumnMajor(text, key, mode='encrypt'):
    def encrypt(text, key):
        # Create a 2D array for the rail fence cipher
        rail = [['\\n' for i in range(len(text))] for j in range(key)]
        
        row, col = 0, 0
        direction = 1  # 1 means moving down, -1 means moving up
        for char in text:
            rail[row][col] = char
            col += 1
            row += direction
            
            # Change direction when we reach the top or bottom rail
            if row == key or row == -1:
                direction *= -1
                row += direction * 2
        
        # Construct the encrypted message by reading column by column
        result = ''.join([''.join([rail[i][j] for i in range(key) if rail[i][j] != '\\n']) for j in range(len(text))])
        return result

    def decrypt(text, key):
        # First, create a rail array to determine the positions
        rail = [['\\n' for i in range(len(text))] for j in range(key)]
        row, col = 0, 0
        direction = 1
        for i in range(len(text)):
            rail[row][col] = '*'
            col += 1
            row += direction
            if row == key or row == -1:
                direction *= -1
                row += direction * 2
        
        # Fill in the rail fence with the characters from the encrypted text
        result = list(text)
        char_idx = 0
        for c in range(len(text)):
            for r in range(key):
                if rail[r][c] == '*' and char_idx < len(text):
                    rail[r][c] = text[char_idx]
                    char_idx += 1
        
        # Read the rail fence row by row to get the decrypted message
        decoded = ''.join([rail[r][c] for r in range(key) for c in range(len(text))])
        return decoded

# Example Usage:
text = "HELLOFROMTHEOTHERSIDE"
key = 3
encoded_text = RailFence_ColumnMajor(text, key, mode='encrypt')
decoded_text = RailFence_ColumnMajor(encoded_text, key, mode='decrypt')

print(f"Encoded: {encoded_text}")
print(f"Decoded: {decoded_text}")
    """
    print(code)

def RailFence():
    code = """
def RailFence_RowMajor(text, key, mode='encrypt'):
    def encrypt(text, key):
        # Create a 2D array for the rail fence cipher
        rail = [['\\n' for i in range(len(text))] for j in range(key)]
        
        row, col = 0, 0
        direction = 1  # 1 means moving down, -1 means moving up
        for char in text:
            rail[row][col] = char
            col += 1
            row += direction
            
            # Change direction when we reach the top or bottom rail
            if row == key or row == -1:
                direction *= -1
                row += direction * 2
        
        # Construct the encrypted message by reading row by row
        result = ''.join([''.join([rail[i][j] for i in range(key) if rail[i][j] != '\\n']) for j in range(len(text))])
        return result

    def decrypt(text, key):
        # First, create a rail array to determine the positions
        rail = [['\\n' for i in range(len(text))] for j in range(key)]
        row, col = 0, 0
        direction = 1
        for i in range(len(text)):
            rail[row][col] = '*'
            col += 1
            row += direction
            if row == key or row == -1:
                direction *= -1
                row += direction * 2
        
        # Fill in the rail fence with the characters from the encrypted text
        result = list(text)
        char_idx = 0
        for r in range(key):
            for c in range(len(text)):
                if rail[r][c] == '*' and char_idx < len(text):
                    rail[r][c] = text[char_idx]
                    char_idx += 1
        
        # Read the rail fence column by column to get the decrypted message
        decoded = ''.join([rail[r][c] for c in range(len(text)) for r in range(key)])
        return decoded

# Example Usage:
text = "HELLOFROMTHEOTHERSIDE"
key = 3
encoded_text = RailFence_RowMajor(text, key, mode='encrypt')
decoded_text = RailFence_RowMajor(encoded_text, key, mode='decrypt')

print(f"Encoded: {encoded_text}")
print(f"Decoded: {decoded_text}")
    """
    print(code)


def DES():
    code = """
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt(plaintext, key):
    # Ensure key is 8 bytes (64 bits) for DES
    cipher = DES.new(key, DES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), DES.block_size))
    return cipher.iv + ciphertext  # Return the IV concatenated with ciphertext

def decrypt(ciphertext, key):
    # Extract the IV from the ciphertext
    iv = ciphertext[:DES.block_size]
    ciphertext = ciphertext[DES.block_size:]
    
    cipher = DES.new(key, DES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES.block_size)
    return plaintext.decode()

# Example Usage:
key = get_random_bytes(8)  # Key must be 8 bytes (64 bits)
plaintext = "This is a secret message."

# Encrypt the message
encrypted = encrypt(plaintext, key)
print(f"Encrypted: {encrypted.hex()}")

# Decrypt the message
decrypted = decrypt(encrypted, key)
print(f"Decrypted: {decrypted}")
    """
    print(code)

def AES():
    code = """
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt(plaintext, key):
    # Ensure key is 16, 24, or 32 bytes for AES
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return cipher.iv + ciphertext  # Return the IV concatenated with ciphertext

def decrypt(ciphertext, key):
    # Extract the IV from the ciphertext
    iv = ciphertext[:AES.block_size]
    ciphertext = ciphertext[AES.block_size:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()

# Example Usage:
key = get_random_bytes(16)  # Key must be 16, 24, or 32 bytes (128, 192, or 256 bits)
plaintext = "This is a secret message."

# Encrypt the message
encrypted = encrypt(plaintext, key)
print(f"Encrypted: {encrypted.hex()}")

# Decrypt the message
decrypted = decrypt(encrypted, key)
print(f"Decrypted: {decrypted}")
    """
    print(code)

def RSA():
    code = """
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

def generate_keys():
    # Generate a pair of RSA keys (private and public)
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def encrypt(plaintext, public_key):
    # Encrypt the plaintext using the public key
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return ciphertext

def decrypt(ciphertext, private_key):
    # Decrypt the ciphertext using the private key
    key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(key)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode()

# Example Usage:
private_key, public_key = generate_keys()

plaintext = "This is a secret message."

# Encrypt the message
encrypted = encrypt(plaintext, public_key)
print(f"Encrypted: {encrypted.hex()}")

# Decrypt the message
decrypted = decrypt(encrypted, private_key)
print(f"Decrypted: {decrypted}")
    """
    print(code)





