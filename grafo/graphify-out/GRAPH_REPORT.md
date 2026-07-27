# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 241 nodes · 499 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3262aac7`
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

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 48 edges
2. `VentanaIngreso` - 17 edges
3. `SelectorFecha` - 15 edges
4. `registrar()` - 15 edges
5. `VisorPDF` - 13 edges
6. `_leer_registros()` - 11 edges
7. `descifrar()` - 11 edges
8. `_leer_usuarios()` - 10 edges
9. `registrar_oficio()` - 9 edges
10. `adjuntar_respuesta()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `_leer_registros()` --calls--> `descifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `cifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `escribir_bytes_protegido()`  [EXTRACTED]
  almacen_oficios.py → permisos.py
- `_generar_referencia()` --calls--> `obtener_secuencial_inicial()`  [EXTRACTED]
  almacen_oficios.py → parametros.py
- `registrar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py

## Import Cycles
- None detected.

## Communities (14 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (47): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), eliminar_respuesta(), filtrar_oficios(), _generar_referencia(), _guardar_registros(), _leer_registros() (+39 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (37): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+29 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (5): iniciar(), Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (6): AplicacionPrincipal, Permite al superusuario indicar la última Referencia UDC registrada         en e, Tablero con scroll vertical: tarjetas de indicadores y gráficos., Activa la rueda del ratón solo mientras el cursor está en el tablero., Marco superior con logo y título., Muestra el PDF de respuesta dentro de la aplicación.

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 6 - "Community 6"
Cohesion: 0.23
Nodes (12): analizar_referencia(), definir_secuencial_inicial(), esta_configurado(), _guardar(), _leer(), obtener_referencia_inicial(), obtener_secuencial_inicial(), Parámetros del sistema (archivo cifrado `datos/parametros.dat`).  Hoy guarda un (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.24
Nodes (12): anexar_texto_protegido(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.24
Nodes (5): Busca solo entre los oficios visibles para el usuario en sesión., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Precarga el panel de edición con los datos del oficio seleccionado., Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Carga un PDF con la respuesta del oficio seleccionado.

### Community 9 - "Community 9"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (3): Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Devuelve la clave interna a partir de la etiqueta mostrada., Elimina el PDF adjunto (por si se cargó el archivo equivocado).

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 3` to `Community 2`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`?**
  _High betweenness centrality (0.434) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 5` to `Community 3`, `Community 8`, `Community 2`, `Community 10`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07482993197278912 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.09872241579558652 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.14761904761904762 - nodes in this community are weakly interconnected._