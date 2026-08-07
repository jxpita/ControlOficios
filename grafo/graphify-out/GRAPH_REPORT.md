# Graph Report - .  (2026-08-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 351 nodes · 733 edges · 24 communities (23 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a958ead`
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
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22

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

## Communities (24 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (40): _buscar(), cambiar_clave_propia(), cerrar_sesion(), _contar_superusuarios(), crear_usuario(), editar_usuario(), eliminar_usuario(), existe_algun_usuario() (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (10): DialogoExportar, iniciar(), Exporta a CSV los oficios de una fecha o de un rango de fechas., Exporta los oficios a un CSV acotando por fecha.      Siempre hay que elegir un, Centra la ventana en la pantalla., Crea el banner corporativo y la tarjeta central. Devuelve el         contenedor, Campo para elegir un archivo: botón + nombre del archivo elegido.      Guarda la, Cierra la sesión actual y vuelve a la pantalla de ingreso. (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.16
Nodes (19): _cifrador(), cifrar(), descifrar(), obtener_clave(), Devuelve la clave Fernet; la genera la primera vez que se ejecuta., Descifra. Lanza cryptography.fernet.InvalidToken si el archivo     fue alterado, Fernet, analizar_referencia() (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (20): actualizar_estado_asignado(), actualizar_oficio(), _exigir_respuesta_para_finalizar(), filtrar_oficios(), Cantidad de investigados: número entero no negativo, opcional.     Devuelve el v, Fecha de asignación (opcional). No puede ser anterior a la de recepción:     un, Un oficio solo puede PASAR a "Finalizado" si ya tiene adjunta la     respuesta e, Valida la fecha de respuesta (opcional). No puede ser anterior a la de     recep (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (5): AplicacionPrincipal, Permite al superusuario o a un administrador indicar la última         Referenci, Panel de copias de seguridad. Solo lo ve el superusuario., Diálogo para que el usuario en sesión cambie su propia contraseña.         Dispo, Desplaza el área que está bajo el puntero.          Si el cursor está sobre una

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (8): abrir_con_sistema(), abrir_visor(), Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio sin, Centra horizontalmente la página dentro del lienzo (y verticalmente         si s, Abre el PDF dentro de la aplicación.      Devuelve True si se mostró en la app;, Abre el PDF con el lector predeterminado del sistema operativo.     Alternativa, Ventana con el PDF renderizado página a página., VisorPDF

### Community 6 - "Community 6"
Cohesion: 0.19
Nodes (17): adjuntar_respuesta(), eliminar_respuesta(), _generar_referencia(), _guardar_registros(), _leer_registros(), listar_oficios_visibles(), proxima_referencia(), _puede_editar() (+9 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (7): Guarda los cambios del panel según el rol: el gestor puede cambiar         respo, Sustituye el documento del oficio por si se cargó el equivocado., Carga un PDF con la respuesta del oficio seleccionado., Elimina el PDF adjunto (por si se cargó el archivo equivocado)., Busca solo entre los oficios visibles para el usuario en sesión., Panel de búsqueda: por texto (Referencia UDC / Referencia oficio /         Causa, Devuelve la clave interna a partir de la etiqueta mostrada.

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (7): Precarga el panel de edición con los datos del oficio seleccionado.          Sol, Marco superior con logo y título., Texto que se muestra en los desplegables para un responsable.         Incluye el, Personas a las que se les puede asignar un oficio.          Un administrador no, A partir del texto del desplegable devuelve (usuario, nombre).         Para "(Si, True si el usuario en sesión puede crear/editar/eliminar usuarios         y reas, Crea la copia del día en segundo plano.          Va en un hilo aparte para que l

### Community 9 - "Community 9"
Cohesion: 0.23
Nodes (15): listar_oficios(), _convertir_fecha(), dias_promedio_respuesta(), distribucion_estados(), por_responsable(), Cálculo de métricas para el tablero (dashboard). No depende de la interfaz: solo, Cantidad de oficios por responsable, de mayor a menor.     Los oficios sin respo, Cantidad por estado, en el orden definido en configuracion.ESTADOS. (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (15): bloquear(), _esta_abandonado(), Path, True si el bloqueo es tan antiguo que solo puede ser basura., Toma el bloqueo `nombre` mientras dure el bloque `with`.      Lanza ValueError s, _ruta_bloqueo(), _cargar(), _es_formato_actual() (+7 more)

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (15): date, _archivos_a_respaldar(), crear_respaldo(), crear_respaldo_silencioso(), existe_del_dia(), listar_respaldos(), purgar_antiguos(), Path (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (14): _guardar_documento(), Copia un adjunto a la carpeta de datos y devuelve su nombre de archivo.      El, anexar_texto(), _chmod(), escribir_bytes_protegido(), hacer_escribible(), proteger(), proteger_directorio() (+6 more)

### Community 13 - "Community 13"
Cohesion: 0.20
Nodes (5): Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no         cabe, Campo de fecha con calendario emergente. No requiere librerías externas.      Mu, `permitir_vacio=True` deja el campo en blanco y ofrece un botón         "Limpiar, Fecha desde la que se abre el calendario (la escrita, o hoy)., SelectorFecha

### Community 14 - "Community 14"
Cohesion: 0.24
Nodes (4): Restablece el formulario para crear un usuario nuevo., Refresca la vista al volver a la ventana.          Con varias personas usando la, Repuebla los desplegables de responsable con los usuarios actuales., Roles que puede otorgar quien está en sesión (solo el superusuario         puede

### Community 15 - "Community 15"
Cohesion: 0.20
Nodes (4): Barras verticales: oficios recibidos por día., Barras verticales: oficios recibidos por mes., Gráfico de anillo con la distribución por estado., Barras horizontales: cantidad de oficios por responsable.

### Community 16 - "Community 16"
Cohesion: 0.32
Nodes (8): exportar_csv(), Path, Devuelve la ruta del PDF de respuesta adjunto, o None si no hay., Devuelve la ruta del documento del oficio (PDF o Word), o None., Vuelca los oficios indicados a un CSV y devuelve cuántos escribió.      Se usa U, _ruta_adjunto(), ruta_documento(), ruta_respuesta()

### Community 17 - "Community 17"
Cohesion: 0.25
Nodes (3): Diálogo modal para escribir y confirmar una nueva contraseña.         Devuelve l, ¿El usuario en sesión puede gestionar a ese usuario? Se consulta         antes d, Muestra el motivo si no se puede gestionar. True = sin permisos.

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (3): Abre el documento del oficio (PDF dentro de la aplicación; el Word,         con, Muestra el PDF de respuesta dentro de la aplicación., Abre un PDF en el visor integrado y, si no está disponible, ofrece         el le

### Community 19 - "Community 19"
Cohesion: 0.33
Nodes (3): Bloqueo entre procesos para la carpeta de datos compartida.  Problema que resuel, Configuración central de la aplicación. Define rutas, nombres de archivo y const, Registro de actividad (auditoría) en un archivo de texto plano.  Guarda TODA acc

### Community 20 - "Community 20"
Cohesion: 0.33
Nodes (6): _buscar_recurso(), _crear_subcarpeta(), _leer_ruta_configurada(), Path, Ubica un recurso de la aplicación (ícono o logo).      Se busca primero junto al, Ruta de la carpeta de datos indicada por el usuario, o None.      Se busca en do

### Community 22 - "Community 22"
Cohesion: 0.50
Nodes (4): Rol del usuario indicado, o '' si no existe., Un ADMINISTRADOR no puede asignar oficios a un superusuario.      El superusuari, _rol_de(), _validar_asignacion()

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AplicacionPrincipal` connect `Community 4` to `Community 1`, `Community 7`, `Community 8`, `Community 14`, `Community 15`, `Community 17`, `Community 18`, `Community 21`?**
  _High betweenness centrality (0.422) - this node is a cross-community bridge._
- **Why does `SelectorFecha` connect `Community 13` to `Community 8`, `Community 1`, `Community 7`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.1048780487804878 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.11088709677419355 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._