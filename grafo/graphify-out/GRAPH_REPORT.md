# Graph Report - .  (2026-08-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 359 nodes · 746 edges · 19 communities (17 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7f402cce`
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
1. `AplicacionPrincipal` - 63 edges
2. `registrar()` - 22 edges
3. `VentanaIngreso` - 17 edges
4. `SelectorFecha` - 16 edges
5. `registrar_oficio()` - 15 edges
6. `con_bloqueo()` - 14 edges
7. `_leer_registros()` - 13 edges
8. `VisorPDF` - 13 edges
9. `actualizar_oficio()` - 12 edges
10. `_leer_usuarios()` - 11 edges

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

## Communities (19 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (55): actualizar_estado_asignado(), actualizar_oficio(), adjuntar_respuesta(), eliminar_respuesta(), _exigir_respuesta_para_finalizar(), exportar_csv(), exportar_oficios(), exportar_xlsx() (+47 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (38): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (26): listar_oficios(), iniciar(), _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al (+18 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (10): DialogoExportar, Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Exporta a CSV los oficios de una fecha o de un rango de fechas., Exporta los oficios a un CSV acotando por fecha.      Siempre hay que elegir un, Campo para elegir un archivo: botón + nombre del archivo elegido.      Guarda la, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy). (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (19): _guardar_documento(), Copia un adjunto a la carpeta de datos y devuelve su nombre de archivo.      El, Sustituye el documento del oficio (PDF o Word) por si se cargó el     archivo eq, reemplazar_documento(), anexar_texto(), _chmod(), escribir_bytes_protegido(), hacer_escribible() (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (19): _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Fernet, analizar_referencia() (+11 more)

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (4): Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Cierra la sesión actual y vuelve a la pantalla de ingreso., VentanaIngreso

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (5): AplicacionPrincipal, Permite al superusuario o a un administrador indicar la última         Referenci, Panel de copias de seguridad. Solo lo ve el superusuario., Diálogo para que el usuario en sesión cambie su propia contraseña.         Dispo, Desplaza el área que está bajo el puntero.          Si el cursor está sobre una

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (7): Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Busca solo entre los oficios visibles para el usuario en sesión., Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Devuelve la clave interna a partir de la etiqueta mostrada.

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (7): Precarga el panel de edición con los datos del oficio seleccionado.          Sol, Marco superior con logo y título., Texto que se muestra en los desplegables para un responsable.         Incluye el, Personas a las que se les puede asignar un oficio.          Un administrador no, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Crea la copia del día en segundo plano.          Va en un hilo aparte para que l

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (16): bloquear(), _esta_abandonado(), Path, Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), _cargar() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (15): date, _archivos_a_respaldar(), crear_respaldo(), crear_respaldo_silencioso(), existe_del_dia(), listar_respaldos(), purgar_antiguos(), Path (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (6): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales.

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (5): abrir_visor(), Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Ventana con el PDF renderizado página a página., VisorPDF

### Community 14 - "Community 14"
Cohesion: 0.21
Nodes (4): Restablece el formulario para crear un usuario nuevo., ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Muestra el motivo si no se puede gestionar. True = sin permisos., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word,         con, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece         el le

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 7` to `Community 2`, `Community 3`, `Community 6`, `Community 8`, `Community 9`, `Community 12`, `Community 14`, `Community 15`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.415) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 3` to `Community 8`, `Community 9`, `Community 2`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `VentanaIngreso` connect `Community 6` to `Community 2`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06688311688311688 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.11336032388663968 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.10344827586206896 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.10461538461538461 - nodes in this community are weakly interconnected._