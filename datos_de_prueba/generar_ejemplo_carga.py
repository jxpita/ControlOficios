"""
Genera el ARCHIVO DE EJEMPLO de la carga masiva.

Crea `Ejemplo de carga masiva.xlsx`: seis oficios con los casos habituales,
escrito con el MISMO formato que produce «Exportar oficios», que es el que
exige la importación. Sirve como plantilla: se borra el contenido de ejemplo y
se escriben los oficios reales debajo de la cabecera.

    python datos_de_prueba/generar_ejemplo_carga.py

El archivo lo escribe la propia exportación de la aplicación
(`almacen_oficios.exportar_xlsx`), de modo que el ejemplo no puede desviarse
del formato: si se añade una columna a la exportación, aparece aquí sola.

Los responsables se indican con su NOMBRE DE CUENTA, en minúsculas y sin
espacios (cmroman, jportero…). Esas cuentas tienen que existir en el sistema
antes de cargar el archivo; si no, la importación lo dice y no carga nada.

Se diferencia de `generar_datos_prueba.py` en el propósito: aquel produce un
volumen grande para ver el tablero con contenido; este es el modelo del formato.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import almacen_oficios                                    # noqa: E402

SALIDA = Path(__file__).resolve().parent / "Ejemplo de carga masiva.xlsx"

SB = "Superintendencia de Bancos"
FGE = "Fiscalía General del Estado"

# Cuentas de la unidad. El archivo las nombra por su usuario; el nombre completo
# es informativo (al importar se toma el de la cuenta).
RESPONSABLES = {
    "cmroman": "Camila Maria Roman Townsed",
    "jportero": "Joel Tyrone Portero Cervantes",
    "dtfranco": "Damara Tais Franco Pacheco",
    "lgjarrin": "Lizzi Gabriela Jarrin Aguilar",
}

# Fechas relativas a hoy: el ejemplo no envejece y ninguna queda en el futuro,
# que es algo que la aplicación no admite.
HOY = date.today()


def _dia(dias_atras):
    return (HOY - timedelta(days=dias_atras)).isoformat()


def _persona(nombre, tipo_id, identificacion, tipo, lci="No"):
    return {"nombre": nombre, "tipo_identificacion": tipo_id,
            "identificacion": identificacion, "tipo_implicado": tipo, "lci": lci}


def _oficio(institucion, codigo, accion, causal, oficio, recepcion,
            usuario="", asignacion="", respuesta="", estado="Por asignar",
            prioridad="Media", observacion="", implicados=(),
            cantidad_investigados=""):
    """Un oficio con la forma con la que lo guarda el sistema.

    La Referencia UDC, el documento del oficio, quién lo registró y cuándo son
    columnas que rellena el sistema al importar: aquí van vacías a propósito,
    para que se vea que su contenido no se toma del archivo.
    """
    implicados = list(implicados)
    return {
        "referencia": "",
        "institucion": institucion,
        "codigo_oficio": codigo,
        "tipo_accion": accion,
        "causal_oficio": causal,
        "fecha_oficio": oficio,
        "fecha_recepcion": recepcion,
        "fecha_asignacion": asignacion,
        "fecha_respuesta": respuesta,
        "cantidad_investigados": (str(len(implicados)) if implicados
                                  else str(cantidad_investigados or "")),
        "prioridad": prioridad,
        "id_empleado": usuario,
        "empleado": RESPONSABLES.get(usuario, ""),
        "estado": estado,
        "archivo_oficio": "",
        "archivo_respuesta": "",
        "observacion": observacion,
        "registrado_por": "",
        "fecha_registro": "",
        "origen": "",
        "anulado": "",
        "motivo_anulacion": "",
        "implicados": implicados,
    }


# Los seis casos que muestra el ejemplo:
#   1) Finalizado con una sola persona: trae sus dos fechas, como exige el
#      sistema para dar un oficio por finalizado.
#   2) En proceso con TRES personas investigadas: ocupa tres filas que repiten
#      la Referencia oficio y los datos del oficio.
#   3) Por asignar: sin responsable, sin fecha de asignación y sin respuesta.
#   4) Empresa identificada con RUC, finalizado.
#   5) En proceso, prioridad alta, con dos personas y una en la lista de
#      control interno (LCI).
#   6) Por asignar sin detalle de personas: solo la cantidad de investigados.
OFICIOS = [
    _oficio(SB, "SB-2026-0101-OF", "Certificación", "LAVADO DE ACTIVOS",
            _dia(41), _dia(40), usuario="cmroman", asignacion=_dia(39),
            respuesta=_dia(30), estado="Finalizado", prioridad="Alta",
            observacion="Atendido dentro del plazo",
            implicados=[_persona("ORDOÑEZ VILLAGOMEZ DAVID MIGUEL", "Cédula",
                                 "1400349096", "Cliente", "Sí")]),
    _oficio(FGE, "FPP-FED4-2026-000123-O", "Retención", "COHECHO",
            _dia(21), _dia(20), usuario="jportero", asignacion=_dia(20),
            estado="En proceso",
            implicados=[
                _persona("ACOSTA JEREZ DIANA CAROLINA", "Cédula",
                         "0923847561", "Cliente"),
                _persona("MENDOZA SALAS LUIS ALBERTO", "Cédula",
                         "1712345678", "Ex cliente"),
                _persona("QUISPE ANDRADE PEDRO JOSÉ", "Pasaporte",
                         "AB123456", "No cliente")]),
    _oficio(SB, "SB-2026-0118-OF", "Información", "DEFRAUDACIÓN TRIBUTARIA",
            _dia(8), _dia(5), prioridad="Baja",
            observacion="Pendiente de asignar",
            implicados=[_persona("CEVALLOS MORA JORGE ANDRÉS", "Cédula",
                                 "1309876543", "Sin identificación")]),
    _oficio(SB, "SB-2026-0125-OF", "Bloqueo y retención",
            "ENRIQUECIMIENTO ILÍCITO", _dia(15), _dia(12), usuario="lgjarrin",
            asignacion=_dia(12), respuesta=_dia(3), estado="Finalizado",
            prioridad="Alta", observacion="Se remitió por correo",
            implicados=[_persona("COMERCIAL LOS ANDES S.A.", "RUC",
                                 "1791234567001", "Cliente", "Sí")]),
    _oficio(FGE, "FPP-FED4-2026-000188-O", "Levantamiento",
            "TRAFICO ILÍCITO DE SUSTANCIAS CATALOGADAS SUJETAS A FISCALIZACIÓN",
            _dia(14), _dia(10), usuario="dtfranco", asignacion=_dia(9),
            estado="En proceso", prioridad="Alta",
            implicados=[
                _persona("VILLACÍS ROJAS ANDREA PAOLA", "Cédula",
                         "0102938475", "No cliente", "Sí"),
                _persona("ZAMBRANO LOOR KEVIN DANIEL", "Cédula",
                         "1301122334", "Cliente")]),
    _oficio(FGE, "FPP-FED2-2026-000204-O", "Inmovilización", "PECULADO",
            _dia(4), _dia(2), prioridad="Media",
            observacion="Llegó sin el detalle de las personas",
            cantidad_investigados=2),
]


if __name__ == "__main__":
    # Lo escribe la exportación de la aplicación: el ejemplo y el formato real
    # no pueden separarse.
    almacen_oficios.exportar_xlsx(OFICIOS, str(SALIDA))
    filas = sum(max(len(o["implicados"]), 1) for o in OFICIOS)
    print(f"{SALIDA.name}: {len(OFICIOS)} oficios en {filas} filas.")
    print("  Mismo formato que «Exportar oficios»: cabecera en la fila 1 y "
          "una fila por persona investigada.")
    print("  Responsables por nombre de cuenta: "
          + ", ".join(sorted(RESPONSABLES)) + ".")
    print("  Esas cuentas deben existir en el sistema antes de cargar.")
