"""
Carga masiva de oficios desde la matriz de Excel (.xlsx) o desde un CSV.

Sirve para volcar de una vez el histórico que la unidad venía llevando en la
"Matriz-Req-Inf", sin tener que reescribir oficio por oficio.

Formato establecido
-------------------
La cabecera ocupa la fila 4, de la columna B a la AA (la fila 3 solo lleva
rótulos de agrupación y las filas 1-2 están vacías). Los datos empiezan en la
fila 5.

El archivo que se cargue debe respetar ese formato: las 26 columnas, completas
y EN SU ORDEN (ver `CABECERA_MATRIZ`). Antes de leer un solo dato se comprueba
la cabecera y, si no cuadra, se rechaza el archivo indicando qué columna está
fuera de sitio, cuál falta o cuál sobra. Solo se toleran diferencias de
redacción —mayúsculas, tildes, espacios de más y títulos repartidos en varias
líneas—, nunca de orden ni de contenido.

Correspondencia con los campos de la aplicación
-----------------------------------------------
    Matriz                                  Campo del oficio
    --------------------------------------- ----------------------
    Institución del Estado                   institucion (fija la sigla de la
                                             Referencia UDC, que genera el
                                             sistema)
    Prioridad                                prioridad
    Apellidos, Nombres - Razón Social        )
    TiPASo Id / Identificación               ) implicados (uno por fila del
    Tipo de Implicado / LCI                  ) mismo oficio)
    Tipo de Accion                           tipo_accion
    Referencia - Oficio FGE; Juzgado...      codigo_oficio (Referencia oficio)
    Delito                                   causal_oficio
    Fecha Circular                           fecha_oficio
    Fecha Emisión                            fecha_recepcion
    Fecha Asignación                         fecha_asignacion
    Fecha Envío                              fecha_respuesta
    Usuario                                  responsable
    Estado                                   estado
    Observación                              observacion
    (nº de filas con la misma Ref. oficio)   cantidad_investigados

Las columnas restantes de la matriz (Mes, Medio Respuesta, Días,
Canal Recepción, Expediente Fiscal, la Referencia de la circular de la
Superintendencia y el bloque RCSA) no tienen equivalente en la aplicación y se
ignoran; la carga informa de ello.

La Referencia UDC NO viene en el archivo: la genera el sistema al importar, con
la nomenclatura que corresponda a la institución de cada fila.

Varias filas con la misma Referencia oficio se entienden como el mismo oficio
con varios investigados: se agrupan en un solo registro, cada fila aporta un
implicado y la cantidad de investigados es el número de implicados.
"""
import csv
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from configuracion import ESTADOS, INSTITUCIONES

# Fila de la cabecera y primera fila de datos en la matriz de Excel.
FILA_CABECERA = 4
PRIMERA_FILA_DATOS = FILA_CABECERA + 1

# FORMATO ESTABLECIDO de la matriz: las 26 columnas de la B a la AA, EN ESTE
# ORDEN. El archivo que se cargue tiene que respetarlo; si no, se rechaza
# indicando qué columna no cuadra.
#
# Cada entrada es (nombre que se muestra, texto por el que se reconoce, campo
# del oficio). El reconocimiento se hace sobre el encabezado normalizado (sin
# tildes, en minúsculas y con los espacios colapsados) y basta con que EMPIECE
# por ese texto, para que encajen los títulos largos repartidos en varias
# líneas ("Referencia - Oficio\nFGE; Juzgado, Tribunal"). Un campo en None es
# una columna de la matriz que la aplicación no guarda.
CABECERA_MATRIZ = [
    ("Institución del Estado",              "institucion",            "institucion"),
    ("Mes",                                 "mes",                    None),
    ("Fecha Asignación",                    "fecha asignacion",       "fecha_asignacion"),
    ("Usuario",                             "usuario",                "empleado"),
    ("Prioridad",                           "prioridad",              "prioridad"),
    ("Fecha Emisión",                       "fecha emision",          "fecha_recepcion"),
    ("Referencia",                          "referencia",             None),
    ("Medio Repuesta",                      "medio repuesta",         None),
    ("Fecha Envío",                         "fecha envio",            "fecha_respuesta"),
    ("Estado",                              "estado",                 "estado"),
    ("Días",                                "dias",                   None),
    ("Canal Recepc",                        "canal recepc",           None),
    ("Fecha Circular",                      "fecha circular",         "fecha_oficio"),
    ("Apellidos, Nombres - Razón Social",   "apellidos",              "implicado_nombre"),
    ("TiPASo Id CED; PAS; RUCUC",           "tipaso id",              "implicado_tipo_id"),
    ("Identificación Ced; Pas; RUC",        "identificacion",         "implicado_identificacion"),
    ("Referencia - Oficio FGE; Juzgado",    "referencia - oficio",    "codigo_oficio"),
    ("Número Expediente Fiscal",            "numero expediente",      None),
    ("Referencia - Circular Superintendencia Bancos",
                                            "referencia - circular",  None),
    ("Delito",                              "delito",                 "causal_oficio"),
    ("Tipo de Accion",                      "tipo de accion",         "tipo_accion"),
    ("Observación",                         "observacion",            "observacion"),
    ("Tipo de Implicado",                   "tipo de implicado",      "implicado_tipo"),
    ("LCI - SI o NO",                       "lci",                    "implicado_lci"),
    ("Fecha - Solicitud",                   "fecha - solicitud",      None),
    ("Ref Solic- No. LCI-202X-000",         "ref solic",              None),
]

# Primera columna de la matriz (la A queda vacía) y última.
PRIMERA_COLUMNA = "B"
ULTIMA_COLUMNA = "AA"

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


# --- Validación del formato --------------------------------------------------
def _letra_columna(posicion: int) -> str:
    """Letra de la columna de Excel para la posición indicada (0 -> 'B')."""
    numero = posicion + 2                      # la matriz empieza en la B
    letras = ""
    while numero:
        numero, resto = divmod(numero - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def _recortar(celdas: List) -> Tuple[List[str], List[str], int]:
    """Encabezados de la fila sin las columnas vacías de los extremos.

    Devuelve (normalizados, tal como vienen, desplazamiento inicial). Los
    normalizados sirven para comparar y los originales para los mensajes, que
    así muestran el texto exacto que tiene el archivo. El desplazamiento
    recoge la columna A de la matriz, que va vacía.
    """
    titulos = [normalizar(c) for c in celdas]
    originales = [" ".join(str(c).split()) if c is not None else "" for c in celdas]
    inicio = 0
    while inicio < len(titulos) and not titulos[inicio]:
        inicio += 1
    fin = len(titulos)
    while fin > inicio and not titulos[fin - 1]:
        fin -= 1
    return titulos[inicio:fin], originales[inicio:fin], inicio


def coincidencias(celdas: List) -> int:
    """Cuántas columnas de la fila encajan, en su posición, con el formato."""
    titulos, _originales, _inicio = _recortar(celdas)
    return sum(1 for posicion, (_, prefijo, _campo) in enumerate(CABECERA_MATRIZ)
               if posicion < len(titulos) and titulos[posicion].startswith(prefijo))


def validar_cabecera(celdas: List) -> int:
    """Comprueba que la fila sea la cabecera del formato establecido.

    El orden de las columnas IMPORTA: se exige la secuencia completa de la B a
    la AA. Devuelve el desplazamiento con el que empiezan las columnas dentro de
    la fila; si el archivo no cumple, lanza un ValueError explicando qué falla.
    """
    titulos, originales, inicio = _recortar(celdas)
    problemas = []
    for posicion, (nombre, prefijo, _campo) in enumerate(CABECERA_MATRIZ):
        letra = _letra_columna(posicion)
        if posicion >= len(titulos):
            problemas.append(f"falta la columna {letra} «{nombre}»")
        elif not titulos[posicion].startswith(prefijo):
            encontrado = originales[posicion][:40] or "(vacía)"
            problemas.append(
                f"la columna {letra} debería ser «{nombre}» y contiene "
                f"«{encontrado}»")
    sobran = len(titulos) - len(CABECERA_MATRIZ)
    if sobran > 0:
        problemas.append(
            f"hay {sobran} columna(s) de más después de la {ULTIMA_COLUMNA}")

    if problemas:
        detalle = "\n".join(f"  · {p}" for p in problemas[:8])
        if len(problemas) > 8:
            detalle += f"\n  · … y {len(problemas) - 8} diferencia(s) más"
        raise ValueError(
            "El archivo no tiene el formato establecido.\n\n"
            f"La cabecera debe ocupar la fila {FILA_CABECERA}, de la columna "
            f"{PRIMERA_COLUMNA} a la {ULTIMA_COLUMNA}, con las "
            f"{len(CABECERA_MATRIZ)} columnas en su orden.\n\n"
            f"Diferencias encontradas:\n{detalle}\n\n"
            "Suba el archivo con el formato establecido."
        )
    return inicio


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
        raise ValueError(
            "El archivo no tiene el formato establecido: se esperaba la "
            f"cabecera en la fila {FILA_CABECERA} y el archivo solo tiene "
            f"{len(filas)} fila(s).\n\nSuba el archivo con el formato "
            "establecido."
        )
    return filas[FILA_CABECERA - 1:], []


def _leer_csv(ruta: Path) -> Tuple[List[List], List[str]]:
    """Lee un CSV detectando el separador (barra vertical, punto y coma o coma).

    La cabecera se busca en las primeras filas, porque un CSV exportado desde la
    matriz puede arrastrar las filas de rótulos que van encima. Se elige la fila
    que MÁS se parezca al formato establecido; si ninguna encaja del todo, la
    validación posterior explica en qué se diferencia.
    """
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        muestra = archivo.read(8192)
        archivo.seek(0)
        separador = max("|;,\t", key=muestra.count)
        filas = [f for f in csv.reader(archivo, delimiter=separador)]
    filas = [f for f in filas if any(_a_texto(c) for c in f)]
    if not filas:
        raise ValueError("El archivo está vacío.")
    candidatas = filas[:FILA_CABECERA + 4]
    mejor = max(range(len(candidatas)), key=lambda i: coincidencias(candidatas[i]))
    return filas[mejor:], []


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

    # El formato es fijo: se comprueba que estén TODAS las columnas y en su
    # orden antes de leer un solo dato.
    cabecera = crudas[0]
    inicio = validar_cabecera(cabecera)
    # Ya validado el orden, cada campo se toma por su posición.
    mapa = {inicio + posicion: campo
            for posicion, (_nombre, _prefijo, campo) in enumerate(CABECERA_MATRIZ)
            if campo}
    ignoradas = [nombre for nombre, _prefijo, campo in CABECERA_MATRIZ if not campo]

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
        # Una fila sin referencia de oficio ni institución es una fila en
        # blanco del final.
        if not datos.get("codigo_oficio") and not datos.get("institucion"):
            continue
        if problema:
            errores.append(problema)
            continue
        datos["estado"] = ESTADOS_EQUIVALENTES.get(
            normalizar(datos.get("estado")), datos.get("estado") or "")
        filas.append(datos)
    return filas, ignoradas, errores


# --- Agrupación y preparación ------------------------------------------------
# La matriz abrevia; la aplicación guarda el nombre completo del catálogo.
_TIPOS_IDENTIFICACION = {
    "ced": "Cédula", "cedula": "Cédula", "c.c": "Cédula", "cc": "Cédula",
    "pas": "Pasaporte", "pasaporte": "Pasaporte",
    "ruc": "RUC", "rucuc": "RUC",
}
_TIPOS_IMPLICADO = {
    "cliente": "Cliente",
    "no cliente": "No cliente", "nocliente": "No cliente",
    "ex cliente": "Ex cliente", "excliente": "Ex cliente",
    "sin identificacion": "Sin identificación",
    "sin identificar": "Sin identificación",
}


def _implicado_de(fila: Dict, no_validas: Optional[set] = None) -> Optional[Dict]:
    """Construye el implicado de una fila de la matriz, o None si no trae uno.

    Lo que no se reconoce no tumba la carga: es un histórico, y perder el
    oficio entero por un «Tipo de Implicado» mal escrito sería peor que
    anotarlo como «Sin identificación». Los valores que no encajen se informan
    en la vista previa para que alguien los revise después.

    Lo mismo vale para la identificación: si no cumple lo que exige su tipo
    —10 dígitos la cédula, 13 el RUC, letras y números el pasaporte— la
    persona entra SIN identificación en lugar de rechazar el oficio, y el
    documento se anota en `no_validas` para poder corregirlo luego.
    """
    nombre = (fila.get("implicado_nombre") or "").strip()
    if len(nombre) < 3:
        return None
    tipo_id = _TIPOS_IDENTIFICACION.get(normalizar(fila.get("implicado_tipo_id")), "")
    # Sin tipo reconocido no se puede guardar la identificación: el alta exige
    # decir de qué documento se trata.
    identificacion = (fila.get("implicado_identificacion") or "").strip() \
        if tipo_id else ""
    if identificacion:
        # Import diferido: la regla vive donde se validan los oficios.
        import almacen_oficios
        try:
            identificacion = almacen_oficios.validar_identificacion(
                tipo_id, identificacion)
        except ValueError:
            if no_validas is not None:
                no_validas.add(f"{tipo_id} {identificacion}")
            tipo_id, identificacion = "", ""
    return {
        "nombre": nombre,
        "tipo_identificacion": tipo_id,
        "identificacion": identificacion,
        "tipo_implicado": _TIPOS_IMPLICADO.get(
            normalizar(fila.get("implicado_tipo")), "Sin identificación"),
        "lci": "Sí" if normalizar(fila.get("implicado_lci")) in ("si", "s", "x")
               else "No",
    }


def agrupar_por_referencia(filas: List[Dict],
                           no_validas: Optional[set] = None) -> List[Dict]:
    """Une las filas que comparten Referencia oficio en un solo oficio.

    En la matriz cada fila es un investigado, así que un mismo requerimiento
    puede ocupar varias. Se conserva la primera fila y la cantidad de
    investigados pasa a ser el número de filas agrupadas.

    Se agrupa por Referencia oficio porque la Referencia UDC ya no viene en el
    archivo: la genera el sistema al importar.
    """
    agrupados: Dict[str, Dict] = {}
    orden: List[str] = []
    for fila in filas:
        clave = (fila.get("codigo_oficio") or f"__fila_{fila['_fila']}").strip().upper()
        implicado = _implicado_de(fila, no_validas)
        if clave not in agrupados:
            copia = dict(fila)
            copia["cantidad_investigados"] = 1
            copia["implicados"] = [implicado] if implicado else []
            agrupados[clave] = copia
            orden.append(clave)
        else:
            agrupados[clave]["cantidad_investigados"] += 1
            if implicado:
                agrupados[clave].setdefault("implicados", []).append(implicado)
            # Se completa lo que la primera fila hubiera dejado en blanco.
            for campo, valor in fila.items():
                if (campo not in ("_fila", "implicados") and valor
                        and not agrupados[clave].get(campo)):
                    agrupados[clave][campo] = valor
    # Con detalle anotado, la cantidad de investigados la cuenta el detalle.
    for oficio in agrupados.values():
        if oficio.get("implicados"):
            oficio["cantidad_investigados"] = len(oficio["implicados"])
    return [agrupados[c] for c in orden]


def _claves_de(nombre: str, cuenta: str):
    """Formas con las que se puede nombrar a una persona en la matriz.

    La matriz la anota como "C. Roman": la inicial del primer nombre y UNO de
    sus apellidos. Como no se sabe cuál de las palabras del nombre completo es
    el apellido que usaron, se generan todas las combinaciones posibles de
    inicial + cada una de las palabras siguientes:

        "Camila Maria Roman Townsed"  ->  c. maria / c. roman / c. townsed
                                          (y las mismas sin el punto)

    Así "C. Roman" encaja con Camila Maria Roman Townsed, "J. Portero" con Joel
    Tyrone Portero Cervantes y "J. Rosero" con Juan Pablo Rosero Rodríguez.
    """
    claves = set()
    if cuenta:
        claves.add(normalizar(cuenta))
    nombre = normalizar(nombre)
    if not nombre:
        return claves
    claves.add(nombre)
    partes = nombre.split()
    if len(partes) >= 2:
        inicial = partes[0][0]
        for palabra in partes[1:]:
            claves.add(f"{inicial}. {palabra}")
            claves.add(f"{inicial} {palabra}")
        # "Roman Townsed", "Camila Roman"... por si la matriz usa dos palabras.
        claves.add(f"{partes[0]} {partes[-1]}")
        claves.add(" ".join(partes[-2:]))
    return claves


def emparejar_responsables(filas: List[Dict], usuarios: List[Dict]) -> Dict:
    """Traduce la columna "Usuario" de la matriz a cuentas del sistema.

    Se prueba con el nombre de cuenta, el nombre completo y la forma
    "inicial. apellido" contra CUALQUIERA de los apellidos de la persona (ver
    `_claves_de`).

    Si una misma forma apunta a dos personas distintas (dos "J. Rosero", por
    ejemplo) se considera AMBIGUA y no se empareja: es preferible dejar el
    oficio por asignar que atribuírselo a quien no fue.

    Lo que no se consigue emparejar se deja SIN responsable; de eso se encarga
    `preparar`, que además lo pone en "Por asignar". Devuelve un diccionario con
    los nombres no reconocidos y los ambiguos, para poder informarlos.
    """
    indice: Dict[str, Optional[Dict]] = {}
    for usuario in usuarios:
        for clave in _claves_de(usuario.get("nombre", ""), usuario["usuario"]):
            if clave in indice and indice[clave] is not usuario:
                indice[clave] = None          # ambigua: apunta a más de uno
            else:
                indice.setdefault(clave, usuario)

    sin_identificar, ambiguos = [], []
    for fila in filas:
        original = fila.get("empleado", "")
        buscado = normalizar(original)
        fila["id_empleado"] = ""
        if not buscado:
            fila["empleado"] = ""
            continue
        # Se prueba tal cual y sin el punto de la inicial ("J Rosero").
        encontrado = indice.get(buscado, "sin clave")
        if encontrado == "sin clave":
            encontrado = indice.get(" ".join(buscado.replace(".", " ").split()),
                                    "sin clave")
        if encontrado not in (None, "sin clave"):
            fila["id_empleado"] = encontrado["usuario"]
            fila["empleado"] = encontrado["nombre"]
        else:
            (ambiguos if encontrado is None else sin_identificar).append(original)
            fila["empleado"] = ""
    return {"sin_identificar": sorted(set(sin_identificar)),
            "ambiguos": sorted(set(ambiguos))}


# Formas habituales de nombrar a cada institución en la matriz, además de su
# nombre completo y su sigla.
_SINONIMOS_INSTITUCION = {
    "superintendencia de bancos": "Superintendencia de Bancos",
    "superintendencia": "Superintendencia de Bancos",
    "sb": "Superintendencia de Bancos",
    "sbs": "Superintendencia de Bancos",
    "fiscalia general del estado": "Fiscalía General del Estado",
    "fiscalia": "Fiscalía General del Estado",
    "fge": "Fiscalía General del Estado",
}


def _reconocer_institucion(valor: str) -> str:
    """Nombre normalizado de la institución, o '' si no se reconoce."""
    clave = normalizar(valor)
    if not clave:
        return ""
    if clave in _SINONIMOS_INSTITUCION:
        return _SINONIMOS_INSTITUCION[clave]
    for nombre in INSTITUCIONES:
        if clave == normalizar(nombre):
            return nombre
    return ""


def _reconocer_tipo_accion(valor: str, catalogo: List[str]) -> str:
    """Tipo de acción del catálogo que corresponde al texto de la matriz.

    La matriz los escribe en mayúsculas y a veces con más palabras
    ("LEVANTAMIENTO DE MEDIDAS"), así que además de la coincidencia exacta se
    admite que el texto EMPIECE por un tipo del catálogo. Devuelve '' si no se
    reconoce.
    """
    clave = normalizar(valor)
    if not clave:
        return ""
    for tipo in catalogo:
        if clave == normalizar(tipo):
            return tipo
    # "levantamiento de medidas" -> "Levantamiento"
    candidatos = [t for t in catalogo if clave.startswith(normalizar(t))]
    if len(candidatos) == 1:
        return candidatos[0]
    return ""


def preparar(ruta, usuarios: List[Dict]) -> Dict:
    """Deja las filas listas para importar y resume lo que se va a hacer."""
    filas, ignoradas, errores = leer_archivo(ruta)
    identificaciones_no_validas = set()
    filas = agrupar_por_referencia(filas, identificaciones_no_validas)
    emparejados = emparejar_responsables(filas, usuarios)

    # La institución decide la nomenclatura de la Referencia UDC y el tipo de
    # acción es obligatorio, así que ambos se traducen aquí y lo que no se
    # reconozca se informa: son filas que no se podrán importar.
    import tipos_accion
    catalogo = tipos_accion.listar()
    instituciones_desconocidas, tipos_desconocidos = set(), set()
    for fila in filas:
        original = fila.get("institucion", "")
        fila["institucion"] = _reconocer_institucion(original)
        if not fila["institucion"]:
            instituciones_desconocidas.add(original or "(vacía)")
        original = fila.get("tipo_accion", "")
        fila["tipo_accion"] = _reconocer_tipo_accion(original, catalogo)
        if not fila["tipo_accion"]:
            tipos_desconocidos.add(original or "(vacío)")

    sin_estado_original = 0
    for fila in filas:
        if not fila.get("empleado"):
            # Sin responsable identificado el oficio entra POR ASIGNAR, sea
            # cual sea el estado que traiga el archivo. Se retira también la
            # fecha de respuesta: las reglas del sistema no admiten un oficio
            # respondido sin nadie a cargo, y con ella puesta el estado saltaría
            # a "Finalizado". Quien lo asigne la vuelve a poner.
            if fila.get("estado") != "Por asignar" or fila.get("fecha_respuesta"):
                sin_estado_original += 1
            fila["estado"] = "Por asignar"
            fila["fecha_respuesta"] = ""
        elif fila.get("estado") not in ESTADOS:
            fila["estado"] = "En proceso"
    return {
        "filas": filas,
        "columnas_ignoradas": ignoradas,
        "errores": errores,
        "responsables_sin_identificar": emparejados["sin_identificar"],
        "responsables_ambiguos": emparejados["ambiguos"],
        "puestos_por_asignar": sin_estado_original,
        "instituciones_desconocidas": sorted(instituciones_desconocidas),
        "tipos_accion_desconocidos": sorted(tipos_desconocidos),
        "identificaciones_no_validas": sorted(identificaciones_no_validas),
    }
