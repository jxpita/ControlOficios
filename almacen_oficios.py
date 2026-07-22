"""
Capa de almacenamiento de OFICIOS.

*** Punto clave de arquitectura ***
Toda la app (interfaz y métricas) habla SOLO con las funciones de este módulo.
El día que migres a SQLite o a un motor SQL (ver README), reescribes el
cuerpo de estas funciones y NO tocas la interfaz ni las métricas.

Formato: oficios.dat cifrado con Fernet; internamente una lista JSON.
El código de oficio/circular se mapea a una referencia interna:
    UDC-OFICIO-AAAAMMDD-NNNN   (NNNN = secuencial de 4 dígitos, desde 0000)
El secuencial se reinicia por cada DÍA DE RECEPCIÓN. (Ver _generar_referencia
si prefieres usar la fecha de registro o un contador global.)
"""
import json
from datetime import datetime
from typing import List, Dict

from cryptography.fernet import InvalidToken

from configuracion import ARCHIVO_OFICIOS, PREFIJO_REFERENCIA, ESTADOS
from cifrado import cifrar, descifrar
import registro_actividad


# --- Persistencia ------------------------------------------------------------
def _leer_registros() -> List[Dict]:
    if not ARCHIVO_OFICIOS.exists():
        return []
    try:
        return json.loads(descifrar(ARCHIVO_OFICIOS.read_bytes()))
    except InvalidToken:
        raise ValueError(
            "El archivo de oficios fue alterado o la clave no coincide."
        )


def _guardar_registros(registros: List[Dict]) -> None:
    ARCHIVO_OFICIOS.write_bytes(
        cifrar(json.dumps(registros, ensure_ascii=False, indent=2))
    )


# --- Validaciones y referencia ----------------------------------------------
def _validar_fecha(texto: str, campo: str) -> str:
    try:
        datetime.strptime(texto, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"{campo} debe tener formato AAAA-MM-DD.")
    return texto


def _generar_referencia(fecha_recepcion: str, registros: List[Dict]) -> str:
    """Secuencial por día de recepción. Usa max+1 (tolerante a huecos)."""
    parte_fecha = fecha_recepcion.replace("-", "")            # AAAAMMDD
    prefijo_dia = f"{PREFIJO_REFERENCIA}-{parte_fecha}-"
    secuencial_max = -1
    for registro in registros:
        referencia = registro.get("referencia", "")
        if referencia.startswith(prefijo_dia):
            try:
                secuencial_max = max(secuencial_max, int(referencia.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefijo_dia}{secuencial_max + 1:04d}"           # primero -> 0000


# --- Reglas de negocio: relación responsable / estado -----------------------
def _resolver_estado(nombre_empleado: str, estado: str) -> str:
    """Aplica las reglas de negocio entre responsable y estado.

    - Sin responsable: el único estado válido es "Por asignar". Si se pidió
      "En proceso" o "Finalizado" se lanza un error (esos estados exigen
      responsable).
    - Con responsable: no puede quedar en "Por asignar"; al asignar un
      responsable el oficio pasa automáticamente a "En proceso". Si el estado
      pedido es "En proceso" o "Finalizado" se respeta.
    Devuelve el estado ya corregido.
    """
    tiene_responsable = bool((nombre_empleado or "").strip())
    if not tiene_responsable:
        if estado in ("En proceso", "Finalizado"):
            raise ValueError(
                f"El estado \"{estado}\" requiere un responsable asignado."
            )
        return "Por asignar"
    # Con responsable asignado
    if estado == "Por asignar":
        return "En proceso"
    return estado


# --- Operaciones -------------------------------------------------------------
def registrar_oficio(codigo_oficio: str, fecha_recepcion: str, fecha_oficio: str,
                     id_empleado: str, nombre_empleado: str, estado: str,
                     registrado_por: str) -> str:
    codigo_oficio = codigo_oficio.strip()
    if not codigo_oficio:
        raise ValueError("Debe ingresar el código de oficio o circular.")
    _validar_fecha(fecha_recepcion, "Fecha de recepción")
    _validar_fecha(fecha_oficio, "Fecha de oficio")
    # La fecha de oficio no puede ser posterior a la de recepción: no se puede
    # recibir un oficio antes de que exista.
    if datetime.strptime(fecha_oficio, "%Y-%m-%d") > datetime.strptime(fecha_recepcion, "%Y-%m-%d"):
        raise ValueError(
            "La fecha de oficio no puede ser posterior a la fecha de recepción."
        )
    if estado not in ESTADOS:
        raise ValueError("Estado no válido.")

    # El responsable es opcional. Las reglas ajustan el estado en consecuencia.
    nombre_empleado = (nombre_empleado or "").strip()
    id_empleado = (id_empleado or "").strip()
    estado = _resolver_estado(nombre_empleado, estado)

    registros = _leer_registros()
    referencia = _generar_referencia(fecha_recepcion, registros)
    ahora = datetime.now().isoformat(timespec="seconds")
    registros.append({
        "referencia": referencia,
        "codigo_oficio": codigo_oficio,
        "fecha_recepcion": fecha_recepcion,
        "fecha_oficio": fecha_oficio,
        "id_empleado": id_empleado,
        "empleado": nombre_empleado,
        "estado": estado,
        "registrado_por": registrado_por,
        "fecha_registro": ahora,
        "historial": [{"estado": estado, "por": registrado_por, "cuando": ahora}],
    })
    _guardar_registros(registros)
    registro_actividad.registrar(
        "REGISTRAR_OFICIO",
        f"referencia={referencia}; codigo={codigo_oficio}; "
        f"responsable={nombre_empleado or '(sin responsable)'}; estado={estado}",
        registrado_por)
    return referencia


def listar_oficios() -> List[Dict]:
    return _leer_registros()


def actualizar_oficio(referencia: str, nuevo_estado: str, id_empleado: str,
                     nombre_empleado: str, actualizado_por: str) -> str:
    """Actualiza estado y/o responsable de un oficio en una sola operación,
    respetando las reglas de negocio (ver `_resolver_estado`).

    Devuelve el estado final aplicado (puede diferir del solicitado si las
    reglas lo ajustaron, p. ej. al asignar responsable a un "Por asignar").
    """
    if nuevo_estado not in ESTADOS:
        raise ValueError("Estado no válido.")
    nombre_empleado = (nombre_empleado or "").strip()
    id_empleado = (id_empleado or "").strip()
    estado_final = _resolver_estado(nombre_empleado, nuevo_estado)

    registros = _leer_registros()
    for registro in registros:
        if registro["referencia"] == referencia:
            cambios = []
            if nombre_empleado != registro.get("empleado", ""):
                registro["id_empleado"] = id_empleado
                registro["empleado"] = nombre_empleado
                cambios.append(
                    f"Responsable: {nombre_empleado or '(sin responsable)'}"
                )
            if estado_final != registro.get("estado"):
                registro["estado"] = estado_final
                cambios.append(f"Estado: {estado_final}")
            if cambios:
                registro.setdefault("historial", []).append({
                    "evento": " · ".join(cambios),
                    "por": actualizado_por,
                    "cuando": datetime.now().isoformat(timespec="seconds"),
                })
                _guardar_registros(registros)
                registro_actividad.registrar(
                    "ACTUALIZAR_OFICIO",
                    f"referencia={referencia}; " + "; ".join(cambios),
                    actualizado_por)
            return estado_final
    raise ValueError("No se encontró la referencia indicada.")
