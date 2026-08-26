# Graph Report - ControlOficios  (2026-08-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 672 nodes · 1330 edges · 44 communities (38 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `76ceae2e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ValueError
- VentanaIngreso
- tipos_accion.py
- carga_masiva.py
- registrar
- anular_oficio
- metricas.py
- AplicacionPrincipal
- DialogoImplicados
- parametros.py
- VisorPDF
- ._refrescar_listado
- ._refrescar_tablero
- Control de Oficios — Unidad de Cumplimiento
- ._responsable_por_display
- ._construir_configuracion
- _leer_registros
- ._construir_registro
- manual.js
- 4. Compilar a ejecutable (lo más ligero posible)
- 2.1 Roles de usuario
- Grafo de conocimiento (graphify)
- 4.2 Despliegue en una carpeta compartida (varias personas)
- 4.3 Copia de seguridad programada (opcional, en otro disco)
- 1. Requisitos
- 2. Ejecutar en desarrollo
- almacen_oficios.py
- ._guardar_oficio
- Fuente del manual de usuario
- ._al_recuperar_foco
- dependencies
- respaldo.py
- compilar.sh
- logo.py
- ._mostrar_pdf
- paginas.py
- SelectorFecha
- 2.3 Tablero (dashboard)
- .__init__
- aplicacion.py
- DialogoCargaMasiva
- DialogoMantenimiento
- SelectorArchivo

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 96 edges
2. `registrar()` - 32 edges
3. `con_bloqueo()` - 25 edges
4. `_leer_registros()` - 24 edges
5. `registrar_oficio()` - 21 edges
6. `SelectorFecha` - 18 edges
7. `_guardar_registros()` - 18 edges
8. `Control de Oficios — Unidad de Cumplimiento` - 18 edges
9. `actualizar_oficio()` - 17 edges
10. `VentanaIngreso` - 16 edges

## Surprising Connections (you probably didn't know these)
- `actualizar_estado_asignado()` --references--> `con_bloqueo()`  [EXTRACTED]
  almacen_oficios.py → bloqueo.py
- `actualizar_estado_asignado()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `actualizar_oficio()` --references--> `con_bloqueo()`  [EXTRACTED]
  almacen_oficios.py → bloqueo.py
- `actualizar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `corregir_oficio()` --references--> `con_bloqueo()`  [EXTRACTED]
  almacen_oficios.py → bloqueo.py

## Import Cycles
- None detected.

## Communities (44 total, 6 thin omitted)

### Community 0 - "ValueError"
Cohesion: 0.10
Nodes (41): actualizar_estado_asignado(), actualizar_oficio(), corregir_oficio(), _exigir_cantidad_coherente(), _exigir_datos_para_finalizar(), _exigir_no_anulado(), _FilaRepetida, filtrar_oficios() (+33 more)

### Community 1 - "VentanaIngreso"
Cohesion: 0.28
Nodes (3): Crea el banner corporativo y la tarjeta central. Devuelve el contenedor interno…, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 2 - "tipos_accion.py"
Cohesion: 0.06
Nodes (57): Bloqueo entre procesos para la carpeta de datos compartida. Problema que…, _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo fue alterado o…, _buscar_recurso() (+49 more)

### Community 3 - "carga_masiva.py"
Cohesion: 0.08
Nodes (36): _a_fecha(), _a_texto(), agrupar_por_referencia(), _claves_de(), coincidencias(), emparejar_responsables(), _implicado_de(), leer_archivo() (+28 more)

### Community 4 - "registrar"
Cohesion: 0.11
Nodes (38): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+30 more)

### Community 5 - "anular_oficio"
Cohesion: 0.29
Nodes (7): anular_oficio(), esta_anulado(), listar_oficios_visibles(), Oficios que puede VER el usuario en sesión. - Superusuario y administrador:…, Retira un oficio de la operación sin borrarlo. No se elimina a propósito: la…, Devuelve a la operación un oficio anulado por error., reactivar_oficio()

### Community 6 - "metricas.py"
Cohesion: 0.18
Nodes (19): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), investigados_por_mes(), personas_investigadas(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz:… (+11 more)

### Community 7 - "AplicacionPrincipal"
Cohesion: 0.10
Nodes (8): AplicacionPrincipal, Ajusta cuántas filas muestra la tabla de oficios al alto disponible. Dentro de…, Repuebla los desplegables de tipo de acción tras cambiar el catálogo., Nombre del tipo elegido en la lista, sin el contador., Acorta el título de la cabecera cuando la ventana es estrecha. `pack` no encoge…, Diálogo para que el usuario en sesión cambie su propia contraseña. Disponible…, Desplaza el área que está bajo el puntero. Si el cursor está sobre una tabla,…, Coloca una etiqueta y su campo en una fila del grupo. Con `estirar` el campo…

### Community 8 - "DialogoImplicados"
Cohesion: 0.33
Nodes (3): DialogoImplicados, Personas investigadas en un oficio: verlas, añadirlas y corregirlas. Se abre…, Deja el formulario en blanco para añadir a otra persona.

### Community 9 - "parametros.py"
Cohesion: 0.16
Nodes (25): _generar_referencia(), Genera la Referencia UDC: REQ-UDC-<sigla>-<año>-<secuencial de 4 dígitos>. El…, analizar_referencia(), anio_vigente(), _clave(), definir_secuencial_inicial(), esta_configurado(), formatear_referencia() (+17 more)

### Community 10 - "VisorPDF"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin…, Centra horizontalmente la página dentro del lienzo (y verticalmente si sobra…, Abre el PDF dentro de la aplicación. Devuelve True si se mostró en la app;…, Abre el PDF con el lector predeterminado del sistema operativo. Alternativa…, Ventana con el PDF renderizado página a página., VisorPDF

### Community 11 - "._refrescar_listado"
Cohesion: 0.11
Nodes (9): Valor elegido en un desplegable de filtro, o '' si es "(Todos)"., Devuelve la clave interna a partir de la etiqueta mostrada., Guarda los cambios del panel según el rol: el gestor puede cambiar responsable,…, Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Corrige los datos de identificación de un oficio, o lo retira., Abre los implicados del oficio sobre el que se hizo doble clic. (+1 more)

### Community 12 - "._refrescar_tablero"
Cohesion: 0.15
Nodes (6): (y del título, margen superior) medidos con las fuentes de verdad. La barra más…, Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Barras verticales: personas investigadas por mes. La barra mide las PERSONAS;…, Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 13 - "Control de Oficios — Unidad de Cumplimiento"
Cohesion: 0.15
Nodes (12): 2.2 Bitácora de auditoría, 3.1 `herramienta_admin.py` (utilidad de consola), 3.2 Referencia UDC y secuencial inicial, 3.3 Búsqueda de oficios, 3.4 Catálogo de tipos de acción, 3.5 Datos de prueba, 3. Estructura, 4.1 Uso compartido por varias personas (+4 more)

### Community 14 - "._responsable_por_display"
Cohesion: 0.17
Nodes (8): Repuebla los desplegables de filtro conservando lo elegido. El tipo de acción…, Precarga el panel de edición con los datos del oficio seleccionado. Solo…, Repuebla los desplegables del tablero conservando lo elegido., Oficios visibles tras aplicar los filtros del tablero., Texto que se muestra en los desplegables para un responsable. Incluye el…, Personas a las que se les puede asignar un oficio. Un administrador no puede…, A partir del texto del desplegable devuelve (usuario, nombre). Para "(Sin…, Tipos de acción del catálogo, para los desplegables.

### Community 15 - "._construir_configuracion"
Cohesion: 0.24
Nodes (5): Permite al superusuario o a un administrador indicar la última Referencia UDC…, Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana. Con un…, Catálogo de tipos de acción, mantenible por los gestores., Panel para volcar de una vez el histórico de la matriz de Excel., Panel de copias de seguridad. Solo lo ve el superusuario.

### Community 16 - "_leer_registros"
Cohesion: 0.09
Nodes (32): actualizar_implicado(), adjuntar_respuesta(), agregar_implicado(), contar_por_tipo_accion(), eliminar_implicado(), eliminar_respuesta(), _guardar_documento(), _guardar_registros() (+24 more)

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
Cohesion: 0.20
Nodes (10): 2.1 Roles de usuario, Campos del oficio, Carga masiva de oficios, Documento del oficio, Exportar oficios, Implicados (personas investigadas), Mantenimiento de oficios, Responsables de oficios (+2 more)

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

### Community 27 - "almacen_oficios.py"
Cohesion: 0.12
Nodes (24): causales_registradas(), _encabezados_exportacion(), exportar_csv(), exportar_oficios(), exportar_xlsx(), _fila_exportacion(), filas_exportacion(), hay_soporte_xlsx() (+16 more)

### Community 30 - "Fuente del manual de usuario"
Cohesion: 0.33
Nodes (5): Al actualizar el manual, Archivos, Compilar, Dependencias, Fuente del manual de usuario

### Community 31 - "._al_recuperar_foco"
Cohesion: 0.13
Nodes (7): Restablece el formulario para crear un usuario nuevo., Diálogo modal para escribir y confirmar una nueva contraseña. Devuelve la…, Refresca la vista al volver a la ventana. Con varias personas usando la misma…, Repuebla los desplegables de responsable con los usuarios actuales., ¿El usuario en sesión puede gestionar a ese usuario? Se consulta antes de abrir…, Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario puede crear…

### Community 32 - "dependencies"
Cohesion: 0.50
Nodes (3): docx, dependencies, docx

### Community 33 - "respaldo.py"
Cohesion: 0.08
Nodes (32): bloquear(), _esta_abandonado(), Path, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`. Lanza ValueError si…, _ruta_bloqueo(), date, _fechas_recepcion() (+24 more)

### Community 36 - "._mostrar_pdf"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word, con el…, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece el lector…

### Community 38 - "SelectorFecha"
Cohesion: 0.20
Nodes (4): Fecha desde la que se abre el calendario (la escrita, o hoy)., Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no cabe debajo,…, Campo de fecha con calendario emergente. No requiere librerías externas.…, SelectorFecha

### Community 39 - "2.3 Tablero (dashboard)"
Cohesion: 0.67
Nodes (3): 2.3 Tablero (dashboard), Filtros del tablero, Métricas

### Community 40 - ".__init__"
Cohesion: 0.18
Nodes (4): Ancho de corte de las etiquetas de los formularios. El corte es el 45 % del…, Marco superior con logo y título., Crea la copia del día en segundo plano. Va en un hilo aparte para que la…, `permitir_vacio=True` deja el campo en blanco y ofrece un botón "Limpiar" en el…

### Community 41 - "aplicacion.py"
Cohesion: 0.22
Nodes (6): DialogoExportar, iniciar(), maximizar_ventana(), Exporta a CSV los oficios de una fecha o de un rango de fechas., Exporta los oficios, con o sin acotarlos por fecha. Sin fechas se exporta…, Abre la ventana ocupando toda la pantalla, sin bloquear el redimensionado. No…

### Community 42 - "DialogoCargaMasiva"
Cohesion: 0.33
Nodes (3): DialogoCargaMasiva, Muestra qué se va a importar y, si se confirma, lo guarda. La carga no se hace…, Resume en pocas líneas lo que conviene saber antes de confirmar.

## Knowledge Gaps
- **64 isolated node(s):** `2.2 Bitácora de auditoría`, `3.1 `herramienta_admin.py` (utilidad de consola)`, `3.2 Referencia UDC y secuencial inicial`, `3.3 Búsqueda de oficios`, `3.4 Catálogo de tipos de acción` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `AplicacionPrincipal` to `VentanaIngreso`, `._mostrar_pdf`, `.__init__`, `aplicacion.py`, `DialogoCargaMasiva`, `._refrescar_listado`, `._refrescar_tablero`, `._responsable_por_display`, `._construir_configuracion`, `._construir_registro`, `._guardar_oficio`, `._al_recuperar_foco`?**
  _High betweenness centrality (0.312) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `SelectorFecha` to `.__init__`, `aplicacion.py`, `DialogoMantenimiento`, `._construir_registro`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `ValueError` (e.g. with `cambiar_clave_propia()` and `crear_usuario()`) actually correct?**
  _`ValueError` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `2.2 Bitácora de auditoría`, `3.1 `herramienta_admin.py` (utilidad de consola)`, `3.2 Referencia UDC y secuencial inicial` to the rest of the system?**
  _64 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ValueError` be split into smaller, more focused modules?**
  _Cohesion score 0.1024390243902439 - nodes in this community are weakly interconnected._
- **Should `tipos_accion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._
- **Should `carga_masiva.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._