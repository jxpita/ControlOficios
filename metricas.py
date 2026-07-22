"""
Cálculo de métricas para el tablero (dashboard).
No depende de la interfaz: solo procesa lo que devuelve almacen_oficios.
"""
from datetime import datetime, date, timedelta
from collections import Counter
from typing import Dict, List, Tuple

from almacen_oficios import listar_oficios
from configuracion import ESTADOS


def _convertir_fecha(fecha_iso: str):
    try:
        return datetime.strptime(fecha_iso[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def resumen() -> Dict:
    registros = listar_oficios()
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

    return {
        "total": len(registros),
        "por_estado": {estado: por_estado.get(estado, 0) for estado in ESTADOS},
        "recibidos_hoy": conteo_hoy,
        "recibidos_semana": conteo_semana,
        "recibidos_mes": conteo_mes,
        "pendientes": por_estado.get("Por asignar", 0) + por_estado.get("En proceso", 0),
        "finalizados": por_estado.get("Finalizado", 0),
    }


def serie_por_dia(dias: int = 14) -> List[Tuple[str, int]]:
    """Oficios recibidos por día en los últimos N días (para el gráfico)."""
    conteo = Counter()
    for reg in listar_oficios():
        fecha = _convertir_fecha(reg.get("fecha_recepcion", ""))
        if fecha:
            conteo[fecha] += 1
    hoy = date.today()
    return [
        ((hoy - timedelta(days=i)).isoformat(), conteo.get(hoy - timedelta(days=i), 0))
        for i in range(dias - 1, -1, -1)
    ]
