# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 138 nodes · 284 edges · 7 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f05e4fbb`
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

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 27 edges
2. `VentanaIngreso` - 17 edges
3. `SelectorFecha` - 12 edges
4. `registrar()` - 10 edges
5. `_leer_usuarios()` - 9 edges
6. `descifrar()` - 9 edges
7. `registrar_oficio()` - 7 edges
8. `crear_usuario()` - 7 edges
9. `editar_usuario()` - 7 edges
10. `escribir_bytes_protegido()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `_leer_registros()` --calls--> `descifrar()`  [EXTRACTED]
  almacen_oficios.py → cifrado.py
- `_guardar_registros()` --calls--> `escribir_bytes_protegido()`  [EXTRACTED]
  almacen_oficios.py → permisos.py
- `registrar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `actualizar_oficio()` --calls--> `registrar()`  [EXTRACTED]
  almacen_oficios.py → registro_actividad.py
- `_leer_usuarios()` --calls--> `descifrar()`  [EXTRACTED]
  autenticacion.py → cifrado.py

## Import Cycles
- None detected.

## Communities (7 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (6): AplicacionPrincipal, Marco superior con logo y título., True si el usuario en sesión puede crear/editar/eliminar usuarios., Devuelve (id_empleado, nombre_empleado) a partir del texto elegido         en un, Precarga los desplegables con el responsable y estado del oficio         selecci, Restablece el formulario para crear un usuario nuevo.

### Community 1 - "Community 1"
Cohesion: 0.16
Nodes (22): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (14): Lectura de la base plana de empleados (para el combobox). Formato del archivo em, iniciar(), _cifrador(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Configuración central de la aplicación. Define rutas, nombres de archivo y const (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (18): actualizar_oficio(), _generar_referencia(), _guardar_registros(), _leer_registros(), listar_oficios(), Capa de almacenamiento de OFICIOS.  *** Punto clave de arquitectura *** Toda la, Actualiza estado y/o responsable de un oficio en una sola operación,     respeta, Secuencial por día de recepción. Usa max+1 (tolerante a huecos). (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.22
Nodes (4): Cierra la sesión actual y vuelve a la pantalla de ingreso., Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, VentanaIngreso

### Community 5 - "Community 5"
Cohesion: 0.24
Nodes (12): anexar_texto_protegido(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio(), Endurecimiento de permisos de los archivos que crea la aplicación.  Objetivo: qu, Devuelve el permiso de escritura al propietario si el archivo existe. (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.31
Nodes (3): Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 0` to `Community 2`, `Community 4`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **Why does `VentanaIngreso` connect `Community 4` to `Community 2`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 6` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.12903225806451613 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._