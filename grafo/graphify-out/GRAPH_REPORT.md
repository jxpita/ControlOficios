# Graph Report - .  (2026-08-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 608 nodes · 1294 edges · 37 communities (36 shown, 1 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `54de9ccd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ValueError
- aplicacion.py
- tipos_accion.py
- carga_masiva.py
- autenticacion.py
- ._construir_registro
- metricas.py
- AplicacionPrincipal
- DialogoImplicados
- parametros.py
- VisorPDF
- ._refrescar_listado
- ._refrescar_tablero
- Control de Oficios — Unidad de Cumplimiento
- respaldo.py
- ._construir_configuracion
- almacen_oficios.py
- .get
- ._mostrar_pdf
- 4. Compilar a ejecutable (lo más ligero posible)
- 2.1 Roles de usuario
- Grafo de conocimiento (graphify)
- 4.2 Despliegue en una carpeta compartida (varias personas)
- 4.3 Copia de seguridad programada (opcional, en otro disco)
- 1. Requisitos
- 2. Ejecutar en desarrollo
- exportar_oficios
- permisos.py
- con_bloqueo
- ._aviso_sin_alcance
- ._al_recuperar_foco
- configuracion.py
- herramienta_admin.py
- registrar
- cifrado.py
- filtrar_oficios

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 91 edges
2. `registrar()` - 32 edges
3. `con_bloqueo()` - 25 edges
4. `_leer_registros()` - 24 edges
5. `registrar_oficio()` - 20 edges
6. `_guardar_registros()` - 18 edges
7. `Control de Oficios — Unidad de Cumplimiento` - 18 edges
8. `SelectorFecha` - 17 edges
9. `actualizar_oficio()` - 16 edges
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

## Communities (37 total, 1 thin omitted)

### Community 0 - "ValueError"
Cohesion: 0.12
Nodes (35): actualizar_estado_asignado(), actualizar_oficio(), corregir_oficio(), _exigir_cantidad_coherente(), _exigir_datos_para_finalizar(), _exigir_no_anulado(), _FilaRepetida, _preparar_importado() (+27 more)

### Community 1 - "aplicacion.py"
Cohesion: 0.05
Nodes (22): DialogoCargaMasiva, DialogoExportar, iniciar(), maximizar_ventana(), Fecha desde la que se abre el calendario (la escrita, o hoy)., Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Exporta a CSV los oficios de una fecha o de un rango de fechas., Ancho de corte de las etiquetas de los formularios.          El corte es el 45 % (+14 more)

### Community 2 - "tipos_accion.py"
Cohesion: 0.22
Nodes (18): agregar(), eliminar(), _exigir_gestor(), existe(), _guardar(), _leer(), listar(), _normalizar() (+10 more)

### Community 3 - "carga_masiva.py"
Cohesion: 0.10
Nodes (35): _a_fecha(), _a_texto(), agrupar_por_referencia(), _claves_de(), coincidencias(), emparejar_responsables(), _implicado_de(), leer_archivo() (+27 more)

### Community 4 - "autenticacion.py"
Cohesion: 0.13
Nodes (32): _buscar(), cambiar_clave_propia(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios() (+24 more)

### Community 5 - "._construir_registro"
Cohesion: 0.09
Nodes (14): Panel de búsqueda. Tres bloques que se acumulan entre sí:          - por texto,, Repuebla los desplegables de filtro conservando lo elegido.          El tipo de, Precarga el panel de edición con los datos del oficio seleccionado.          Sol, Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Repuebla los desplegables de tipo de acción tras cambiar el catálogo., Texto que se muestra en los desplegables para un responsable.         Incluye el, Personas a las que se les puede asignar un oficio.          Un administrador no, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si (+6 more)

### Community 6 - "metricas.py"
Cohesion: 0.23
Nodes (15): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz: solo, Cantidad de oficios por responsable, de mayor a menor.     Los oficios sin respo, Cantidad por estado, en el orden definido en configuracion.ESTADOS. (+7 more)

### Community 7 - "AplicacionPrincipal"
Cohesion: 0.09
Nodes (9): AplicacionPrincipal, Suma una persona a la lista del oficio que se está registrando., Ajusta cuántas filas muestra la tabla de oficios al alto disponible.          De, Tablero con scroll vertical: tarjetas de indicadores y gráficos., Acorta el título de la cabecera cuando la ventana es estrecha.          `pack` n, Diálogo para que el usuario en sesión cambie su propia contraseña.         Dispo, Desplaza el área que está bajo el puntero.          Si el cursor está sobre una, Adelanta la Referencia UDC que se asignará al oficio en curso.          Depende (+1 more)

### Community 8 - "DialogoImplicados"
Cohesion: 0.33
Nodes (3): DialogoImplicados, Personas investigadas en un oficio: verlas, añadirlas y corregirlas.      Se abr, Deja el formulario en blanco para añadir a otra persona.

### Community 9 - "parametros.py"
Cohesion: 0.16
Nodes (25): _generar_referencia(), Genera la Referencia UDC:  REQ-UDC-<sigla>-<año>-<secuencial de 4 dígitos>., analizar_referencia(), anio_vigente(), _clave(), definir_secuencial_inicial(), esta_configurado(), formatear_referencia() (+17 more)

### Community 10 - "VisorPDF"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 11 - "._refrescar_listado"
Cohesion: 0.11
Nodes (8): Valor elegido en un desplegable de filtro, o '' si es "(Todos)"., Devuelve la clave interna a partir de la etiqueta mostrada., Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Corrige los datos de identificación de un oficio, o lo retira., Abre los implicados del oficio sobre el que se hizo doble clic., Busca solo entre los oficios visibles para el usuario en sesión.          Incluy

### Community 12 - "._refrescar_tablero"
Cohesion: 0.18
Nodes (5): (y del título, margen superior) medidos con las fuentes de verdad.          La b, Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 13 - "Control de Oficios — Unidad de Cumplimiento"
Cohesion: 0.14
Nodes (13): 2.2 Bitácora de auditoría, 2.3 Tablero (dashboard), 3.1 `herramienta_admin.py` (utilidad de consola), 3.2 Referencia UDC y secuencial inicial, 3.3 Búsqueda de oficios, 3.4 Catálogo de tipos de acción, 3.5 Datos de prueba, 3. Estructura (+5 more)

### Community 14 - "respaldo.py"
Cohesion: 0.09
Nodes (30): bloquear(), _esta_abandonado(), Path, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), date, _fechas_recepcion() (+22 more)

### Community 15 - "._construir_configuracion"
Cohesion: 0.24
Nodes (5): Permite al superusuario o a un administrador indicar la última         Referenci, Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana.          Con, Catálogo de tipos de acción, mantenible por los gestores., Panel para volcar de una vez el histórico de la matriz de Excel., Panel de copias de seguridad. Solo lo ve el superusuario.

### Community 16 - "almacen_oficios.py"
Cohesion: 0.09
Nodes (36): actualizar_implicado(), agregar_implicado(), anular_oficio(), causales_registradas(), contar_por_tipo_accion(), eliminar_implicado(), esta_anulado(), _guardar_registros() (+28 more)

### Community 17 - ".get"
Cohesion: 0.22
Nodes (3): DialogoMantenimiento, Nombre del tipo elegido en la lista, sin el contador., Corrige los datos de identificación de un oficio y permite retirarlo.      Son l

### Community 18 - "._mostrar_pdf"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word,         con, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece         el le

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

### Community 27 - "exportar_oficios"
Cohesion: 0.15
Nodes (17): _encabezados_exportacion(), exportar_csv(), exportar_oficios(), exportar_xlsx(), _fila_exportacion(), filas_exportacion(), Path, Devuelve la ruta del PDF de respuesta adjunto, o None si no hay. (+9 more)

### Community 28 - "permisos.py"
Cohesion: 0.25
Nodes (10): anexar_texto(), _chmod(), escribir_bytes_protegido(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Deja el archivo en solo lectura para el propietario (0o400)., Restringe una carpeta al propietario (0o700). (+2 more)

### Community 29 - "con_bloqueo"
Cohesion: 0.20
Nodes (14): adjuntar_respuesta(), eliminar_respuesta(), _guardar_documento(), _puede_editar(), Sustituye el documento del oficio (PDF o Word) por si se cargó el     archivo eq, Copia un PDF de respuesta a datos/respuestas/ y lo asocia al oficio.      El arc, Elimina el PDF de respuesta adjunto (por si se cargó el archivo     equivocado)., Copia un adjunto a la carpeta de datos y devuelve su nombre de archivo.      El (+6 more)

### Community 30 - "._aviso_sin_alcance"
Cohesion: 0.20
Nodes (4): Diálogo modal para escribir y confirmar una nueva contraseña.         Devuelve l, ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 31 - "._al_recuperar_foco"
Cohesion: 0.27
Nodes (3): Restablece el formulario para crear un usuario nuevo., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales.

### Community 32 - "configuracion.py"
Cohesion: 0.24
Nodes (8): Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al, Ruta de la carpeta de datos indicada por el usuario, o None.      Se busca en do

### Community 33 - "herramienta_admin.py"
Cohesion: 0.31
Nodes (9): _cargar(), _es_formato_actual(), exportar_csv_oficios(), main(), mostrar_json(), purgar_formato_anterior(), herramienta_admin.py — utilidad SOLO para el administrador. Descifra y muestra e, True si la referencia usa el formato vigente REQ-UDC-<SIGLA>-NNNN. (+1 more)

### Community 34 - "registrar"
Cohesion: 0.29
Nodes (7): cerrar_sesion(), Registra en la bitácora el cierre de sesión del usuario., Registro de actividad (auditoría) en un archivo de texto plano.  Guarda TODA acc, Último recurso: dejar la línea en un archivo local para no perderla., Añade una línea a la bitácora de auditoría.      Si la escritura falla, la línea, registrar(), _respaldar()

### Community 35 - "cifrado.py"
Cohesion: 0.36
Nodes (7): _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Fernet

## Knowledge Gaps
- **47 isolated node(s):** `Dependencias`, `IMPORTANTE: actualizar el grafo tras CADA cambio de código`, `Qué se versiona y qué no`, `Consultar el grafo`, `Dependencias externas` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `AplicacionPrincipal` to `aplicacion.py`, `._construir_registro`, `._refrescar_listado`, `._refrescar_tablero`, `._construir_configuracion`, `.get`, `._mostrar_pdf`, `._aviso_sin_alcance`, `._al_recuperar_foco`?**
  _High betweenness centrality (0.329) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `aplicacion.py` to `.get`, `._construir_registro`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `ValueError` (e.g. with `cambiar_clave_propia()` and `crear_usuario()`) actually correct?**
  _`ValueError` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependencias`, `IMPORTANTE: actualizar el grafo tras CADA cambio de código`, `Qué se versiona y qué no` to the rest of the system?**
  _47 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ValueError` be split into smaller, more focused modules?**
  _Cohesion score 0.11932773109243698 - nodes in this community are weakly interconnected._
- **Should `aplicacion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0523532522474881 - nodes in this community are weakly interconnected._
- **Should `carga_masiva.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09682539682539683 - nodes in this community are weakly interconnected._