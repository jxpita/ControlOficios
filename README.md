# Gestor de Oficios — Unidad de Cumplimiento

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

En el primer arranque no hay usuarios: la pantalla pedirá crear un
**administrador**. Luego inicia sesión con esas credenciales.

## 3. Estructura

```
oficios_tracker/
├── aplicacion.py         # Interfaz (ingreso + pestañas). Punto de entrada.
├── configuracion.py      # Rutas y constantes
├── cifrado.py            # Cifrado Fernet + hashing de contraseñas
├── autenticacion.py      # Ingreso y usuarios del sistema
├── almacen_empleados.py  # Lee empleados.csv para el combo
├── almacen_oficios.py    # CRUD de oficios + referencia secuencial
├── metricas.py           # Cálculo de métricas del tablero
└── datos/                # Se crea sola; contiene:
    ├── clave_maestra.key   (clave de cifrado — PROTEGER / RESPALDAR)
    ├── credenciales.dat    (usuarios del sistema, cifrado)
    ├── oficios.dat         (registros, cifrado)
    └── empleados.csv       (idUsuario,nombreUsuario,nombreEmpleado)
```

La referencia interna tiene el formato **`UDC-OFICIO-AAAAMMDD-NNNN`**.
El secuencial `NNNN` (4 dígitos, desde `0000`) se reinicia por cada **día de
recepción**. Si prefieres usar la fecha de registro o un contador global que
nunca reinicie, se cambia únicamente en `almacen_oficios._generar_referencia`.

## 4. Compilar a ejecutable (lo más ligero posible)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name GestorOficios aplicacion.py
```

- `--windowed` (equivale a `--noconsole`): oculta la consola negra.
- `--onefile`: un único `.exe` en `dist/GestorOficios.exe`.

Para reducir tamaño:

1. Trabaja dentro de un **entorno virtual** con solo `cryptography` y
   `pyinstaller` instalados (evita arrastrar librerías de más).
2. Añade **UPX**: descarga upx y usa `--upx-dir C:\ruta\upx`.
3. `--onedir` (en lugar de `--onefile`) arranca más rápido y suele pesar menos
   en total, aunque genera una carpeta en vez de un archivo único.

Nota: `cryptography` incluye binarios de OpenSSL, así que ~8–15 MB es lo
esperable para el ejecutable. Es el precio de tener cifrado serio.

**Importante sobre las rutas:** el código detecta si corre como `.exe` y guarda
la carpeta `datos/` **junto al ejecutable** (no en la carpeta temporal). Copia
tu `empleados.csv` dentro de `datos/` al lado del `.exe`.

## 5. Notas de seguridad (léelas)

- **Contraseñas:** no se guardan ni en claro ni "cifradas": se guarda su
  **hash con sal** (PBKDF2-HMAC-SHA256). Nadie —ni tú— puede recuperarlas;
  solo verificarlas. Es lo correcto.
- **Oficios y credenciales:** cifrado **autenticado** con Fernet. Si alguien
  edita un byte del archivo, el descifrado falla y la app avisa de manipulación.
- **Límite honesto:** la `clave_maestra.key` vive en disco junto a los datos.
  Esto **frena la manipulación casual** (abrir el archivo y editarlo), pero un
  usuario con acceso a la máquina y al ejecutable podría, con esfuerzo, extraer
  la clave. El cifrado de archivos da *confidencialidad e integridad*, no
  *control de acceso real*. Para eso, ver la sección 6.
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
