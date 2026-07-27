# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 181 nodes · 377 edges · 13 communities (8 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `47b1c72b`
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

## God Nodes (most connected - your core abstractions)
1. `AplicacionPrincipal` - 35 edges
2. `VentanaIngreso` - 17 edges
3. `SelectorFecha` - 13 edges
4. `registrar()` - 13 edges
5. `VisorPDF` - 12 edges
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

## Communities (13 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (30): _buscar(), cerrar_sesion(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario(), _guardar_usuarios(), _leer_usuarios() (+22 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (24): actualizar_estado_asignado(), actualizar_oficio(), _generar_referencia(), _guardar_registros(), _leer_registros(), listar_oficios(), Capa de almacenamiento de OFICIOS.  *** Punto clave de arquitectura *** Toda la, Valida la fecha de respuesta (opcional). No puede ser anterior a la de     recep (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (5): iniciar(), Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., Centra la ventana en la pantalla., VentanaIngreso

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (16): adjuntar_respuesta(), _puede_editar(), Un gestor puede sobre cualquier oficio; un usuario regular solo sobre     los of, Copia un PDF de respuesta a datos/respuestas/ y lo asocia al oficio.      El arc, anexar_texto_protegido(), _chmod(), escribir_bytes_protegido(), hacer_escribible() (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.20
Nodes (7): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 5 - "Community 5"
Cohesion: 0.27
Nodes (4): Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 7 - "Community 7"
Cohesion: 0.24
Nodes (3): Texto que se muestra en los desplegables para un responsable.         Incluye el, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, Precarga el panel de edición con los datos del oficio seleccionado.

### Community 8 - "Community 8"
Cohesion: 0.27
Nodes (7): Configuración central de la aplicación. Define rutas, nombres de archivo y const, _cargar(), exportar_csv_oficios(), main(), mostrar_json(), herramienta_admin.py — utilidad SOLO para el administrador. Descifra y muestra e, Registro de actividad (auditoría) en un archivo de texto plano.  Guarda TODA acc

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 6` to `Community 2`, `Community 7`, `Community 9`, `Community 10`, `Community 11`, `Community 12`?**
  _High betweenness centrality (0.384) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 5` to `Community 10`, `Community 2`, `Community 11`, `Community 7`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13306451612903225 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14153846153846153 - nodes in this community are weakly interconnected._