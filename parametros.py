"""
Parámetros del sistema (archivo cifrado `datos/parametros.dat`).

Hoy guarda un único parámetro: el **secuencial inicial de la Referencia UDC**,
que es independiente para cada institución.

Contexto: la Referencia UDC tiene el formato

    REQ-UDC-<sigla>-<secuencial de 4 dígitos>      REQ-UDC-SB-0001
                                                   REQ-UDC-FGE-0001

La sigla la aporta la institución que remite el oficio (ver
`configuracion.INSTITUCIONES`) y el secuencial corre de forma **continua** para
cada una: no se reinicia por año, porque el año no forma parte de la
referencia.

Si al empezar ya se llevaba una numeración fuera del sistema, un gestor indica
por institución cuál fue el último número usado y la aplicación continúa desde
el siguiente.
"""
import json
import re
from typing import Dict, Optional

from cryptography.fernet import InvalidToken

from configuracion import (
    ARCHIVO_PARAMETROS, PREFIJO_REFERENCIA, INSTITUCIONES, ROLES_GESTORES
)
from cifrado import cifrar, descifrar
import registro_actividad
import permisos
import bloqueo


# Acepta "REQ-UDC-SB-0001" con cualquiera de las siglas configuradas, sin
# distinguir mayúsculas ni espacios sobrantes.
_PATRON_REFERENCIA = re.compile(
    rf"^{re.escape(PREFIJO_REFERENCIA)}-([A-Za-zÁÉÍÓÚÑ]+)-(\d{{1,6}})$",
    re.IGNORECASE)


# --- Persistencia ------------------------------------------------------------
def _leer() -> Dict:
    if not ARCHIVO_PARAMETROS.exists():
        return {}
    try:
        return json.loads(descifrar(ARCHIVO_PARAMETROS.read_bytes()))
    except InvalidToken:
        raise ValueError(
            "El archivo de parámetros fue alterado o la clave no coincide."
        )


def _guardar(datos: Dict) -> None:
    permisos.escribir_bytes_protegido(
        ARCHIVO_PARAMETROS, cifrar(json.dumps(datos, ensure_ascii=False, indent=2))
    )


# --- Instituciones y siglas ---------------------------------------------------
def sigla_de(institucion: str) -> str:
    """Sigla de la referencia para esa institución (por ejemplo 'SB')."""
    institucion = " ".join(str(institucion or "").split())
    for nombre, sigla in INSTITUCIONES.items():
        if nombre.casefold() == institucion.casefold() or sigla.casefold() == institucion.casefold():
            return sigla
    raise ValueError(
        f"«{institucion}» no es una institución válida. "
        f"Opciones: {', '.join(INSTITUCIONES)}."
    )


def institucion_de(sigla: str) -> str:
    """Nombre de la institución a partir de su sigla."""
    for nombre, propia in INSTITUCIONES.items():
        if propia.casefold() == str(sigla or "").casefold():
            return nombre
    return ""


def validar_institucion(institucion: str) -> str:
    """Devuelve el nombre normalizado de la institución (o lanza un error)."""
    return institucion_de(sigla_de(institucion))


# --- Secuencial inicial de la Referencia UDC ---------------------------------
def analizar_referencia(referencia: str, institucion: Optional[str] = None):
    """Descompone una referencia UDC en (sigla, secuencial).

    Acepta la referencia completa (`REQ-UDC-SB-0241`) o solo el número
    (`241`), en cuyo caso hay que indicar la institución.
    """
    referencia = " ".join(str(referencia or "").split())
    if not referencia:
        raise ValueError("Debe ingresar la última Referencia UDC registrada.")

    coincidencia = _PATRON_REFERENCIA.match(referencia)
    if coincidencia:
        sigla = coincidencia.group(1).upper()
        if not institucion_de(sigla):
            raise ValueError(
                f"«{sigla}» no corresponde a ninguna institución. "
                f"Siglas válidas: {', '.join(INSTITUCIONES.values())}."
            )
        return sigla, int(coincidencia.group(2))
    if referencia.isdigit() and institucion:
        return sigla_de(institucion), int(referencia)
    ejemplo = f"{PREFIJO_REFERENCIA}-{list(INSTITUCIONES.values())[0]}-0241"
    raise ValueError(
        f"Formato no válido. Use {PREFIJO_REFERENCIA}-SIGLA-NNNN "
        f"(por ejemplo {ejemplo})."
    )


def formatear_referencia(sigla: str, secuencial: int) -> str:
    return f"{PREFIJO_REFERENCIA}-{sigla.upper()}-{int(secuencial):04d}"


def obtener_secuencial_inicial(institucion: str) -> int:
    """Último secuencial ya usado fuera del sistema para esa institución.
    Devuelve 0 si no se configuró nada."""
    try:
        sigla = sigla_de(institucion)
    except ValueError:
        return 0
    datos = (_leer().get("secuenciales") or {}).get(sigla) or {}
    return int(datos.get("secuencial", 0))


def obtener_referencia_inicial(institucion: str) -> str:
    """Referencia configurada para esa institución, o '' si no hay ninguna."""
    try:
        sigla = sigla_de(institucion)
    except ValueError:
        return ""
    datos = (_leer().get("secuenciales") or {}).get(sigla) or {}
    if not datos:
        return ""
    return formatear_referencia(sigla, datos["secuencial"])


def esta_configurado(institucion: Optional[str] = None) -> bool:
    secuenciales = _leer().get("secuenciales") or {}
    if institucion is None:
        return bool(secuenciales)
    try:
        return sigla_de(institucion) in secuenciales
    except ValueError:
        return False


@bloqueo.con_bloqueo("parametros")
def definir_secuencial_inicial(referencia: str, actor: str, actor_rol: str,
                               institucion: Optional[str] = None) -> str:
    """Fija la última referencia usada antes del sistema para una institución.

    Pueden definirla el **superusuario** y los **administradores**. Devuelve la
    referencia normalizada que quedó guardada.
    """
    if actor_rol not in ROLES_GESTORES:
        raise ValueError(
            "Solo el superusuario o un administrador pueden definir el "
            "secuencial inicial."
        )
    sigla, secuencial = analizar_referencia(referencia, institucion)
    # Si se indicó la institución en el desplegable y además una referencia
    # completa de otra, manda lo escrito pero se avisa de la contradicción.
    if institucion:
        esperada = sigla_de(institucion)
        if esperada != sigla:
            raise ValueError(
                f"La referencia corresponde a {institucion_de(sigla)} pero se "
                f"eligió {institucion_de(esperada)}. Corrija una de las dos."
            )

    datos = _leer()
    datos.setdefault("secuenciales", {})[sigla] = {
        "secuencial": secuencial,
        "definido_por": actor,
        "definido_el": __import__("datetime").date.today().isoformat(),
    }
    _guardar(datos)
    normalizada = formatear_referencia(sigla, secuencial)
    registro_actividad.registrar(
        "DEFINIR_SECUENCIAL_INICIAL",
        f"institucion={institucion_de(sigla)}; referencia={normalizada}", actor)
    return normalizada
