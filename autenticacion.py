import json
from typing import List, Dict, Optional

from cryptography.fernet import InvalidToken

from configuracion import (
    ARCHIVO_CREDENCIALES,
    ROL_SUPERUSUARIO, ROL_ADMINISTRADOR, ROL_USUARIO,
    ROLES_ASIGNABLES_ADMIN, ROLES_ASIGNABLES_SUPER, ROLES_GESTORES,
)
from cifrado import cifrar, descifrar, generar_hash_clave, verificar_clave
import registro_actividad
import permisos
import bloqueo


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
    permisos.escribir_bytes_protegido(
        ARCHIVO_CREDENCIALES,
        cifrar(json.dumps(usuarios, ensure_ascii=False, indent=2)),
    )


def roles_asignables(actor_rol: str) -> List[str]:
    """Roles que puede otorgar quien gestiona usuarios.

    El superusuario puede otorgar cualquiera; el administrador solo el rol
    'usuario', porque su ámbito son los usuarios regulares (no puede crear ni
    promover administradores)."""
    return list(ROLES_ASIGNABLES_SUPER if actor_rol == ROL_SUPERUSUARIO
                else ROLES_ASIGNABLES_ADMIN)


def _validar_rol_asignable(rol: str, actor_rol: str, accion: str) -> None:
    """Comprueba que el actor pueda otorgar ese rol, con un mensaje que
    explique el motivo cuando no puede."""
    permitidos = roles_asignables(actor_rol)
    if rol in permitidos:
        return
    if rol in (ROL_SUPERUSUARIO, ROL_ADMINISTRADOR):
        raise ValueError(
            f"Solo un superusuario puede {accion} un '{rol}'. "
            f"Un administrador solo gestiona usuarios con rol '{ROL_USUARIO}'."
        )
    raise ValueError(
        "El rol debe ser " + " o ".join(f"'{r}'" for r in permitidos) + "."
    )


def _contar_superusuarios(usuarios: List[Dict]) -> int:
    return sum(1 for u in usuarios if u.get("rol") == ROL_SUPERUSUARIO)


def puede_gestionar_a(actor: str, actor_rol: str, objetivo_usuario: str,
                      objetivo_rol: str) -> bool:
    """¿El actor puede modificar a ese usuario?

    - Superusuario: a cualquiera.
    - Administrador: solo a usuarios con rol 'usuario', y a su propia cuenta.
      No alcanza a otros administradores ni a los superusuarios.
    """
    if actor_rol == ROL_SUPERUSUARIO:
        return True
    if actor_rol != ROL_ADMINISTRADOR:
        return False
    if (objetivo_usuario or "").strip().lower() == (actor or "").strip().lower():
        return True          # su propia cuenta
    return objetivo_rol == ROL_USUARIO


def _validar_alcance(objetivo: Dict, actor: str, actor_rol: str,
                     accion: str) -> None:
    """Comprueba el alcance del actor sobre el usuario objetivo."""
    if puede_gestionar_a(actor, actor_rol, objetivo.get("usuario", ""),
                         objetivo.get("rol", "")):
        return
    raise ValueError(
        f"Un administrador solo puede {accion} usuarios con rol "
        f"'{ROL_USUARIO}' (y su propia cuenta). Para {accion} a otro "
        "administrador o a un superusuario se necesita un superusuario."
    )


def _validar_gestion_de_superusuario(objetivo: Dict, usuarios: List[Dict],
                                     actor_rol: str, accion: str) -> None:
    """Reglas para tocar a un superusuario.

    - Solo otro superusuario puede hacerlo (un administrador nunca).
    - Nunca se puede dejar al sistema sin superusuarios: el último está
      protegido frente a eliminación y cambio de rol.
    """
    if objetivo.get("rol") != ROL_SUPERUSUARIO:
        return
    if actor_rol != ROL_SUPERUSUARIO:
        raise ValueError(
            f"Solo un superusuario puede {accion} a otro superusuario."
        )
    if _contar_superusuarios(usuarios) <= 1:
        raise ValueError(
            f"No se puede {accion} al único superusuario del sistema. "
            "Cree otro superusuario antes."
        )


def _buscar(usuarios: List[Dict], usuario: str) -> Optional[Dict]:
    usuario = usuario.strip().lower()
    for usu in usuarios:
        if usu["usuario"] == usuario:
            return usu
    return None


def existe_algun_usuario() -> bool:
    return len(_leer_usuarios()) > 0


@bloqueo.con_bloqueo("credenciales")
def crear_usuario(usuario: str, nombre: str, clave: str,
                  rol: str = ROL_USUARIO, actor: str = "sistema",
                  actor_rol: str = None) -> str:
    """Crea un usuario. El primer usuario del sistema se crea siempre como
    superusuario. Después, un **superusuario** puede crear cualquier rol
    (incluidos otros superusuarios y administradores) y un **administrador**
    solo usuarios con rol 'usuario'. Devuelve el rol finalmente asignado."""
    usuario = usuario.strip().lower()
    if not usuario or not clave:
        raise ValueError("Usuario y contraseña son obligatorios.")
    usuarios = _leer_usuarios()
    if _buscar(usuarios, usuario) is not None:
        raise ValueError(f"El usuario '{usuario}' ya existe.")

    if not usuarios:
        # Primer usuario del sistema: superusuario.
        rol = ROL_SUPERUSUARIO
    else:
        _validar_rol_asignable(rol, actor_rol, "crear")

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


@bloqueo.con_bloqueo("credenciales")
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

    # Alcance: un administrador solo llega a usuarios regulares y a sí mismo.
    _validar_alcance(objetivo, actor, actor_rol, "editar")

    cambios = []
    if nombre is not None and nombre.strip() and nombre.strip() != objetivo["nombre"]:
        objetivo["nombre"] = nombre.strip()
        cambios.append(f"nombre={objetivo['nombre']}")

    if rol is not None and rol != objetivo["rol"]:
        _validar_rol_asignable(rol, actor_rol, "asignar el rol de")
        # Degradar a un superusuario solo es posible si queda otro.
        _validar_gestion_de_superusuario(objetivo, usuarios, actor_rol,
                                         "cambiar el rol")
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


@bloqueo.con_bloqueo("credenciales")
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
    # Alcance: un administrador solo llega a usuarios regulares.
    _validar_alcance(objetivo, actor, actor_rol, "eliminar")
    # Un superusuario nunca se elimina si es el último que queda.
    _validar_gestion_de_superusuario(objetivo, usuarios, actor_rol, "eliminar")
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


@bloqueo.con_bloqueo("credenciales")
def restablecer_clave(usuario: str, actor: str, actor_rol: str,
                      nueva_clave: str) -> None:
    """Restablece (recupera) la contraseña de un usuario. Pensado para que un
    gestor le ceda el teclado al usuario y este escriba su nueva contraseña.

    Un **superusuario** puede restablecer la de cualquiera. Un
    **administrador** solo la de usuarios con rol 'usuario' y la suya propia."""
    if actor_rol not in ROLES_GESTORES:
        raise ValueError("No tiene permisos para restablecer contraseñas.")
    if not nueva_clave:
        raise ValueError("La nueva contraseña no puede estar vacía.")

    usuarios = _leer_usuarios()
    objetivo = _buscar(usuarios, usuario)
    if objetivo is None:
        raise ValueError("No se encontró el usuario indicado.")
    # Alcance: un administrador solo llega a usuarios regulares y a sí mismo.
    _validar_alcance(objetivo, actor, actor_rol, "restablecer la contraseña de")

    objetivo["sal"], objetivo["hash"] = generar_hash_clave(nueva_clave)
    _guardar_usuarios(usuarios)
    registro_actividad.registrar(
        "RESTABLECER_CLAVE", f"usuario={objetivo['usuario']}", actor)


def cerrar_sesion(usuario: str) -> None:
    """Registra en la bitácora el cierre de sesión del usuario."""
    registro_actividad.registrar("CIERRE_SESION", f"usuario={usuario}", usuario)


def listar_usuarios() -> List[Dict]:
    return [{"usuario": usu["usuario"], "nombre": usu["nombre"],
             "rol": usu.get("rol", ROL_USUARIO)} for usu in _leer_usuarios()]
