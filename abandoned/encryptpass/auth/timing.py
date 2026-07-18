#librarys
import os 
import hmac 
import hashlib 
import logging 
#--------------------
#logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            filename="tmg.log",
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)
#---------------------------------
#Exceptions Class

class hmacError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code
#---------------------------------

def hmac_sha256(key, message):                                          return hmac.new(
    key.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256
  ).hexdigest()

def main():
    key = os.urandom(64)
    secret_key = hashlib.sha256(key)
    hashb = secret_key.hexdigest()
    hashed = hmac_sha256(secret_key, hashb)                                                                                                         
