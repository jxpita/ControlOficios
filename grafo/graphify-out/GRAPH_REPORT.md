# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 186 nodes · 385 edges · 9 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d0093b2b`
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

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 35 edges
2. `VentanaIngreso` - 17 edges
3. `SelectorFecha` - 14 edges
4. `registrar()` - 13 edges
5. `VisorPDF` - 13 edges
6. `_leer_usuarios()` - 10 edges
7. `adjuntar_respuesta()` - 9 edges
8. `descifrar()` - 9 edges
9. `_leer_registros()` - 8 edges
10. `registrar_oficio()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_leer_registros()` --calls--> `descifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `cifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `escribir_bytes_protegido()`  [EXTRACTED]
  almacen_oficios.py → permisos.py
- `registrar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `actualizar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py

## Import Cycles
- None detected.

## Communities (9 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (13): AplicacionPrincipal, Marco superior con logo y título., Texto que se muestra en los desplegables para un responsable.         Incluye el, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, Repuebla los desplegables de responsable con los usuarios actuales., True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Precarga el panel de edición con los datos del oficio seleccionado., Guarda los cambios del panel según el rol: el gestor puede cambiar         respo (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.16
Nodes (24): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (23): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), _generar_referencia(), _guardar_registros(), _leer_registros(), _puede_editar(), Capa de almacenamiento de OFICIOS.  *** Punto clave de arquitectura *** Toda la (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (5): iniciar(), Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 5 - "Community 5"
Cohesion: 0.20
Nodes (13): _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Fernet (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.23
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 7 - "Community 7"
Cohesion: 0.24
Nodes (12): anexar_texto_protegido(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.48
Nodes (6): listar_oficios(), _convertir_fecha(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz: solo, Oficios recibidos por día en los últimos N días (para el gráfico)., resumen(), serie_por_dia()

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 0` to `Community 3`?**
  _High betweenness centrality (0.373) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 6` to `Community 0`, `Community 3`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08985507246376812 - nodes in this community are weakly interconnected._