"""Lee manual.pdf y anota en paginas.json la página de cada título del índice.

Los títulos se extraen del propio manual.js (las llamadas a h1/h2), así que no
hay una lista duplicada que mantener.
"""
import json
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent

fuente = (BASE / "manual.js").read_text(encoding="utf-8")
# Solo las llamadas dentro del contenido, no las definiciones de las funciones.
titulos = re.findall(r'\n  h([12])\("([^"]+)"\)', fuente)

texto = subprocess.run(
    ["pdftotext", "-layout", str(BASE / "manual.pdf"), "-"],
    capture_output=True, text=True, check=True,
).stdout
paginas = texto.split("\f")

# El contenido empieza después de la portada y del índice: se busca a partir de
# la página donde aparece el primer título de nivel 1 por segunda vez.
primer_titulo = titulos[0][1]
inicio = 0
for numero, pagina in enumerate(paginas, start=1):
    if primer_titulo in pagina and numero > 1:
        # La primera aparición (aparte de la portada) es la del índice.
        if inicio == 0:
            inicio = numero
        else:
            inicio = numero
            break

resultado = {}
faltantes = []
for _, titulo in titulos:
    for numero in range(inicio, len(paginas) + 1):
        if titulo in paginas[numero - 1]:
            resultado[titulo] = numero
            break
    else:
        faltantes.append(titulo)

(BASE / "paginas.json").write_text(
    json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"{len(resultado)} títulos ubicados, contenido desde la página {inicio}")
if faltantes:
    print("SIN UBICAR:", faltantes)
