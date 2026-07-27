# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 151 nodes · 321 edges · 12 communities (6 shown, 6 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3c56957`
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

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 34 edges
2. `VentanaIngreso` - 17 edges
3. `SelectorFecha` - 12 edges
4. `registrar()` - 12 edges
5. `_leer_usuarios()` - 10 edges
6. `descifrar()` - 9 edges
7. `registrar_oficio()` - 7 edges
8. `_guardar_usuarios()` - 7 edges
9. `crear_usuario()` - 7 edges
10. `editar_usuario()` - 7 edges

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

## Communities (12 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (24): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+16 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (19): actualizar_estado_asignado(), actualizar_oficio(), _generar_referencia(), _guardar_registros(), _leer_registros(), listar_oficios(), Capa de almacenamiento de OFICIOS.  *** Punto clave de arquitectura *** Toda la, Actualiza estado y/o responsable de un oficio en una sola operación,     respeta (+11 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (5): iniciar(), Cierra la sesión actual y vuelve a la pantalla de ingreso., Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, VentanaIngreso

### Community 3 - "Community 3"
Cohesion: 0.20
Nodes (13): _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Fernet (+5 more)

### Community 4 - "Community 4"
Cohesion: 0.24
Nodes (12): anexar_texto_protegido(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.31
Nodes (3): Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 6` to `Community 2`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`?**
  _High betweenness centrality (0.414) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 5` to `Community 8`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._