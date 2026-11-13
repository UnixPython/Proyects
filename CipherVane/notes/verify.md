from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Ejemplo de clave pública en formato PEM (curva SECP256R1 / P-256)
pem_public_key = b"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1234567890abcdef1234567890ab
cdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab
cd==
-----END PUBLIC KEY-----"""


def verificar_clave_pem(pem_data: bytes) -> bool:
  try:
    # 1. Carga y valida automáticamente que el punto esté en la curva
    public_key = serialization.load_pem_public_key(pem_data)

    # 2. Comprobar que efectivamente sea una clave de Curva Elíptica (y no RSA, por ejemplo)
    if not isinstance(public_key, ec.EllipticCurvePublicKey):
      print("Error: La clave no es de tipo curva elíptica.")
      return False

    # 3. (Opcional) Verificar que pertenezca a una curva específica (ej. SECP256R1)
    if not isinstance(public_key.curve, ec.SECP256R1):
      print(
          f"Advertencia: Curva inesperada ({public_key.curve.name}). Se"
          " esperaba secp256r1."
      )
      return False

    print(f"Clave válida. Curva: {public_key.curve.name}")
    return True

  except ValueError as e:
    # Se lanza si el formato PEM es inválido o el punto NO pertenece a la curva
    print(f"Clave inválida o corrupta: {e}")
    return False
  except UnsupportedAlgorithm as e:
    print(f"Algoritmo o curva no soportada: {e}")
    return False


# Prueba con una clave real generada al vuelo para demostrar que funciona:
clave_privada_test = ec.generate_private_key(ec.SECP256R1())
pem_valido = clave_privada_test.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

verificar_clave_pem(pem_valido)
