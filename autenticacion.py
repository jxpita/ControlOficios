import json
from typing import List, Dict, Optional

from cryptography.fernet import InvalidToken

from configuracion import ARCHIVO_CREDENCIALES
from cifrado import cifrar, descifrar, generar_hash_clave, verificar_clave


def _leer_usuarios() -> List[Dict]:
    if not ARCHIVO_CREDENCIALES.exists():
        return []
    try:
        return json.loads(descifrar(ARCHIVO_CREDENCIALES.read_bytes()))
    except InvalidToken:
        raise ValueError(
            "El archivo de credenciales fue alterado o la clave no coincide."
        )


def _guardar_usuarios(usuarios: List[Dict]) -> None:
    ARCHIVO_CREDENCIALES.write_bytes(
        cifrar(json.dumps(usuarios, ensure_ascii=False, indent=2))
    )


def existe_algun_usuario() -> bool:
    return len(_leer_usuarios()) > 0


def crear_usuario(usuario: str, nombre: str, clave: str) -> None:
    usuario = usuario.strip().lower()
    if not usuario or not clave:
        raise ValueError("Usuario y contraseña son obligatorios.")
    usuarios = _leer_usuarios()
    if any(usu["usuario"] == usuario for usu in usuarios):
        raise ValueError(f"El usuario '{usuario}' ya existe.")
    sal, hash_clave = generar_hash_clave(clave)
    usuarios.append(
        {"usuario": usuario, "nombre": nombre.strip(), "sal": sal, "hash": hash_clave}
    )
    _guardar_usuarios(usuarios)


def validar_acceso(usuario: str, clave: str) -> Optional[Dict]:
    usuario = usuario.strip().lower()
    for usu in _leer_usuarios():
        if usu["usuario"] == usuario and verificar_clave(clave, usu["sal"], usu["hash"]):
            return {"usuario": usu["usuario"], "nombre": usu["nombre"]}
    return None


def listar_usuarios() -> List[Dict]:
    return [{"usuario": usu["usuario"], "nombre": usu["nombre"]} for usu in _leer_usuarios()]
