# Control de Oficios — Unidad de Cumplimiento

Aplicación de escritorio (Python + Tkinter) para registrar y hacer seguimiento
a los oficios/circulares que llegan a la unidad. Almacenamiento en archivos
cifrados. Incluye ingreso (login), alta de usuarios y un tablero de métricas.

Todos los nombres de archivos, funciones y variables están en español. Solo
permanecen en inglés las palabras propias de Python y de las librerías
(`def`, `class`, `import`, `ttk`, `.pack()`, etc.), que no se pueden traducir.

## 1. Requisitos

- Python 3.9 o superior (recomendado 3.11+).

### Dependencias externas

La aplicación usa **solo tres** librerías de terceros. Instalación completa
(recomendada, para tener todas las funciones):

```bash
pip install -r requirements.txt
```

O, si prefieres instalarlas a mano:

```bash
pip install cryptography pymupdf pillow
```

| Librería | `import` | ¿Obligatoria? | Para qué se usa | Si falta… |
|---|---|---|---|---|
| **cryptography** | `cryptography` | **Sí** | Cifrado Fernet de `oficios.dat` y `credenciales.dat`; hashing PBKDF2 de contraseñas | La app **no arranca** |
| **PyMuPDF** | `fitz` | No | Visor de PDF integrado: renderiza cada página de la respuesta | "Ver respuesta (PDF)" ofrece abrirlo con el lector del sistema |
| **Pillow** | `PIL` | No | 1) Logo del banco en la cabecera y el login. 2) Mejora la nitidez del visor de PDF (renderiza a 2× y reduce con LANCZOS) | Sin logo; el visor usa el modo PPM nativo de Tk (funciona, algo menos nítido) |

Las dependencias opcionales se importan con `try/except ImportError` y siempre
tienen una alternativa, así que **la aplicación funciona sin ellas**.

**Sobre PyMuPDF:** se eligió frente a otras opciones (como `pdf2image`) porque
se instala como *wheel* —no necesita binarios externos como poppler—, funciona
en Windows sin instalar nada más y se empaqueta bien con PyInstaller. Añade
~25 MB al ejecutable; si no necesitas ver los PDF dentro de la app, puedes
omitirla.

**Gráficos del tablero:** se dibujan con el `Canvas` de Tkinter, así que **no
se requiere matplotlib** ni ninguna otra librería de gráficos.

### Módulos de la biblioteca estándar

No hay que instalarlos (vienen con Python), pero conviene saber que se usan:
`tkinter` (interfaz), `json`, `csv`, `datetime`, `pathlib`, `os`, `sys`,
`shutil`, `subprocess`, `calendar`, `collections`, `typing`, `hashlib`, `hmac`
y `base64`.

`tkinter` viene incluido con Python en Windows y macOS. En Linux, si falta:
`sudo apt install python3-tk`.

## 2. Ejecutar en desarrollo

```bash
python aplicacion.py
```

En el primer arranque no hay usuarios: la pantalla pedirá crear el
**superusuario**. Luego inicia sesión con esas credenciales.

## 2.1 Roles de usuario

- **Superusuario:** es el primer usuario que se crea. Es el único que puede
  **crear otros superusuarios**, gestionar a otros superusuarios (editarlos,
  eliminarlos o restablecerles la contraseña) y acceder a las **copias de
  seguridad** en Configuración. El **último superusuario que quede** no puede
  eliminarse ni degradarse, para que el sistema nunca se quede sin uno.
- **Administrador:** su ámbito son los usuarios con rol **'usuario'** (y su
  propia cuenta): puede crearlos, editarlos, eliminarlos y restablecerles la
  contraseña. **No puede crear administradores ni superusuarios, ni promover a
  nadie a esos roles, ni modificar a otro administrador o a un superusuario.**
- **Usuario (regular):** usa la aplicación (registrar oficios, tablero) pero
  **no ve la pestaña "Usuarios"** ni puede gestionar cuentas. Los oficios que
  registra quedan **auto-asignados a él mismo**: no puede asignarlos a otra
  persona ni dejarlos sin responsable (eso corresponde a un gestor). **Solo ve
  los oficios que él registró o que tiene asignados**, no los del resto. Sobre
  esos oficios puede modificar la **fecha de respuesta**, la **observación** y
  **alternar el estado entre "En proceso" y "Finalizado"** (por si finalizó por
  error y quiere reabrirlo); no puede reasignar responsables ni dejarlo en
  "Por asignar".

### Visibilidad de los oficios

| Rol | Oficios que ve |
|---|---|
| Superusuario / Administrador | **Todos** |
| Usuario (regular) | Solo los que **registró** o tiene **asignados** |

El filtro se aplica en la capa de almacenamiento
(`almacen_oficios.listar_oficios_visibles`), y alcanza tanto a la tabla de la
pestaña *Oficios* como a las métricas del *Tablero*.

La gestión de usuarios (crear, editar, eliminar, asignar rol y **restablecer
contraseñas**) está disponible solo para superusuario y administrador. Nadie
puede eliminarse a sí mismo mientras su sesión está activa.

**Quién puede modificar a quién:**

| Actor | Superusuario | Administrador | Usuario | Su propia cuenta |
|---|---|---|---|---|
| **Superusuario** | ✅ | ✅ | ✅ | ✅ |
| **Administrador** | ❌ | ❌ | ✅ | ✅ |

**Qué rol puede otorgar cada uno** (al crear un usuario o al editarlo):

| Actor | Roles que puede asignar |
|---|---|
| **Superusuario** | superusuario, administrador, usuario |
| **Administrador** | usuario |

Ambas reglas se aplican a crear, editar, eliminar y restablecer contraseñas, y
se validan en el almacenamiento (no solo en la interfaz). El **último
superusuario** nunca puede eliminarse ni degradarse.

**Restablecer contraseñas:** un gestor selecciona al usuario y pulsa
"Restablecer contraseña"; se abre un diálogo para escribir la nueva clave (la
idea es cederle el teclado al usuario). Así un administrador que olvidó su
contraseña puede ser ayudado por el superusuario u otro administrador. La
contraseña del **superusuario** solo puede cambiarla él mismo (por ahora no se
contempla el caso en que el superusuario la olvide).

### Responsables de oficios

El **responsable** de un oficio es cualquier **usuario del sistema** (sin
importar su rol); se elige de la lista de usuarios.

**Al registrar**, solo superusuario y administrador pueden elegir el
responsable (o dejarlo sin asignar). Un **usuario regular** ve su propio nombre
fijo: el oficio que registra se le asigna automáticamente a él.

Solo **administrador y superusuario** pueden reasignar responsables o cambiar
libremente el estado de cualquier oficio (respetando las reglas: un oficio con responsable no puede
quedar "Por asignar"; "En proceso"/"Finalizado" exigen responsable).

**Fecha de respuesta y estado:** si un oficio tiene fecha de respuesta es
porque ya fue respondido, así que su estado es siempre **"Finalizado"**. La
regla se aplica al registrar y al modificar, para cualquier rol: si se indica
una fecha de respuesta, el estado pasa a "Finalizado" aunque se haya elegido
otro. Para **reabrir** un oficio hay que **borrar antes esa fecha** (el
calendario tiene un botón "Limpiar"). Además, indicar una fecha de respuesta
exige que el oficio tenga responsable.

### Campos del oficio

En el formulario, los campos **obligatorios se marcan con un asterisco (\*)**;
el resto son opcionales.

| Campo | Obligatorio | Notas |
|---|---|---|
| Referencia oficio | **Sí \*** | No puede repetirse |
| Causal oficio | No | Texto libre |
| Referencia SB | No | Texto libre |
| Fecha de oficio | **Sí \*** | No puede ser posterior a la de recepción |
| Fecha de recepción | **Sí \*** | |
| Fecha de respuesta | No | No puede ser anterior a la de recepción. **Si se indica, el oficio pasa a "Finalizado"** y exige responsable |
| Usuario responsable | No | Sin responsable ⇒ "Por asignar" |
| Estado | **Sí \*** | |
| Observación | No | Texto libre, editable después |

La **Referencia UDC** no se ingresa: la genera el sistema (ver más abajo).

**Ninguna fecha puede ser posterior a hoy** (no se registra lo que aún no ha
ocurrido): el calendario muestra los días futuros deshabilitados y el
almacenamiento rechaza una fecha futura escrita a mano.

El calendario se abre **hacia arriba** cuando no hay espacio suficiente debajo
del campo, y se ajusta para no salirse de la pantalla.

**Qué puede modificar cada rol** en la pestaña *Oficios*:

| | F. respuesta | Responsable | Estado | Observación |
|---|---|---|---|---|
| Superusuario / Administrador | ✅ | ✅ | ✅ (cualquiera) | ✅ |
| Usuario (en sus oficios) | ✅ | ❌ | ✅ (En proceso ↔ Finalizado) | ✅ |

### Respuesta en PDF

Cada oficio puede llevar adjunta **la respuesta en PDF**:

- **"Adjuntar respuesta (PDF)"** copia el archivo a `datos/respuestas/` con el
  nombre `<referencia>.pdf` (queda en solo lectura, como el resto de los datos).
- **"Ver respuesta (PDF)"** lo muestra **dentro de la aplicación** (visor con
  navegación de páginas, zoom y desplazamiento) si PyMuPDF está instalado; si
  no, ofrece abrirlo con el lector del sistema.
- **"Eliminar PDF"** borra el archivo adjunto (por si se cargó el equivocado) y
  permite volver a adjuntar el correcto.
- La columna **PDF** de la tabla indica con "Sí" qué oficios ya tienen respuesta.
- Un usuario regular solo puede adjuntar o eliminar respuestas en **sus**
  oficios; los gestores, en cualquiera.

## 2.3 Tablero (dashboard)

El tablero tiene **desplazamiento vertical** y muestra únicamente los oficios
que el usuario puede ver (ver *Visibilidad de los oficios*).

**Indicadores:** total, por estado (por asignar / en proceso / finalizados),
% finalizados, días promedio de respuesta, recibidos hoy / semana / mes,
con y sin respuesta, con PDF adjunto y sin responsable.

**Gráficos:**

- Oficios recibidos **por día** (últimos 14 días).
- **Distribución por estado** (gráfico de anillo con leyenda y porcentajes).
- Oficios **por responsable** (barras horizontales).
- Oficios recibidos **por mes** (últimos 6 meses).

Todos los gráficos se dibujan con el `Canvas` de Tkinter: **no requieren
matplotlib ni ninguna librería de gráficos**.

## 2.2 Bitácora de auditoría

Toda acción que **modifica datos persistentes** queda registrada en
`datos/actividad.log` (texto plano): alta de oficios, cambios de estado o de
responsable, alta/edición/eliminación de usuarios e inicios de sesión (exitosos
y fallidos). No se registra la navegación ni los clics de la interfaz. Cada
línea tiene el formato:

```
AAAA-MM-DDTHH:MM:SS | actor | ACCION | detalle
```

## 3. Estructura

```
oficios_tracker/
├── aplicacion.py         # Interfaz (ingreso + pestañas). Punto de entrada.
├── configuracion.py      # Rutas y constantes
├── cifrado.py            # Cifrado Fernet + hashing de contraseñas
├── autenticacion.py      # Ingreso, usuarios y roles del sistema
├── registro_actividad.py # Bitácora de auditoría (log en texto plano)
├── permisos.py           # Endurece permisos y escritura atómica de archivos
├── bloqueo.py            # Bloqueo entre procesos (uso compartido en red)
├── parametros.py         # Parámetros del sistema (secuencial inicial UDC)
├── almacen_oficios.py    # CRUD de oficios + referencia secuencial
├── visor_pdf.py          # Visor de PDF integrado (requiere PyMuPDF)
├── metricas.py           # Cálculo de métricas del tablero
├── herramienta_admin.py  # Utilidad de consola para el administrador (ver 3.1)
├── requirements.txt      # Dependencias del proyecto
├── respaldo.py           # Copia de seguridad automática (una por día)
├── respaldo_datos.ps1    # Copia de seguridad programable de datos/ (Windows)
└── datos/                # Se crea sola; contiene:
    ├── clave_maestra.key   (clave de cifrado — PROTEGER / RESPALDAR)
    ├── credenciales.dat    (usuarios del sistema, cifrado)
    ├── oficios.dat         (registros, cifrado; con copia .bak)
    ├── parametros.dat      (secuencial inicial de la Referencia UDC, cifrado)
    ├── actividad.log       (bitácora de auditoría, texto plano)
    ├── respuestas/         (PDF de respuesta, uno por oficio)
    └── respaldos/          (copias de seguridad diarias, .zip)
```

### 3.1 `herramienta_admin.py` (utilidad de consola)

**No forma parte de la aplicación**: ningún módulo la importa. Es un script
independiente que se ejecuta a mano desde la consola, en la carpeta del
proyecto (necesita `datos/clave_maestra.key` para descifrar). Sirve para
inspeccionar o exportar los datos sin pasar por la interfaz:

```bash
# Ver todos los oficios en JSON legible
python herramienta_admin.py oficios

# Ver los usuarios del sistema (sin contraseñas: solo se guardan hashes con
# sal, no se pueden recuperar, solo verificar en el ingreso)
python herramienta_admin.py credenciales

# Exportar los oficios a un CSV que abre directo en Excel (con tildes)
python herramienta_admin.py oficios --csv reporte.csv

# Eliminar los oficios que aún usan la referencia ANTIGUA
# (UDC-OFICIO-AAAAMMDD-NNNN), previa confirmación
python herramienta_admin.py oficios --purgar-formato-anterior
```

Salvo `--purgar-formato-anterior`, es de **solo lectura y exportación**. Esa
purga lista primero los registros afectados, exige escribir `PURGAR` para
confirmar y deja constancia en la bitácora. Si la ejecutas sin argumentos, la
herramienta imprime su propia ayuda.

## 3.2 Referencia UDC y secuencial inicial

La **Referencia UDC** la genera el sistema con el formato
**`REQ-INF-<año>-<NNNN>`** (por ejemplo `REQ-INF-2026-0242`). El secuencial
`NNNN` es de 4 dígitos y **se reinicia cada año** empezando en `0001`.

**Continuidad con el Excel anterior:** los oficios que se llevaban en Excel no
se migran; el sistema continúa desde el último registrado allí. Para eso, el
**superusuario o un administrador** abre la pestaña **Configuración** (visible
solo para ellos) e ingresa **una sola vez** la última Referencia UDC usada, por ejemplo
`REQ-INF-2026-0241`. A partir de ahí el sistema numera `REQ-INF-2026-0242`,
`REQ-INF-2026-0243`, …

Detalles:

- Se acepta la referencia completa (`REQ-INF-2026-0241`) o solo el número
  (`241`, que asume el año en curso).
- La pestaña muestra siempre cuál será la **próxima** Referencia UDC.
- El valor se guarda cifrado en `datos/parametros.dat` y el cambio queda en la
  bitácora de auditoría, con el usuario que lo definió.
- Reconfigurarlo **nunca genera duplicados**: la numeración usa
  `max(valor configurado, mayor secuencial ya existente) + 1`.
- Si nunca se configura, la numeración arranca en `REQ-INF-<año>-0001`.

**El formato anterior (`UDC-OFICIO-AAAAMMDD-NNNN`) quedó descartado:** el
sistema no lo genera nunca, lo rechaza si se intenta usar como secuencial
inicial, y los registros antiguos que pudieran existir **no influyen en la
numeración** (aunque tuvieran un secuencial más alto). Para eliminarlos, use
`herramienta_admin.py oficios --purgar-formato-anterior` (ver 3.1).

Además de la Referencia UDC (siempre única), la **Referencia oficio** que
ingresa el usuario **no puede repetirse**: al registrar se rechaza una
referencia ya existente (sin distinguir mayúsculas/minúsculas ni espacios).

## 3.3 Búsqueda de oficios

La pestaña *Oficios* incluye un panel **Buscar oficios** con dos filtros
combinables:

- **Por texto**, eligiendo el campo: Referencia UDC, Referencia oficio,
  Causal oficio o Referencia SB. La coincidencia es **parcial** y no distingue
  mayúsculas/minúsculas.
- **Por fecha**, eligiendo el tipo (fecha de oficio, de recepción o de
  respuesta) y un rango *desde* / *hasta*. Ambos extremos aplican **siempre al
  mismo tipo de fecha**, por lo que no es posible mezclar (p. ej. desde = fecha
  de oficio y hasta = fecha de recepción). Si se deja *hasta* vacío, se busca
  por esa **fecha única**.

El panel indica cuántos oficios se están mostrando del total, y "Limpiar
filtros" restablece la lista completa.

La pestaña *Oficios* tiene **desplazamiento vertical** que abarca sus tres
secciones (*Buscar oficios*, el listado y *Modificar oficio seleccionado*), de
modo que en pantallas pequeñas ninguna quede fuera de la vista. La rueda del
ratón desplaza la tabla cuando el puntero está sobre ella, y la pestaña
completa en cualquier otro punto.

## 4. Compilar a ejecutable (lo más ligero posible)

```bash
pip install pyinstaller
```

### Paso previo: descomprimir UPX

**UPX** comprime los binarios y reduce bastante el tamaño final. Si tienes
`upx-5.2.0-win64.zip` en la raíz del proyecto, descomprímelo una sola vez
(PowerShell):

```powershell
Expand-Archive -Path .\upx-5.2.0-win64.zip -DestinationPath . -Force
```

Queda la carpeta `upx-5.2.0-win64\` con `upx.exe` dentro; esa carpeta es la que
se le pasa a PyInstaller con `--upx-dir`.

### Dónde queda todo: la carpeta `bin/`

Por omisión PyInstaller crea `dist/` y `build/` en la raíz del proyecto. Los
comandos de abajo lo redirigen todo a **`bin/`**, con una subcarpeta por tipo de
compilación:

```
bin/
├── CON_DEPENDENCIAS/          (un solo .exe: las dependencias van DENTRO)
│   ├── ControlOficios.exe
│   ├── datos/                 <- íconos (copiados a mano)
│   ├── build/                 <- archivos temporales de compilación
│   └── ControlOficios.spec
└── SIN_DEPENDENCIAS/          (el .exe y sus dependencias, por separado)
    ├── ControlOficios/
    │   ├── ControlOficios.exe
    │   ├── _internal/         <- dependencias (PyInstaller 6+)
    │   └── datos/             <- íconos (copiados a mano)
    ├── build/
    └── ControlOficios.spec
```

`bin/` está en `.gitignore`: los ejecutables no se versionan.

### Opción A — CON_DEPENDENCIAS (un solo ejecutable, `--onefile`)

Todo queda empaquetado **dentro** de un único `.exe`, lo más cómodo de
distribuir.

```powershell
pyinstaller --onefile --windowed --clean --name ControlOficios `
            --icon datos\bdp_icon_alt.ico `
            --upx-dir upx-5.2.0-win64 `
            --upx-exclude vcruntime140.dll `
            --distpath bin\CON_DEPENDENCIAS `
            --workpath bin\CON_DEPENDENCIAS\build `
            --specpath bin\CON_DEPENDENCIAS `
            aplicacion.py
```

Copie los íconos junto al ejecutable:

```powershell
New-Item -ItemType Directory -Force -Path bin\CON_DEPENDENCIAS\datos | Out-Null
Copy-Item datos\bdp_icon*.ico bin\CON_DEPENDENCIAS\datos\
```

Resultado: **`bin\CON_DEPENDENCIAS\ControlOficios.exe`**

### Opción B — SIN_DEPENDENCIAS (dependencias aparte, `--onedir`)

Genera el `.exe` con sus dependencias **al lado**, no integradas. **Arranca
bastante más rápido** (el modo `--onefile` se descomprime en una carpeta
temporal en cada ejecución) y suele ser la opción más liviana en total.

```powershell
pyinstaller --onedir --windowed --clean --name ControlOficios `
            --icon datos\bdp_icon_alt.ico `
            --upx-dir upx-5.2.0-win64 `
            --upx-exclude vcruntime140.dll `
            --distpath bin\SIN_DEPENDENCIAS `
            --workpath bin\SIN_DEPENDENCIAS\build `
            --specpath bin\SIN_DEPENDENCIAS `
            aplicacion.py
```

Copie los íconos junto al ejecutable:

```powershell
New-Item -ItemType Directory -Force -Path bin\SIN_DEPENDENCIAS\ControlOficios\datos | Out-Null
Copy-Item datos\bdp_icon*.ico bin\SIN_DEPENDENCIAS\ControlOficios\datos\
```

Resultado: **`bin\SIN_DEPENDENCIAS\ControlOficios\ControlOficios.exe`**.
Para distribuirlo se comparte **la carpeta `ControlOficios` completa**, no solo
el `.exe`.

> Los nombres describen el **ejecutable**: en `CON_DEPENDENCIAS` el `.exe` las
> lleva dentro; en `SIN_DEPENDENCIAS` el `.exe` no las incluye y viajan a su
> lado en `_internal/`.

> El acento grave `` ` `` es continuación de línea en **PowerShell**. En **CMD**
> use `^`, y en una sola línea no hace falta ningún símbolo.

> Si quiere borrar los temporales al terminar:
> `Remove-Item -Recurse -Force bin\*\build`

### Qué hace cada opción

| Opción | Para qué sirve |
|---|---|
| `--onefile` / `--onedir` | Un único `.exe` **o** una carpeta con el `.exe` y sus dependencias |
| `--windowed` | Oculta la consola negra (equivale a `--noconsole`) |
| `--clean` | Limpia la caché de compilaciones anteriores (evita arrastrar restos) |
| `--name ControlOficios` | El ejecutable se llamará `ControlOficios.exe` |
| `--icon datos\bdp_icon_alt.ico` | **Incrusta el ícono del banco en el `.exe`** |
| `--upx-dir upx-5.2.0-win64` | Carpeta donde está `upx.exe`; activa la compresión |
| `--upx-exclude vcruntime140.dll` | Evita comprimir esa DLL: UPX suele dañarla y el `.exe` no abriría |
| `--distpath bin\...` | Dónde se deja el ejecutable (en vez de `dist/`) |
| `--workpath bin\...\build` | Dónde se dejan los temporales de compilación (en vez de `build/`) |
| `--specpath bin\...` | Dónde se deja el archivo `.spec` (en vez de la raíz) |

### IMPORTANTE: la carpeta `datos/` va junto al ejecutable

El código detecta si corre como `.exe` y usa la carpeta `datos/` **que está al
lado del ejecutable** (no una interna del paquete). Allí se crean solos la
clave, las credenciales, los oficios, la bitácora y las respuestas en PDF.

Por eso hay que **copiar los `.ico` a esa carpeta** (los comandos de arriba ya
lo hacen): sin ellos la app funciona, pero las ventanas y la cabecera se ven sin
el ícono ni el logo del banco.

### Ícono del ejecutable — detalles

- `--icon` afecta al ícono del **archivo `.exe`** (Explorador, barra de tareas,
  accesos directos). El ícono de las **ventanas** en ejecución lo pone la propia
  app leyendo `datos/bdp_icon_alt.ico`.
- Si cambia el ícono y Windows sigue mostrando el anterior, es la **caché de
  íconos**: renombre el `.exe` o reinicie el Explorador.

### Consejos para que pese lo menos posible

1. Compile dentro de un **entorno virtual** con solo lo necesario
   (`cryptography`, `pyinstaller`, y opcionalmente `pymupdf` y `Pillow`). Así
   PyInstaller no arrastra librerías de más. `pymupdf` añade ~25 MB: si no
   necesita ver los PDF dentro de la app, omítalo y se usará el lector del
   sistema.
2. Use **UPX** (`--upx-dir`), como en los comandos de arriba.
3. Prefiera **`--onedir`** si el tamaño total y el arranque le importan más que
   distribuir un archivo único.

`cryptography` incluye binarios de OpenSSL, así que ~8–15 MB es lo esperable.
Es el precio de tener cifrado serio.

### Si algo falla con UPX

- Si el `.exe` no abre o falla al iniciar, añada más exclusiones
  (`--upx-exclude python311.dll`, `--upx-exclude libcrypto-*.dll`) o compile sin
  compresión usando `--noupx`, para confirmar si UPX es la causa.
- **Algunos antivirus** desconfían de los ejecutables comprimidos con UPX. Si
  aparecen falsos positivos, compile sin UPX.
- No hace falta instalar UPX: basta con la carpeta descomprimida.

## 4.1 Uso compartido por varias personas

La aplicación puede vivir en una **carpeta de red** usada por varias personas a
la vez (3-4 en la práctica). Estas son las salvaguardas incorporadas:

**Bloqueo entre procesos (`bloqueo.py`).** Guardar implica leer todo el
archivo, modificarlo y reescribirlo. Si dos personas hacían eso a la vez, la
segunda escritura pisaba a la primera y **se perdía un registro sin aviso**.
Ahora cada operación de escritura toma un bloqueo (`datos/oficios.lock`,
`credenciales.lock`, `parametros.lock`) creado de forma atómica, de modo que la
secuencia es indivisible. Si otro usuario está guardando, se espera unos
milisegundos; si tras 10 segundos sigue ocupado, se avisa con un mensaje claro
en vez de congelar la aplicación.

> Medido en el proyecto: con 8 procesos registrando oficios simultáneamente,
> **sin** bloqueo se guardaba 1 de 8 (7 oficios perdidos); **con** bloqueo se
> guardan los 8, sin referencias duplicadas.

Si un equipo se apaga de golpe con el bloqueo tomado, el archivo queda
huérfano; por eso lleva dentro su marca de tiempo y, pasados 30 segundos, se
considera abandonado y se rompe solo.

**Escritura atómica y copia de respaldo.** Los datos se escriben en un archivo
temporal y luego se renombra sobre el definitivo. Quien lea en ese momento ve
**o la versión anterior o la nueva, nunca una a medias** (antes podía aparecer
el falso mensaje de "archivo alterado"). Además protege ante un corte de luz a
mitad de escritura. De cada archivo se conserva la versión anterior en
`<nombre>.bak`.

**Bitácora sin pérdidas.** El log ya no alterna a solo lectura tras cada línea:
ese vaivén hacía que un proceso bloqueara al otro y la línea de auditoría se
perdiera en silencio. Y si aun así la escritura falla, la línea **no se
descarta**: se guarda en `%TEMP%\controloficios-auditoria-pendiente.log`.

**Vista siempre al día.** Al volver a la ventana de la aplicación, los datos se
recargan automáticamente, así se ve lo que otras personas hayan registrado. El
refresco respeta lo que se esté escribiendo: no borra una observación a medio
redactar.

**Recomendación adicional (no es código):** programe una **copia diaria
automática de la carpeta `datos/`**. Cubre concurrencia, borrado accidental,
disco dañado y errores humanos; es la medida más rentable de todas.

## 4.2 Despliegue en una carpeta compartida (varias personas)

### Dónde viven los datos

Por omisión la aplicación usa la carpeta `datos/` **junto al ejecutable**. Para
un uso compartido conviene **separarlos**, de modo que varias versiones de la
aplicación compartan una única carpeta de datos. Hay dos formas, y la primera
tiene prioridad:

1. La variable de entorno **`CONTROLOFICIOS_DATOS`**.
2. Un archivo de texto **`datos.ruta`** junto al ejecutable, con la ruta en una
   línea. Se ignoran las líneas vacías y las que empiezan por `#`; las rutas
   relativas se resuelven desde la carpeta del ejecutable.

En el repositorio hay un `datos.ruta.ejemplo` con las variantes comentadas
(ruta relativa, UNC `\\servidor\...` o unidad asignada).

### Estructura recomendada en el recurso compartido

```
\\servidor\ControlOficios\
├── datos\                      <- ÚNICA carpeta de datos, fuera de las versiones
│   ├── oficios.dat
│   ├── credenciales.dat
│   ├── clave_maestra.key
│   ├── respuestas\             (PDF de respuesta)
│   └── respaldos\              (copias diarias, también en el compartido)
├── app\
│   ├── ControlOficios_v1.1\    <- versión anterior (para volver atrás)
│   └── ControlOficios_v1.2\    <- versión vigente
│       ├── ControlOficios.exe
│       ├── _internal\
│       └── datos.ruta          <- contiene:  ..\..\datos
└── ControlOficios.lnk          <- acceso directo a la versión vigente
```

### Cómo publicar una versión nueva

No se puede sobrescribir un `.exe` que alguien tiene abierto, así que **no se
reemplaza: se agrega**.

1. Compile y copie `bin\ControlOficios` al compartido como
   `app\ControlOficios_v1.3`. Nadie tiene esa carpeta abierta, así que no hay
   archivos bloqueados.
2. Ponga dentro el archivo `datos.ruta` con `..\..\datos`.
3. Apunte el acceso directo `ControlOficios.lnk` a la carpeta nueva.
4. Quien tenga la aplicación abierta sigue con la versión anterior hasta que la
   cierre; la próxima vez que abra, entra en la nueva.
5. Cuando ya nadie use la versión antigua, bórrela.

**Para volver atrás**, apunte el acceso directo a la versión anterior.

> Si cada persona **copia** el `.lnk` a su escritorio, esa copia queda fijada a
> la versión de ese momento. Haga que su acceso directo del escritorio apunte
> al `.lnk` del compartido (Windows resuelve la cadena), o que abran siempre
> desde la carpeta compartida.

### Los íconos

Se buscan primero **junto al ejecutable** y, si no están, en la carpeta de
datos. Así cada carpeta de versión puede llevar los suyos, o se dejan una sola
vez en `datos\`.

### Si la carpeta de datos no responde

Si la unidad de red está caída o la ruta de `datos.ruta` es incorrecta, la
aplicación **no falla con un error técnico**: muestra un mensaje indicando la
ruta que intentó usar y qué revisar.

### Arranque desde el compartido

Cargar `_internal` por red es más lento que desde disco local, sobre todo la
primera vez del día (después la caché de Windows lo acelera). Es el precio de
tener una sola instalación centralizada.

## 4.2 Copias de seguridad automáticas (dentro de la aplicación)

**No requiere permisos ni tareas programadas**: la propia aplicación crea
**una copia al día**, la primera vez que alguien la abre. Si otra persona ya la
creó, no se repite.

- Se guardan en **`datos/respaldos/datos_AAAA-MM-DD.zip`**.
- Se conservan los últimos **30 días**; las más antiguas se eliminan solas.
- Incluyen los archivos pequeños y críticos: `oficios.dat`,
  `credenciales.dat`, `parametros.dat`, `clave_maestra.key` y `actividad.log`.
- **No incluyen los PDF de respuesta** (pesan mucho y no cambian una vez
  cargados) ni los archivos temporales, de bloqueo o `.bak`.
- Se ejecuta **en segundo plano**: la ventana abre sin esperar. Si el respaldo
  falla, queda anotado en la bitácora (`RESPALDO_FALLIDO`) pero **nunca impide
  usar la aplicación**.
- El **superusuario** ve en la pestaña *Configuración* la última copia, cuántas
  hay, y puede crear una a demanda o abrir la carpeta. Ese panel **no lo ven
  los administradores**.

> Referencia de tamaño: 500 oficios ocupan ~442 KB, así que la copia diaria
> pesa muy poco y no ralentiza el arranque.

**Límites que conviene conocer:** como las copias quedan junto a los datos,
protegen ante borrado accidental, archivo corrupto o error humano, pero **no
ante un fallo del disco**. Y si nadie abre la aplicación un día, ese día no hay
copia. Para cubrir esos casos, use además la tarea programada de la sección
siguiente, que puede escribir en otro disco y se ejecuta aunque nadie entre.

## 4.3 Copia de seguridad programada (opcional, en otro disco)

En el proyecto se incluye **`respaldo_datos.ps1`**, que comprime la carpeta
`datos/` con la fecha en el nombre y elimina los respaldos antiguos.

### Prueba manual

Copie el script junto al ejecutable y ejecútelo desde PowerShell:

```powershell
cd C:\ControlOficios
.\respaldo_datos.ps1
```

Genera `C:\ControlOficios\Respaldos\datos_2026-07-28_2130.zip` y anota el
resultado en `Respaldos\respaldos.log`. Si Windows bloquea la ejecución de
scripts, permítalo solo para esa sesión:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Rutas y retención propias:

```powershell
.\respaldo_datos.ps1 -Origen "C:\ControlOficios\datos" `
                     -Destino "D:\Respaldos\ControlOficios" `
                     -DiasConservar 60
```

### Programarlo a diario

Una sola línea en PowerShell **como administrador** (se ejecuta todos los días
a las 20:00, aunque nadie haya iniciado sesión):

```powershell
schtasks /Create /TN "ControlOficios - Respaldo" /SC DAILY /ST 20:00 /RL HIGHEST /RU SYSTEM ^
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\ControlOficios\respaldo_datos.ps1"
```

Comprobar, ejecutar a demanda o eliminar la tarea:

```powershell
schtasks /Query  /TN "ControlOficios - Respaldo"
schtasks /Run    /TN "ControlOficios - Respaldo"
schtasks /Delete /TN "ControlOficios - Respaldo" /F
```

También puede hacerse desde la interfaz: **Programador de tareas → Crear tarea
básica**, con desencadenador *Diariamente* y acción *Iniciar un programa*
(`powershell.exe`, argumentos
`-NoProfile -ExecutionPolicy Bypass -File C:\ControlOficios\respaldo_datos.ps1`).

### Recomendaciones

- **Guarde el respaldo en otro disco o equipo.** Si queda en la misma carpeta
  compartida, un fallo de ese disco se lleva los datos y las copias.
- **Restrinja el acceso a la carpeta de respaldos.** El comprimido incluye
  `clave_maestra.key`: quien lo tenga puede descifrar los oficios y las
  credenciales. Es el mismo cuidado que merece la carpeta `datos/`.
- **Pruebe una restauración** al menos una vez: descomprima un respaldo en una
  carpeta vacía, ponga ahí el ejecutable y verifique que abre con normalidad.
  Un respaldo que nunca se restauró no está comprobado.
- El script **excluye** los archivos temporales (`.tmp`) y de bloqueo
  (`.lock`), y hace una copia intermedia antes de comprimir para no tropezar
  con archivos que la aplicación esté escribiendo en ese momento.

## 5. Notas de seguridad (léelas)

- **Contraseñas:** no se guardan ni en claro ni "cifradas": se guarda su
  **hash con sal** (PBKDF2-HMAC-SHA256). Nadie —ni tú— puede recuperarlas;
  solo verificarlas. Es lo correcto.
- **Oficios y credenciales:** cifrado **autenticado** con Fernet. Si alguien
  edita un byte del archivo, el descifrado falla y la app avisa de manipulación.
- **Permisos restringidos (módulo `permisos.py`):** todos los archivos que crea
  la app (`clave_maestra.key`, `credenciales.dat`, `oficios.dat` y
  `actividad.log`) quedan tras cada escritura en **solo lectura del propietario**
  (`0o400`), y la carpeta `datos/` se restringe a `0o700`. La app puede seguir
  operando porque, justo antes de reescribir, restaura el permiso y vuelve a
  bloquearlo. Esto **impide la modificación y el borrado casual** y bloquea a
  **otros usuarios del sistema**.
  - En **Windows**, `0o400` marca el archivo como *solo lectura*: no se puede
    modificar ni borrar con normalidad.
  - En **Linux/macOS**, el borrado depende de los permisos de la carpeta, por
    eso `datos/` queda en `0o700`.
- **Sobre el borrado (importante):** los permisos de archivo (`chmod`/solo
  lectura) **impiden modificar** el contenido, pero **no impiden borrar**. El
  borrado lo controla el **directorio contenedor**, y su dueño siempre puede
  eliminar lo que contiene (por eso puedes borrar `actividad.log` e incluso la
  carpeta `datos/`). No existe una forma **portable** desde Python de impedir
  que el dueño borre sus propios archivos o carpetas. Para impedirlo de verdad
  hacen falta mecanismos del sistema operativo, y todos requieren privilegios y
  pueden revertirse por un administrador:
  - **Windows (NTFS):** ACL con `icacls` denegando *Delete*/*Delete subfolders
    and files* a la cuenta (`icacls datos /deny "usuario:(DE,DC)"`).
  - **Linux:** atributo inmutable `sudo chattr +i archivo` (requiere root).
  - **La solución real** es sacar el almacén del control del usuario: una **base
    de datos** o un **destino de log remoto/append-only** donde el usuario solo
    pueda *agregar*, no borrar ni editar (ver sección 6).
- **Límite honesto:** la cuenta que **ejecuta la app es dueña** de los archivos,
  y `root`/Administrador ignora estos permisos; con esfuerzo podría revertirlos.
  La `clave_maestra.key` también vive en disco junto a los datos. El endurecimiento
  de permisos + el cifrado dan *confidencialidad, integridad y freno a la
  manipulación*, **no control de acceso absoluto**. Para eso, ver la sección 6.
- Respalda `clave_maestra.key`: **si se pierde, los datos cifrados no se
  recuperan.**

## 6. Alternativa recomendada (a mediano plazo)

Migrar el almacenamiento a **base de datos**. La verdadera garantía de que
"nadie altera la información" no viene de ofuscar un archivo, sino de que los
usuarios **no tengan permiso de escritura directa** sobre el almacén:

- **Paso intermedio — SQLite:** un solo archivo `.db`, sin servidor, muy ligero
  y perfecto para las consultas del tablero. Si necesitas cifrado en reposo,
  se combina con SQLCipher o con firma HMAC por registro.
- **Objetivo — motor centralizado (SQL Server / PostgreSQL):** la app se conecta
  con una **cuenta de servicio de permisos mínimos**; idealmente las escrituras
  van solo por **procedimientos almacenados**, y una **tabla de auditoría con
  triggers** deja rastro inalterable de cada cambio. Ahí el control lo impone el
  motor, no el "secreto" del archivo.

La migración es barata **por diseño**: la interfaz y el tablero solo hablan con
las funciones de `almacen_oficios.py` / `autenticacion.py`. Cambiar a SQLite o
SQL Server significa reescribir el cuerpo de esos módulos, sin tocar la interfaz
ni `metricas.py`.
