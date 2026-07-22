"""
Lectura de la base plana de empleados (para el combobox).
Formato del archivo empleados.csv:  idUsuario,nombreUsuario,nombreEmpleado
En el combo se muestra 'nombreEmpleado', pero se conserva el idUsuario.

(Las claves idUsuario/nombreUsuario/nombreEmpleado se conservan tal cual
porque reflejan exactamente la estructura que definiste para el archivo.)
"""
import csv
from typing import List, Dict

from configuracion import ARCHIVO_EMPLEADOS


def cargar_empleados() -> List[Dict]:
    empleados: List[Dict] = []
    if not ARCHIVO_EMPLEADOS.exists():
        return empleados
    with open(ARCHIVO_EMPLEADOS, newline="", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo):
            if not fila or len(fila) < 3:
                continue
            id_usuario = fila[0].strip()
            nombre_usuario = fila[1].strip()
            nombre_empleado = fila[2].strip()
            if id_usuario.lower() == "idusuario":  # saltar encabezado si existe
                continue
            empleados.append({
                "idUsuario": id_usuario,
                "nombreUsuario": nombre_usuario,
                "nombreEmpleado": nombre_empleado,
            })
    return empleados
