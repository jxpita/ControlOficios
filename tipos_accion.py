"""
Catálogo de TIPOS DE ACCIÓN que se piden en un oficio.

Es una lista mantenible desde la pestaña Configuración: la primera vez se
siembra con los valores de `TIPOS_ACCION_INICIALES` y a partir de ahí el
superusuario o un administrador pueden añadir, renombrar o retirar entradas.

Se guarda aparte de los parámetros del sistema porque es un catálogo con vida
propia (crece con el tiempo) y no un ajuste único.

Un tipo que ya esté en uso NO se puede eliminar: dejaría oficios apuntando a
algo que ya no existe. Renombrarlo sí, y el cambio se propaga a los oficios que
lo tenían, para que no queden descolgados.
"""
import json
from typing import Dict, List

from cryptography.fernet import InvalidToken

from configuracion import (
    ARCHIVO_TIPOS_ACCION, TIPOS_ACCION_INICIALES, ROLES_GESTORES
)
from cifrado import cifrar, descifrar
import registro_actividad
import permisos
import bloqueo


def _leer() -> List[str]:
    if not ARCHIVO_TIPOS_ACCION.exists():
        return list(TIPOS_ACCION_INICIALES)
    try:
        datos = json.loads(descifrar(ARCHIVO_TIPOS_ACCION.read_bytes()))
    except InvalidToken:
        raise ValueError(
            "El catálogo de tipos de acción fue alterado o la clave no coincide."
        )
    tipos = datos.get("tipos") if isinstance(datos, dict) else datos
    return [t for t in (tipos or []) if str(t).strip()]


def _guardar(tipos: List[str]) -> None:
    permisos.escribir_bytes_protegido(
        ARCHIVO_TIPOS_ACCION,
        cifrar(json.dumps({"tipos": tipos}, ensure_ascii=False, indent=2)),
    )


_ACENTOS = str.maketrans("áéíóúàèìòùäëïöüâêîôûÁÉÍÓÚÄËÏÖÜÂÊÎÔÛ",
                         "aeiouaeiouaeiouaeiouAEIOUAEIOUAEIOU")


def _normalizar(texto) -> str:
    """Para comparar sin distinguir mayúsculas, tildes ni espacios sobrantes.

    Las tildes se ignoran a propósito: la matriz escribe «RETENCIÓN» y quien
    teclea a mano suele omitirlas, y son el mismo tipo de acción.
    """
    return " ".join(str(texto or "").translate(_ACENTOS).split()).casefold()


def listar() -> List[str]:
    """Tipos de acción disponibles, en orden alfabético."""
    return sorted(_leer(), key=_normalizar)


def existe(tipo: str) -> bool:
    return _normalizar(tipo) in {_normalizar(t) for t in _leer()}


def validar(tipo: str) -> str:
    """Comprueba que el tipo de acción esté en el catálogo y lo devuelve tal
    como está registrado en él (para no guardar variantes de escritura)."""
    tipo = " ".join(str(tipo or "").split())
    if not tipo:
        raise ValueError("Debe indicar el tipo de acción del oficio.")
    for registrado in _leer():
        if _normalizar(registrado) == _normalizar(tipo):
            return registrado
    raise ValueError(
        f"El tipo de acción «{tipo}» no está en el catálogo. "
        "Puede añadirlo desde la pestaña Configuración."
    )


def _exigir_gestor(actor_rol: str) -> None:
    if actor_rol not in ROLES_GESTORES:
        raise ValueError(
            "El mantenimiento de los tipos de acción está reservado a "
            "administradores y al superusuario."
        )


@bloqueo.con_bloqueo("tipos_accion")
def agregar(tipo: str, actor: str, actor_rol: str) -> str:
    _exigir_gestor(actor_rol)
    tipo = " ".join(str(tipo or "").split())
    if len(tipo) < 3:
        raise ValueError("Indique el nombre del tipo de acción.")
    tipos = _leer()
    if any(_normalizar(t) == _normalizar(tipo) for t in tipos):
        raise ValueError(f"El tipo de acción «{tipo}» ya existe.")
    tipos.append(tipo)
    _guardar(tipos)
    registro_actividad.registrar("AGREGAR_TIPO_ACCION", f"tipo={tipo}", actor)
    return tipo


@bloqueo.con_bloqueo("tipos_accion")
def renombrar(anterior: str, nuevo: str, actor: str, actor_rol: str) -> int:
    """Cambia el nombre de un tipo de acción y lo propaga a los oficios que lo
    usaban. Devuelve cuántos oficios se actualizaron."""
    _exigir_gestor(actor_rol)
    nuevo = " ".join(str(nuevo or "").split())
    if len(nuevo) < 3:
        raise ValueError("Indique el nuevo nombre del tipo de acción.")
    tipos = _leer()
    posicion = next((i for i, t in enumerate(tipos)
                     if _normalizar(t) == _normalizar(anterior)), None)
    if posicion is None:
        raise ValueError(f"El tipo de acción «{anterior}» no existe.")
    if (any(_normalizar(t) == _normalizar(nuevo) for t in tipos)
            and _normalizar(nuevo) != _normalizar(anterior)):
        raise ValueError(f"Ya existe un tipo de acción llamado «{nuevo}».")

    tipos[posicion] = nuevo
    _guardar(tipos)
    # Import diferido: el almacén de oficios no depende de este módulo.
    import almacen_oficios
    actualizados = almacen_oficios.renombrar_tipo_accion(anterior, nuevo, actor)
    registro_actividad.registrar(
        "RENOMBRAR_TIPO_ACCION",
        f"anterior={anterior}; nuevo={nuevo}; oficios={actualizados}", actor)
    return actualizados


@bloqueo.con_bloqueo("tipos_accion")
def eliminar(tipo: str, actor: str, actor_rol: str) -> None:
    """Retira un tipo de acción del catálogo, siempre que no esté en uso."""
    _exigir_gestor(actor_rol)
    tipos = _leer()
    if not any(_normalizar(t) == _normalizar(tipo) for t in tipos):
        raise ValueError(f"El tipo de acción «{tipo}» no existe.")
    if len(tipos) <= 1:
        raise ValueError(
            "Debe quedar al menos un tipo de acción: es un campo obligatorio "
            "del oficio."
        )
    import almacen_oficios
    en_uso = almacen_oficios.contar_por_tipo_accion(tipo)
    if en_uso:
        raise ValueError(
            f"No se puede eliminar: {en_uso} oficio(s) usan «{tipo}». "
            "Puede renombrarlo, y el cambio se aplicará a esos oficios."
        )
    _guardar([t for t in tipos if _normalizar(t) != _normalizar(tipo)])
    registro_actividad.registrar("ELIMINAR_TIPO_ACCION", f"tipo={tipo}", actor)


def uso_actual() -> Dict[str, int]:
    """Cuántos oficios usa cada tipo de acción, para mostrarlo en el catálogo."""
    import almacen_oficios
    return {tipo: almacen_oficios.contar_por_tipo_accion(tipo)
            for tipo in listar()}
