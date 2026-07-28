"""
Bloqueo entre procesos para la carpeta de datos compartida.

Problema que resuelve: los archivos se guardan leyendo todo el contenido,
modificándolo en memoria y reescribiéndolo completo. Si dos personas hacen esa
secuencia a la vez (la app puede estar en una carpeta de red usada por varias),
la segunda escritura pisa a la primera y **se pierde un registro sin aviso**.
El mismo choque puede generar dos Referencias UDC iguales.

Solución: un archivo de bloqueo por cada archivo de datos. Se crea con
`O_CREAT | O_EXCL`, operación **atómica** incluso sobre carpetas de red (SMB):
o lo crea este proceso, o ya existía y toca esperar.

Bloqueos huérfanos: si un proceso muere sin liberar (cierre forzado, corte de
luz), el archivo quedaría para siempre. Por eso dentro se guarda la marca de
tiempo y, si supera `ANTIGUEDAD_MAXIMA`, se considera abandonado y se rompe.
Como cada operación protegida dura milisegundos, un bloqueo de más de 30
segundos solo puede ser basura.

Uso:
    with bloqueo.bloquear("oficios"):
        registros = _leer_registros()
        ...
        _guardar_registros(registros)
"""
import functools
import os
import socket
import time
from contextlib import contextmanager
from pathlib import Path

from configuracion import DIR_DATOS

# Tiempo máximo que se espera a que otro proceso libere el bloqueo.
ESPERA_MAXIMA = 10.0
# Antigüedad a partir de la cual un bloqueo se considera abandonado.
ANTIGUEDAD_MAXIMA = 30.0
# Pausa entre intentos.
INTERVALO = 0.05


def _ruta_bloqueo(nombre: str) -> Path:
    return DIR_DATOS / f"{nombre}.lock"


def _esta_abandonado(ruta: Path) -> bool:
    """True si el bloqueo es tan antiguo que solo puede ser basura."""
    try:
        antiguedad = time.time() - ruta.stat().st_mtime
    except OSError:
        return False          # desapareció justo ahora: no hay que romper nada
    return antiguedad > ANTIGUEDAD_MAXIMA


@contextmanager
def bloquear(nombre: str, espera_maxima: float = ESPERA_MAXIMA):
    """Toma el bloqueo `nombre` mientras dure el bloque `with`.

    Lanza ValueError si tras `espera_maxima` segundos otro proceso sigue
    ocupándolo, para que la interfaz pueda mostrar un aviso claro en vez de
    quedarse congelada.
    """
    ruta = _ruta_bloqueo(nombre)
    limite = time.monotonic() + espera_maxima
    descriptor = None

    while True:
        try:
            descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break                                   # bloqueo obtenido
        except FileExistsError:
            if _esta_abandonado(ruta):
                try:
                    ruta.unlink()                   # romper el bloqueo huérfano
                except OSError:
                    pass
                continue
            if time.monotonic() >= limite:
                raise ValueError(
                    "Otro usuario está guardando cambios en este momento. "
                    "Espere unos segundos e inténtelo de nuevo."
                )
            time.sleep(INTERVALO)
        except OSError as error:
            # La carpeta no existe o no hay permisos: no se puede coordinar.
            raise ValueError(f"No se pudo obtener el bloqueo de datos: {error}")

    try:
        # Dejar rastro de quién lo tomó (ayuda a diagnosticar si algo se traba).
        try:
            os.write(descriptor, f"{socket.gethostname()}|{os.getpid()}|"
                                 f"{time.strftime('%Y-%m-%dT%H:%M:%S')}".encode())
        except OSError:
            pass
        os.close(descriptor)
        descriptor = None
        yield
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            ruta.unlink()
        except OSError:
            pass


def con_bloqueo(nombre: str):
    """Decorador: ejecuta la función completa bajo el bloqueo `nombre`.

    Se aplica a las operaciones que leen, modifican y reescriben un archivo de
    datos, para que esa secuencia sea indivisible frente a otros usuarios.

    Cuidado: las funciones así decoradas **no deben llamarse entre sí** con el
    mismo nombre de bloqueo (el bloqueo no es reentrante y se produciría una
    espera hasta agotar el tiempo).
    """
    def decorador(funcion):
        @functools.wraps(funcion)
        def envoltura(*args, **kwargs):
            with bloquear(nombre):
                return funcion(*args, **kwargs)
        return envoltura
    return decorador
