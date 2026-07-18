from cli import run
try:
    if __name__ == "__main__":
        run()
except KeyboardInterrupt:
    print("Se canceló el proceso")
except FileNotFoundError:
    print("Archivo no existe")
