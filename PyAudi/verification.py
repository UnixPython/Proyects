import logging
import subprocess

logger = logging.getLogger(__name__)

def verify():
    try:
        cmd = [
            "dpkg -l | grep aide",
            "dpkg -l | grep aide-common",
            "dpkg -l | grep lynis",
            "dpkg -l | grep chkrootkit",
            "dpkg -l | grep rkhunter",
            "dpkg -l | grep tripwire",
        ]

        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=True
        )
        logger.info("Se realizó la ejecución.")
        return result.stdout
    except FileNotFoundError as cmd:
        print("[!] No se encontró el binario. ", cmd)
    except KeyboardInterrupt:
        print("Se canceló el proceso.")
        logger.warning("[*] El usuario canceló el proceso.")
    else:
        if result.returncode != 0:
            print(f"[!] Falló el proceso con código {result.returncode}")
            print(f"[!] Error: {result.stderr}")

def install_and_verify_tools():
    """
    Instala las herramientas Y verifica que estén instaladas correctamente
    """
    tools = {
        'aide': 'aide --version',
        'lynis': 'lynis --version',
        'chkrootkit': 'chkrootkit -V',
        'rkhunter': 'rkhunter --version',
        'tripwire': 'tripwire --version'
    }
    
    try:
        # 1. ACTUALIZAR REPOSITORIOS
        print("[*] Actualizando repositorios...")
        subprocess.run(
            "sudo apt update",
            shell=True,
            capture_output=True,
            check=True
        )
        logger.info("Repositorios actualizados")
        print("[✓] Repositorios actualizados\n")
        
        # 2. INSTALAR HERRAMIENTAS
        print("[*] Instalando herramientas de auditoría...\n")
        
        install_cmd = "sudo apt install -y aide aide-common lynis chkrootkit rkhunter tripwire audispd-plugins"
        
        result = subprocess.run(
            install_cmd,
            shell=True,
            text=True,
            check=True,
            capture_output=True
        )
        
        if result.returncode != 0:
            print(f"[!] Error en instalación: {result.stderr}")
            logger.error(f"Error instalando herramientas: {result.stderr}")
            return False
        
        logger.info("Herramientas instaladas correctamente")
        print("[✓] Herramientas instaladas\n")
        
        # 3. VERIFICAR INSTALACIÓN
        print("[*] Verificando instalación...\n")
        
        results = {}
        for tool, version_cmd in tools.items():
            try:
                result = subprocess.run(
                    version_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0][:50]
                    print(f"[✓] {tool:15} | {version}")
                    results[tool] = 'OK'
                    logger.info(f"{tool} verificado correctamente")
                else:
                    print(f"[!] {tool:15} | Error en verificación")
                    results[tool] = 'ERROR'
                    logger.warning(f"{tool} no pudo ser verificado")
                    
            except subprocess.TimeoutExpired:
                print(f"[!] {tool:15} | Timeout")
                results[tool] = 'TIMEOUT'
            except Exception as e:
                print(f"[!] {tool:15} | {str(e)}")
                results[tool] = 'ERROR'
        
        # 4. RESUMEN
        print(f"\n{'='*50}")
        total = len(results)
        ok = len([v for v in results.values() if v == 'OK'])
        print(f"[RESUMEN] {ok}/{total} herramientas instaladas correctamente")
        print(f"{'='*50}\n")
        
        logger.info(f"Instalación completada: {ok}/{total} herramientas OK")
        
        return ok == total
        
    except FileNotFoundError as e:
        print(f"[!] Binario no encontrado: {e}")
        logger.error(f"FileNotFoundError: {e}")
        return False
        
    except KeyboardInterrupt:
        print("\n[!] Instalación cancelada por el usuario")
        logger.warning("Instalación cancelada por teclado (Ctrl+C)")
        return False 
