"""
SIMULACIÓN CONCEPTUAL — crypt.py (EncryptPart)
 
Solo prints e inputs. No hay cifrado, no hay derivación de clave,
no se toca ningún dispositivo real. Sirve para visualizar el flujo
de la CLI antes de implementar la lógica de verdad.
"""
 
import time
import random
 
 
def pausa(segundos=0.6):
    time.sleep(segundos)
 
 
def simular_registro():
    print("Detectando si hay registro...")
    pausa()
 
    # Simulación: la mitad de las veces "existe", la otra mitad no
    existe = random.choice([True, False])
 
    if not existe:
        print("(-) No existe registro\n")
        print("Register Crypto")
        usuario = input("usuario: ")
        contrasena = input("contraseña del usuario: ")
        pausa()
        print("---")
        print("Completado\n")
 
        id_generado = random.randint(1000000000, 9999999999)
        print(f"ID: {id_generado}")
        print(f"Usuario: {usuario}")
        print("Contraseña: " + "*" * len(contrasena))
        print("Fingerprint system: 9f86d081884c7d659a2f...")
        print("Archivo de sesión: register.enc\n")
        return True
    else:
        print("(+) Registro encontrado: register.enc\n")
        print("Login Crypto")
        usuario = input("usuario: ")
 
        intentos = 0
        max_intentos = 3
        while intentos < max_intentos:
            contrasena = input("contraseña: ")
            pausa()
            # Simulación: 70% de probabilidad de "acierto"
            if random.random() < 0.7:
                print("(+) Autenticado\n")
                return True
            else:
                intentos += 1
                print(f"(-) Contraseña incorrecta (intento {intentos}/{max_intentos})")
 
        print("(-) Demasiados intentos fallidos. Abortando.\n")
        return False
 
 
def simular_seleccion_particion():
    print("Particiones detectadas:")
    particiones = ["/dev/sdb1", "/dev/sdc1"]
    for i, p in enumerate(particiones, 1):
        print(f"  [{i}] {p}")
 
    seleccion = input("Seleccioná partición a encriptar (número): ")
    try:
        idx = int(seleccion) - 1
        particion = particiones[idx]
    except (ValueError, IndexError):
        print("(-) Selección inválida. Abortando.")
        return None
 
    pausa()
    # Simulación: a veces "está montada"
    if random.choice([True, False]):
        print(f"(-) {particion} está montada. Desmontá antes de continuar (umount {particion})")
        return None
 
    print(f"(+) {particion} disponible para cifrado")
    return particion
 
 
def simular_cifrado(particion):
    password_particion = input("\nPASSWORD de encriptado de la partición: ")
    pausa()
 
    print(f"\nCifrando {particion}...")
    for pct in [0, 25, 50, 75, 100]:
        print(f"  Progreso: {pct}%")
        pausa(0.3)
 
    print(f"\nPartición {particion} completada con encriptado listo.")
 
 
def main():
    print("$ python3 main.py encriptar particiones\n")
 
    autenticado = simular_registro()
    if not autenticado:
        return
 
    particion = simular_seleccion_particion()
    if particion is None:
        return
 
    simular_cifrado(particion)
 
 
if __name__ == "__main__":
    main()
