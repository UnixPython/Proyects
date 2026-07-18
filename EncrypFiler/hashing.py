import hashlib
import hmac 

# hashear archivo SHA-256
def calculate_hash_archive(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha256.update(bloque)
    return sha256.hexdigest()

#corregir con compare_digest 
# verificación de hashing (texto)
def verify_hash(data, hash_original):
    hash_calculate = hashlib.sha256(data.encode("utf-8")).hexdigest()
    return hmac.compare_digest(hash_calculate, hash_original)
    
# guardar hash de archivo
def save_hash(file_path, hash_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            sha256.update(bloque)

    with open(hash_path, "w") as f_hash:
        f_hash.write(sha256.hexdigest())
