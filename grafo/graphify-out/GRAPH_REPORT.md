# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 246 nodes · 512 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b7ca4bcf`
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
1. `AplicacionPrincipal` - 48 edges
2. `VentanaIngreso` - 17 edges
3. `registrar()` - 16 edges
4. `SelectorFecha` - 15 edges
5. `VisorPDF` - 13 edges
6. `_leer_registros()` - 11 edges
7. `descifrar()` - 11 edges
8. `_leer_usuarios()` - 10 edges
9. `_guardar_registros()` - 9 edges
10. `registrar_oficio()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `_guardar_registros()` --calls--> `escribir_bytes_protegido()`  [EXTRACTED]
  almacen_oficios.py → permisos.py
- `_generar_referencia()` --calls--> `obtener_secuencial_inicial()`  [EXTRACTED]
  almacen_oficios.py → parametros.py
- `registrar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `actualizar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `actualizar_estado_asignado()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py

## Import Cycles
- None detected.

## Communities (16 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (45): actualizar_estado_asignado(), actualizar_oficio(), eliminar_respuesta(), filtrar_oficios(), _generar_referencia(), _guardar_registros(), _leer_registros(), listar_oficios_visibles() (+37 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (23): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+15 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (5): iniciar(), Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (17): adjuntar_respuesta(), Devuelve la ruta del PDF de respuesta adjunto, o None si no hay., Copia un PDF de respuesta a datos/respuestas/ y lo asocia al oficio.      El arc, ruta_respuesta(), Path, anexar_texto_protegido(), _chmod(), escribir_bytes_protegido() (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (15): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz: solo, Cantidad de oficios por responsable, de mayor a menor.     Los oficios sin respo, Cantidad por estado, en el orden definido en configuracion.ESTADOS. (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (5): A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado).

### Community 7 - "Community 7"
Cohesion: 0.23
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 8 - "Community 8"
Cohesion: 0.19
Nodes (4): AplicacionPrincipal, Permite al superusuario o a un administrador indicar la última         Referenci, Desplaza el área que está bajo el puntero.          Si el cursor está sobre una, Muestra el PDF de respuesta dentro de la aplicación.

### Community 9 - "Community 9"
Cohesion: 0.23
Nodes (12): analizar_referencia(), definir_secuencial_inicial(), esta_configurado(), _guardar(), _leer(), obtener_referencia_inicial(), obtener_secuencial_inicial(), Parámetros del sistema (archivo cifrado `datos/parametros.dat`).  Hoy guarda un (+4 more)

### Community 10 - "Community 10"
Cohesion: 0.24
Nodes (3): Marco superior con logo y título., Repuebla los desplegables de responsable con los usuarios actuales., Restablece el formulario para crear un usuario nuevo.

### Community 11 - "Community 11"
Cohesion: 0.27
Nodes (4): Texto que se muestra en los desplegables para un responsable.         Incluye el, Busca solo entre los oficios visibles para el usuario en sesión., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Precarga el panel de edición con los datos del oficio seleccionado.

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 8` to `Community 2`, `Community 6`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.433) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 7` to `Community 2`, `Community 11`, `Community 6`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07428571428571429 - nodes in this community are weakly interconnected._