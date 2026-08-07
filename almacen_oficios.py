"""
Capa de almacenamiento de OFICIOS.

*** Punto clave de arquitectura ***
Toda la app (interfaz y métricas) habla SOLO con las funciones de este módulo.
El día que migres a SQLite o a un motor SQL (ver README), reescribes el
cuerpo de estas funciones y NO tocas la interfaz ni las métricas.

Formato: oficios.dat cifrado con Fernet; internamente una lista JSON.
La Referencia oficio (campo 'codigo_oficio') se mapea a una Referencia UDC:
    REQ-INF-AAAA-NNNN   (NNNN = secuencial de 4 dígitos, desde 0001)
El secuencial es POR AÑO y arranca desde el último valor registrado en el Excel
anterior, que el superusuario configura una sola vez (ver el módulo parametros).
"""
import csv
import json
import shutil
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

from cryptography.fernet import InvalidToken

from configuracion import (
    ARCHIVO_OFICIOS, PREFIJO_REFERENCIA, ESTADOS, ROLES_GESTORES, DIR_RESPUESTAS,
    DIR_DOCUMENTOS, EXTENSIONES_DOCUMENTO, ROL_ADMINISTRADOR, ROL_SUPERUSUARIO,
)
from cifrado import cifrar, descifrar
import registro_actividad
import permisos
import parametros
import bloqueo


# --- Persistencia ------------------------------------------------------------
def _leer_registros() -> List[Dict]:
    if not ARCHIVO_OFICIOS.exists():
        return []
    try:
        return json.loads(descifrar(ARCHIVO_OFICIOS.read_bytes()))
    except InvalidToken:
        raise ValueError(
            "El archivo de oficios fue alterado o la clave no coincide."
        )


def _guardar_registros(registros: List[Dict]) -> None:
    permisos.escribir_bytes_protegido(
        ARCHIVO_OFICIOS,
        cifrar(json.dumps(registros, ensure_ascii=False, indent=2)),
    )


# --- Validaciones y referencia ----------------------------------------------
def _validar_fecha(texto: str, campo: str) -> str:
    """Valida el formato y que la fecha no sea futura: no se puede registrar
    algo que todavía no ha ocurrido."""
    try:
        valor = datetime.strptime(texto, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"{campo} debe tener formato AAAA-MM-DD.")
    if valor > date.today():
        raise ValueError(f"{campo} no puede ser posterior a hoy.")
    return texto


def _generar_referencia(registros: List[Dict], anio: int = None) -> str:
    """Genera la Referencia UDC:  REQ-INF-<año>-<secuencial de 4 dígitos>.

    El secuencial es **por año** (vuelve a 0001 cada año) y arranca desde el
    último registrado en el Excel anterior, que el superusuario configura una
    sola vez (ver `parametros`).

    Se usa max(secuencial configurado, mayor secuencial existente) + 1, de modo
    que nunca se genera una referencia duplicada aunque se reconfigure el valor
    inicial o queden huecos en la numeración.
    """
    anio = anio or date.today().year
    prefijo_anio = f"{PREFIJO_REFERENCIA}-{anio:04d}-"
    secuencial_max = parametros.obtener_secuencial_inicial(anio)
    for registro in registros:
        referencia = registro.get("referencia", "")
        if referencia.startswith(prefijo_anio):
            try:
                secuencial_max = max(secuencial_max, int(referencia.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefijo_anio}{secuencial_max + 1:04d}"          # primero -> 0001


# --- Reglas de negocio: relación responsable / estado -----------------------
def _resolver_estado(nombre_empleado: str, estado: str,
                     fecha_respuesta: str = "") -> str:
    """Aplica las reglas de negocio entre responsable, fecha de respuesta y
    estado.

    - Con fecha de respuesta: el oficio ya fue respondido, así que el estado es
      siempre "Finalizado" (y exige responsable).
    - Sin responsable: el único estado válido es "Por asignar". Si se pidió
      "En proceso" o "Finalizado" se lanza un error (esos estados exigen
      responsable).
    - Con responsable: no puede quedar en "Por asignar"; al asignar un
      responsable el oficio pasa automáticamente a "En proceso". Si el estado
      pedido es "En proceso" o "Finalizado" se respeta.
    Devuelve el estado ya corregido.
    """
    tiene_responsable = bool((nombre_empleado or "").strip())
    if (fecha_respuesta or "").strip():
        # Si ya hay respuesta, el oficio está finalizado.
        if not tiene_responsable:
            raise ValueError(
                "Para registrar una fecha de respuesta debe asignar un "
                "responsable (el oficio pasa a \"Finalizado\")."
            )
        return "Finalizado"
    if not tiene_responsable:
        if estado in ("En proceso", "Finalizado"):
            raise ValueError(
                f"El estado \"{estado}\" requiere un responsable asignado."
            )
        return "Por asignar"
    # Con responsable asignado
    if estado == "Por asignar":
        return "En proceso"
    return estado


def _rol_de(usuario: str) -> str:
    """Rol del usuario indicado, o '' si no existe."""
    if not (usuario or "").strip():
        return ""
    # Import diferido: `autenticacion` no depende de este módulo, pero así se
    # mantiene la dependencia acotada a esta comprobación.
    import autenticacion
    objetivo = (usuario or "").strip().lower()
    for registro in autenticacion.listar_usuarios():
        if registro["usuario"].strip().lower() == objetivo:
            return registro.get("rol", "")
    return ""


def _validar_asignacion(id_empleado: str, actor_rol: str) -> None:
    """Un ADMINISTRADOR no puede asignar oficios a un superusuario.

    El superusuario sí puede asignar a cualquiera. Se comprueba aquí, en el
    almacén, para que la regla se cumpla venga de donde venga la llamada.
    """
    if actor_rol != ROL_ADMINISTRADOR:
        return
    if _rol_de(id_empleado) == ROL_SUPERUSUARIO:
        raise ValueError(
            "Como administrador no puede asignar oficios a un superusuario. "
            "Esa asignación corresponde a un superusuario."
        )


def _validar_cantidad_investigados(valor) -> str:
    """Cantidad de investigados: número entero no negativo, opcional.
    Devuelve el valor normalizado como texto ('' si no se indicó)."""
    texto = str(valor if valor is not None else "").strip()
    if not texto:
        return ""
    try:
        cantidad = int(texto)
    except ValueError:
        raise ValueError("La cantidad de investigados debe ser un número entero.")
    if cantidad < 0:
        raise ValueError("La cantidad de investigados no puede ser negativa.")
    return str(cantidad)


def _validar_fecha_asignacion(fecha_asignacion: str, fecha_recepcion: str) -> str:
    """Fecha de asignación (opcional). No puede ser anterior a la de recepción:
    un oficio se asigna después de recibirlo. Devuelve la fecha normalizada."""
    fecha_asignacion = (fecha_asignacion or "").strip()
    if not fecha_asignacion:
        return ""
    _validar_fecha(fecha_asignacion, "Fecha de asignación")
    if (datetime.strptime(fecha_asignacion, "%Y-%m-%d")
            < datetime.strptime(fecha_recepcion, "%Y-%m-%d")):
        raise ValueError(
            "La fecha de asignación no puede ser anterior a la fecha de recepción."
        )
    return fecha_asignacion


def _exigir_respuesta_para_finalizar(estado: str, archivo_respuesta: str,
                                     estado_previo: str = "") -> None:
    """Un oficio solo puede PASAR a "Finalizado" si ya tiene adjunta la
    respuesta en PDF.

    La regla se aplica al marcar el oficio como finalizado. Los que ya estaban
    finalizados antes de existir esta exigencia siguen siendo editables (por
    ejemplo, para corregirles la observación), porque de lo contrario quedarían
    bloqueados para siempre.
    """
    if estado != "Finalizado" or estado_previo == "Finalizado":
        return
    if not (archivo_respuesta or "").strip():
        raise ValueError(
            "Para finalizar el oficio debe adjuntar antes la respuesta en PDF."
        )


def _guardar_documento(referencia: str, ruta_origen: str, carpeta: Path,
                       extensiones, etiqueta: str) -> str:
    """Copia un adjunto a la carpeta de datos y devuelve su nombre de archivo.

    El archivo se guarda como '<referencia><extensión original>', de modo que
    cada oficio tiene como mucho un documento de cada tipo.
    """
    origen = Path(ruta_origen)
    if not origen.exists():
        raise ValueError("No se encontró el archivo seleccionado.")
    extension = origen.suffix.lower()
    if extension not in extensiones:
        admitidas = " o ".join(e.upper().lstrip(".") for e in extensiones)
        raise ValueError(f"{etiqueta} debe ser un archivo {admitidas}.")
    nombre = f"{referencia}{extension}"
    destino = carpeta / nombre
    try:
        # El destino puede existir en solo lectura de una carga previa.
        permisos.hacer_escribible(destino)
        shutil.copyfile(origen, destino)
        permisos.proteger(destino)
    except OSError as error:
        raise ValueError(f"No se pudo guardar el archivo: {error}")
    return nombre


# --- Operaciones -------------------------------------------------------------
def _validar_fecha_respuesta(fecha_respuesta: str, fecha_recepcion: str) -> str:
    """Valida la fecha de respuesta (opcional). No puede ser anterior a la de
    recepción: no se responde un oficio antes de recibirlo. Devuelve la fecha
    normalizada ('' si no se indicó)."""
    fecha_respuesta = (fecha_respuesta or "").strip()
    if not fecha_respuesta:
        return ""
    _validar_fecha(fecha_respuesta, "Fecha de respuesta")
    if (datetime.strptime(fecha_respuesta, "%Y-%m-%d")
            < datetime.strptime(fecha_recepcion, "%Y-%m-%d")):
        raise ValueError(
            "La fecha de respuesta no puede ser anterior a la fecha de recepción."
        )
    return fecha_respuesta


@bloqueo.con_bloqueo("oficios")
def registrar_oficio(codigo_oficio: str, fecha_recepcion: str, fecha_oficio: str,
                     id_empleado: str, nombre_empleado: str, estado: str,
                     registrado_por: str, fecha_respuesta: str = "",
                     observacion: str = "", causal_oficio: str = "",
                     referencia_sb: str = "", actor_rol: str = None,
                     ruta_documento: str = "", fecha_asignacion: str = "",
                     cantidad_investigados="", ruta_respuesta: str = "") -> str:
    """`codigo_oficio` es la **Referencia oficio** (obligatoria).
    `causal_oficio` y `referencia_sb` son opcionales.

    `ruta_documento` es el documento del oficio (PDF o Word) y es
    **obligatorio**: no se registra un oficio sin su soporte.

    `ruta_respuesta` es opcional y solo hace falta para registrar de entrada un
    oficio ya finalizado, porque finalizar exige tener la respuesta adjunta.

    Un **usuario regular** solo puede registrar oficios **auto-asignados**: el
    responsable debe ser él mismo. Asignar a otra persona queda reservado a
    superusuario y administradores, y un administrador no puede asignárselos a
    un superusuario.
    """
    codigo_oficio = codigo_oficio.strip()
    if not codigo_oficio:
        raise ValueError("Debe ingresar la referencia del oficio o circular.")
    causal_oficio = (causal_oficio or "").strip()
    referencia_sb = (referencia_sb or "").strip()
    if not (ruta_documento or "").strip():
        raise ValueError(
            "Debe adjuntar el documento del oficio en formato PDF o Word (.docx)."
        )

    # Auto-asignación obligatoria para los usuarios regulares.
    if actor_rol is not None and actor_rol not in ROLES_GESTORES:
        if (id_empleado or "").strip().lower() != (registrado_por or "").strip().lower():
            raise ValueError(
                "Solo puede registrar oficios asignados a usted mismo. "
                "Asignarlos a otra persona corresponde a un administrador."
            )
    _validar_asignacion(id_empleado, actor_rol)
    _validar_fecha(fecha_recepcion, "Fecha de recepción")
    _validar_fecha(fecha_oficio, "Fecha de oficio")
    # La fecha de oficio no puede ser posterior a la de recepción: no se puede
    # recibir un oficio antes de que exista.
    if datetime.strptime(fecha_oficio, "%Y-%m-%d") > datetime.strptime(fecha_recepcion, "%Y-%m-%d"):
        raise ValueError(
            "La fecha de oficio no puede ser posterior a la fecha de recepción."
        )
    # Fecha de respuesta, fecha de asignación, cantidad de investigados y
    # observación son opcionales.
    fecha_respuesta = _validar_fecha_respuesta(fecha_respuesta, fecha_recepcion)
    fecha_asignacion = _validar_fecha_asignacion(fecha_asignacion, fecha_recepcion)
    cantidad_investigados = _validar_cantidad_investigados(cantidad_investigados)
    observacion = (observacion or "").strip()
    if estado not in ESTADOS:
        raise ValueError("Estado no válido.")

    # El responsable es opcional. Las reglas ajustan el estado en consecuencia
    # (incluida la fecha de respuesta, que implica "Finalizado").
    nombre_empleado = (nombre_empleado or "").strip()
    id_empleado = (id_empleado or "").strip()
    estado = _resolver_estado(nombre_empleado, estado, fecha_respuesta)
    # Finalizar exige la respuesta adjunta, así que para registrar un oficio ya
    # finalizado hay que aportarla en el mismo formulario.
    _exigir_respuesta_para_finalizar(estado, ruta_respuesta)

    registros = _leer_registros()
    # La referencia del oficio no puede repetirse (aunque la Referencia UDC sea
    # única). Se compara sin distinguir mayúsculas/minúsculas ni espacios.
    codigo_normalizado = codigo_oficio.casefold()
    for registro in registros:
        if registro.get("codigo_oficio", "").strip().casefold() == codigo_normalizado:
            raise ValueError(
                f"Ya existe un oficio con la referencia \"{codigo_oficio}\". "
                "La referencia del oficio no puede repetirse."
            )
    referencia = _generar_referencia(registros)
    # Los adjuntos se copian una vez conocida la referencia, que da nombre al
    # archivo. Si algo falla, se lanza el error antes de guardar el registro.
    archivo_oficio = _guardar_documento(
        referencia, ruta_documento, DIR_DOCUMENTOS, EXTENSIONES_DOCUMENTO,
        "El documento del oficio")
    archivo_respuesta = ""
    if (ruta_respuesta or "").strip():
        archivo_respuesta = _guardar_documento(
            referencia, ruta_respuesta, DIR_RESPUESTAS, (".pdf",),
            "La respuesta")
    ahora = datetime.now().isoformat(timespec="seconds")
    registros.append({
        "referencia": referencia,          # Referencia UDC
        "codigo_oficio": codigo_oficio,    # Referencia oficio
        "causal_oficio": causal_oficio,
        "referencia_sb": referencia_sb,
        "fecha_recepcion": fecha_recepcion,
        "fecha_oficio": fecha_oficio,
        "fecha_asignacion": fecha_asignacion,
        "fecha_respuesta": fecha_respuesta,
        "cantidad_investigados": cantidad_investigados,
        "id_empleado": id_empleado,
        "empleado": nombre_empleado,
        "estado": estado,
        "observacion": observacion,
        "archivo_oficio": archivo_oficio,      # documento del oficio (PDF/Word)
        "archivo_respuesta": archivo_respuesta,  # PDF de respuesta adjunto
        "registrado_por": registrado_por,
        "fecha_registro": ahora,
        "historial": [{"estado": estado, "por": registrado_por, "cuando": ahora}],
    })
    _guardar_registros(registros)
    registro_actividad.registrar(
        "REGISTRAR_OFICIO",
        f"referencia={referencia}; codigo={codigo_oficio}; "
        f"responsable={nombre_empleado or '(sin responsable)'}; estado={estado}",
        registrado_por)
    return referencia


def proxima_referencia() -> str:
    """Referencia UDC que se asignaría al próximo oficio (solo informativa)."""
    return _generar_referencia(_leer_registros())


def listar_oficios() -> List[Dict]:
    return _leer_registros()


def listar_oficios_visibles(actor: str, actor_rol: str) -> List[Dict]:
    """Oficios que puede VER el usuario en sesión.

    - Superusuario y administrador: todos.
    - Usuario regular: solo los que él registró o los que tiene asignados.
    """
    registros = _leer_registros()
    if actor_rol in ROLES_GESTORES:
        return registros
    actor_norm = (actor or "").strip().lower()
    return [
        registro for registro in registros
        if (registro.get("id_empleado", "") or "").strip().lower() == actor_norm
        or (registro.get("registrado_por", "") or "").strip().lower() == actor_norm
    ]


@bloqueo.con_bloqueo("oficios")
def actualizar_oficio(referencia: str, nuevo_estado: str, id_empleado: str,
                     nombre_empleado: str, actualizado_por: str,
                     actor_rol: str = None, fecha_respuesta: str = None,
                     observacion: str = None, fecha_asignacion: str = None,
                     cantidad_investigados=None) -> str:
    """Actualiza estado, responsable, fecha de respuesta y/o observación de un
    oficio en una sola operación, respetando las reglas de negocio
    (ver `_resolver_estado`).

    Reservado a GESTORES (administrador / superusuario): pueden reasignar el
    responsable y fijar cualquier estado. Los usuarios regulares no pueden usar
    esta vía (ver `actualizar_estado_asignado`).

    Devuelve el estado final aplicado (puede diferir del solicitado si las
    reglas lo ajustaron, p. ej. al asignar responsable a un "Por asignar").
    """
    if actor_rol is not None and actor_rol not in ROLES_GESTORES:
        raise ValueError(
            "No tiene permisos para reasignar el responsable ni cambiar "
            "libremente el estado del oficio."
        )
    if nuevo_estado not in ESTADOS:
        raise ValueError("Estado no válido.")
    nombre_empleado = (nombre_empleado or "").strip()
    id_empleado = (id_empleado or "").strip()
    registros = _leer_registros()
    for registro in registros:
        if registro["referencia"] == referencia:
            cambios = []
            # La restricción de asignar a un superusuario solo aplica cuando el
            # responsable CAMBIA: un administrador puede seguir editando la
            # observación de un oficio que ya estaba asignado a un superusuario.
            if id_empleado != (registro.get("id_empleado", "") or "").strip():
                _validar_asignacion(id_empleado, actor_rol)
            # La fecha de respuesta se resuelve primero: si el oficio queda con
            # respuesta, el estado pasa obligatoriamente a "Finalizado".
            if fecha_respuesta is not None:
                nueva_fecha = _validar_fecha_respuesta(
                    fecha_respuesta, registro["fecha_recepcion"])
            else:
                nueva_fecha = registro.get("fecha_respuesta", "")
            estado_final = _resolver_estado(nombre_empleado, nuevo_estado, nueva_fecha)
            _exigir_respuesta_para_finalizar(
                estado_final, registro.get("archivo_respuesta", ""),
                registro.get("estado", ""))
            if fecha_asignacion is not None:
                nueva_asignacion = _validar_fecha_asignacion(
                    fecha_asignacion, registro["fecha_recepcion"])
                if nueva_asignacion != registro.get("fecha_asignacion", ""):
                    registro["fecha_asignacion"] = nueva_asignacion
                    cambios.append(
                        f"F. asignación: {nueva_asignacion or '(sin fecha)'}")
            if cantidad_investigados is not None:
                nueva_cantidad = _validar_cantidad_investigados(cantidad_investigados)
                if nueva_cantidad != registro.get("cantidad_investigados", ""):
                    registro["cantidad_investigados"] = nueva_cantidad
                    cambios.append(
                        f"Cant. investigados: {nueva_cantidad or '(sin dato)'}")
            if fecha_respuesta is not None:
                if nueva_fecha != registro.get("fecha_respuesta", ""):
                    registro["fecha_respuesta"] = nueva_fecha
                    cambios.append(f"F. respuesta: {nueva_fecha or '(sin fecha)'}")
            if observacion is not None:
                nueva_obs = observacion.strip()
                if nueva_obs != registro.get("observacion", ""):
                    registro["observacion"] = nueva_obs
                    cambios.append("Observación actualizada")
            if nombre_empleado != registro.get("empleado", ""):
                registro["id_empleado"] = id_empleado
                registro["empleado"] = nombre_empleado
                cambios.append(
                    f"Responsable: {nombre_empleado or '(sin responsable)'}"
                )
            if estado_final != registro.get("estado"):
                registro["estado"] = estado_final
                cambios.append(f"Estado: {estado_final}")
            if cambios:
                registro.setdefault("historial", []).append({
                    "evento": " · ".join(cambios),
                    "por": actualizado_por,
                    "cuando": datetime.now().isoformat(timespec="seconds"),
                })
                _guardar_registros(registros)
                registro_actividad.registrar(
                    "ACTUALIZAR_OFICIO",
                    f"referencia={referencia}; " + "; ".join(cambios),
                    actualizado_por)
            return estado_final
    raise ValueError("No se encontró la referencia indicada.")


@bloqueo.con_bloqueo("oficios")
def actualizar_estado_asignado(referencia: str, actor: str, nuevo_estado: str,
                               fecha_respuesta: str = None,
                               observacion: str = None,
                               cantidad_investigados=None) -> str:
    """Actualización desde el rol de usuario regular, sobre sus propios oficios.

    Puede cambiar la fecha de respuesta, la observación y alternar el estado
    entre "En proceso" y "Finalizado" (por si finalizó por error y quiere
    reabrirlo). No puede reasignar el responsable ni dejarlo en "Por asignar".

    Si el oficio queda con fecha de respuesta, el estado pasa siempre a
    "Finalizado": para reabrirlo hay que borrar antes esa fecha.
    """
    estados_permitidos = ("En proceso", "Finalizado")
    if nuevo_estado not in estados_permitidos:
        raise ValueError(
            "Como usuario solo puede alternar entre \"En proceso\" y \"Finalizado\"."
        )
    actor_norm = (actor or "").strip().lower()
    registros = _leer_registros()
    for registro in registros:
        if registro["referencia"] == referencia:
            responsable = (registro.get("id_empleado", "") or "").strip().lower()
            if not responsable or responsable != actor_norm:
                raise ValueError("Solo puede modificar oficios asignados a usted.")
            cambios = []
            # La fecha de respuesta manda sobre el estado.
            if fecha_respuesta is not None:
                nueva_fecha = _validar_fecha_respuesta(
                    fecha_respuesta, registro["fecha_recepcion"])
            else:
                nueva_fecha = registro.get("fecha_respuesta", "")
            estado_final = _resolver_estado(
                registro.get("empleado", ""), nuevo_estado, nueva_fecha)
            _exigir_respuesta_para_finalizar(
                estado_final, registro.get("archivo_respuesta", ""),
                registro.get("estado", ""))
            if cantidad_investigados is not None:
                nueva_cantidad = _validar_cantidad_investigados(cantidad_investigados)
                if nueva_cantidad != registro.get("cantidad_investigados", ""):
                    registro["cantidad_investigados"] = nueva_cantidad
                    cambios.append(
                        f"Cant. investigados: {nueva_cantidad or '(sin dato)'}")
            if fecha_respuesta is not None:
                if nueva_fecha != registro.get("fecha_respuesta", ""):
                    registro["fecha_respuesta"] = nueva_fecha
                    cambios.append(f"F. respuesta: {nueva_fecha or '(sin fecha)'}")
            if observacion is not None:
                nueva_obs = observacion.strip()
                if nueva_obs != registro.get("observacion", ""):
                    registro["observacion"] = nueva_obs
                    cambios.append("Observación actualizada")
            if registro.get("estado") != estado_final:
                registro["estado"] = estado_final
                cambios.append(f"Estado: {estado_final}")
            if cambios:
                registro.setdefault("historial", []).append({
                    "evento": " · ".join(cambios),
                    "por": actor,
                    "cuando": datetime.now().isoformat(timespec="seconds"),
                })
                _guardar_registros(registros)
                registro_actividad.registrar(
                    "ACTUALIZAR_OFICIO",
                    f"referencia={referencia}; " + "; ".join(cambios), actor)
            return estado_final
    raise ValueError("No se encontró la referencia indicada.")


# --- Respuesta en PDF adjunta ------------------------------------------------
def _puede_editar(registro: Dict, actor: str, actor_rol: str) -> bool:
    """Un gestor puede sobre cualquier oficio; un usuario regular solo sobre
    los oficios asignados a él."""
    if actor_rol in ROLES_GESTORES:
        return True
    responsable = (registro.get("id_empleado", "") or "").strip().lower()
    return bool(responsable) and responsable == (actor or "").strip().lower()


def _ruta_adjunto(referencia: str, campo: str, carpeta: Path) -> Optional[Path]:
    for registro in _leer_registros():
        if registro["referencia"] == referencia:
            nombre = registro.get(campo, "")
            if not nombre:
                return None
            ruta = carpeta / nombre
            return ruta if ruta.exists() else None
    return None


def ruta_respuesta(referencia: str) -> Optional[Path]:
    """Devuelve la ruta del PDF de respuesta adjunto, o None si no hay."""
    return _ruta_adjunto(referencia, "archivo_respuesta", DIR_RESPUESTAS)


def ruta_documento(referencia: str) -> Optional[Path]:
    """Devuelve la ruta del documento del oficio (PDF o Word), o None."""
    return _ruta_adjunto(referencia, "archivo_oficio", DIR_DOCUMENTOS)


@bloqueo.con_bloqueo("oficios")
def reemplazar_documento(referencia: str, ruta_origen: str, actor: str,
                         actor_rol: str) -> str:
    """Sustituye el documento del oficio (PDF o Word) por si se cargó el
    archivo equivocado. Mismos permisos que adjuntar la respuesta."""
    registros = _leer_registros()
    for registro in registros:
        if registro["referencia"] == referencia:
            if not _puede_editar(registro, actor, actor_rol):
                raise ValueError(
                    "Solo puede cambiar el documento de oficios asignados a usted.")
            anterior = registro.get("archivo_oficio", "")
            nombre = _guardar_documento(
                referencia, ruta_origen, DIR_DOCUMENTOS, EXTENSIONES_DOCUMENTO,
                "El documento del oficio")
            # Si la extensión cambió (.pdf -> .docx), retirar el archivo previo.
            if anterior and anterior != nombre:
                try:
                    permisos.hacer_escribible(DIR_DOCUMENTOS / anterior)
                    (DIR_DOCUMENTOS / anterior).unlink(missing_ok=True)
                except OSError:
                    pass
            registro["archivo_oficio"] = nombre
            registro.setdefault("historial", []).append({
                "evento": "Documento del oficio actualizado",
                "por": actor,
                "cuando": datetime.now().isoformat(timespec="seconds"),
            })
            _guardar_registros(registros)
            registro_actividad.registrar(
                "REEMPLAZAR_DOCUMENTO",
                f"referencia={referencia}; archivo={nombre}", actor)
            return nombre
    raise ValueError("No se encontró la referencia indicada.")


@bloqueo.con_bloqueo("oficios")
def adjuntar_respuesta(referencia: str, ruta_origen: str, actor: str,
                       actor_rol: str) -> str:
    """Copia un PDF de respuesta a datos/respuestas/ y lo asocia al oficio.

    El archivo se guarda como '<referencia>.pdf'. Si ya había uno, se
    reemplaza. Devuelve el nombre del archivo guardado.
    """
    registros = _leer_registros()
    for registro in registros:
        if registro["referencia"] == referencia:
            if not _puede_editar(registro, actor, actor_rol):
                raise ValueError("Solo puede adjuntar respuestas a oficios asignados a usted.")
            nombre = _guardar_documento(
                referencia, ruta_origen, DIR_RESPUESTAS, (".pdf",), "La respuesta")
            registro["archivo_respuesta"] = nombre
            registro.setdefault("historial", []).append({
                "evento": "Respuesta en PDF adjuntada",
                "por": actor,
                "cuando": datetime.now().isoformat(timespec="seconds"),
            })
            _guardar_registros(registros)
            registro_actividad.registrar(
                "ADJUNTAR_RESPUESTA",
                f"referencia={referencia}; archivo={nombre}", actor)
            return nombre
    raise ValueError("No se encontró la referencia indicada.")


@bloqueo.con_bloqueo("oficios")
def eliminar_respuesta(referencia: str, actor: str, actor_rol: str) -> None:
    """Elimina el PDF de respuesta adjunto (por si se cargó el archivo
    equivocado). Mismos permisos que adjuntar: un usuario regular solo sobre
    los oficios asignados a él."""
    registros = _leer_registros()
    for registro in registros:
        if registro["referencia"] == referencia:
            if not _puede_editar(registro, actor, actor_rol):
                raise ValueError("Solo puede eliminar respuestas de oficios asignados a usted.")
            nombre = registro.get("archivo_respuesta", "")
            if not nombre:
                raise ValueError("Este oficio no tiene una respuesta en PDF adjunta.")
            # Un oficio finalizado no puede quedarse sin su respuesta: primero
            # hay que reabrirlo (borrando la fecha de respuesta).
            if registro.get("estado") == "Finalizado":
                raise ValueError(
                    "No se puede quitar la respuesta de un oficio finalizado. "
                    "Reabra antes el oficio borrando su fecha de respuesta."
                )
            ruta = DIR_RESPUESTAS / nombre
            try:
                permisos.hacer_escribible(ruta)
                ruta.unlink(missing_ok=True)
            except OSError as error:
                raise ValueError(f"No se pudo eliminar el PDF: {error}")
            registro["archivo_respuesta"] = ""
            registro.setdefault("historial", []).append({
                "evento": "Respuesta en PDF eliminada",
                "por": actor,
                "cuando": datetime.now().isoformat(timespec="seconds"),
            })
            _guardar_registros(registros)
            registro_actividad.registrar(
                "ELIMINAR_RESPUESTA",
                f"referencia={referencia}; archivo={nombre}", actor)
            return
    raise ValueError("No se encontró la referencia indicada.")


# --- Búsqueda / filtros ------------------------------------------------------
# Campos de texto por los que se puede buscar: clave interna -> etiqueta.
CAMPOS_BUSQUEDA = {
    "referencia": "Referencia UDC",
    "codigo_oficio": "Referencia oficio",
    "causal_oficio": "Causal oficio",
    "referencia_sb": "Referencia SB",
}

# Tipos de fecha por los que se puede filtrar (y exportar).
CAMPOS_FECHA = {
    "fecha_oficio": "Fecha de oficio",
    "fecha_recepcion": "Fecha de recepción",
    "fecha_asignacion": "Fecha de asignación",
    "fecha_respuesta": "Fecha de respuesta",
}

# Columnas del CSV de exportación: clave interna -> encabezado.
COLUMNAS_EXPORTACION = {
    "referencia": "Referencia UDC",
    "codigo_oficio": "Referencia oficio",
    "causal_oficio": "Causal oficio",
    "referencia_sb": "Referencia SB",
    "fecha_oficio": "F. oficio",
    "fecha_recepcion": "F. recepción",
    "fecha_asignacion": "F. asignación",
    "fecha_respuesta": "F. respuesta",
    "cantidad_investigados": "Cant. investigados",
    "empleado": "Responsable",
    "estado": "Estado",
    "archivo_oficio": "Documento del oficio",
    "archivo_respuesta": "Respuesta en PDF",
    "observacion": "Observación",
    "registrado_por": "Registrado por",
    "fecha_registro": "Fecha de registro",
}


def exportar_csv(registros: List[Dict], ruta_destino: str, exportado_por: str = "",
                 detalle: str = "") -> int:
    """Vuelca los oficios indicados a un CSV y devuelve cuántos escribió.

    Se usa UTF-8 con BOM y separador ';' para que Excel en español lo abra
    directo, con las tildes correctas y las columnas ya separadas.
    """
    if not registros:
        raise ValueError("No hay oficios que exportar con ese criterio.")
    destino = Path(ruta_destino)
    try:
        with destino.open("w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(COLUMNAS_EXPORTACION.values())
            for registro in registros:
                escritor.writerow([
                    " ".join(str(registro.get(clave, "") or "").split())
                    for clave in COLUMNAS_EXPORTACION
                ])
    except OSError as error:
        raise ValueError(f"No se pudo escribir el archivo: {error}")
    registro_actividad.registrar(
        "EXPORTAR_OFICIOS",
        f"cantidad={len(registros)}; archivo={destino.name}"
        + (f"; {detalle}" if detalle else ""),
        exportado_por)
    return len(registros)


def filtrar_oficios(registros: List[Dict], campo_texto: str = "", texto: str = "",
                    campo_fecha: str = "", desde: str = "", hasta: str = "") -> List[Dict]:
    """Filtra una lista de oficios.

    - `campo_texto` + `texto`: coincidencia parcial, sin distinguir
      mayúsculas/minúsculas, sobre uno de los campos de `CAMPOS_BUSQUEDA`.
    - `campo_fecha` + `desde`/`hasta`: rango sobre UN SOLO tipo de fecha
      (`CAMPOS_FECHA`). Ambos extremos se comparan contra el mismo campo, por
      lo que no es posible mezclar tipos de fecha. Si solo se indica `desde`,
      se busca esa **fecha única**; si solo se indica `hasta`, todo lo anterior
      o igual a esa fecha.

    Los oficios sin la fecha indicada (por ejemplo sin fecha de respuesta) no
    aparecen cuando se filtra por ese campo.
    """
    resultado = registros

    texto = (texto or "").strip().casefold()
    if texto:
        if campo_texto not in CAMPOS_BUSQUEDA:
            raise ValueError("Campo de búsqueda no válido.")
        resultado = [r for r in resultado
                     if texto in (r.get(campo_texto, "") or "").casefold()]

    desde = (desde or "").strip()
    hasta = (hasta or "").strip()
    if desde or hasta:
        if campo_fecha not in CAMPOS_FECHA:
            raise ValueError("Tipo de fecha no válido.")
        etiqueta = CAMPOS_FECHA[campo_fecha]
        if desde:
            _validar_fecha(desde, f"{etiqueta} (desde)")
        if hasta:
            _validar_fecha(hasta, f"{etiqueta} (hasta)")
        if desde and hasta and desde > hasta:
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )
        # Fecha única: solo se indicó el extremo inicial.
        if desde and not hasta:
            hasta = desde
        filtrados = []
        for registro in resultado:
            valor = (registro.get(campo_fecha, "") or "").strip()
            if not valor:
                continue          # sin esa fecha -> no participa del filtro
            if desde and valor < desde:
                continue
            if hasta and valor > hasta:
                continue
            filtrados.append(registro)
        resultado = filtrados

    return resultado
