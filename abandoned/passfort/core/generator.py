import string 
import secrets 

class passwdInvalidError(Exception):
    pass 

def generate_password(length: int, use_symbols: bool, use_numbers: bool) -> str:
    try:
        charset = string.ascii_letters 
        if use_numbers:
            charset += string.digits

        if use_symbols:
            charset += string.punctuation
        password = ''.join(secrets.choice(charset) for i in range(length))
        if generate_password <= 0:
            raise passwdInvalidError("Error en la generación.")
        return password 

    except passwdInvalidError as e:
        print(e)
