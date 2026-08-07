"""
Carga masiva de oficios desde la matriz de Excel (.xlsx) o desde un CSV.

Sirve para volcar de una vez el histórico que la unidad venía llevando en la
"Matriz-Req-Inf", sin tener que reescribir oficio por oficio.

Cómo está organizada la matriz
------------------------------
La cabecera ocupa la fila 4, de la columna B a la AA (la fila 3 solo lleva
rótulos de agrupación y las filas 1-2 están vacías). Los datos empiezan en la
fila 5. Las columnas se reconocen por su TEXTO, no por su posición, de modo que
si mañana se inserta o se mueve una columna la carga sigue funcionando.

Correspondencia con los campos de la aplicación
-----------------------------------------------
    Matriz                                  Campo del oficio
    --------------------------------------- ----------------------
    Ref Prev & Cump                         referencia (Referencia UDC)
    Referencia - Oficio FGE; Juzgado...      codigo_oficio (Referencia oficio)
    Referencia - Circular Superintendencia   referencia_sb
    Delito                                   causal_oficio
    Fecha Circular                           fecha_oficio
    Fecha Emisión                            fecha_recepcion
    Fecha Asignación                         fecha_asignacion
    Fecha Envío                              fecha_respuesta
    Usuario                                  responsable
    Estado                                   estado
    Observación                              observacion
    (nº de filas con la misma Referencia UDC) cantidad_investigados

Las columnas restantes de la matriz (Mes, Prioridad, Medio Respuesta, Días,
Canal Recepción, los datos del investigado, Expediente Fiscal, Tipo de Acción,
Tipo de Implicado, LCI y el bloque RCSA) no tienen equivalente en la aplicación
y se ignoran; la carga informa de ello.

Varias filas con la misma Referencia UDC se entienden como el mismo oficio con
varios investigados: se agrupan en un solo registro y la cantidad de
investigados es el número de filas.
"""
import csv
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from configuracion import ESTADOS

# Fila de la cabecera y primera fila de datos en la matriz de Excel.
FILA_CABECERA = 4
PRIMERA_FILA_DATOS = FILA_CABECERA + 1

# Encabezado de la matriz -> campo del oficio. La comparación se hace
# normalizada (sin tildes, sin mayúsculas y sin espacios de más), y basta con
# que el encabezado del archivo EMPIECE por el texto indicado: así encajan los
# títulos largos que ocupan varias líneas ("Referencia - Oficio\nFGE; ...").
COLUMNAS = {
    "ref prev & cump": "referencia",
    "referencia - oficio": "codigo_oficio",
    "referencia - circular": "referencia_sb",
    "delito": "causal_oficio",
    "fecha circular": "fecha_oficio",
    "fecha emision": "fecha_recepcion",
    "fecha asignacion": "fecha_asignacion",
    "fecha envio": "fecha_respuesta",
    "usuario": "empleado",
    "estado": "estado",
    "observacion": "observacion",
}

# Estados de la matriz -> estados de la aplicación.
ESTADOS_EQUIVALENTES = {
    "finalizado": "Finalizado",
    "finalizada": "Finalizado",
    "atendido": "Finalizado",
    "cerrado": "Finalizado",
    "en proceso": "En proceso",
    "en tramite": "En proceso",
    "pendiente": "En proceso",
    "por asignar": "Por asignar",
    "sin asignar": "Por asignar",
}

_ACENTOS = str.maketrans("áéíóúàèìòùäëïöüâêîôûÁÉÍÓÚÄËÏÖÜÂÊÎÔÛ",
                         "aeiouaeiouaeiouaeiouAEIOUAEIOUAEIOU")


def normalizar(texto) -> str:
    """Texto en minúsculas, sin tildes y con los espacios colapsados."""
    if texto is None:
        return ""
    return " ".join(str(texto).translate(_ACENTOS).lower().split())


def _a_fecha(valor) -> str:
    """Convierte a 'AAAA-MM-DD'. Devuelve '' si la celda está vacía.

    Acepta lo que Excel entrega como fecha real y también las fechas escritas a
    mano en los formatos habituales, incluido el día/mes/año que se usa aquí.
    """
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    texto = str(valor).strip()
    if not texto or texto in {"-", "--", "N/A", "n/a"}:
        return ""
    # Excel a veces deja la hora pegada a la fecha.
    texto = texto.split(" ")[0].replace("/", "-").replace(".", "-")
    for formato in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d-%m-%y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"No se reconoce la fecha «{valor}»")


def _a_texto(valor) -> str:
    """Contenido de una celda como texto limpio. Los guiones sueltos que la
    matriz usa para 'sin dato' se tratan como vacío."""
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)          # 1650110974001.0 -> 1650110974001
    texto = " ".join(str(valor).split())
    return "" if texto in {"-", "--", "N/A", "n/a"} else texto


# --- Lectura del archivo -----------------------------------------------------
def _mapear_cabecera(celdas: List) -> Dict[int, str]:
    """Relaciona el índice de cada columna con el campo del oficio."""
    mapa = {}
    for indice, celda in enumerate(celdas):
        titulo = normalizar(celda)
        if not titulo:
            continue
        for prefijo, campo in COLUMNAS.items():
            if titulo.startswith(prefijo):
                mapa[indice] = campo
                break
    return mapa


def _leer_xlsx(ruta: Path) -> Tuple[List[List], List[str]]:
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise ValueError(
            "Para leer archivos de Excel hace falta la librería openpyxl:\n\n"
            "    pip install openpyxl\n\n"
            "También puede guardar la matriz como CSV y cargarla así."
        )
    libro = load_workbook(ruta, data_only=True, read_only=True)
    hoja = libro.active
    filas = [list(f) for f in hoja.iter_rows(values_only=True)]
    libro.close()
    if len(filas) < FILA_CABECERA:
        raise ValueError("El archivo no tiene la cabecera esperada en la fila 4.")
    return filas[FILA_CABECERA - 1:], []


def _leer_csv(ruta: Path) -> Tuple[List[List], List[str]]:
    """Lee un CSV detectando el separador (barra vertical, punto y coma o coma).

    La cabecera se busca en las primeras filas, porque un CSV exportado desde la
    matriz puede arrastrar las filas de rótulos de arriba.
    """
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        muestra = archivo.read(8192)
        archivo.seek(0)
        separador = max("|;,\t", key=muestra.count)
        filas = [f for f in csv.reader(archivo, delimiter=separador)]
    if not filas:
        raise ValueError("El archivo está vacío.")
    # La cabecera es la primera fila que contenga alguna columna reconocible.
    for indice, fila in enumerate(filas[:10]):
        if _mapear_cabecera(fila):
            return filas[indice:], []
    raise ValueError(
        "No se reconoció ninguna columna. Compruebe que el archivo tiene la "
        "cabecera de la matriz (Ref Prev & Cump, Fecha Asignación, Estado…)."
    )


def leer_archivo(ruta) -> Tuple[List[Dict], List[str], List[str]]:
    """Lee la matriz y devuelve (filas, columnas_ignoradas, errores).

    Cada fila es un diccionario con los campos ya normalizados y una clave
    `_fila` con su número dentro del archivo, para poder señalar los errores.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise ValueError("No se encontró el archivo seleccionado.")
    if ruta.suffix.lower() in (".xlsx", ".xlsm"):
        crudas, _ = _leer_xlsx(ruta)
    elif ruta.suffix.lower() == ".csv":
        crudas, _ = _leer_csv(ruta)
    else:
        raise ValueError("El archivo debe ser una hoja de Excel (.xlsx) o un CSV.")

    cabecera = crudas[0]
    mapa = _mapear_cabecera(cabecera)
    if not mapa:
        raise ValueError(
            "No se reconoció ninguna columna de la matriz. Compruebe que la "
            f"cabecera está en la fila {FILA_CABECERA} (de la columna B a la AA)."
        )
    ignoradas = sorted({_a_texto(cabecera[i]).replace("\n", " ")
                        for i in range(len(cabecera))
                        if i not in mapa and _a_texto(cabecera[i])})

    filas, errores = [], []
    for desplazamiento, cruda in enumerate(crudas[1:], start=1):
        numero = FILA_CABECERA + desplazamiento
        datos = {"_fila": numero}
        problema = None
        for indice, campo in mapa.items():
            valor = cruda[indice] if indice < len(cruda) else None
            if campo.startswith("fecha_"):
                try:
                    datos[campo] = _a_fecha(valor)
                except ValueError as error:
                    problema = f"Fila {numero}: {error}"
                    datos[campo] = ""
            else:
                datos[campo] = _a_texto(valor)
        # Una fila sin ninguna referencia es una fila en blanco del final.
        if not datos.get("referencia") and not datos.get("codigo_oficio"):
            continue
        if problema:
            errores.append(problema)
            continue
        datos["estado"] = ESTADOS_EQUIVALENTES.get(
            normalizar(datos.get("estado")), datos.get("estado") or "")
        filas.append(datos)
    return filas, ignoradas, errores


# --- Agrupación y preparación ------------------------------------------------
def agrupar_por_referencia(filas: List[Dict]) -> List[Dict]:
    """Une las filas que comparten Referencia UDC en un solo oficio.

    En la matriz cada fila es un investigado, así que un mismo requerimiento
    puede ocupar varias. Se conserva la primera fila y la cantidad de
    investigados pasa a ser el número de filas agrupadas.
    """
    agrupados: Dict[str, Dict] = {}
    orden: List[str] = []
    for fila in filas:
        clave = (fila.get("referencia") or f"__fila_{fila['_fila']}").strip().upper()
        if clave not in agrupados:
            copia = dict(fila)
            copia["cantidad_investigados"] = 1
            agrupados[clave] = copia
            orden.append(clave)
        else:
            agrupados[clave]["cantidad_investigados"] += 1
            # Se completa lo que la primera fila hubiera dejado en blanco.
            for campo, valor in fila.items():
                if campo != "_fila" and valor and not agrupados[clave].get(campo):
                    agrupados[clave][campo] = valor
    return [agrupados[c] for c in orden]


def emparejar_responsables(filas: List[Dict], usuarios: List[Dict]) -> List[str]:
    """Traduce la columna "Usuario" de la matriz a cuentas del sistema.

    La matriz anota a la persona en formato "C. Roman", que no es un nombre de
    usuario. Se intenta encajar por nombre de cuenta, por nombre completo y por
    la forma "inicial. apellido".

    Cuando no se encuentra la cuenta se CONSERVA el nombre tal cual venía en la
    matriz, pero sin enlazarlo a ningún usuario del sistema. Es lo fiel a un
    histórico: el expediente dice quién lo atendió, aunque esa persona ya no
    tenga cuenta. Además evita perder la fila entera, porque un oficio con
    fecha de respuesta necesita responsable para poder quedar finalizado.
    Esos oficios los ve solo un gestor, que puede reasignarlos a una cuenta
    real. Devuelve la lista de nombres que no se pudieron identificar.
    """
    indice = {}
    for usuario in usuarios:
        cuenta = usuario["usuario"]
        nombre = usuario.get("nombre", "")
        indice[normalizar(cuenta)] = usuario
        indice[normalizar(nombre)] = usuario
        partes = normalizar(nombre).split()
        if len(partes) >= 2:
            # "Juan Carlos Roman Diaz" -> "j. roman" y "j roman"
            apellido = partes[len(partes) // 2] if len(partes) > 2 else partes[-1]
            indice[f"{partes[0][0]}. {apellido}"] = usuario
            indice[f"{partes[0][0]} {apellido}"] = usuario

    sin_identificar = []
    for fila in filas:
        buscado = normalizar(fila.get("empleado"))
        if not buscado:
            fila["id_empleado"] = ""
            fila["empleado"] = ""
            continue
        encontrado = indice.get(buscado) or indice.get(buscado.replace(".", "").strip())
        if encontrado:
            fila["id_empleado"] = encontrado["usuario"]
            fila["empleado"] = encontrado["nombre"]
        else:
            sin_identificar.append(fila["empleado"])
            fila["id_empleado"] = ""      # sin cuenta: nadie puede actuar sobre él
    return sorted(set(sin_identificar))


# Marca para los oficios ya tramitados cuya matriz no anota quién los atendió.
# No es un nombre inventado: deja constancia de que el dato no está, y permite
# conservar el expediente (un oficio con fecha de respuesta necesita
# responsable para poder quedar finalizado).
RESPONSABLE_NO_CONSTA = "(no consta en la matriz)"


def preparar(ruta, usuarios: List[Dict]) -> Dict:
    """Deja las filas listas para importar y resume lo que se va a hacer."""
    filas, ignoradas, errores = leer_archivo(ruta)
    filas = agrupar_por_referencia(filas)
    sin_responsable = emparejar_responsables(filas, usuarios)
    sin_constancia = 0
    for fila in filas:
        if not fila.get("empleado"):
            # Si el oficio ya fue respondido, descartarlo por no saber quién lo
            # atendió sería perder un expediente real: se deja constancia de
            # que el dato no consta y se conserva la fila.
            if fila.get("fecha_respuesta") or fila.get("estado") in (
                    "En proceso", "Finalizado"):
                fila["empleado"] = RESPONSABLE_NO_CONSTA
                sin_constancia += 1
            else:
                # Sin responsable y sin respuesta, el único estado posible es
                # "Por asignar": las reglas del sistema no admiten otro.
                fila["estado"] = "Por asignar"
        if fila.get("empleado") and fila.get("estado") not in ESTADOS:
            fila["estado"] = "En proceso"
    return {
        "filas": filas,
        "columnas_ignoradas": ignoradas,
        "errores": errores,
        "responsables_sin_identificar": sin_responsable,
        "sin_responsable_anotado": sin_constancia,
    }
