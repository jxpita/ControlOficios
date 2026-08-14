"""
Cálculo de métricas para el tablero (dashboard).
No depende de la interfaz: solo procesa lo que devuelve almacen_oficios.

Todas las funciones aceptan `registros` (una lista ya filtrada de oficios). Si
no se pasa, usan todos los oficios. Así el tablero puede mostrar solo lo que el
usuario en sesión tiene permitido ver.
"""
from datetime import datetime, date, timedelta
from collections import Counter
from typing import Dict, List, Tuple, Optional

from almacen_oficios import listar_oficios
from configuracion import ESTADOS


def _convertir_fecha(fecha_iso: str):
    try:
        return datetime.strptime(fecha_iso[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _registros(registros: Optional[List[Dict]] = None) -> List[Dict]:
    return listar_oficios() if registros is None else registros


def resumen(registros: Optional[List[Dict]] = None) -> Dict:
    registros = _registros(registros)
    por_estado = Counter(reg.get("estado", "Desconocido") for reg in registros)
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # lunes
    inicio_mes = hoy.replace(day=1)

    conteo_hoy = conteo_semana = conteo_mes = 0
    for reg in registros:
        fecha = _convertir_fecha(reg.get("fecha_recepcion", ""))
        if not fecha:
            continue
        if fecha == hoy:
            conteo_hoy += 1
        if fecha >= inicio_semana:
            conteo_semana += 1
        if fecha >= inicio_mes:
            conteo_mes += 1

    # Respuesta: cuántos ya tienen fecha de respuesta y PDF adjunto.
    con_respuesta = sum(1 for reg in registros if reg.get("fecha_respuesta"))
    con_pdf = sum(1 for reg in registros if reg.get("archivo_respuesta"))
    sin_responsable = sum(1 for reg in registros if not reg.get("empleado"))

    total = len(registros)
    finalizados = por_estado.get("Finalizado", 0)
    return {
        "total": total,
        "por_estado": {estado: por_estado.get(estado, 0) for estado in ESTADOS},
        "recibidos_hoy": conteo_hoy,
        "recibidos_semana": conteo_semana,
        "recibidos_mes": conteo_mes,
        "pendientes": por_estado.get("Por asignar", 0) + por_estado.get("En proceso", 0),
        "finalizados": finalizados,
        "con_respuesta": con_respuesta,
        "sin_respuesta": total - con_respuesta,
        "con_pdf": con_pdf,
        "sin_responsable": sin_responsable,
        "porcentaje_finalizados": round(finalizados * 100 / total) if total else 0,
        "dias_promedio_respuesta": dias_promedio_respuesta(registros),
    }


def dias_promedio_respuesta(registros: Optional[List[Dict]] = None) -> Optional[float]:
    """Promedio de días entre la recepción y la respuesta, sobre los oficios
    que ya tienen fecha de respuesta. Devuelve None si no hay ninguno."""
    dias = []
    for reg in _registros(registros):
        recepcion = _convertir_fecha(reg.get("fecha_recepcion", ""))
        respuesta = _convertir_fecha(reg.get("fecha_respuesta", ""))
        if recepcion and respuesta and respuesta >= recepcion:
            dias.append((respuesta - recepcion).days)
    return round(sum(dias) / len(dias), 1) if dias else None


def serie_por_dia(dias: int = 14, registros: Optional[List[Dict]] = None) -> List[Tuple[str, int]]:
    """Oficios recibidos por día en los últimos N días (para el gráfico)."""
    conteo = Counter()
    for reg in _registros(registros):
        fecha = _convertir_fecha(reg.get("fecha_recepcion", ""))
        if fecha:
            conteo[fecha] += 1
    hoy = date.today()
    return [
        ((hoy - timedelta(days=i)).isoformat(), conteo.get(hoy - timedelta(days=i), 0))
        for i in range(dias - 1, -1, -1)
    ]


def serie_por_mes(meses: int = 6, registros: Optional[List[Dict]] = None) -> List[Tuple[str, int]]:
    """Oficios recibidos por mes en los últimos N meses (AAAA-MM, cantidad)."""
    conteo = Counter()
    for reg in _registros(registros):
        fecha = _convertir_fecha(reg.get("fecha_recepcion", ""))
        if fecha:
            conteo[(fecha.year, fecha.month)] += 1

    hoy = date.today()
    serie = []
    anio, mes = hoy.year, hoy.month
    for _ in range(meses):
        serie.append((f"{anio:04d}-{mes:02d}", conteo.get((anio, mes), 0)))
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    return list(reversed(serie))


def personas_investigadas(registro: Dict) -> int:
    """Cuántas personas investiga un oficio.

    Manda el detalle de implicados; si el oficio no lo tiene —histórico cargado
    de la matriz sin los nombres— se usa la cantidad que traía.
    """
    implicados = registro.get("implicados") or []
    if implicados:
        return len(implicados)
    try:
        return int(registro.get("cantidad_investigados") or 0)
    except (TypeError, ValueError):
        return 0


def investigados_por_mes(meses: int = 6,
                         registros: Optional[List[Dict]] = None
                         ) -> List[Tuple[str, int, int]]:
    """Personas investigadas por mes: (AAAA-MM, personas, oficios).

    Se cuenta por el mes de RECEPCIÓN del oficio, igual que el resto de series,
    y se devuelve además cuántos oficios aportaron esas personas: un mes con
    pocos oficios puede concentrar mucha gente, y esa es justamente la
    diferencia que interesa ver.
    """
    personas, oficios = Counter(), Counter()
    for reg in _registros(registros):
        fecha = _convertir_fecha(reg.get("fecha_recepcion", ""))
        if not fecha:
            continue
        personas[(fecha.year, fecha.month)] += personas_investigadas(reg)
        oficios[(fecha.year, fecha.month)] += 1

    hoy = date.today()
    serie = []
    anio, mes = hoy.year, hoy.month
    for _ in range(meses):
        clave = (anio, mes)
        serie.append((f"{anio:04d}-{mes:02d}", personas.get(clave, 0),
                      oficios.get(clave, 0)))
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    return list(reversed(serie))


def por_responsable(registros: Optional[List[Dict]] = None,
                    tope: int = 8) -> List[Tuple[str, int]]:
    """Cantidad de oficios por responsable, de mayor a menor.
    Los oficios sin responsable se agrupan como "(Sin responsable)"."""
    conteo = Counter()
    for reg in _registros(registros):
        conteo[reg.get("empleado") or "(Sin responsable)"] += 1
    return conteo.most_common(tope)


def distribucion_estados(registros: Optional[List[Dict]] = None) -> List[Tuple[str, int]]:
    """Cantidad por estado, en el orden definido en configuracion.ESTADOS."""
    conteo = Counter(reg.get("estado", "Desconocido") for reg in _registros(registros))
    return [(estado, conteo.get(estado, 0)) for estado in ESTADOS]
