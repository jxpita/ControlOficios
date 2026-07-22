import json
from typing import List, Dict, Optional

from cryptography.fernet import InvalidToken

from configuracion import (
    ARCHIVO_CREDENCIALES,
    ROL_SUPERUSUARIO, ROL_ADMINISTRADOR, ROL_USUARIO,
    ROLES_ASIGNABLES, ROLES_GESTORES,
)
from cifrado import cifrar, descifrar, generar_hash_clave, verificar_clave
import registro_actividad


def _normalizar_roles(usuarios: List[Dict]) -> List[Dict]:
    """Garantiza que cada usuario tenga un rol. Para archivos antiguos (sin
    campo 'rol'): si no hay ningún superusuario, el primero pasa a serlo y el
    resto quedan como 'usuario'."""
    tiene_super = any(u.get("rol") == ROL_SUPERUSUARIO for u in usuarios)
    for indice, usu in enumerate(usuarios):
        if not usu.get("rol"):
            if not tiene_super and indice == 0:
                usu["rol"] = ROL_SUPERUSUARIO
                tiene_super = True
            else:
                usu["rol"] = ROL_USUARIO
    return usuarios


def _leer_usuarios() -> List[Dict]:
    if not ARCHIVO_CREDENCIALES.exists():
        return []
    try:
        return _normalizar_roles(json.loads(descifrar(ARCHIVO_CREDENCIALES.read_bytes())))
    except InvalidToken:
        raise ValueError(
            "El archivo de credenciales fue alterado o la clave no coincide."
        )


def _guardar_usuarios(usuarios: List[Dict]) -> None:
    ARCHIVO_CREDENCIALES.write_bytes(
        cifrar(json.dumps(usuarios, ensure_ascii=False, indent=2))
    )


def _buscar(usuarios: List[Dict], usuario: str) -> Optional[Dict]:
    usuario = usuario.strip().lower()
    for usu in usuarios:
        if usu["usuario"] == usuario:
            return usu
    return None


def existe_algun_usuario() -> bool:
    return len(_leer_usuarios()) > 0


def crear_usuario(usuario: str, nombre: str, clave: str,
                  rol: str = ROL_USUARIO, actor: str = "sistema") -> str:
    """Crea un usuario. El primer usuario del sistema se crea siempre como
    superusuario; el resto solo pueden ser 'administrador' o 'usuario'.
    Devuelve el rol finalmente asignado."""
    usuario = usuario.strip().lower()
    if not usuario or not clave:
        raise ValueError("Usuario y contraseña son obligatorios.")
    usuarios = _leer_usuarios()
    if _buscar(usuarios, usuario) is not None:
        raise ValueError(f"El usuario '{usuario}' ya existe.")

    if not usuarios:
        # Primer usuario del sistema: superusuario.
        rol = ROL_SUPERUSUARIO
    elif rol not in ROLES_ASIGNABLES:
        raise ValueError("El rol debe ser 'administrador' o 'usuario'.")

    sal, hash_clave = generar_hash_clave(clave)
    usuarios.append({
        "usuario": usuario,
        "nombre": nombre.strip(),
        "sal": sal,
        "hash": hash_clave,
        "rol": rol,
    })
    _guardar_usuarios(usuarios)
    registro_actividad.registrar(
        "CREAR_USUARIO", f"usuario={usuario}; nombre={nombre.strip()}; rol={rol}",
        actor if actor != "sistema" else usuario)
    return rol


def editar_usuario(usuario: str, actor: str, actor_rol: str,
                   nombre: Optional[str] = None, clave: Optional[str] = None,
                   rol: Optional[str] = None) -> None:
    """Edita nombre, contraseña y/o rol de un usuario existente.
    Solo superusuario y administrador pueden editar. El rol del superusuario
    no puede cambiarse y nadie puede convertirse en superusuario."""
    if actor_rol not in ROLES_GESTORES:
        raise ValueError("No tiene permisos para editar usuarios.")

    usuarios = _leer_usuarios()
    objetivo = _buscar(usuarios, usuario)
    if objetivo is None:
        raise ValueError("No se encontró el usuario indicado.")

    cambios = []
    if nombre is not None and nombre.strip() and nombre.strip() != objetivo["nombre"]:
        objetivo["nombre"] = nombre.strip()
        cambios.append(f"nombre={objetivo['nombre']}")

    if rol is not None and objetivo["rol"] != ROL_SUPERUSUARIO:
        if rol not in ROLES_ASIGNABLES:
            raise ValueError("El rol debe ser 'administrador' o 'usuario'.")
        if rol != objetivo["rol"]:
            objetivo["rol"] = rol
            cambios.append(f"rol={rol}")

    if clave:
        objetivo["sal"], objetivo["hash"] = generar_hash_clave(clave)
        cambios.append("contraseña=(actualizada)")

    if not cambios:
        return
    _guardar_usuarios(usuarios)
    registro_actividad.registrar(
        "EDITAR_USUARIO", f"usuario={objetivo['usuario']}; {'; '.join(cambios)}", actor)


def eliminar_usuario(usuario: str, actor: str, actor_rol: str) -> None:
    """Elimina un usuario. El superusuario NO puede eliminarse bajo ninguna
    circunstancia y un usuario no puede eliminarse a sí mismo."""
    if actor_rol not in ROLES_GESTORES:
        raise ValueError("No tiene permisos para eliminar usuarios.")

    usuario = usuario.strip().lower()
    usuarios = _leer_usuarios()
    objetivo = _buscar(usuarios, usuario)
    if objetivo is None:
        raise ValueError("No se encontró el usuario indicado.")
    if objetivo["rol"] == ROL_SUPERUSUARIO:
        raise ValueError("El superusuario no puede eliminarse.")
    if usuario == (actor or "").strip().lower():
        raise ValueError("No puede eliminar su propio usuario mientras la sesión está activa.")

    usuarios = [u for u in usuarios if u["usuario"] != usuario]
    _guardar_usuarios(usuarios)
    registro_actividad.registrar("ELIMINAR_USUARIO", f"usuario={usuario}", actor)


def validar_acceso(usuario: str, clave: str) -> Optional[Dict]:
    usuario = usuario.strip().lower()
    for usu in _leer_usuarios():
        if usu["usuario"] == usuario and verificar_clave(clave, usu["sal"], usu["hash"]):
            registro_actividad.registrar("INICIO_SESION", f"usuario={usuario}", usuario)
            return {"usuario": usu["usuario"], "nombre": usu["nombre"],
                    "rol": usu.get("rol", ROL_USUARIO)}
    registro_actividad.registrar(
        "INICIO_SESION_FALLIDO", f"usuario={usuario}", usuario or "desconocido")
    return None


def listar_usuarios() -> List[Dict]:
    return [{"usuario": usu["usuario"], "nombre": usu["nombre"],
             "rol": usu.get("rol", ROL_USUARIO)} for usu in _leer_usuarios()]
