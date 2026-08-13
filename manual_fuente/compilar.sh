#!/bin/bash
# Compila el manual en dos pasadas: la primera para medir en qué página cae
# cada título, la segunda para escribir esos números en el índice.
set -e
cd "$(dirname "$0")"
DOCX="$(cd "$(dirname "$0")/.." && pwd)/Manual de usuario - Control de Oficios.docx"

rm -f paginas.json
python3 logo.py >/dev/null
node manual.js                                   # pasada 1: índice sin números
cp "$DOCX" manual.docx
rm -f manual.pdf
soffice --headless -env:UserInstallation=file:///tmp/lo_manual \
    --convert-to pdf --outdir . manual.docx >/dev/null 2>&1
python paginas.py                                # deduce las páginas
node manual.js                                   # pasada 2: índice con números
cp "$DOCX" manual.docx
rm -f manual.pdf page-*.jpg
soffice --headless -env:UserInstallation=file:///tmp/lo_manual \
    --convert-to pdf --outdir . manual.docx >/dev/null 2>&1
pdftoppm -jpeg -r 100 manual.pdf page
ls page-*.jpg
