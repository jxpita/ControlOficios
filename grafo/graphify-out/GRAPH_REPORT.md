# Graph Report - .  (2026-07-30)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 293 nodes · 615 edges · 17 communities (16 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bb7e3422`
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
1. `AplicacionPrincipal` - 56 edges
2. `registrar()` - 19 edges
3. `VentanaIngreso` - 17 edges
4. `SelectorFecha` - 15 edges
5. `VisorPDF` - 13 edges
6. `_leer_registros()` - 12 edges
7. `con_bloqueo()` - 12 edges
8. `descifrar()` - 11 edges
9. `registrar_oficio()` - 10 edges
10. `adjuntar_respuesta()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `_leer_registros()` --calls--> `descifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `cifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `escribir_bytes_protegido()`  [EXTRACTED]
  almacen_oficios.py → permisos.py
- `_generar_referencia()` --calls--> `obtener_secuencial_inicial()`  [EXTRACTED]
  almacen_oficios.py → parametros.py
- `adjuntar_respuesta()` --calls--> `hacer_escribible()`  [EXTRACTED]
  almacen_oficios.py → permisos.py

## Import Cycles
- None detected.

## Communities (17 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (37): bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), _cifrador() (+29 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (38): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), eliminar_respuesta(), filtrar_oficios(), _generar_referencia(), _guardar_registros(), _leer_registros() (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (26): _buscar(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios() (+18 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (5): iniciar(), Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (5): AplicacionPrincipal, Permite al superusuario o a un administrador indicar la última         Referenci, Panel de copias de seguridad. Solo lo ve el superusuario., Desplaza el área que está bajo el puntero.          Si el cursor está sobre una, Muestra el PDF de respuesta dentro de la aplicación.

### Community 6 - "Community 6"
Cohesion: 0.23
Nodes (15): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz: solo, Cantidad de oficios por responsable, de mayor a menor.     Los oficios sin respo, Cantidad por estado, en el orden definido en configuracion.ESTADOS. (+7 more)

### Community 7 - "Community 7"
Cohesion: 0.22
Nodes (15): date, _archivos_a_respaldar(), crear_respaldo(), crear_respaldo_silencioso(), existe_del_dia(), listar_respaldos(), purgar_antiguos(), Path (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (5): Busca solo entre los oficios visibles para el usuario en sesión., Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Devuelve la clave interna a partir de la etiqueta mostrada., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado).

### Community 9 - "Community 9"
Cohesion: 0.20
Nodes (5): Texto que se muestra en los desplegables para un responsable.         Incluye el, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Precarga el panel de edición con los datos del oficio seleccionado., Guarda los cambios del panel según el rol: el gestor puede cambiar         respo

### Community 10 - "Community 10"
Cohesion: 0.23
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (4): Restablece el formulario para crear un usuario nuevo., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 12 - "Community 12"
Cohesion: 0.23
Nodes (12): anexar_texto(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.20
Nodes (4): Tablero con scroll vertical: tarjetas de indicadores y gráficos., Marco superior con logo y título., Crea la copia del día en segundo plano.          Va en un hilo aparte para que l, Convierte un contenedor en un área con scroll vertical.          Devuelve (lienz

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 5` to `Community 3`, `Community 8`, `Community 9`, `Community 11`, `Community 13`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.430) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 10` to `Community 8`, `Community 9`, `Community 3`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07641196013289037 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.10121457489878542 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.14814814814814814 - nodes in this community are weakly interconnected._