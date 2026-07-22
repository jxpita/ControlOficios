"""
Endurecimiento de permisos de los archivos que crea la aplicación.

Objetivo: que los archivos de datos y la bitácora queden como **solo lectura**
y accesibles **solo por el propietario**, para dificultar que alguien los
modifique o elimine "a conveniencia".

Cómo funciona:
- Tras cada escritura, el archivo se deja en modo 0o400 (solo lectura para el
  propietario; sin ningún acceso para el resto de usuarios del sistema).
- Como la propia aplicación necesita volver a escribir (la bitácora crece y los
  .dat se reescriben), antes de cada escritura se restaura temporalmente el
  permiso de escritura (0o600) y al terminar se vuelve a bloquear.

Límites (importante, sin sobrevender):
- En Windows, 0o400 marca el archivo como "solo lectura": no se puede modificar
  ni borrar con normalidad (Explorador / `del` lo rechazan sin forzar).
- En Linux/macOS, el borrado depende de los permisos del DIRECTORIO, no del
  archivo; por eso también se restringe la carpeta `datos/` a 0o700.
- El propietario que ejecuta la app puede, con esfuerzo, revertir los permisos
  (es su archivo). Esto **frena la manipulación casual y a otros usuarios del
  sistema**, pero no sustituye a un control real (base de datos con permisos
  mínimos / medio append-only). La integridad de los .dat ya está respaldada
  por el cifrado autenticado Fernet.
"""
import os

MODO_SOLO_LECTURA = 0o400   # r--------  (solo lectura, solo propietario)
MODO_ESCRITURA = 0o600      # rw-------  (lectura/escritura, solo propietario)
MODO_DIRECTORIO = 0o700     # rwx------  (solo el propietario entra/lista/borra)


def _chmod(ruta, modo) -> None:
    try:
        os.chmod(ruta, modo)
    except (OSError, NotImplementedError):
        # Nunca debe interrumpir la operación principal si el SO no lo soporta.
        pass


def hacer_escribible(ruta) -> None:
    """Devuelve el permiso de escritura al propietario si el archivo existe."""
    if os.path.exists(ruta):
        _chmod(ruta, MODO_ESCRITURA)


def proteger(ruta) -> None:
    """Deja el archivo en solo lectura para el propietario (0o400)."""
    _chmod(ruta, MODO_SOLO_LECTURA)


def proteger_directorio(ruta) -> None:
    """Restringe una carpeta al propietario (0o700)."""
    _chmod(ruta, MODO_DIRECTORIO)


def escribir_bytes_protegido(ruta, datos: bytes) -> None:
    """Escribe (reemplaza) el contenido y deja el archivo en solo lectura."""
    hacer_escribible(ruta)
    with open(ruta, "wb") as archivo:
        archivo.write(datos)
    proteger(ruta)


def anexar_texto_protegido(ruta, texto: str) -> None:
    """Añade texto al final del archivo y lo deja de nuevo en solo lectura."""
    hacer_escribible(ruta)
    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(texto)
    proteger(ruta)
