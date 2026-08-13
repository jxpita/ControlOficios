# Graph Report - .  (2026-08-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 649 nodes · 1337 edges · 39 communities (35 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1bb7e573`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ValueError
- aplicacion.py
- tipos_accion.py
- carga_masiva.py
- autenticacion.py
- ._valores_responsables
- configuracion.py
- AplicacionPrincipal
- DialogoImplicados
- parametros.py
- VisorPDF
- .get
- ._puede_gestionar_usuarios
- Control de Oficios — Unidad de Cumplimiento
- respaldo.py
- ._construir_configuracion
- registrar
- .__init__
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
- _leer_registros
- Fuente del manual de usuario
- ._aviso_sin_alcance
- dependencies
- descifrar
- compilar.sh
- logo.py
- ._oficio_por_referencia
- paginas.py
- _validar_asignacion

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 91 edges
2. `registrar()` - 32 edges
3. `con_bloqueo()` - 25 edges
4. `_leer_registros()` - 24 edges
5. `registrar_oficio()` - 21 edges
6. `_guardar_registros()` - 18 edges
7. `Control de Oficios — Unidad de Cumplimiento` - 18 edges
8. `actualizar_oficio()` - 17 edges
9. `SelectorFecha` - 17 edges
10. `VentanaIngreso` - 16 edges

## Surprising Connections (you probably didn't know these)
- `_leer_registros()` --calls--> `descifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `purgar_formato_anterior()` --calls--> `_leer_registros()`  [EXTRACTED]
  herramienta_admin.py → almacen_oficios.py
- `_guardar_registros()` --calls--> `cifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `escribir_bytes_protegido()`  [EXTRACTED]
  almacen_oficios.py → permisos.py
- `purgar_formato_anterior()` --calls--> `_guardar_registros()`  [EXTRACTED]
  herramienta_admin.py → almacen_oficios.py

## Import Cycles
- None detected.

## Communities (39 total, 4 thin omitted)

### Community 0 - "ValueError"
Cohesion: 0.12
Nodes (37): actualizar_estado_asignado(), actualizar_oficio(), corregir_oficio(), _exigir_cantidad_coherente(), _exigir_datos_para_finalizar(), _exigir_no_anulado(), _FilaRepetida, filtrar_oficios() (+29 more)

### Community 1 - "aplicacion.py"
Cohesion: 0.06
Nodes (21): DialogoCargaMasiva, DialogoExportar, DialogoMantenimiento, iniciar(), maximizar_ventana(), Fecha desde la que se abre el calendario (la escrita, o hoy)., Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Exporta a CSV los oficios de una fecha o de un rango de fechas. (+13 more)

### Community 2 - "tipos_accion.py"
Cohesion: 0.22
Nodes (18): agregar(), eliminar(), _exigir_gestor(), existe(), _guardar(), _leer(), listar(), _normalizar() (+10 more)

### Community 3 - "carga_masiva.py"
Cohesion: 0.10
Nodes (35): _a_fecha(), _a_texto(), agrupar_por_referencia(), _claves_de(), coincidencias(), emparejar_responsables(), _implicado_de(), leer_archivo() (+27 more)

### Community 4 - "autenticacion.py"
Cohesion: 0.10
Nodes (39): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+31 more)

### Community 5 - "._valores_responsables"
Cohesion: 0.19
Nodes (6): Repuebla los desplegables de filtro conservando lo elegido.          El tipo de, Precarga el panel de edición con los datos del oficio seleccionado.          Sol, Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Texto que se muestra en los desplegables para un responsable.         Incluye el, Personas a las que se les puede asignar un oficio.          Un administrador no, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si

### Community 6 - "configuracion.py"
Cohesion: 0.13
Nodes (22): listar_oficios(), _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al, Ruta de la carpeta de datos indicada por el usuario, o None.      Se busca en do (+14 more)

### Community 7 - "AplicacionPrincipal"
Cohesion: 0.09
Nodes (10): AplicacionPrincipal, Ajusta cuántas filas muestra la tabla de oficios al alto disponible.          De, Abre el documento del oficio (PDF dentro de la aplicación; el Word,         con, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece         el le, Diálogo modal para escribir y confirmar una nueva contraseña.         Devuelve l, Acorta el título de la cabecera cuando la ventana es estrecha.          `pack` n, Diálogo para que el usuario en sesión cambie su propia contraseña.         Dispo (+2 more)

### Community 8 - "DialogoImplicados"
Cohesion: 0.33
Nodes (3): DialogoImplicados, Personas investigadas en un oficio: verlas, añadirlas y corregirlas.      Se abr, Deja el formulario en blanco para añadir a otra persona.

### Community 9 - "parametros.py"
Cohesion: 0.09
Nodes (40): _generar_referencia(), Genera la Referencia UDC:  REQ-UDC-<sigla>-<año>-<secuencial de 4 dígitos>., analizar_referencia(), anio_vigente(), _clave(), definir_secuencial_inicial(), esta_configurado(), formatear_referencia() (+32 more)

### Community 10 - "VisorPDF"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 11 - ".get"
Cohesion: 0.12
Nodes (7): Panel de búsqueda. Tres bloques que se acumulan entre sí:          - por texto,, Valor elegido en un desplegable de filtro, o '' si es "(Todos)"., Devuelve la clave interna a partir de la etiqueta mostrada., Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Nombre del tipo elegido en la lista, sin el contador.

### Community 12 - "._puede_gestionar_usuarios"
Cohesion: 0.13
Nodes (8): (y del título, margen superior) medidos con las fuentes de verdad.          La b, Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas

### Community 13 - "Control de Oficios — Unidad de Cumplimiento"
Cohesion: 0.14
Nodes (13): 2.2 Bitácora de auditoría, 2.3 Tablero (dashboard), 3.1 `herramienta_admin.py` (utilidad de consola), 3.2 Referencia UDC y secuencial inicial, 3.3 Búsqueda de oficios, 3.4 Catálogo de tipos de acción, 3.5 Datos de prueba, 3. Estructura (+5 more)

### Community 14 - "respaldo.py"
Cohesion: 0.11
Nodes (24): date, _fechas_recepcion(), generar_filas(), _mes_atras(), Genera el archivo de datos de prueba para la carga masiva.  Crea `Matriz de prue, (año, mes) de la fecha indicada retrocediendo esa cantidad de meses., Fecha de recepción de cada oficio, repartida según los dos patrones., Una fila por investigado. Algunos oficios repiten Referencia oficio para     que (+16 more)

### Community 15 - "._construir_configuracion"
Cohesion: 0.24
Nodes (5): Permite al superusuario o a un administrador indicar la última         Referenci, Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana.          Con, Catálogo de tipos de acción, mantenible por los gestores., Panel para volcar de una vez el histórico de la matriz de Excel., Panel de copias de seguridad. Solo lo ve el superusuario.

### Community 16 - "registrar"
Cohesion: 0.13
Nodes (27): actualizar_implicado(), adjuntar_respuesta(), agregar_implicado(), eliminar_implicado(), eliminar_respuesta(), _guardar_registros(), importar_oficios(), _oficio_editable() (+19 more)

### Community 17 - ".__init__"
Cohesion: 0.10
Nodes (10): Ancho de corte de las etiquetas de los formularios.          El corte es el 45 %, Repuebla los desplegables de tipo de acción tras cambiar el catálogo., Tablero con scroll vertical: tarjetas de indicadores y gráficos., Marco superior con logo y título., Crea la copia del día en segundo plano.          Va en un hilo aparte para que l, Convierte un contenedor en un área con scroll vertical.          Devuelve (lienz, Tipos de acción del catálogo, para los desplegables., Ancho de una columna de tabla: el mayor entre lo que pide el dato y         lo q (+2 more)

### Community 18 - "manual.js"
Cohesion: 0.09
Nodes (12): bandaAzul, contenido, doc, {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, Footer, PageNumber, Tab, TabStopType, LeaderType,
}, ENTRADAS, fs, h1(), h2() (+4 more)

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
Cohesion: 0.13
Nodes (24): causales_registradas(), _encabezados_exportacion(), exportar_csv(), exportar_oficios(), exportar_xlsx(), _fila_exportacion(), filas_exportacion(), _guardar_documento() (+16 more)

### Community 29 - "_leer_registros"
Cohesion: 0.16
Nodes (14): anular_oficio(), contar_por_tipo_accion(), esta_anulado(), _leer_registros(), listar_implicados(), listar_oficios_visibles(), proxima_referencia(), Implicados anotados en un oficio, en el orden en que se registraron. (+6 more)

### Community 30 - "Fuente del manual de usuario"
Cohesion: 0.33
Nodes (5): Al actualizar el manual, Archivos, Compilar, Dependencias, Fuente del manual de usuario

### Community 31 - "._aviso_sin_alcance"
Cohesion: 0.21
Nodes (4): Restablece el formulario para crear un usuario nuevo., ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 32 - "dependencies"
Cohesion: 0.50
Nodes (3): docx, dependencies, docx

### Community 33 - "descifrar"
Cohesion: 0.15
Nodes (18): bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), descifrar() (+10 more)

### Community 36 - "._oficio_por_referencia"
Cohesion: 0.33
Nodes (3): Corrige los datos de identificación de un oficio, o lo retira., Abre los implicados del oficio sobre el que se hizo doble clic., Busca solo entre los oficios visibles para el usuario en sesión.          Incluy

### Community 38 - "_validar_asignacion"
Cohesion: 0.50
Nodes (4): Rol del usuario indicado, o '' si no existe., Un ADMINISTRADOR no puede asignar oficios a un superusuario.      El superusuari, _rol_de(), _validar_asignacion()

## Knowledge Gaps
- **62 isolated node(s):** `compilar.sh script`, `fs`, `{
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, Footer, PageNumber, Tab, TabStopType, LeaderType,
}`, `bandaAzul`, `portada` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `AplicacionPrincipal` to `aplicacion.py`, `._oficio_por_referencia`, `._valores_responsables`, `.get`, `._puede_gestionar_usuarios`, `._construir_configuracion`, `.__init__`, `._guardar_oficio`, `._aviso_sin_alcance`?**
  _High betweenness centrality (0.290) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `aplicacion.py` to `.__init__`, `.get`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `ValueError` (e.g. with `cambiar_clave_propia()` and `crear_usuario()`) actually correct?**
  _`ValueError` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `compilar.sh script`, `fs`, `{
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, Footer, PageNumber, Tab, TabStopType, LeaderType,
}` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ValueError` be split into smaller, more focused modules?**
  _Cohesion score 0.11561561561561562 - nodes in this community are weakly interconnected._
- **Should `aplicacion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056107539450613676 - nodes in this community are weakly interconnected._
- **Should `carga_masiva.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09682539682539683 - nodes in this community are weakly interconnected._