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
import tempfile
from datetime import datetime
from pathlib import Path

from configuracion import ARCHIVO_LOG
import permisos

# Si no se puede escribir en la bitácora principal (por ejemplo, la carpeta
# compartida no responde o otro proceso la tiene tomada), la línea se guarda
# aquí en lugar de perderse en silencio.
ARCHIVO_PENDIENTES = Path(tempfile.gettempdir()) / "controloficios-auditoria-pendiente.log"


def _respaldar(linea: str, motivo: str) -> None:
    """Último recurso: dejar la línea en un archivo local para no perderla."""
    try:
        with open(ARCHIVO_PENDIENTES, "a", encoding="utf-8") as archivo:
            archivo.write(f"{linea.rstrip()}  <-- no se pudo escribir en la "
                          f"bitácora principal ({motivo})\n")
    except OSError:
        # Si ni siquiera el respaldo local funciona, no hay nada más que hacer:
        # la auditoría nunca debe tumbar la aplicación.
        pass


def registrar(accion: str, detalle: str = "", actor: str = "sistema") -> None:
    """Añade una línea a la bitácora de auditoría.

    Si la escritura falla, la línea **no se descarta**: se guarda en un archivo
    local de pendientes (ver `ARCHIVO_PENDIENTES`), porque perder registros de
    auditoría en silencio es peor que tenerlos dispersos.
    """
    marca = datetime.now().isoformat(timespec="seconds")
    actor = (actor or "desconocido").strip() or "desconocido"
    # Se eliminan saltos de línea del detalle para no romper el formato por línea.
    detalle = " ".join(str(detalle).splitlines())
    linea = f"{marca} | {actor} | {accion} | {detalle}\n"
    try:
        permisos.anexar_texto(ARCHIVO_LOG, linea)
    except OSError as error:
        _respaldar(linea, str(error))
