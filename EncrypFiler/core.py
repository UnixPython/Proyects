import os
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
from Crypto.Cipher import AES 

def encrypt(filepath, password):
    password = password.encode() #str 
    salt = get_random_bytes(16) #sal de 16 digitos
    key = scrypt(password, salt, 32, N=2**14, r=8, p=1)  # type: ignore[reportArgumentType]
    #leer archivo
    with open(filepath, "rb") as f:
          data = f.read()
    cipher = AES.new(key, AES.MODE_GCM)  # type: ignore[reportCallIssue,reportArgumentType]
    ciphertext, tag = cipher.encrypt_and_digest(data)
    with open(filepath + ".enc", "wb") as f:
        f.write(salt)
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)
    os.remove(filepath)

def decrypt(filepath, password):
    try:
        password = password.encode()
        with open(filepath, "rb") as f:
            salt = f.read(16)
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        key = scrypt(password, salt, 32, N=2**14, r=8, p=1)  # type: ignore[reportArgumentType]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # type: ignore[reportCallIssue,reportArgumentType]
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        with open(filepath.replace(".enc", ""), "wb") as f:
            f.write(plaintext)
        print("Decryptacion correcta")
        return True
    except ValueError as e:
        print("Decryptacion invalida: ", str(e))
        return False

