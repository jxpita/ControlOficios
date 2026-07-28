"""
Parámetros del sistema (archivo cifrado `datos/parametros.dat`).

Hoy guarda un único parámetro: el **secuencial inicial de la Referencia UDC**.

Contexto: antes los oficios se llevaban en un Excel y no se migran los
registros anteriores. El superusuario indica una sola vez cuál fue la última
referencia registrada allí (por ejemplo `REQ-INF-2026-0241`) y el sistema
continúa a partir de ella (`REQ-INF-2026-0242`, ...).

El secuencial es **por año**: cada año la numeración vuelve a empezar en 0001,
y el valor configurado aplica al año que indica la propia referencia.
"""
import json
import re
from datetime import date
from typing import Dict, Optional

from cryptography.fernet import InvalidToken

from configuracion import ARCHIVO_PARAMETROS, PREFIJO_REFERENCIA, ROLES_GESTORES
from cifrado import cifrar, descifrar
import registro_actividad
import permisos
import bloqueo


# Acepta "REQ-INF-2026-0241" (con el prefijo configurado) sin distinguir
# mayúsculas ni espacios sobrantes.
_PATRON_REFERENCIA = re.compile(
    rf"^{re.escape(PREFIJO_REFERENCIA)}-(\d{{4}})-(\d{{1,6}})$", re.IGNORECASE)


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


# --- Secuencial inicial de la Referencia UDC ---------------------------------
def analizar_referencia(referencia: str):
    """Descompone una referencia UDC en (año, secuencial).

    Acepta la referencia completa (`REQ-INF-2026-0241`) o solo el número
    (`241`), en cuyo caso se asume el año en curso.
    """
    referencia = (referencia or "").strip()
    if not referencia:
        raise ValueError("Debe ingresar la última Referencia UDC registrada.")

    coincidencia = _PATRON_REFERENCIA.match(referencia)
    if coincidencia:
        return int(coincidencia.group(1)), int(coincidencia.group(2))
    if referencia.isdigit():
        return date.today().year, int(referencia)
    raise ValueError(
        f"Formato no válido. Use {PREFIJO_REFERENCIA}-AAAA-NNNN "
        f"(por ejemplo {PREFIJO_REFERENCIA}-{date.today().year}-0241)."
    )


def obtener_secuencial_inicial(anio: Optional[int] = None) -> int:
    """Último secuencial ya usado (fuera del sistema) para ese año.
    Devuelve 0 si no se configuró nada para ese año."""
    anio = anio or date.today().year
    datos = _leer().get("secuencial_inicial") or {}
    if datos.get("anio") == anio:
        return int(datos.get("secuencial", 0))
    return 0


def obtener_referencia_inicial() -> str:
    """Referencia configurada tal como se mostraría, o '' si no hay ninguna."""
    datos = _leer().get("secuencial_inicial") or {}
    if not datos:
        return ""
    return f"{PREFIJO_REFERENCIA}-{datos['anio']:04d}-{int(datos['secuencial']):04d}"


def esta_configurado() -> bool:
    return bool(_leer().get("secuencial_inicial"))


@bloqueo.con_bloqueo("parametros")
def definir_secuencial_inicial(referencia: str, actor: str, actor_rol: str) -> str:
    """Fija la última referencia registrada antes de usar el sistema.

    Pueden definirla el **superusuario** y los **administradores**. Devuelve la
    referencia normalizada que quedó guardada.
    """
    if actor_rol not in ROLES_GESTORES:
        raise ValueError(
            "Solo el superusuario o un administrador pueden definir el "
            "secuencial inicial."
        )
    anio, secuencial = analizar_referencia(referencia)
    if anio < 2000 or anio > date.today().year + 1:
        raise ValueError("El año de la referencia no es válido.")

    datos = _leer()
    datos["secuencial_inicial"] = {
        "anio": anio,
        "secuencial": secuencial,
        "definido_por": actor,
        "definido_el": date.today().isoformat(),
    }
    _guardar(datos)
    normalizada = f"{PREFIJO_REFERENCIA}-{anio:04d}-{secuencial:04d}"
    registro_actividad.registrar(
        "DEFINIR_SECUENCIAL_INICIAL", f"referencia={normalizada}", actor)
    return normalizada
