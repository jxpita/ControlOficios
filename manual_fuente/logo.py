"""Prepara el logo del banco para la portada del manual.

El archivo original es un JPEG con el logotipo blanco sobre un fondo azul que
NO coincide exactamente con el azul corporativo de la aplicación (#152342). Si
se coloca tal cual sobre una banda de ese azul se nota el recuadro.

Aquí se recorta el logotipo y se vuelve a pintar sobre el azul exacto,
conservando el suavizado de los bordes: se interpreta el brillo de cada píxel
como "cuánto blanco hay" y se mezcla blanco sobre azul con esa proporción.
"""
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "logo_banco.jpeg"

AZUL = (0x15, 0x23, 0x42)     # COLOR_AZUL de configuracion.py
BLANCO = (255, 255, 255)
MARGEN = 16                   # píxeles de aire alrededor del logotipo
ESCALA = 2                    # para que no se vea pixelado al imprimir

imagen = Image.open(ORIGEN).convert("RGB")
gris = imagen.convert("L")

# Recorte ajustado al logotipo blanco.
izq, arr, der, aba = gris.point(lambda v: 255 if v > 110 else 0).getbbox()
caja = (max(izq - MARGEN, 0), max(arr - MARGEN, 0),
        min(der + MARGEN, imagen.width), min(aba + MARGEN, imagen.height))
gris = gris.crop(caja)

# Brillo del fondo original: ese nivel es "0 % de blanco". Se toma la mediana
# del borde de la imagen (que es todo fondo) y no el mínimo global, porque el
# ruido del JPEG deja píxeles sueltos más oscuros que falsearían la referencia.
borde = (list(gris.crop((0, 0, gris.width, 3)).getdata())
         + list(gris.crop((0, gris.height - 3, gris.width, gris.height)).getdata())
         + list(gris.crop((0, 0, 3, gris.height)).getdata())
         + list(gris.crop((gris.width - 3, 0, gris.width, gris.height)).getdata()))
borde.sort()
fondo = borde[len(borde) // 2]
RUIDO = 8          # margen para que el grano del JPEG no aclare el fondo
rango = max(255 - fondo - RUIDO, 1)

# alfa = proporción de blanco de cada píxel (0 = fondo, 255 = blanco puro).
alfa = gris.point(
    lambda v: max(0, min(255, round((v - fondo - RUIDO) * 255 / rango))))

logo = Image.composite(
    Image.new("RGB", gris.size, BLANCO),
    Image.new("RGB", gris.size, AZUL),
    alfa,
)
logo = logo.resize((logo.width * ESCALA, logo.height * ESCALA), Image.LANCZOS)
logo.save(BASE / "logo_portada.png")

print(f"logo_portada.png  {logo.width}x{logo.height}  "
      f"proporción {logo.width / logo.height:.2f}")
