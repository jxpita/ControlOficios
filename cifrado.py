import os
import hmac
import base64
import hashlib
from typing import Optional, Tuple

from cryptography.fernet import Fernet

from configuracion import ARCHIVO_CLAVE, ITERACIONES_PBKDF2
import permisos


# --- Clave maestra Fernet ----------------------------------------------------
def obtener_clave() -> bytes:
    """Devuelve la clave Fernet; la genera la primera vez que se ejecuta."""
    if ARCHIVO_CLAVE.exists():
        return ARCHIVO_CLAVE.read_bytes()
    clave = Fernet.generate_key()
    # La clave nunca se reescribe: se deja como solo lectura del propietario.
    permisos.escribir_bytes_protegido(ARCHIVO_CLAVE, clave)
    return clave


def _cifrador() -> Fernet:
    return Fernet(obtener_clave())


def cifrar(texto: str) -> bytes:
    return _cifrador().encrypt(texto.encode("utf-8"))


def descifrar(datos: bytes) -> str:
    """Descifra. Lanza cryptography.fernet.InvalidToken si el archivo
    fue alterado o si la clave no corresponde."""
    return _cifrador().decrypt(datos).decode("utf-8")


# --- Hashing de contraseñas --------------------------------------------------
def generar_hash_clave(clave: str, sal: Optional[bytes] = None) -> Tuple[str, str]:
    """Devuelve (sal_b64, hash_b64)."""
    if sal is None:
        sal = os.urandom(16)
    clave_derivada = hashlib.pbkdf2_hmac(
        "sha256", clave.encode("utf-8"), sal, ITERACIONES_PBKDF2
    )
    return base64.b64encode(sal).decode(), base64.b64encode(clave_derivada).decode()


def verificar_clave(clave: str, sal_b64: str, hash_b64: str) -> bool:
    sal = base64.b64decode(sal_b64)
    _, nuevo_hash = generar_hash_clave(clave, sal)
    return hmac.compare_digest(nuevo_hash, hash_b64)  # comparación segura
