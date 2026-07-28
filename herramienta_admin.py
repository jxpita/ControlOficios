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

    python herramienta_admin.py oficios --purgar-formato-anterior
        -> ELIMINA los oficios que aún usan la referencia antigua
           (UDC-OFICIO-AAAAMMDD-NNNN), previa confirmación. Útil para descartar
           los registros de prueba anteriores al formato REQ-INF-AAAA-NNNN.

Salvo '--purgar-formato-anterior', la herramienta es de solo lectura.
"""
import sys
import json
import csv

from cryptography.fernet import InvalidToken

from configuracion import ARCHIVO_OFICIOS, ARCHIVO_CREDENCIALES, PREFIJO_REFERENCIA
from cifrado import descifrar
import almacen_oficios
import registro_actividad
import bloqueo


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
    # 'referencia' es la Referencia UDC y 'codigo_oficio' la Referencia oficio.
    # Orden de fechas: oficio -> recepción -> respuesta; la observación al final.
    columnas = ["referencia", "codigo_oficio", "causal_oficio", "referencia_sb",
                "fecha_oficio", "fecha_recepcion", "fecha_respuesta",
                "empleado", "estado", "registrado_por", "fecha_registro",
                "archivo_respuesta", "observacion"]
    # utf-8-sig para que Excel respete las tildes al abrir el CSV
    with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        for registro in registros:
            escritor.writerow(registro)
    print(f"Exportado a '{ruta_csv}' ({len(registros)} registros).")


def _es_formato_actual(referencia):
    """True si la referencia usa el formato vigente REQ-INF-AAAA-NNNN."""
    return (referencia or "").upper().startswith(f"{PREFIJO_REFERENCIA}-")


def purgar_formato_anterior(registros):
    """Elimina los oficios cuya Referencia UDC usa el formato antiguo
    (UDC-OFICIO-AAAAMMDD-NNNN). Pide confirmación antes de borrar."""
    antiguos = [r for r in registros if not _es_formato_actual(r.get("referencia", ""))]
    if not antiguos:
        print("No hay oficios con el formato de referencia anterior. Nada que purgar.")
        return

    print(f"Se encontraron {len(antiguos)} oficio(s) con el formato anterior:")
    for registro in antiguos:
        print(f"  {registro.get('referencia','')}  ->  "
              f"{registro.get('codigo_oficio','')}  ({registro.get('estado','')})")
    print("\nESTA ACCIÓN NO SE PUEDE DESHACER.")
    respuesta = input("Escriba 'PURGAR' para confirmar: ").strip()
    if respuesta != "PURGAR":
        print("Cancelado. No se eliminó ningún registro.")
        return

    # Bajo bloqueo: releer para no pisar lo que otro usuario haya registrado
    # mientras se leía la lista y se pedía la confirmación.
    with bloqueo.bloquear("oficios"):
        actuales = almacen_oficios._leer_registros()
        quedan = [r for r in actuales if _es_formato_actual(r.get("referencia", ""))]
        almacen_oficios._guardar_registros(quedan)
    antiguos = [r for r in actuales if not _es_formato_actual(r.get("referencia", ""))]
    registro_actividad.registrar(
        "PURGAR_FORMATO_ANTERIOR",
        f"eliminados={len(antiguos)}; "
        f"referencias={','.join(r.get('referencia','') for r in antiguos)}",
        "herramienta_admin")
    print(f"Eliminados {len(antiguos)} registro(s). Quedan {len(quedan)}.")
    print("Nota: los PDF de respuesta de esos oficios siguen en datos/respuestas/; "
          "elimínelos a mano si ya no los necesita.")


def main():
    argumentos = sys.argv[1:]
    if not argumentos or argumentos[0] not in ("oficios", "credenciales"):
        print(__doc__)
        return

    objetivo = argumentos[0]
    ruta = ARCHIVO_OFICIOS if objetivo == "oficios" else ARCHIVO_CREDENCIALES
    registros = _cargar(ruta)

    if "--purgar-formato-anterior" in argumentos:
        if objetivo != "oficios":
            print("La purga solo aplica a 'oficios'.")
            return
        purgar_formato_anterior(registros)
    elif "--csv" in argumentos:
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
