"""
Genera el archivo de datos de prueba para la carga masiva.

Crea `Matriz de prueba - 110 oficios.xlsx` con el formato que exige la
importación —el de la exportación, sin la columna Referencia UDC, que la numera
el sistema— y 110 oficios repartidos entre las dos instituciones.

Los datos se reparten a propósito para que el TABLERO se vea con contenido:

- **Fechas de recepción** repartidas por los últimos seis meses, con un grupo
  reciente en las dos últimas semanas y alguno de hoy mismo, para que los
  gráficos por día y por mes no salgan vacíos.
- **Responsables** con cargas distintas, de modo que el gráfico por responsable
  tenga barras de tamaños diferentes; unos pocos oficios entran sin responsable.
- **Estados** mezclados: mayoría finalizados, varios en proceso y algunos por
  asignar.
- **Tiempos de respuesta** variados, para que el promedio de días sea
  representativo.
- **Implicados**: cada oficio investiga a un número distinto de personas, de
  una sola a ocho, y de cada una se anota nombre, identificación, tipo de
  implicado y LCI. Como el archivo dedica una fila a cada persona, tiene
  bastantes más filas que oficios.

    python datos_de_prueba/generar_datos_prueba.py

Los responsables se indican con su NOMBRE DE CUENTA (cmroman, jportero…), que
tiene que existir en el sistema antes de cargar el archivo.

No forma parte de la aplicación: es una utilidad para preparar una demostración
o para probar la carga masiva sin arriesgar datos reales.
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import carga_masiva                                       # noqa: E402

SALIDA = Path(__file__).resolve().parent / "Matriz de prueba - 110 oficios.xlsx"
CANTIDAD_OFICIOS = 110

INSTITUCIONES = ["Superintendencia de Bancos", "Fiscalía General del Estado"]

# Cuentas de la unidad, por su nombre de usuario. Son cuentas con rol
# "usuario": los oficios se asignan a quien los tramita, no a quien administra
# el sistema. La cadena vacía es el oficio que llega sin responsable, que entra
# como "Por asignar".
#
# Cuántos oficios lleva cada uno (suman CANTIDAD_OFICIOS), para que el gráfico
# por responsable tenga barras claramente distintas.
CARGA_POR_USUARIO = {
    "cmroman": 30,
    "jportero": 26,
    "dtfranco": 22,
    "lgjarrin": 18,
    "": 14,                # oficios que llegan sin responsable
}

# Nombre completo de cada cuenta. Es informativo: al importar, el nombre se
# toma de la cuenta del sistema.
NOMBRES = {
    "cmroman": "Camila Maria Roman Townsed",
    "jportero": "Joel Tyrone Portero Cervantes",
    "dtfranco": "Damara Tais Franco Pacheco",
    "lgjarrin": "Lizzi Gabriela Jarrin Aguilar",
}

TIPOS_ACCION = ["Certificación", "Retención", "Información", "Inmovilización",
                "Levantamiento", "Bloqueo y retención", "Rectificación"]

DELITOS = [
    "TRAFICO ILÍCITO DE SUSTANCIAS CATALOGADAS SUJETAS A FISCALIZACIÓN",
    "LAVADO DE ACTIVOS", "COHECHO", "PECULADO", "ENRIQUECIMIENTO ILÍCITO",
    "DEFRAUDACIÓN TRIBUTARIA", "ESTAFA", "DESAPARICIÓN INVOLUNTARIA",
]

# Personas investigadas. El archivo dedica una fila a cada una, así que un
# oficio con cuatro implicados ocupa cuatro filas.
INVESTIGADOS = [
    "ORDOÑEZ VILLAGOMEZ DAVID MIGUEL", "ENOMENGA VARGAS ERICK LENIN",
    "BOLAÑOS RUBIO MARCO OLGER", "ACOSTA JEREZ DIANA CAROLINA",
    "MENDOZA SALAS LUIS ALBERTO", "PARRA NUÑEZ SOFIA ELENA",
    "CEVALLOS MORA JORGE ANDRÉS", "TAPIA LEÓN MARIA FERNANDA",
    "QUISPE ANDRADE PEDRO JOSÉ", "VILLACÍS ROJAS ANDREA PAOLA",
    "ZAMBRANO LOOR KEVIN DANIEL", "INTRIAGO CEDEÑO GLORIA ISABEL",
    "MACÍAS PALACIOS BYRON EDUARDO", "SUÁREZ VERA NATALIA CRISTINA",
    "CHÁVEZ ARIAS RAMIRO ANTONIO", "GUERRERO PINTO LUCÍA BELÉN",
    "COMERCIAL LOS ANDES S.A.", "IMPORTADORA DEL PACÍFICO CÍA. LTDA.",
    "AGRÍCOLA SANTA RITA S.A.", "TRANSPORTES DEL LITORAL CÍA. LTDA.",
]

# Cuántas personas investiga cada oficio. Se recorre en orden para que el
# archivo tenga de todo: oficios de una sola persona y otros de hasta ocho.
PATRON_INVESTIGADOS = [1, 1, 2, 1, 3, 1, 1, 4, 2, 1, 5, 1, 2, 1, 6,
                       3, 1, 2, 1, 8, 1, 1, 2, 7, 1, 3, 1, 1, 2, 1]

TIPOS_IDENTIFICACION = ["Cédula", "Pasaporte", "RUC"]
TIPOS_IMPLICADO = ["Cliente", "Ex cliente", "No cliente", "Sin identificación"]


def _identificacion(tipo, aleatorio):
    """Documento con el formato que exige cada tipo.

    La aplicación valida la cédula con 10 dígitos, el RUC con 13 y el pasaporte
    con letras y números, así que el archivo de prueba los genera ya válidos.
    """
    if tipo == "Cédula":
        return str(aleatorio.randint(10 ** 9, 10 ** 10 - 1))
    if tipo == "RUC":
        # Los RUC de persona natural son la cédula seguida de "001".
        return f"{aleatorio.randint(10 ** 9, 10 ** 10 - 1)}001"
    letras = "".join(aleatorio.choice("ABCDEFGHJKLMNPRSTUVWXYZ") for _ in range(2))
    return f"{letras}{aleatorio.randint(100000, 999999)}"


# Cómo se reparten las fechas de recepción, para que los gráficos del tablero
# tengan altibajos en vez de una línea plana.
#
# Días hacia atrás de los oficios recientes (0 = hoy). El gráfico por día cubre
# las dos últimas semanas: se repiten unos días y se saltan otros a propósito.
DIAS_RECIENTES = [0, 0, 0, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 6, 6,
                  6, 7, 7, 8, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 13, 13]

# Cuántos oficios llegaron en cada mes anterior, del más reciente al más
# antiguo. Suman el resto de los oficios.
REPARTO_MESES = [20, 9, 16, 11, 18]


def _mes_atras(fecha, meses):
    """(año, mes) de la fecha indicada retrocediendo esa cantidad de meses."""
    mes = fecha.month - meses
    return fecha.year + (mes - 1) // 12, (mes - 1) % 12 + 1


def _fechas_recepcion(cantidad, hoy):
    """Fecha de recepción de cada oficio, repartida según los dos patrones."""
    fechas = [hoy - timedelta(days=dias) for dias in DIAS_RECIENTES]
    restantes = cantidad - len(fechas)
    for meses, cuantos in enumerate(REPARTO_MESES, start=1):
        anio, mes = _mes_atras(hoy, meses)
        for indice in range(min(cuantos, restantes)):
            # Días del 1 al 28: cualquier mes los tiene.
            fechas.append(date(anio, mes, 1 + indice * 27 // max(cuantos - 1, 1)))
        restantes -= cuantos
        if restantes <= 0:
            break
    # Si el reparto no llegó a cubrirlos todos, el resto va al mes más antiguo.
    while len(fechas) < cantidad:
        anio, mes = _mes_atras(hoy, len(REPARTO_MESES))
        fechas.append(date(anio, mes, 1 + len(fechas) % 28))
    return fechas[:cantidad]


def generar_oficios():
    """Los oficios con la forma con la que los guarda el sistema.

    De ahí los escribe `carga_masiva.escribir_plantilla` en el formato que esa
    misma carga espera leer.
    """
    random.seed(2026)          # mismo archivo en cada ejecución
    hoy = date.today()
    fechas = _fechas_recepcion(CANTIDAD_OFICIOS, hoy)
    # Se reparten al azar para que la carga de cada persona no quede pegada a
    # un tramo de fechas concreto.
    responsables = [usuario
                    for usuario, cantidad in CARGA_POR_USUARIO.items()
                    for _ in range(cantidad)]
    random.shuffle(responsables)

    oficios = []
    for numero in range(1, CANTIDAD_OFICIOS + 1):
        institucion = INSTITUCIONES[numero % 2]      # mitad y mitad
        sigla = "SB" if institucion.startswith("Super") else "FGE"

        recepcion = fechas[numero - 1]
        oficio = recepcion - timedelta(days=random.randint(1, 20))
        usuario = responsables[numero - 1]
        # Ninguna fecha puede ser futura: la aplicación las rechaza.
        asignacion = (min(recepcion + timedelta(days=random.randint(0, 3)), hoy)
                      if usuario else None)

        # Lo recién llegado suele estar en proceso y lo antiguo ya respondido,
        # que es como se ve una carga real.
        antiguo = (hoy - recepcion).days > 20
        respuesta = None
        if usuario and (antiguo or numero % 4 == 0):
            # Tiempos de respuesta variados: de 1 a 30 días.
            respuesta = asignacion + timedelta(days=1 + (numero * 7) % 30)
            if respuesta > hoy:
                respuesta = None
        # Sin responsable el oficio queda "Por asignar", sin asignación ni
        # respuesta: son las reglas que valida la propia carga.
        estado = ("Finalizado" if respuesta else
                  "En proceso" if usuario else "Por asignar")

        cuantos = PATRON_INVESTIGADOS[(numero - 1) % len(PATRON_INVESTIGADOS)]
        implicados = []
        for persona in random.sample(INVESTIGADOS, cuantos):
            # Las empresas se identifican con RUC; las personas, con cualquiera
            # de los tres documentos.
            tipo_id = ("RUC" if persona.endswith(("S.A.", "LTDA."))
                       else random.choice(TIPOS_IDENTIFICACION))
            implicados.append({
                "nombre": persona,
                "tipo_identificacion": tipo_id,
                "identificacion": _identificacion(tipo_id, random),
                "tipo_implicado": random.choice(TIPOS_IMPLICADO),
                "lci": random.choice(["Sí", "No", "No"]),
            })

        oficios.append({
            "institucion": institucion,
            "codigo_oficio": f"{sigla}-{recepcion.year}-{numero:04d}-OF",
            "tipo_accion": TIPOS_ACCION[numero % len(TIPOS_ACCION)],
            "causal_oficio": DELITOS[numero % len(DELITOS)],
            "fecha_oficio": oficio.isoformat(),
            "fecha_recepcion": recepcion.isoformat(),
            "fecha_asignacion": asignacion.isoformat() if asignacion else "",
            "fecha_respuesta": respuesta.isoformat() if respuesta else "",
            "cantidad_investigados": str(len(implicados)),
            "prioridad": random.choice(["Alta", "Media", "Baja"]),
            "id_empleado": usuario,
            "empleado": NOMBRES.get(usuario, ""),
            "estado": estado,
            "archivo_oficio": "",
            "archivo_respuesta": "",
            "observacion": random.choice(
                ["", "", "Atendido dentro del plazo", "Requiere seguimiento",
                 "Se remitió por correo"]),
            "registrado_por": "",
            "fecha_registro": "",
            "origen": "",
            "anulado": "",
            "motivo_anulacion": "",
            "implicados": implicados,
        })
    return oficios


def _resumen(oficios):
    """Cómo quedó repartido lo generado (para verlo al ejecutar el script)."""
    from collections import Counter
    estados = Counter(o["estado"] for o in oficios)
    usuarios = Counter(o["id_empleado"] or "(sin responsable)" for o in oficios)
    entidades = Counter(o["institucion"] for o in oficios)
    reparto = Counter(len(o["implicados"]) for o in oficios)
    return estados, usuarios, entidades, reparto


if __name__ == "__main__":
    oficios = generar_oficios()
    # Lo escribe el propio módulo de la carga: los datos de prueba y el
    # formato real no pueden separarse.
    carga_masiva.escribir_plantilla(oficios, str(SALIDA))
    estados, usuarios, entidades, reparto = _resumen(oficios)
    filas = sum(max(len(o["implicados"]), 1) for o in oficios)
    print(f"{SALIDA.name}: {len(oficios)} oficios en {filas} filas "
          f"(una por persona investigada).")
    print("  Estados:      " + ", ".join(f"{k}: {v}" for k, v in estados.items()))
    print("  Instituciones:" + ", ".join(f" {k}: {v}" for k, v in entidades.items()))
    print("  Responsables: " + ", ".join(f"{k}: {v}"
                                         for k, v in usuarios.most_common()))
    print("  Implicados:   " + ", ".join(
        f"{cuantos} implicado(s): {cuantos_oficios} oficio(s)"
        for cuantos, cuantos_oficios in sorted(reparto.items())))
