"""
Copia de seguridad automática de los datos, integrada en la aplicación.

Por qué dentro de la app y no una tarea programada: la aplicación puede vivir
en un equipo compartido donde no se pueden ejecutar scripts ni crear tareas del
Programador de Windows. Al ir dentro del ejecutable no hace falta ningún
permiso especial.

Cómo funciona: **una copia por día**. La primera persona que abre la aplicación
crea el respaldo del día; el resto ven que ya existe y no hacen nada. Los
respaldos van a `datos/respaldos/datos_AAAA-MM-DD.zip` y se conservan los
últimos N días (30 por omisión).

Qué se respalda: los archivos pequeños y críticos (oficios, credenciales,
parámetros, clave maestra y bitácora). Los **PDF de respuesta quedan fuera**:
pesan mucho, no cambian una vez cargados y harían lento cada arranque.

El respaldo nunca debe estorbar: si falla, se anota en la bitácora y la
aplicación sigue funcionando con normalidad.
"""
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from configuracion import (
    DIR_DATOS, DIR_RESPALDOS, DIR_RESPUESTAS, DIAS_RESPALDO_POR_DEFECTO
)
import registro_actividad
import bloqueo

# Archivos que NO se incluyen: temporales, bloqueos y las copias .bak (que solo
# son la versión inmediatamente anterior y duplicarían el tamaño sin aportar
# nada, porque ya se conserva una copia por día).
_SUFIJOS_EXCLUIDOS = (".lock", ".tmp", ".bak")


def ruta_del_dia(dia: Optional[date] = None) -> Path:
    dia = dia or date.today()
    return DIR_RESPALDOS / f"datos_{dia.isoformat()}.zip"


def existe_del_dia(dia: Optional[date] = None) -> bool:
    return ruta_del_dia(dia).exists()


def _archivos_a_respaldar() -> List[Path]:
    """Archivos de `datos/` que entran en el respaldo (sin PDF ni temporales)."""
    seleccionados = []
    for ruta in sorted(DIR_DATOS.iterdir()):
        if ruta.is_dir():
            continue                       # respuestas/ y respaldos/ quedan fuera
        if ruta.suffix.lower() in _SUFIJOS_EXCLUIDOS:
            continue
        seleccionados.append(ruta)
    return seleccionados


def listar_respaldos() -> List[Path]:
    """Respaldos existentes, del más reciente al más antiguo."""
    if not DIR_RESPALDOS.exists():
        return []
    return sorted(DIR_RESPALDOS.glob("datos_*.zip"), reverse=True)


def purgar_antiguos(dias: int = DIAS_RESPALDO_POR_DEFECTO) -> int:
    """Elimina los respaldos con más de `dias` de antigüedad.
    Devuelve cuántos se eliminaron."""
    if dias <= 0:
        return 0
    limite = date.today() - timedelta(days=dias)
    eliminados = 0
    for archivo in listar_respaldos():
        try:
            fecha = datetime.strptime(archivo.stem.replace("datos_", ""),
                                      "%Y-%m-%d").date()
        except ValueError:
            continue                        # nombre inesperado: no se toca
        if fecha < limite:
            try:
                archivo.unlink()
                eliminados += 1
            except OSError:
                pass
    return eliminados


def crear_respaldo(actor: str = "sistema", forzar: bool = False,
                   dias_conservar: int = DIAS_RESPALDO_POR_DEFECTO) -> Optional[Path]:
    """Crea el respaldo del día si aún no existe.

    Devuelve la ruta del archivo creado, o None si ya existía (y no se forzó).
    Lanza ValueError si no se pudo crear, para que quien llama decida si
    informar al usuario o solo registrarlo.
    """
    destino = ruta_del_dia()
    if destino.exists() and not forzar:
        return None

    DIR_RESPALDOS.mkdir(exist_ok=True)
    # Se escribe en un temporal y se renombra, para que nadie vea un ZIP a
    # medias si el proceso se interrumpe.
    temporal = destino.with_name(destino.name + ".tmp")
    try:
        # El bloqueo garantiza copiar una versión coherente, sin que otro
        # usuario esté reescribiendo los archivos en ese instante.
        with bloqueo.bloquear("oficios"):
            archivos = _archivos_a_respaldar()
            with zipfile.ZipFile(temporal, "w", zipfile.ZIP_DEFLATED) as comprimido:
                for archivo in archivos:
                    comprimido.write(archivo, arcname=archivo.name)
        temporal.replace(destino)
    except Exception as error:
        try:
            temporal.unlink(missing_ok=True)
        except OSError:
            pass
        raise ValueError(f"No se pudo crear el respaldo: {error}")

    eliminados = purgar_antiguos(dias_conservar)
    tamano_kb = destino.stat().st_size / 1024
    registro_actividad.registrar(
        "RESPALDO_CREADO",
        f"archivo={destino.name}; archivos={len(archivos)}; "
        f"tamano={tamano_kb:.0f} KB; purgados={eliminados}",
        actor)
    return destino


def crear_respaldo_silencioso(actor: str = "sistema",
                              dias_conservar: int = DIAS_RESPALDO_POR_DEFECTO) -> None:
    """Versión para ejecutar al abrir la aplicación: nunca lanza errores.

    Un fallo del respaldo (red caída, disco lleno, sin permisos) jamás debe
    impedir que la aplicación se use, así que solo se deja constancia.
    """
    try:
        crear_respaldo(actor, dias_conservar=dias_conservar)
    except Exception as error:
        registro_actividad.registrar("RESPALDO_FALLIDO", str(error), actor)
