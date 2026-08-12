"""
Genera el archivo de datos de prueba para la carga masiva.

Crea `Matriz de prueba - 55 oficios.xlsx` con el FORMATO ESTABLECIDO (cabecera
en la fila 4, de la columna B a la AA) y 55 oficios repartidos entre las dos
instituciones, con casos variados: finalizados, en proceso, sin responsable,
con varios investigados y sin fecha de respuesta.

Algunos oficios ocupan más de una fila (una por investigado), igual que en la
matriz real, así que el archivo tiene más filas que oficios.

    python datos_de_prueba/generar_datos_prueba.py

No forma parte de la aplicación: es una utilidad para preparar una demostración
o para probar la carga masiva sin arriesgar datos reales.
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from carga_masiva import CABECERA_MATRIZ, FILA_CABECERA   # noqa: E402

SALIDA = Path(__file__).resolve().parent / "Matriz de prueba - 55 oficios.xlsx"
CANTIDAD_OFICIOS = 55

INSTITUCIONES = ["Superintendencia de Bancos", "Fiscalía General del Estado"]

# Los nombres se escriben como en la matriz real: inicial y apellido. Al
# importar, la aplicación los empareja con las cuentas del sistema; los que no
# existan entrarán como "Por asignar", que también conviene ver en la prueba.
USUARIOS = ["C. Roman", "J. Portero", "J. Rosero", "M. Vera", ""]

TIPOS_ACCION = ["CERTIFICACIÓN", "RETENCIÓN", "INFORMACIÓN", "INMOVILIZACIÓN",
                "LEVANTAMIENTO DE MEDIDAS", "BLOQUEO Y RETENCIÓN",
                "RECTIFICACIÓN"]

DELITOS = [
    "TRAFICO ILÍCITO DE SUSTANCIAS CATALOGADAS SUJETAS A FISCALIZACIÓN",
    "LAVADO DE ACTIVOS", "COHECHO", "PECULADO", "ENRIQUECIMIENTO ILÍCITO",
    "DEFRAUDACIÓN TRIBUTARIA", "ESTAFA", "DESAPARICIÓN INVOLUNTARIA",
]

APELLIDOS = ["ORDOÑEZ VILLAGOMEZ DAVID MIGUEL", "ENOMENGA VARGAS ERICK LENIN",
             "BOLAÑOS RUBIO MARCO OLGER", "ACOSTA JEREZ DIANA CAROLINA",
             "MENDOZA SALAS LUIS ALBERTO", "PARRA NUÑEZ SOFIA ELENA",
             "CEVALLOS MORA JORGE ANDRÉS", "TAPIA LEÓN MARIA FERNANDA"]

MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
         "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def generar_filas():
    """Una fila por investigado. Algunos oficios repiten Referencia oficio para
    que la carga los agrupe y calcule la cantidad de investigados."""
    random.seed(2026)          # mismo archivo en cada ejecución
    hoy = date.today()
    filas = []
    for numero in range(1, CANTIDAD_OFICIOS + 1):
        institucion = random.choice(INSTITUCIONES)
        sigla = "SB" if institucion.startswith("Super") else "FGE"

        recepcion = hoy - timedelta(days=random.randint(5, 240))
        oficio = recepcion - timedelta(days=random.randint(1, 20))
        asignacion = recepcion + timedelta(days=random.randint(0, 3))
        # Tres de cada cuatro ya están respondidos.
        respondido = random.random() < 0.75
        respuesta = asignacion + timedelta(days=random.randint(1, 25)) \
            if respondido else None
        if respuesta and respuesta > hoy:
            respuesta = None
            respondido = False

        usuario = random.choice(USUARIOS)
        if not usuario:
            # Sin responsable no puede haber respuesta: la aplicación lo dejaría
            # "Por asignar" y le quitaría la fecha; se genera ya coherente.
            respuesta, respondido = None, False

        referencia_oficio = f"{sigla}-{recepcion.year}-{numero:04d}-OF"
        # Uno de cada cinco oficios tiene entre 2 y 4 investigados.
        investigados = random.choice([1, 1, 1, 1, 2, 3, 4])
        for _ in range(investigados):
            filas.append({
                "Institución del Estado": institucion,
                "Mes": MESES[recepcion.month - 1],
                "Fecha Asignación": asignacion,
                "Usuario": usuario,
                "Prioridad": random.choice(["Alta", "Media", "Baja"]),
                "Fecha Emisión": recepcion,
                "Referencia": f"{str(recepcion.year)[2:]}-{numero:04d}-UDC",
                "Medio Repuesta": random.choice(["Electrónico", "Físico"]),
                "Fecha Envío": respuesta,
                "Estado": "Finalizado" if respondido else "En proceso",
                "Días": (respuesta - asignacion).days if respuesta else "",
                "Canal Recepc": random.choice(["Proveedor", "Ventanilla",
                                               "Correo"]),
                "Fecha Circular": oficio,
                "Apellidos, Nombres - Razón Social": random.choice(APELLIDOS),
                "TiPASo Id CED; PAS; RUCUC": random.choice(["CED", "PAS", "RUC"]),
                "Identificación Ced; Pas; RUC": str(random.randint(10 ** 9,
                                                                  10 ** 10 - 1)),
                "Referencia - Oficio FGE; Juzgado": referencia_oficio,
                "Número Expediente Fiscal": "-",
                "Referencia - Circular Superintendencia Bancos":
                    f"SB-SG-{recepcion.year}-{random.randint(10000, 99999)}-C",
                "Delito": random.choice(DELITOS),
                "Tipo de Accion": random.choice(TIPOS_ACCION),
                "Observación": random.choice(
                    ["", "", "Atendido dentro del plazo",
                     "Requiere seguimiento", "Se remitió por correo"]),
                "Tipo de Implicado": random.choice(
                    ["CLIENTE", "EX CLIENTE", "NO CLIENTE", "SIN IDENTIFICACION"]),
                "LCI - SI o NO": random.choice(["SI", "NO"]),
                "Fecha - Solicitud": recepcion + timedelta(days=1),
                "Ref Solic- No. LCI-202X-000": f"LCI-{recepcion.year}-"
                                               f"{random.randint(1, 99):03d}",
            })
    return filas


def escribir(filas):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Matriz-Req-Inf"

    # Rótulos de agrupación de la fila 3, como en la matriz real.
    hoja["D3"] = "Gestión - Asignación"
    hoja["H3"] = "BDP - Oficio de Respuesta"
    hoja["Q3"] = "Información del Oficio .- SB; FGE, FJ; "
    hoja["Z3"] = "Registro - RCSA"

    encabezados = [nombre for nombre, _prefijo, _campo in CABECERA_MATRIZ]
    relleno = PatternFill("solid", fgColor="152342")
    for indice, titulo in enumerate(encabezados, start=2):   # la B es la 2
        celda = hoja.cell(row=FILA_CABECERA, column=indice, value=titulo)
        celda.font = Font(bold=True, color="FFFFFF", size=9)
        celda.fill = relleno
        celda.alignment = Alignment(wrap_text=True, vertical="center")

    for numero, fila in enumerate(filas, start=FILA_CABECERA + 1):
        for indice, titulo in enumerate(encabezados, start=2):
            hoja.cell(row=numero, column=indice, value=fila.get(titulo, ""))

    hoja.freeze_panes = f"A{FILA_CABECERA + 1}"
    for indice in range(2, len(encabezados) + 2):
        hoja.column_dimensions[hoja.cell(row=FILA_CABECERA,
                                         column=indice).column_letter].width = 18
    libro.save(SALIDA)


if __name__ == "__main__":
    filas = generar_filas()
    escribir(filas)
    oficios = len({f["Referencia - Oficio FGE; Juzgado"] for f in filas})
    print(f"{SALIDA.name}: {len(filas)} filas -> {oficios} oficios "
          f"(las filas que comparten Referencia oficio se agrupan).")
