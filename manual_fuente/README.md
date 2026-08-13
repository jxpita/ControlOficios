# Fuente del manual de usuario

Genera **`Manual de usuario - Control de Oficios.docx`**, que se encuentra en
la raíz del proyecto. El manual no se escribe a mano en Word: se compone desde
aquí, de modo que al cambiar la aplicación baste con actualizar el texto y
volver a compilarlo.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `manual.js` | Portada, índice, contenido y pie de página. Es el archivo que se edita |
| `logo.py` | Recorta el logotipo del banco y lo repinta sobre el azul corporativo exacto |
| `logo_banco.jpeg` | Logotipo original del que parte `logo.py` |
| `paginas.py` | Deduce en qué página cae cada título, para numerar el índice |
| `compilar.sh` | Compila el documento en dos pasadas |

## Compilar

```bash
npm install docx          # solo la primera vez
./compilar.sh
```

Se compila **en dos pasadas**: la primera genera el documento con el índice sin
numerar y lo convierte a PDF; `paginas.py` lee de ese PDF en qué página quedó
cada título; la segunda pasada vuelve a generarlo, ya con los números. Un
índice automático de Word no sirve aquí, porque solo se rellena al abrirlo en
Word y quedaría vacío en cualquier otro visor.

`compilar.sh` deja además el PDF y una imagen por página, útiles para revisar
el resultado antes de distribuirlo.

## Dependencias

`docx` (npm), `Pillow` (Python), LibreOffice (`soffice`) y `pdftoppm`
(Poppler). Solo hacen falta para **regenerar** el manual; la aplicación no las
necesita.

## Al actualizar el manual

En `manual.js`, junto al principio, están la versión de la aplicación, la
versión del documento y la fecha de elaboración, que aparecen en la portada y
en el pie de página. Conviene actualizarlas en el mismo cambio.
