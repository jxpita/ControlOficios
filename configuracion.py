"""
Configuración central de la aplicación.
Define rutas, nombres de archivo y constantes usadas por el resto de módulos.
"""
import sys
from pathlib import Path

# --- Directorio base ---------------------------------------------------------
if getattr(sys, "frozen", False):
    DIR_BASE = Path(sys.executable).resolve().parent
else:
    DIR_BASE = Path(__file__).resolve().parent

DIR_DATOS = DIR_BASE / "datos"
DIR_DATOS.mkdir(exist_ok=True)

# --- Archivos ----------------------------------------------------------------
ARCHIVO_CLAVE = DIR_DATOS / "clave_maestra.key"
ARCHIVO_CREDENCIALES = DIR_DATOS / "credenciales.dat"
ARCHIVO_OFICIOS = DIR_DATOS / "oficios.dat"
ARCHIVO_EMPLEADOS = DIR_DATOS / "empleados.csv"

# --- Imágenes (logo e ícono) ------------------------------------------------
ARCHIVO_LOGO = DIR_DATOS / "bdp_icon.jpg"      # logo principal (PNG)
ARCHIVO_ICONO = DIR_DATOS / "bdp_icon_alt.ico"          # ícono de la ventana

# --- Constantes de negocio ---------------------------------------------------
ESTADOS = ["Por asignar", "En proceso", "Finalizado"]
PREFIJO_REFERENCIA = "UDC-OFICIO"

# --- Seguridad ---------------------------------------------------------------
ITERACIONES_PBKDF2 = 240_000

# --- Colores corporativos (Banco del Pacífico) --------------------------------
COLOR_AZUL = "#152342"
COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS_CLARO = "#F0F2F5"          # para fondos alternativos
COLOR_TEXTO = "#152342"               # texto en fondo claro
COLOR_TEXTO_INV = "#FFFFFF"           # texto en fondo oscuro