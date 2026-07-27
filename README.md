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

- **Superusuario:** es el primer usuario que se crea. Puede gestionar usuarios
  y **no puede eliminarse ni cambiar de rol** bajo ninguna circunstancia.
- **Administrador:** puede crear, editar y eliminar otros usuarios (excepto
  eliminar al superusuario) y usar toda la aplicación.
- **Usuario (regular):** usa la aplicación (registrar oficios, tablero) pero
  **no ve la pestaña "Usuarios"** ni puede gestionar cuentas. **Solo ve los
  oficios que él registró o que tiene asignados**, no los del resto. Sobre esos
  oficios puede modificar la **fecha de respuesta**, la **observación** y
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

**Restablecer contraseñas:** un gestor selecciona al usuario y pulsa
"Restablecer contraseña"; se abre un diálogo para escribir la nueva clave (la
idea es cederle el teclado al usuario). Así un administrador que olvidó su
contraseña puede ser ayudado por el superusuario u otro administrador. La
contraseña del **superusuario** solo puede cambiarla él mismo (por ahora no se
contempla el caso en que el superusuario la olvide).

### Responsables de oficios

El **responsable** de un oficio es cualquier **usuario del sistema** (sin
importar su rol); se elige de la lista de usuarios. Solo **administrador y
superusuario** pueden reasignar responsables o cambiar libremente el estado de
cualquier oficio (respetando las reglas: un oficio con responsable no puede
quedar "Por asignar"; "En proceso"/"Finalizado" exigen responsable).

### Campos del oficio

En el formulario, los campos **obligatorios se marcan con un asterisco (\*)**;
el resto son opcionales.

| Campo | Obligatorio | Notas |
|---|---|---|
| Código de oficio | **Sí \*** | No puede repetirse |
| Fecha de oficio | **Sí \*** | No puede ser posterior a la de recepción |
| Fecha de recepción | **Sí \*** | |
| Fecha de respuesta | No | No puede ser anterior a la de recepción |
| Usuario responsable | No | Sin responsable ⇒ "Por asignar" |
| Estado | **Sí \*** | |
| Observación | No | Texto libre, editable después |

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
├── permisos.py           # Endurece permisos (solo lectura) de los archivos
├── almacen_oficios.py    # CRUD de oficios + referencia secuencial
├── visor_pdf.py          # Visor de PDF integrado (requiere PyMuPDF)
├── metricas.py           # Cálculo de métricas del tablero
└── datos/                # Se crea sola; contiene:
    ├── clave_maestra.key   (clave de cifrado — PROTEGER / RESPALDAR)
    ├── credenciales.dat    (usuarios del sistema, cifrado)
    ├── oficios.dat         (registros, cifrado)
    ├── actividad.log       (bitácora de auditoría, texto plano)
    └── respuestas/         (PDF de respuesta, uno por oficio)
```

La referencia interna tiene el formato **`UDC-OFICIO-AAAAMMDD-NNNN`**.
El secuencial `NNNN` (4 dígitos, desde `0000`) se reinicia por cada **día de
recepción**. Si prefieres usar la fecha de registro o un contador global que
nunca reinicie, se cambia únicamente en `almacen_oficios._generar_referencia`.

Además de la referencia interna (siempre única), el **código de oficio** que
ingresa el usuario **no puede repetirse**: al registrar se rechaza un código ya
existente (sin distinguir mayúsculas/minúsculas ni espacios).

## 4. Compilar a ejecutable (lo más ligero posible)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ControlOficios ^
            --icon datos/bdp_icon_alt.ico aplicacion.py
```

> El `^` es continuación de línea en Windows (CMD). En una sola línea, o en
> PowerShell/Linux usa `\` en vez de `^`.

- `--windowed` (equivale a `--noconsole`): oculta la consola negra.
- `--onefile`: un único `.exe` en `dist/ControlOficios.exe`.
- `--name ControlOficios`: el ejecutable se llamará `ControlOficios.exe`.
- `--icon datos/bdp_icon_alt.ico`: **incrusta el ícono del banco en el `.exe`**
  (el que se ve en el Explorador, la barra de tareas y el acceso directo). Debe
  ser un archivo `.ico` (ya lo tienes en `datos/`).

### Ícono del ejecutable — detalles

- El `--icon` afecta al ícono del **archivo `.exe`**. El ícono de las **ventanas**
  en tiempo de ejecución lo pone la propia app con `iconbitmap` (lee
  `datos/bdp_icon_alt.ico`), así que conviene que ese archivo siga junto al `.exe`.
- Si cambias el ícono y Windows sigue mostrando el anterior, es la **caché de
  íconos** de Windows: renombra el `.exe` o reinicia el Explorador.

### Para reducir tamaño

1. Trabaja dentro de un **entorno virtual** con solo lo necesario instalado
   (`cryptography`, `pyinstaller`, y opcionalmente `pymupdf` para el visor de
   PDF y `Pillow` para el logo y la nitidez del visor). Así PyInstaller no
   arrastra librerías de más.
   Ten en cuenta que `pymupdf` añade ~25 MB al ejecutable: si no necesitas
   ver los PDF dentro de la app, omítelo y se usará el lector del sistema.
2. Añade **UPX** (ver abajo): `--upx-dir C:\ruta\upx`.
3. `--onedir` (en lugar de `--onefile`) arranca más rápido y suele pesar menos
   en total, aunque genera una carpeta en vez de un archivo único.

Nota: `cryptography` incluye binarios de OpenSSL, así que ~8–15 MB es lo
esperable para el ejecutable. Es el precio de tener cifrado serio.

### ¿Qué es UPX y cómo se usa?

**UPX** (*Ultimate Packer for eXecutables*) es un **compresor de ejecutables**:
comprime el `.exe` y, al abrirlo, se descomprime solo en memoria. El archivo
en disco pesa menos (a veces 30–50 %) y el programa funciona igual; el único
costo es unos milisegundos extra al iniciar. Es gratuito y de código abierto.

Cómo usarlo con PyInstaller (en Windows):

1. Descarga UPX de <https://upx.github.io> (el `.zip` para Windows) y
   descomprímelo, por ejemplo en `C:\upx`. Dentro está `upx.exe`.
2. Pásale la carpeta a PyInstaller con `--upx-dir`:

   ```bash
   pyinstaller --onefile --windowed --name ControlOficios ^
               --icon datos/bdp_icon_alt.ico ^
               --upx-dir C:\upx aplicacion.py
   ```

   PyInstaller detecta `upx.exe` en esa carpeta y comprime automáticamente los
   binarios al empaquetar.
3. (Opcional) Si algún módulo diera problemas al comprimirse, puedes excluirlo:
   `--upx-exclude vcruntime140.dll`. Y para no usar UPX en una compilación,
   `--noupx`.

Notas: no necesitas instalar UPX (basta con la carpeta descomprimida). Ten en
cuenta que **algunos antivirus** miran con recelo los ejecutables comprimidos
con UPX; si te da falsos positivos, compila sin UPX.

**Importante sobre las rutas:** el código detecta si corre como `.exe` y guarda
la carpeta `datos/` **junto al ejecutable** (no en la carpeta temporal). Ahí se
crean solos la clave, las credenciales, los oficios y la bitácora; coloca junto
al `.exe` el ícono (`datos/bdp_icon_alt.ico`) si quieres que se vea en las ventanas.

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
