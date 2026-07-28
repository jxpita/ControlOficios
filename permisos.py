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
import shutil
from pathlib import Path

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
    """Escribe el contenido de forma **atómica** y deja el archivo en solo
    lectura, conservando una copia de la versión anterior en `<nombre>.bak`.

    Por qué no se escribe directamente sobre el archivo: abrirlo en modo "wb"
    lo vacía primero, así que quien lo leyera en ese instante (otro usuario en
    la carpeta compartida) vería un archivo a medias y creería que está
    corrupto. Escribiendo en un temporal y renombrando, el lector ve **o la
    versión anterior o la nueva, nunca una mezcla**. El renombrado también
    protege ante un corte de luz o un cierre forzado a mitad de escritura.
    """
    ruta = Path(ruta)

    # 1) Respaldo de la última versión buena, por si hiciera falta recuperarla.
    if ruta.exists():
        respaldo = ruta.with_name(ruta.name + ".bak")
        try:
            hacer_escribible(respaldo)
            shutil.copyfile(ruta, respaldo)
            proteger(respaldo)
        except OSError:
            pass          # el respaldo es una ayuda, no debe impedir guardar

    # 2) Escribir en un temporal de la MISMA carpeta (el renombrado solo es
    #    atómico dentro del mismo sistema de archivos).
    temporal = ruta.with_name(ruta.name + ".tmp")
    hacer_escribible(temporal)
    with open(temporal, "wb") as archivo:
        archivo.write(datos)

    # 3) Reemplazo atómico. En Windows os.replace falla si el destino está en
    #    solo lectura, por eso primero se le devuelve el permiso de escritura.
    hacer_escribible(ruta)
    os.replace(temporal, ruta)
    proteger(ruta)


def anexar_texto(ruta, texto: str) -> None:
    """Añade una línea al final del archivo, dejándolo escribible.

    A diferencia de los archivos de datos, la bitácora **no** se deja en solo
    lectura tras cada línea: ese vaivén de permisos hacía que, en la carpeta
    compartida, un proceso pusiera el archivo en solo lectura justo cuando otro
    intentaba escribir, y esa línea de auditoría se perdía. La marca de solo
    lectura además nunca protegió realmente el archivo (el propietario puede
    quitarla), así que no compensa perder registros de auditoría por ella.
    """
    nuevo = not os.path.exists(ruta)
    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(texto)
    if nuevo:
        # Al crearlo, restringirlo al propietario (lectura y escritura).
        _chmod(ruta, MODO_ESCRITURA)
