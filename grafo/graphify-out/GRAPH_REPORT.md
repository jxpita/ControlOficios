# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 260 nodes · 550 edges · 16 communities (14 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c5c927b`
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
1. `AplicacionPrincipal` - 49 edges
2. `VentanaIngreso` - 17 edges
3. `registrar()` - 17 edges
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

## Communities (16 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (33): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+25 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (32): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), eliminar_respuesta(), filtrar_oficios(), _generar_referencia(), _guardar_registros(), _leer_registros() (+24 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (5): iniciar(), Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (19): _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Fernet, analizar_referencia() (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (6): A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Devuelve la clave interna a partir de la etiqueta mostrada., Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado).

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (15): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz: solo, Cantidad de oficios por responsable, de mayor a menor.     Los oficios sin respo, Cantidad por estado, en el orden definido en configuracion.ESTADOS. (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (15): bloquear(), _esta_abandonado(), Path, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), _cargar(), _es_formato_actual() (+7 more)

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (5): abrir_visor(), Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Ventana con el PDF renderizado página a página., VisorPDF

### Community 8 - "Community 8"
Cohesion: 0.21
Nodes (5): Marco superior con logo y título., Texto que se muestra en los desplegables para un responsable.         Incluye el, Busca solo entre los oficios visibles para el usuario en sesión., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Precarga el panel de edición con los datos del oficio seleccionado.

### Community 9 - "Community 9"
Cohesion: 0.23
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 10 - "Community 10"
Cohesion: 0.19
Nodes (4): AplicacionPrincipal, Permite al superusuario o a un administrador indicar la última         Referenci, Desplaza el área que está bajo el puntero.          Si el cursor está sobre una, Muestra el PDF de respuesta dentro de la aplicación.

### Community 11 - "Community 11"
Cohesion: 0.23
Nodes (12): anexar_texto(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.29
Nodes (3): Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., Restablece el formulario para crear un usuario nuevo.

### Community 13 - "Community 13"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 10` to `Community 2`, `Community 4`, `Community 8`, `Community 12`, `Community 13`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.425) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 9` to `Community 8`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.10099573257467995 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.11174242424242424 - nodes in this community are weakly interconnected._