from commands import runs
try:
    if __name__ == "__main__":
        runs()
except KeyboardInterrupt:
    print("Se canceló el proceso")
except FileNotFoundError:
    print("Archivo no existe")
