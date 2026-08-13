# Graph Report - .  (2026-08-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 545 nodes · 1144 edges · 27 communities
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9376e57e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- almacen_oficios.py
- aplicacion.py
- tipos_accion.py
- carga_masiva.py
- autenticacion.py
- .__init__
- configuracion.py
- AplicacionPrincipal
- herramienta_admin.py
- parametros.py
- VisorPDF
- .get
- ._al_recuperar_foco
- Control de Oficios — Unidad de Cumplimiento
- permisos.py
- ._construir_configuracion
- ._refrescar_tablero
- ._aplicar_cambios
- ._mostrar_pdf
- 4. Compilar a ejecutable (lo más ligero posible)
- 2.1 Roles de usuario
- Grafo de conocimiento (graphify)
- 4.2 Despliegue en una carpeta compartida (varias personas)
- 4.3 Copia de seguridad programada (opcional, en otro disco)
- 1. Requisitos
- 2. Ejecutar en desarrollo

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 81 edges
2. `registrar()` - 29 edges
3. `con_bloqueo()` - 22 edges
4. `_leer_registros()` - 20 edges
5. `registrar_oficio()` - 19 edges
6. `Control de Oficios — Unidad de Cumplimiento` - 18 edges
7. `SelectorFecha` - 17 edges
8. `VentanaIngreso` - 16 edges
9. `_guardar_registros()` - 15 edges
10. `actualizar_oficio()` - 15 edges

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

## Communities (27 total, 0 thin omitted)

### Community 0 - "almacen_oficios.py"
Cohesion: 0.06
Nodes (85): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), anular_oficio(), contar_por_tipo_accion(), corregir_oficio(), eliminar_respuesta(), esta_anulado() (+77 more)

### Community 1 - "aplicacion.py"
Cohesion: 0.06
Nodes (21): DialogoCargaMasiva, DialogoExportar, DialogoMantenimiento, iniciar(), maximizar_ventana(), Fecha desde la que se abre el calendario (la escrita, o hoy)., Exporta a CSV los oficios de una fecha o de un rango de fechas., Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe (+13 more)

### Community 2 - "tipos_accion.py"
Cohesion: 0.22
Nodes (18): agregar(), eliminar(), _exigir_gestor(), existe(), _guardar(), _leer(), listar(), _normalizar() (+10 more)

### Community 3 - "carga_masiva.py"
Cohesion: 0.08
Nodes (36): _a_fecha(), _a_texto(), agrupar_por_referencia(), _claves_de(), coincidencias(), emparejar_responsables(), leer_archivo(), _leer_csv() (+28 more)

### Community 4 - "autenticacion.py"
Cohesion: 0.10
Nodes (41): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+33 more)

### Community 5 - ".__init__"
Cohesion: 0.11
Nodes (11): Precarga el panel de edición con los datos del oficio seleccionado.          Sol, Tablero con scroll vertical: tarjetas de indicadores y gráficos., Marco superior con logo y título., Texto que se muestra en los desplegables para un responsable.         Incluye el, Personas a las que se les puede asignar un oficio.          Un administrador no, True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Crea la copia del día en segundo plano.          Va en un hilo aparte para que l, Convierte un contenedor en un área con scroll vertical.          Devuelve (lienz (+3 more)

### Community 6 - "configuracion.py"
Cohesion: 0.13
Nodes (22): listar_oficios(), _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al, Ruta de la carpeta de datos indicada por el usuario, o None.      Se busca en do (+14 more)

### Community 7 - "AplicacionPrincipal"
Cohesion: 0.10
Nodes (9): AplicacionPrincipal, Ajusta cuántas filas muestra la tabla de oficios al alto disponible.          De, Diálogo modal para escribir y confirmar una nueva contraseña.         Devuelve l, Acorta el título de la cabecera cuando la ventana es estrecha.          `pack` n, Diálogo para que el usuario en sesión cambie su propia contraseña.         Dispo, ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Muestra el motivo si no se puede gestionar. True = sin permisos., Desplaza el área que está bajo el puntero.          Si el cursor está sobre una (+1 more)

### Community 8 - "herramienta_admin.py"
Cohesion: 0.08
Nodes (34): bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), date (+26 more)

### Community 9 - "parametros.py"
Cohesion: 0.19
Nodes (19): analizar_referencia(), definir_secuencial_inicial(), esta_configurado(), formatear_referencia(), _guardar(), institucion_de(), _leer(), obtener_referencia_inicial() (+11 more)

### Community 10 - "VisorPDF"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 11 - ".get"
Cohesion: 0.11
Nodes (8): Devuelve la clave interna a partir de la etiqueta mostrada., Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Corrige los datos de identificación de un oficio, o lo retira., Repuebla los desplegables de tipo de acción tras cambiar el catálogo., Nombre del tipo elegido en la lista, sin el contador., Busca solo entre los oficios visibles para el usuario en sesión.          Incluy

### Community 12 - "._al_recuperar_foco"
Cohesion: 0.22
Nodes (4): Restablece el formulario para crear un usuario nuevo., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 13 - "Control de Oficios — Unidad de Cumplimiento"
Cohesion: 0.14
Nodes (13): 2.2 Bitácora de auditoría, 2.3 Tablero (dashboard), 3.1 `herramienta_admin.py` (utilidad de consola), 3.2 Referencia UDC y secuencial inicial, 3.3 Búsqueda de oficios, 3.4 Catálogo de tipos de acción, 3.5 Datos de prueba, 3. Estructura (+5 more)

### Community 14 - "permisos.py"
Cohesion: 0.23
Nodes (12): anexar_texto(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 15 - "._construir_configuracion"
Cohesion: 0.24
Nodes (5): Permite al superusuario o a un administrador indicar la última         Referenci, Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana.          Con, Catálogo de tipos de acción, mantenible por los gestores., Panel para volcar de una vez el histórico de la matriz de Excel., Panel de copias de seguridad. Solo lo ve el superusuario.

### Community 16 - "._refrescar_tablero"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 17 - "._aplicar_cambios"
Cohesion: 0.25
Nodes (3): Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, Adelanta la Referencia UDC que se asignará al oficio en curso.          Depende

### Community 18 - "._mostrar_pdf"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word,         con, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece         el le

### Community 20 - "4. Compilar a ejecutable (lo más ligero posible)"
Cohesion: 0.20
Nodes (10): 4. Compilar a ejecutable (lo más ligero posible), Consejos para que pese lo menos posible, Dónde queda todo: la carpeta `bin/`, IMPORTANTE: la carpeta `datos/` va junto al ejecutable, Opción A — CON_DEPENDENCIAS (un solo ejecutable, `--onefile`), Opción B — SIN_DEPENDENCIAS (dependencias aparte, `--onedir`), Paso previo: descomprimir UPX, Qué hace cada opción (+2 more)

### Community 21 - "2.1 Roles de usuario"
Cohesion: 0.22
Nodes (9): 2.1 Roles de usuario, Campos del oficio, Carga masiva de oficios, Documento del oficio, Exportar oficios, Mantenimiento de oficios, Responsables de oficios, Respuesta en PDF (+1 more)

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
Cohesion: 0.67
Nodes (3): 2. Ejecutar en desarrollo, Cómo se adaptan las pantallas, Tamaño de la ventana

## Knowledge Gaps
- **45 isolated node(s):** `Dependencias`, `IMPORTANTE: actualizar el grafo tras CADA cambio de código`, `Qué se versiona y qué no`, `Consultar el grafo`, `Dependencias externas` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `AplicacionPrincipal` to `aplicacion.py`, `.__init__`, `.get`, `._al_recuperar_foco`, `._construir_configuracion`, `._refrescar_tablero`, `._aplicar_cambios`, `._mostrar_pdf`?**
  _High betweenness centrality (0.323) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `aplicacion.py` to `.__init__`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `ValueError` (e.g. with `cambiar_clave_propia()` and `crear_usuario()`) actually correct?**
  _`ValueError` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependencias`, `IMPORTANTE: actualizar el grafo tras CADA cambio de código`, `Qué se versiona y qué no` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `almacen_oficios.py` be split into smaller, more focused modules?**
  _Cohesion score 0.059370725034199726 - nodes in this community are weakly interconnected._
- **Should `aplicacion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056107539450613676 - nodes in this community are weakly interconnected._
- **Should `carga_masiva.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08367071524966262 - nodes in this community are weakly interconnected._