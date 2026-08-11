# Graph Report - .  (2026-08-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 433 nodes · 944 edges · 19 communities
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5ecff425`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 72 edges
2. `registrar()` - 26 edges
3. `_leer_registros()` - 18 edges
4. `con_bloqueo()` - 18 edges
5. `registrar_oficio()` - 17 edges
6. `SelectorFecha` - 17 edges
7. `VentanaIngreso` - 16 edges
8. `_guardar_registros()` - 14 edges
9. `actualizar_oficio()` - 14 edges
10. `VisorPDF` - 13 edges

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

## Communities (19 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (79): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), anular_oficio(), corregir_oficio(), eliminar_respuesta(), esta_anulado(), _exigir_datos_para_finalizar() (+71 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (16): DialogoCargaMasiva, DialogoExportar, DialogoMantenimiento, iniciar(), maximizar_ventana(), Exporta a CSV los oficios de una fecha o de un rango de fechas., Corrige los datos de identificación de un oficio y permite retirarlo.      Son l, Muestra qué se va a importar y, si se confirma, lo guarda.      La carga no se h (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (41): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+33 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (29): _a_fecha(), _a_texto(), agrupar_por_referencia(), _claves_de(), coincidencias(), emparejar_responsables(), leer_archivo(), _leer_csv() (+21 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (27): analizar_referencia(), definir_secuencial_inicial(), esta_configurado(), _guardar(), _leer(), obtener_referencia_inicial(), obtener_secuencial_inicial(), Parámetros del sistema (archivo cifrado `datos/parametros.dat`).  Hoy guarda un (+19 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (22): listar_oficios(), _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al, Ruta de la carpeta de datos indicada por el usuario, o None.      Se busca en do (+14 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (7): AplicacionPrincipal, Ajusta cuántas filas muestra la tabla de oficios al alto disponible.          De, Diálogo modal para escribir y confirmar una nueva contraseña.         Devuelve l, Acorta el título de la cabecera cuando la ventana es estrecha.          `pack` n, Diálogo para que el usuario en sesión cambie su propia contraseña.         Dispo, Desplaza el área que está bajo el puntero.          Si el cursor está sobre una, Coloca una etiqueta y su campo en una fila del grupo.          Con `estirar` el

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (7): Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Corrige los datos de identificación de un oficio, o lo retira., Busca solo entre los oficios visibles para el usuario en sesión.          Incluy, Devuelve la clave interna a partir de la etiqueta mostrada.

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 9 - "Community 9"
Cohesion: 0.14
Nodes (7): Tablero con scroll vertical: tarjetas de indicadores y gráficos., Marco superior con logo y título., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Crea la copia del día en segundo plano.          Va en un hilo aparte para que l, Convierte un contenedor en un área con scroll vertical.          Devuelve (lienz, Recuadro con título para agrupar campos afines., Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (16): bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), _cargar() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (6): Restablece el formulario para crear un usuario nuevo., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 12 - "Community 12"
Cohesion: 0.18
Nodes (5): Fecha desde la que se abre el calendario (la escrita, o hoy)., Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, SelectorFecha

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (15): date, _archivos_a_respaldar(), crear_respaldo(), crear_respaldo_silencioso(), existe_del_dia(), listar_respaldos(), purgar_antiguos(), Path (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.24
Nodes (4): Precarga el panel de edición con los datos del oficio seleccionado.          Sol, Texto que se muestra en los desplegables para un responsable.         Incluye el, Personas a las que se les puede asignar un oficio.          Un administrador no, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si

### Community 15 - "Community 15"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 16 - "Community 16"
Cohesion: 0.28
Nodes (4): Permite al superusuario o a un administrador indicar la última         Referenci, Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana.          Con, Panel para volcar de una vez el histórico de la matriz de Excel., Panel de copias de seguridad. Solo lo ve el superusuario.

### Community 17 - "Community 17"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word,         con, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece         el le

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 6` to `Community 1`, `Community 7`, `Community 9`, `Community 11`, `Community 14`, `Community 15`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.401) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 12` to `Community 1`, `Community 9`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `ValueError` (e.g. with `cambiar_clave_propia()` and `crear_usuario()`) actually correct?**
  _`ValueError` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06424050632911392 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07641196013289037 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09634551495016612 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.11264367816091954 - nodes in this community are weakly interconnected._