# Control de Oficios — Unidad de Cumplimiento

Aplicación de escritorio (Python + Tkinter) para registrar y hacer seguimiento
a los oficios/circulares que llegan a la unidad. Almacenamiento en archivos
cifrados. Incluye ingreso (login), alta de usuarios y un tablero de métricas.

Todos los nombres de archivos, funciones y variables están en español. Solo
permanecen en inglés las palabras propias de Python y de las librerías
(`def`, `class`, `import`, `ttk`, `.pack()`, etc.), que no se pueden traducir.

## 1. Requisitos

- Python 3.9 o superior (recomendado 3.11+).
- Una sola dependencia externa:

```bash
pip install cryptography
```

`tkinter` viene con Python en Windows y macOS. En Linux, si falta:
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
- **Usuario (regular):** usa la aplicación (registrar oficios, gestionar
  estados/responsables, tablero) pero **no ve la pestaña "Usuarios"** ni puede
  gestionar cuentas.

La gestión de usuarios (crear/editar/eliminar, asignar rol) está disponible
solo para superusuario y administrador. Nadie puede eliminarse a sí mismo
mientras su sesión está activa.

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
├── almacen_empleados.py  # Lee empleados.csv para el combo
├── almacen_oficios.py    # CRUD de oficios + referencia secuencial
├── metricas.py           # Cálculo de métricas del tablero
└── datos/                # Se crea sola; contiene:
    ├── clave_maestra.key   (clave de cifrado — PROTEGER / RESPALDAR)
    ├── credenciales.dat    (usuarios del sistema, cifrado)
    ├── oficios.dat         (registros, cifrado)
    ├── actividad.log       (bitácora de auditoría, texto plano)
    └── empleados.csv       (idUsuario,nombreUsuario,nombreEmpleado)
```

La referencia interna tiene el formato **`UDC-OFICIO-AAAAMMDD-NNNN`**.
El secuencial `NNNN` (4 dígitos, desde `0000`) se reinicia por cada **día de
recepción**. Si prefieres usar la fecha de registro o un contador global que
nunca reinicie, se cambia únicamente en `almacen_oficios._generar_referencia`.

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
   (`cryptography`, `pyinstaller` y, si quieres que se vea el logo, `Pillow`).
   Así PyInstaller no arrastra librerías de más.
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
la carpeta `datos/` **junto al ejecutable** (no en la carpeta temporal). Copia
tu `empleados.csv` dentro de `datos/` al lado del `.exe`.

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
