"""
Configuración central de la aplicación.
Define rutas, nombres de archivo y constantes usadas por el resto de módulos.
"""
import os
import sys
from pathlib import Path

# --- Directorio base (donde está el ejecutable o el código) ------------------
if getattr(sys, "frozen", False):
    DIR_BASE = Path(sys.executable).resolve().parent
else:
    DIR_BASE = Path(__file__).resolve().parent

# Nombre del archivo que puede indicar dónde están los datos.
ARCHIVO_RUTA_DATOS = "datos.ruta"
# Variable de entorno equivalente (tiene prioridad sobre el archivo).
VARIABLE_RUTA_DATOS = "CONTROLOFICIOS_DATOS"


def _leer_ruta_configurada(dir_base: Path):
    """Ruta de la carpeta de datos indicada por el usuario, o None.

    Se busca en dos sitios, en este orden:
      1. La variable de entorno CONTROLOFICIOS_DATOS.
      2. Un archivo de texto `datos.ruta` junto al ejecutable, con la ruta en
         una línea (se ignoran líneas vacías y las que empiezan por '#').

    Sirve para separar los datos del ejecutable: así varias versiones de la
    aplicación (ControlOficios_v1.1, v1.2, ...) comparten una única carpeta de
    datos en el recurso compartido. Las rutas relativas se resuelven respecto
    de la carpeta del ejecutable, de modo que `..\\..\\datos` funciona.
    """
    valor = (os.environ.get(VARIABLE_RUTA_DATOS) or "").strip()
    if not valor:
        archivo = dir_base / ARCHIVO_RUTA_DATOS
        try:
            if archivo.exists():
                for linea in archivo.read_text(encoding="utf-8").splitlines():
                    linea = linea.strip()
                    if linea and not linea.startswith("#"):
                        valor = linea
                        break
        except OSError:
            return None
    if not valor:
        return None

    valor = os.path.expandvars(valor)
    # Las rutas se escriben con '\' (estilo Windows). Fuera de Windows ese
    # carácter no separa carpetas, así que se traduce para que el mismo
    # archivo funcione si alguna vez se ejecuta desde el código en otro SO.
    if os.sep != "\\":
        valor = valor.replace("\\", "/")

    ruta = Path(valor).expanduser()
    if not ruta.is_absolute():
        ruta = dir_base / ruta
    # Normalizar (quitar los '..') para que los mensajes muestren rutas
    # legibles y las comparaciones de rutas sean fiables.
    try:
        return ruta.resolve()
    except OSError:
        return ruta


# --- Carpeta de datos --------------------------------------------------------
# Si no se configura nada, se usa `datos/` junto al ejecutable (comportamiento
# de siempre, ideal para un único equipo).
_configurada = _leer_ruta_configurada(DIR_BASE)
DIR_DATOS = _configurada if _configurada is not None else (DIR_BASE / "datos")

# Si la carpeta no se puede crear o alcanzar (por ejemplo, la unidad de red no
# responde), NO se lanza una excepción aquí: se guarda el motivo y la interfaz
# lo muestra con un mensaje claro al arrancar.
ERROR_DATOS = None
try:
    DIR_DATOS.mkdir(parents=True, exist_ok=True)
except OSError as _error:
    ERROR_DATOS = (
        f"No se pudo acceder a la carpeta de datos:\n{DIR_DATOS}\n\n{_error}\n\n"
        "Verifique la conexión con el recurso compartido o corrija la ruta "
        f"indicada en '{ARCHIVO_RUTA_DATOS}'."
    )
else:
    try:  # restringir la carpeta al propietario (evita borrado por otros usuarios)
        os.chmod(DIR_DATOS, 0o700)
    except (OSError, NotImplementedError):
        pass


def _crear_subcarpeta(nombre: str) -> Path:
    ruta = DIR_DATOS / nombre
    if ERROR_DATOS is None:
        try:
            ruta.mkdir(exist_ok=True)
        except OSError:
            pass
    return ruta


def _buscar_recurso(nombre: str) -> Path:
    """Ubica un recurso de la aplicación (ícono o logo).

    Se busca primero junto al ejecutable, para que cada carpeta de versión
    pueda llevar los suyos, y si no está se usa el de la carpeta de datos
    (que es donde estaban antes)."""
    junto_al_ejecutable = DIR_BASE / nombre
    if junto_al_ejecutable.exists():
        return junto_al_ejecutable
    return DIR_DATOS / nombre


# --- Archivos ----------------------------------------------------------------
ARCHIVO_CLAVE = DIR_DATOS / "clave_maestra.key"
ARCHIVO_CREDENCIALES = DIR_DATOS / "credenciales.dat"
ARCHIVO_OFICIOS = DIR_DATOS / "oficios.dat"
ARCHIVO_PARAMETROS = DIR_DATOS / "parametros.dat"   # parámetros del sistema, cifrado
ARCHIVO_LOG = DIR_DATOS / "actividad.log"   # bitácora de auditoría (texto plano)

# --- Respuestas en PDF adjuntas a los oficios --------------------------------
DIR_RESPUESTAS = _crear_subcarpeta("respuestas")

# --- Documento del oficio (obligatorio al registrarlo) -----------------------
DIR_DOCUMENTOS = _crear_subcarpeta("documentos")
# Formatos admitidos para el documento del oficio.
EXTENSIONES_DOCUMENTO = (".pdf", ".docx")

# --- Copias de seguridad automáticas -----------------------------------------
# Van SIEMPRE dentro de la carpeta de datos, así que si esta vive en el recurso
# compartido, las copias también (nunca quedan en el equipo de cada persona).
DIR_RESPALDOS = _crear_subcarpeta("respaldos")
DIAS_RESPALDO_POR_DEFECTO = 30      # antigüedad máxima que se conserva

# --- Imágenes (logo e ícono) ------------------------------------------------
ARCHIVO_LOGO = _buscar_recurso("bdp_icon.ico")        # logo junto al título
ARCHIVO_ICONO = _buscar_recurso("bdp_icon_alt.ico")   # ícono de la ventana

# --- Constantes de negocio ---------------------------------------------------
ESTADOS = ["Por asignar", "En proceso", "Finalizado"]

# Referencia UDC:  REQ-UDC-<sigla de la institución>-<año>-<secuencial de 4
# dígitos>. Por ejemplo REQ-UDC-SB-2026-0001 y REQ-UDC-FGE-2026-0001. El
# secuencial es INDEPENDIENTE para cada institución y se reinicia cada año.
PREFIJO_REFERENCIA = "REQ-UDC"

# Instituciones del Estado que remiten oficios: nombre -> sigla de la
# referencia. El orden es el que se ve en los desplegables.
INSTITUCIONES = {
    "Superintendencia de Bancos": "SB",
    "Fiscalía General del Estado": "FGE",
}

# Prioridad con la que se atiende un oficio. El orden es el de los
# desplegables, de menor a mayor urgencia.
PRIORIDADES = ["Baja", "Media", "Alta"]
PRIORIDAD_POR_DEFECTO = "Media"

# Tipos de acción que se piden en un oficio. Es el catálogo de partida: se
# puede mantener desde la pestaña Configuración (ver `tipos_accion.py`).
TIPOS_ACCION_INICIALES = [
    "Bloqueo y retención",
    "Certificación",
    "Información",
    "Inmovilización",
    "Levantamiento",
    "Rectificación",
    "Retención",
]

ARCHIVO_TIPOS_ACCION = DIR_DATOS / "tipos_accion.dat"   # catálogo, cifrado

# --- Implicados (personas investigadas en un oficio) -------------------------
# Un oficio puede pedir información de varias personas. De cada una se anota
# quién es, cómo se identifica y su relación con el banco.
TIPOS_IDENTIFICACION = ["Cédula", "Pasaporte", "RUC"]
TIPOS_IMPLICADO = ["Cliente", "No cliente", "Ex cliente", "Sin identificación"]
# LCI = Lista de Control Interno.
VALORES_LCI = ["Sí", "No"]

# --- Roles de usuario --------------------------------------------------------
# El superusuario es el primer usuario que se crea y NO puede eliminarse.
ROL_SUPERUSUARIO = "superusuario"
ROL_ADMINISTRADOR = "administrador"
ROL_USUARIO = "usuario"
# Roles que puede asignar un ADMINISTRADOR: solo gestiona usuarios regulares,
# así que tampoco puede crear ni promover administradores.
ROLES_ASIGNABLES_ADMIN = [ROL_USUARIO]
# Roles que puede asignar un SUPERUSUARIO: cualquiera, incluidos otros
# superusuarios y los administradores.
ROLES_ASIGNABLES_SUPER = [ROL_SUPERUSUARIO, ROL_ADMINISTRADOR, ROL_USUARIO]
# Roles con permiso para crear/editar/eliminar usuarios.
ROLES_GESTORES = (ROL_SUPERUSUARIO, ROL_ADMINISTRADOR)

# --- Seguridad ---------------------------------------------------------------
ITERACIONES_PBKDF2 = 240_000

# --- Colores corporativos (Banco del Pacífico) --------------------------------
COLOR_AZUL = "#152342"
COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS_CLARO = "#F0F2F5"          # para fondos alternativos
COLOR_TEXTO = "#152342"               # texto en fondo claro
COLOR_TEXTO_INV = "#FFFFFF"           # texto en fondo oscuro