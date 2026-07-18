import json
from pathlib import Path
from datetime import datetime

def get_latest_result():
    try:
        print("Se verificará si la carpeta results existe.")

        rutes = Path("results")

        if rutes.exists():
            print("Carpeta existe.")
            archivos = sorted(rutes.glob("*.json"))

            if archivos:
                marca = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                ultimo = archivos[-1]
                print(f"El mas reciente es: {ultimo} {marca}")
                return ultimo
            else:
                print("La carpeta existe pero no tiene archivos .json")
                return
        else:
            print("Carpeta no existe.")
            return None

    except Exception:
        print("Error")

def save_results(datos: dict):
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    rutes = Path("results")
    rutes.mkdir(exist_ok=True)

    with open(rutes / f"resultado_{marca_tiempo}.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)

def load_result(rute_archive):
    try:
        with open(rute_archive, "r", encoding="utf-8") as f:
            content = json.load(f)
        return content
    except Exception:
        return {}
def compare_results(resultado_anterior: dict, resultado_actual: dict) -> dict:
    try:
        for clave, valor in resultado_actual.items():
            if clave in resultado_anterior:
                if valor != resultado_anterior[clave]:
                    return {
                        "clave": clave,
                        "anterior": resultado_anterior[clave],
                        "actual": valor,
                    }

        return {}

    except Exception:
        return {}

def flag_anomalies(resultado: dict) -> list:
    anom = []
    try:
        if resultado:
            anom.append(f"Cambio: {resultado}")
            return anom
        return []
    except ValueError:
        return anom
