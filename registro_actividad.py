"""
Registro de actividad (auditoría) en un archivo de texto plano.

Guarda TODA acción que modifique datos persistentes: alta de oficios,
cambios de estado o de responsable, alta/edición/eliminación de usuarios e
inicios de sesión. NO registra la navegación ni la interacción con la
interfaz (clics, cambios de pestaña, etc.), solo lo que queda guardado en
disco.

Formato de cada línea:
    AAAA-MM-DDTHH:MM:SS | actor | ACCION | detalle

El archivo se define en `configuracion.ARCHIVO_LOG` (por defecto
`datos/actividad.log`). El registro nunca debe interrumpir la operación
principal: si por algún motivo no se puede escribir, se ignora el error.
"""
from datetime import datetime

from configuracion import ARCHIVO_LOG


def registrar(accion: str, detalle: str = "", actor: str = "sistema") -> None:
    """Añade una línea a la bitácora de auditoría."""
    marca = datetime.now().isoformat(timespec="seconds")
    actor = (actor or "desconocido").strip() or "desconocido"
    # Se eliminan saltos de línea del detalle para no romper el formato por línea.
    detalle = " ".join(str(detalle).splitlines())
    linea = f"{marca} | {actor} | {accion} | {detalle}\n"
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(linea)
    except OSError:
        # La auditoría no debe tumbar la aplicación si el disco falla.
        pass
