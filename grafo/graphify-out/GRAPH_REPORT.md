# Graph Report - .  (2026-08-06)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 307 nodes · 639 edges · 17 communities (15 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `344b71a1`
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

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 58 edges
2. `registrar()` - 19 edges
3. `VentanaIngreso` - 17 edges
4. `SelectorFecha` - 15 edges
5. `VisorPDF` - 13 edges
6. `_leer_registros()` - 12 edges
7. `con_bloqueo()` - 12 edges
8. `editar_usuario()` - 11 edges
9. `descifrar()` - 11 edges
10. `registrar_oficio()` - 10 edges

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

## Communities (17 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (35): _buscar(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios() (+27 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (34): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), eliminar_respuesta(), filtrar_oficios(), _generar_referencia(), _guardar_registros(), _leer_registros() (+26 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (29): _cifrador(), cifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Fernet, analizar_referencia(), definir_secuencial_inicial(), esta_configurado() (+21 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (23): listar_oficios(), iniciar(), _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al (+15 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (8): AplicacionPrincipal, Tablero con scroll vertical: tarjetas de indicadores y gráficos., Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable., Convierte un contenedor en un área con scroll vertical.          Devuelve (lienz, Muestra el PDF de respuesta dentro de la aplicación.

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (8): Texto que se muestra en los desplegables para un responsable.         Incluye el, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, Busca solo entre los oficios visibles para el usuario en sesión., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Precarga el panel de edición con los datos del oficio seleccionado., Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Carga un PDF con la respuesta del oficio seleccionado.

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (18): bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), descifrar() (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.22
Nodes (4): Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 9 - "Community 9"
Cohesion: 0.22
Nodes (15): date, _archivos_a_respaldar(), crear_respaldo(), crear_respaldo_silencioso(), existe_del_dia(), listar_respaldos(), purgar_antiguos(), Path (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.19
Nodes (5): Restablece el formulario para crear un usuario nuevo., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 11 - "Community 11"
Cohesion: 0.23
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (4): Permite al superusuario o a un administrador indicar la última         Referenci, Panel de copias de seguridad. Solo lo ve el superusuario., Marco superior con logo y título., Crea la copia del día en segundo plano.          Va en un hilo aparte para que l

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (3): Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Devuelve la clave interna a partir de la etiqueta mostrada., Elimina el PDF adjunto (por si se cargó el archivo equivocado).

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 4` to `Community 3`, `Community 5`, `Community 7`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.432) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 11` to `Community 5`, `Community 3`, `Community 13`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `VentanaIngreso` connect `Community 7` to `Community 3`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.10960960960960961 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.1092436974789916 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.10080645161290322 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.12307692307692308 - nodes in this community are weakly interconnected._