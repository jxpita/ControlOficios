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


# --- Carga de trabajo según el número de investigados ------------------------
# Tramos en los que se agrupan los oficios: (etiqueta, mínimo, máximo).
TRAMOS_INVESTIGADOS = [
    ("1", 1, 1),
    ("2-3", 2, 3),
    ("4-5", 4, 5),
    ("6-10", 6, 10),
    ("+10", 11, None),
]


def _entero(valor) -> Optional[int]:
    try:
        numero = int(str(valor).strip())
    except (ValueError, TypeError, AttributeError):
        return None
    return numero if numero > 0 else None


def _mediana(valores: List[float]) -> Optional[float]:
    if not valores:
        return None
    ordenados = sorted(valores)
    mitad = len(ordenados) // 2
    if len(ordenados) % 2:
        return float(ordenados[mitad])
    return (ordenados[mitad - 1] + ordenados[mitad]) / 2


def esfuerzo_por_oficio(registros: Optional[List[Dict]] = None) -> List[Tuple[int, int]]:
    """Pares (investigados, días de trabajo) de los oficios ya respondidos.

    Los días se cuentan de la **asignación** a la respuesta, que es el tiempo de
    trabajo real del analista; el tiempo desde la recepción incluye la espera
    previa al reparto, que no depende de quien atiende el oficio.

    Solo entran los oficios que tienen las dos fechas y una cantidad de
    investigados registrada: sin esos tres datos el punto no dice nada.
    """
    puntos = []
    for reg in _registros(registros):
        investigados = _entero(reg.get("cantidad_investigados"))
        asignacion = _convertir_fecha(reg.get("fecha_asignacion", ""))
        respuesta = _convertir_fecha(reg.get("fecha_respuesta", ""))
        if investigados and asignacion and respuesta and respuesta >= asignacion:
            puntos.append((investigados, (respuesta - asignacion).days))
    return puntos


def tendencia_esfuerzo(puntos: List[Tuple[int, int]]) -> Optional[Tuple[float, float]]:
    """Recta de tendencia (pendiente, punto de corte) por mínimos cuadrados.

    La pendiente se lee como "días que suma cada investigado adicional".
    Devuelve None si no hay puntos suficientes o si todos tienen el mismo
    número de investigados (no habría nada que correlacionar).
    """
    if len(puntos) < 3:
        return None
    n = len(puntos)
    suma_x = sum(x for x, _ in puntos)
    suma_y = sum(y for _, y in puntos)
    suma_xy = sum(x * y for x, y in puntos)
    suma_xx = sum(x * x for x, _ in puntos)
    denominador = n * suma_xx - suma_x * suma_x
    if not denominador:
        return None
    pendiente = (n * suma_xy - suma_x * suma_y) / denominador
    corte = (suma_y - pendiente * suma_x) / n
    return pendiente, corte


def distribucion_investigados(registros: Optional[List[Dict]] = None) -> List[Dict]:
    """Oficios agrupados por tramo de investigados.

    Para cada tramo devuelve cuántos oficios hay y la MEDIANA de días de los que
    ya están respondidos. Se usa la mediana y no el promedio porque con pocos
    oficios uno que tardó tres meses desplaza el promedio y da una idea falsa
    del trabajo habitual.
    """
    registros = _registros(registros)
    resultado = []
    for etiqueta, minimo, maximo in TRAMOS_INVESTIGADOS:
        oficios_tramo = []
        for reg in registros:
            investigados = _entero(reg.get("cantidad_investigados"))
            if investigados is None or investigados < minimo:
                continue
            if maximo is not None and investigados > maximo:
                continue
            oficios_tramo.append(reg)
        dias = []
        for reg in oficios_tramo:
            asignacion = _convertir_fecha(reg.get("fecha_asignacion", ""))
            respuesta = _convertir_fecha(reg.get("fecha_respuesta", ""))
            if asignacion and respuesta and respuesta >= asignacion:
                dias.append((respuesta - asignacion).days)
        resultado.append({
            "tramo": etiqueta,
            "oficios": len(oficios_tramo),
            "mediana_dias": _mediana(dias),
            "respondidos": len(dias),
        })
    return resultado


def resumen_investigados(registros: Optional[List[Dict]] = None) -> Dict:
    """Totales de personas investigadas, para las tarjetas del tablero."""
    registros = _registros(registros)
    cantidades = [c for c in (_entero(reg.get("cantidad_investigados"))
                              for reg in registros) if c]
    total = sum(cantidades)
    return {
        "total_investigados": total,
        "oficios_con_dato": len(cantidades),
        "promedio_por_oficio": round(total / len(cantidades), 1) if cantidades else None,
        "maximo": max(cantidades) if cantidades else 0,
    }
