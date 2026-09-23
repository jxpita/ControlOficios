# Graph Report - ControlOficios  (2026-09-23)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 704 nodes · 1411 edges · 42 communities (36 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `83145d8f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- registrar_oficio
- tipos_accion.py
- validar_importacion
- carga_masiva.py
- aplicacion.py
- SelectorFecha
- metricas.py
- AplicacionPrincipal
- causales_registradas
- parametros.py
- VisorPDF
- ._refrescar_listado
- ._refrescar_tablero
- Control de Oficios — Unidad de Cumplimiento
- ._al_seleccionar_oficio
- ._construir_configuracion
- autenticacion.py
- ._construir_registro
- manual.js
- 4. Compilar a ejecutable (lo más ligero posible)
- 2.1 Roles de usuario
- Grafo de conocimiento (graphify)
- 4.2 Despliegue en una carpeta compartida (varias personas)
- 4.3 Copia de seguridad programada (opcional, en otro disco)
- 1. Requisitos
- 2. Ejecutar en desarrollo
- exportar_oficios
- hay_soporte_xlsx
- ValueError
- Fuente del manual de usuario
- ._al_recuperar_foco
- dependencies
- respaldo.py
- compilar.sh
- logo.py
- ._mostrar_pdf
- paginas.py
- ._guardar_oficio
- 2.3 Tablero (dashboard)
- almacen_oficios.py
- _validar_prioridad

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 97 edges
2. `registrar()` - 33 edges
3. `_leer_registros()` - 26 edges
4. `con_bloqueo()` - 26 edges
5. `registrar_oficio()` - 23 edges
6. `_preparar_importado()` - 20 edges
7. `actualizar_oficio()` - 19 edges
8. `_guardar_registros()` - 19 edges
9. `SelectorFecha` - 18 edges
10. `Control de Oficios — Unidad de Cumplimiento` - 18 edges

## Surprising Connections (you probably didn't know these)
- `actualizar_estado_asignado()` --references--> `con_bloqueo()`  [EXTRACTED]
  almacen_oficios.py → bloqueo.py
- `actualizar_estado_asignado()` --calls--> `estandarizar_texto()`  [EXTRACTED]
  almacen_oficios.py → configuracion.py
- `actualizar_estado_asignado()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `actualizar_oficio()` --references--> `con_bloqueo()`  [EXTRACTED]
  almacen_oficios.py → bloqueo.py
- `actualizar_oficio()` --calls--> `estandarizar_texto()`  [EXTRACTED]
  almacen_oficios.py → configuracion.py

## Import Cycles
- None detected.

## Communities (42 total, 6 thin omitted)

### Community 0 - "registrar_oficio"
Cohesion: 0.10
Nodes (32): actualizar_estado_asignado(), actualizar_oficio(), _empleado_de(), _exigir_cantidad_coherente(), _exigir_datos_para_finalizar(), _guardar_documento(), _preparar_importado(), Rol del usuario indicado, o '' si no existe. (+24 more)

### Community 1 - "tipos_accion.py"
Cohesion: 0.22
Nodes (18): agregar(), eliminar(), _exigir_gestor(), existe(), _guardar(), _leer(), listar(), _normalizar() (+10 more)

### Community 2 - "validar_importacion"
Cohesion: 0.33
Nodes (6): Comprueba TODAS las filas como si se fueran a guardar, sin guardar nada. Es la…, validar_importacion(), error_de_fila(), etiqueta_filas(), Describe una fila que no se puede importar. Se devuelve en piezas —número de…, Número(s) de línea del archivo que componen el oficio ('11' o '11, 12').

### Community 3 - "carga_masiva.py"
Cohesion: 0.08
Nodes (35): _a_fecha(), _a_texto(), agrupar_por_referencia(), _campos_comparables(), _error_formato(), escribir_plantilla(), filas_plantilla(), _implicado_de() (+27 more)

### Community 4 - "aplicacion.py"
Cohesion: 0.05
Nodes (25): anchos_de_columna(), construir_tabla_errores(), DialogoCargaMasiva, DialogoExportar, DialogoImplicados, DialogoResultadoCarga, iniciar(), maximizar_ventana() (+17 more)

### Community 5 - "SelectorFecha"
Cohesion: 0.10
Nodes (9): DialogoMantenimiento, Fecha desde la que se abre el calendario (la escrita, o hoy)., Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no cabe debajo,…, Campo para elegir un archivo: botón + nombre del archivo elegido. Guarda la…, Corrige los datos de identificación de un oficio y permite retirarlo. Son los…, Campo de fecha con calendario emergente. No requiere librerías externas.…, `permitir_vacio=True` deja el campo en blanco y ofrece un botón "Limpiar" en el…, SelectorArchivo (+1 more)

### Community 6 - "metricas.py"
Cohesion: 0.18
Nodes (19): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), investigados_por_mes(), personas_investigadas(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz:… (+11 more)

### Community 7 - "AplicacionPrincipal"
Cohesion: 0.10
Nodes (8): AplicacionPrincipal, Ajusta cuántas filas muestra la tabla de oficios al alto disponible. Dentro de…, Repuebla los desplegables de tipo de acción tras cambiar el catálogo., Nombre del tipo elegido en la lista, sin el contador., Acorta el título de la cabecera cuando la ventana es estrecha. `pack` no encoge…, Diálogo para que el usuario en sesión cambie su propia contraseña. Disponible…, Desplaza el área que está bajo el puntero. Si el cursor está sobre una tabla,…, Coloca una etiqueta y su campo en una fila del grupo. Con `estirar` el campo…

### Community 9 - "parametros.py"
Cohesion: 0.06
Nodes (59): _generar_referencia(), proxima_referencia(), Genera la Referencia UDC: REQ-UDC-<sigla>-<año>-<secuencial de 4 dígitos>. El…, Referencia UDC que se asignaría al próximo oficio de esa institución (solo…, bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida. Problema que… (+51 more)

### Community 10 - "VisorPDF"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin…, Centra horizontalmente la página dentro del lienzo (y verticalmente si sobra…, Abre el PDF dentro de la aplicación. Devuelve True si se mostró en la app;…, Abre el PDF con el lector predeterminado del sistema operativo. Alternativa…, Ventana con el PDF renderizado página a página., VisorPDF

### Community 11 - "._refrescar_listado"
Cohesion: 0.10
Nodes (10): Valor elegido en un desplegable de filtro, o '' si es "(Todos)"., Devuelve la clave interna a partir de la etiqueta mostrada., Guarda los cambios del panel según el rol: el gestor puede cambiar responsable,…, El botón dice lo que hará: adjuntar el que falta o cambiar el que hay., Pone el documento del oficio: el que falta o uno que sustituya al que hay, si…, Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Corrige los datos de identificación de un oficio, o lo retira. (+2 more)

### Community 12 - "._refrescar_tablero"
Cohesion: 0.15
Nodes (6): (y del título, margen superior) medidos con las fuentes de verdad. La barra más…, Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Barras verticales: personas investigadas por mes. La barra mide las PERSONAS;…, Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 13 - "Control de Oficios — Unidad de Cumplimiento"
Cohesion: 0.15
Nodes (12): 2.2 Bitácora de auditoría, 3.1 `herramienta_admin.py` (utilidad de consola), 3.2 Referencia UDC y secuencial inicial, 3.3 Búsqueda de oficios, 3.4 Catálogo de tipos de acción, 3.5 Datos de prueba, 3. Estructura, 4.1 Uso compartido por varias personas (+4 more)

### Community 14 - "._al_seleccionar_oficio"
Cohesion: 0.17
Nodes (8): Repuebla los desplegables de filtro conservando lo elegido. El tipo de acción…, Precarga el panel de edición con los datos del oficio seleccionado. Solo…, Repuebla los desplegables del tablero conservando lo elegido., Oficios visibles tras aplicar los filtros del tablero., Texto que se muestra en los desplegables para un responsable. Incluye el…, Personas a las que se les puede asignar un oficio. Un administrador no puede…, A partir del texto del desplegable devuelve (usuario, nombre). Para "(Sin…, Tipos de acción del catálogo, para los desplegables.

### Community 15 - "._construir_configuracion"
Cohesion: 0.24
Nodes (5): Permite al superusuario o a un administrador indicar la última Referencia UDC…, Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana. Con un…, Catálogo de tipos de acción, mantenible por los gestores., Panel para volcar de una vez el histórico de la matriz de Excel., Panel de copias de seguridad. Solo lo ve el superusuario.

### Community 16 - "autenticacion.py"
Cohesion: 0.07
Nodes (51): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+43 more)

### Community 17 - "._construir_registro"
Cohesion: 0.13
Nodes (8): Panel de búsqueda. Tres bloques que se acumulan entre sí: - por texto, sobre…, Tablero con scroll vertical: tarjetas de indicadores y gráficos., Filtros que se aplican a TODO el tablero. Son los mismos criterios de la…, True si el usuario en sesión puede crear/editar/eliminar usuarios y…, Convierte un contenedor en un área con scroll vertical. Devuelve (lienzo,…, Ancho de una columna de tabla: el mayor entre lo que pide el dato y lo que…, Recuadro con título para agrupar campos afines., Personas investigadas que se anotan junto con el oficio. Se guardan en memoria…

### Community 18 - "manual.js"
Cohesion: 0.09
Nodes (10): bandaAzul, contenido, doc, {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, Footer, PageNumber, Tab, TabStopType, LeaderType,
}, ENTRADAS, fs, indice, PAGINAS (+2 more)

### Community 20 - "4. Compilar a ejecutable (lo más ligero posible)"
Cohesion: 0.20
Nodes (10): 4. Compilar a ejecutable (lo más ligero posible), Consejos para que pese lo menos posible, Dónde queda todo: la carpeta `bin/`, IMPORTANTE: la carpeta `datos/` va junto al ejecutable, Opción A — CON_DEPENDENCIAS (un solo ejecutable, `--onefile`), Opción B — SIN_DEPENDENCIAS (dependencias aparte, `--onedir`), Paso previo: descomprimir UPX, Qué hace cada opción (+2 more)

### Community 21 - "2.1 Roles de usuario"
Cohesion: 0.15
Nodes (13): 2.1 Roles de usuario, Campos del oficio, Carga masiva de oficios, Documento del oficio, Exportar oficios, Implicados (personas investigadas), Las filas con error se listan una a una, Mantenimiento de oficios (+5 more)

### Community 22 - "Grafo de conocimiento (graphify)"
Cohesion: 0.29
Nodes (6): Consultar el grafo, Dependencias, Grafo de conocimiento (graphify), IMPORTANTE: actualizar el grafo tras CADA cambio de código, Notas para Claude Code — ControlOficios, Qué se versiona y qué no

### Community 23 - "4.2 Despliegue en una carpeta compartida (varias personas)"
Cohesion: 0.29
Nodes (7): 4.2 Despliegue en una carpeta compartida (varias personas), Arranque desde el compartido, Cómo publicar una versión nueva, Dónde viven los datos, Estructura recomendada en el recurso compartido, Los íconos, Si la carpeta de datos no responde

### Community 24 - "4.3 Copia de seguridad programada (opcional, en otro disco)"
Cohesion: 0.50
Nodes (4): 4.3 Copia de seguridad programada (opcional, en otro disco), Programarlo a diario, Prueba manual, Recomendaciones

### Community 25 - "1. Requisitos"
Cohesion: 0.67
Nodes (3): 1. Requisitos, Dependencias externas, Módulos de la biblioteca estándar

### Community 26 - "2. Ejecutar en desarrollo"
Cohesion: 0.50
Nodes (4): 2. Ejecutar en desarrollo, Cómo se adaptan las pantallas, Etiquetas y encabezados, Tamaño de la ventana

### Community 27 - "exportar_oficios"
Cohesion: 0.13
Nodes (19): _encabezados_exportacion(), escribir_xlsx(), exportar_csv(), exportar_oficios(), exportar_xlsx(), _fila_exportacion(), filas_exportacion(), Path (+11 more)

### Community 29 - "ValueError"
Cohesion: 0.18
Nodes (15): actualizar_implicado(), eliminar_implicado(), _exigir_no_anulado(), _oficio_editable(), Comprueba la identificación según su tipo y la devuelve normalizada. -…, Comprueba y normaliza los datos de un implicado., La cantidad de investigados pasa a contarla el detalle. Mientras el oficio no…, Devuelve el oficio indicado, comprobando permisos y que no esté anulado. (+7 more)

### Community 30 - "Fuente del manual de usuario"
Cohesion: 0.33
Nodes (5): Al actualizar el manual, Archivos, Compilar, Dependencias, Fuente del manual de usuario

### Community 31 - "._al_recuperar_foco"
Cohesion: 0.12
Nodes (7): Restablece el formulario para crear un usuario nuevo., Diálogo modal para escribir y confirmar una nueva contraseña. Devuelve la…, Refresca la vista al volver a la ventana. Con varias personas usando la misma…, Repuebla los desplegables de responsable con los usuarios actuales., ¿El usuario en sesión puede gestionar a ese usuario? Se consulta antes de abrir…, Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario puede crear…

### Community 32 - "dependencies"
Cohesion: 0.50
Nodes (3): docx, dependencies, docx

### Community 33 - "respaldo.py"
Cohesion: 0.11
Nodes (26): date, _fechas_recepcion(), generar_oficios(), _identificacion(), _mes_atras(), Genera el archivo de datos de prueba para la carga masiva. Crea `Matriz de…, Documento con el formato que exige cada tipo. La aplicación valida la cédula…, (año, mes) de la fecha indicada retrocediendo esa cantidad de meses. (+18 more)

### Community 36 - "._mostrar_pdf"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word, con el…, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece el lector…

### Community 39 - "2.3 Tablero (dashboard)"
Cohesion: 0.67
Nodes (3): 2.3 Tablero (dashboard), Filtros del tablero, Métricas

### Community 43 - "almacen_oficios.py"
Cohesion: 0.12
Nodes (38): adjuntar_respuesta(), agregar_implicado(), anular_oficio(), contar_por_tipo_accion(), corregir_oficio(), eliminar_respuesta(), esta_anulado(), estandarizar_registros() (+30 more)

### Community 44 - "_validar_prioridad"
Cohesion: 0.29
Nodes (8): filtrar_oficios(), Filtra una lista de oficios. Todos los filtros se acumulan (Y lógico). -…, Prioridad de atención del oficio. Es opcional: el histórico que se carga desde…, Estado del oficio tal como está en el catálogo. Da igual cómo se escriba…, validar_estado(), _validar_prioridad(), opcion_de(), La opción del catálogo que corresponde a lo escrito, o '' si ninguna. Devuelve…

## Knowledge Gaps
- **66 isolated node(s):** `2.2 Bitácora de auditoría`, `3.1 `herramienta_admin.py` (utilidad de consola)`, `3.2 Referencia UDC y secuencial inicial`, `3.3 Búsqueda de oficios`, `3.4 Catálogo de tipos de acción` (+61 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `AplicacionPrincipal` to `aplicacion.py`, `._mostrar_pdf`, `._guardar_oficio`, `._refrescar_listado`, `._refrescar_tablero`, `._al_seleccionar_oficio`, `._construir_configuracion`, `._construir_registro`, `._al_recuperar_foco`?**
  _High betweenness centrality (0.305) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `SelectorFecha` to `._construir_registro`, `aplicacion.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `ValueError` (e.g. with `actualizar_estado_asignado()` and `actualizar_implicado()`) actually correct?**
  _`ValueError` has 54 INFERRED edges - model-reasoned connections that need verification._
- **What connects `2.2 Bitácora de auditoría`, `3.1 `herramienta_admin.py` (utilidad de consola)`, `3.2 Referencia UDC y secuencial inicial` to the rest of the system?**
  _66 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `registrar_oficio` be split into smaller, more focused modules?**
  _Cohesion score 0.1028225806451613 - nodes in this community are weakly interconnected._
- **Should `carga_masiva.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `aplicacion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.054098360655737705 - nodes in this community are weakly interconnected._