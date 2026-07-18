import getpass
import bcrypt

MAX_TRIES = 3

def save_user(username, password):
    with open("users.db", "a") as f:
        f.write(f"{username}:{password}\n")

def user_exists(username):
    try:
        with open("users.db", "r") as f:
            for line in f:
                user = line.strip().split(":")[0]
                if user == username:
                    return True 
    except FileNotFoundError: 
        return False
    return False

def register_user():
    username = input("New user:  ")

    if user_exists(username):
        print("Usuario existe.")
        return 

    passwd = getpass.getpass("New password:   ").encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd, salt).decode()

    save_user(username, hashed)
    print("[+] User created")

def login_user(username, password):
    try:
        with open("users.db", "r") as f:
            for line in f: 
                try:
                    user, passwd = line.strip().split(":")
                except ValueError:
                    print("Error de valor.")
                    continue
                if user == username and bcrypt.checkpw(password.encode(), passwd.encode()):
                    return True
                return False
    except FileNotFoundError:
        print("Archivo no encontrado.")
        return False

def login_flow():
    attempts = 0

    while attempts < MAX_TRIES:
        username = input("User:  ")
        password = getpass.getpass("Password:  ")

        if login_user(username, password):
            print("ACCESS GRANTED!")
            return True
        else:
            print("ACCESS DENIED")
            attempts += 1
    
    print("Too many attempts.")
    return False



