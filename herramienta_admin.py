"""
herramienta_admin.py — utilidad SOLO para el administrador.
Descifra y muestra el contenido de los archivos cifrados (oficios / credenciales).

Requiere estar junto a los demás módulos del proyecto y que la carpeta 'datos'
que ve 'configuracion.py' contenga la 'clave_maestra.key' y los .dat reales.

Uso:
    python herramienta_admin.py oficios
        -> muestra todos los oficios en JSON legible

    python herramienta_admin.py credenciales
        -> muestra los usuarios del sistema (SIN contraseñas: no se pueden recuperar)

    python herramienta_admin.py oficios --csv reporte.csv
        -> exporta los oficios a un CSV que abre directo en Excel
"""
import sys
import json
import csv

from cryptography.fernet import InvalidToken

from configuracion import ARCHIVO_OFICIOS, ARCHIVO_CREDENCIALES
from cifrado import descifrar


def _cargar(ruta):
    if not ruta.exists():
        print(f"No existe el archivo: {ruta}")
        sys.exit(1)
    try:
        return json.loads(descifrar(ruta.read_bytes()))
    except InvalidToken:
        print("ERROR: el archivo fue alterado o la clave no corresponde.")
        sys.exit(1)


def mostrar_json(registros):
    print(json.dumps(registros, ensure_ascii=False, indent=2))


def exportar_csv_oficios(registros, ruta_csv):
    columnas = ["referencia", "codigo_oficio", "fecha_recepcion", "fecha_oficio",
                "empleado", "estado", "registrado_por", "fecha_registro"]
    # utf-8-sig para que Excel respete las tildes al abrir el CSV
    with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        for registro in registros:
            escritor.writerow(registro)
    print(f"Exportado a '{ruta_csv}' ({len(registros)} registros).")


def main():
    argumentos = sys.argv[1:]
    if not argumentos or argumentos[0] not in ("oficios", "credenciales"):
        print(__doc__)
        return

    objetivo = argumentos[0]
    ruta = ARCHIVO_OFICIOS if objetivo == "oficios" else ARCHIVO_CREDENCIALES
    registros = _cargar(ruta)

    if "--csv" in argumentos:
        if objetivo != "oficios":
            print("La exportación --csv está pensada solo para 'oficios'.")
            return
        indice = argumentos.index("--csv")
        ruta_csv = argumentos[indice + 1] if indice + 1 < len(argumentos) else "reporte.csv"
        exportar_csv_oficios(registros, ruta_csv)
    else:
        mostrar_json(registros)
        if objetivo == "credenciales":
            print("\nNota: 'sal' y 'hash' NO son la contraseña. Las contraseñas "
                  "no se pueden recuperar; solo verificar en el ingreso.")


if __name__ == "__main__":
    main()
