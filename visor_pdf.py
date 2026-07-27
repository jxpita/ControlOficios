"""
Visor de PDF integrado en la aplicación (para ver la respuesta de un oficio
sin salir de la interfaz).

Requiere **PyMuPDF** (`pip install pymupdf`). Es la única dependencia extra y
se eligió porque:
  - se instala como "wheel" (no necesita binarios externos como poppler),
  - funciona en Windows sin instalar nada más,
  - se empaqueta bien con PyInstaller.

Si PyMuPDF NO está instalado, la aplicación sigue funcionando: `abrir_visor`
devuelve False y quien lo llama puede ofrecer abrir el PDF con el lector del
sistema (ver `abrir_con_sistema`).

Las páginas se renderizan a imagen con PyMuPDF y se muestran en un Canvas de
Tkinter, con navegación de páginas, zoom y desplazamiento.
"""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

from configuracion import (
    ARCHIVO_ICONO, COLOR_AZUL, COLOR_BLANCO, COLOR_GRIS_CLARO, COLOR_TEXTO
)

try:
    import fitz  # PyMuPDF
    PYMUPDF_DISPONIBLE = True
except ImportError:
    PYMUPDF_DISPONIBLE = False

try:
    from PIL import Image, ImageTk
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False


def abrir_con_sistema(ruta) -> bool:
    """Abre el PDF con el lector predeterminado del sistema operativo.
    Alternativa cuando no se puede mostrar dentro de la app."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(ruta))                      # noqa: S606 (Windows)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(ruta)])
        else:
            subprocess.Popen(["xdg-open", str(ruta)])
        return True
    except Exception:
        return False


class VisorPDF(tk.Toplevel):
    """Ventana con el PDF renderizado página a página."""

    ZOOM_MIN, ZOOM_MAX, ZOOM_PASO = 0.4, 4.0, 0.2

    def __init__(self, maestro, ruta_pdf, titulo="Respuesta del oficio"):
        super().__init__(maestro)
        self.title(titulo)
        self.configure(bg=COLOR_GRIS_CLARO)
        self.geometry("900x700")
        if ARCHIVO_ICONO.exists():
            try:
                self.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        self.documento = fitz.open(str(ruta_pdf))
        self.pagina_actual = 0
        self.zoom = 1.0
        self._imagen = None      # referencia viva para que Tk no la libere
        self._id_imagen = None   # identificador del objeto en el lienzo

        self._construir_barra()
        self._construir_lienzo()
        self._dibujar_pagina()

    # -- Construcción de la interfaz -----------------------------------------
    def _construir_barra(self):
        barra = tk.Frame(self, bg=COLOR_AZUL, height=44)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        def boton(texto, comando, lado="left"):
            btn = tk.Button(barra, text=texto, command=comando, bg=COLOR_AZUL,
                            fg=COLOR_BLANCO, relief="flat", cursor="hand2",
                            activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                            font=("Helvetica", 10, "bold"), padx=10, takefocus=0)
            btn.pack(side=lado, padx=3, pady=6)
            return btn

        boton("‹ Anterior", self.pagina_anterior)
        boton("Siguiente ›", self.pagina_siguiente)
        self.lbl_pagina = tk.Label(barra, text="", bg=COLOR_AZUL, fg=COLOR_BLANCO,
                                   font=("Helvetica", 10))
        self.lbl_pagina.pack(side="left", padx=12)

        boton("Cerrar", self.destroy, lado="right")
        boton("Zoom +", self.acercar, lado="right")
        boton("Zoom −", self.alejar, lado="right")

    def _construir_lienzo(self):
        contenedor = tk.Frame(self, bg=COLOR_GRIS_CLARO)
        contenedor.pack(fill="both", expand=True)

        self.lienzo = tk.Canvas(contenedor, bg=COLOR_GRIS_CLARO, highlightthickness=0)
        barra_v = ttk.Scrollbar(contenedor, orient="vertical", command=self.lienzo.yview)
        barra_h = ttk.Scrollbar(contenedor, orient="horizontal", command=self.lienzo.xview)
        self.lienzo.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)

        barra_v.pack(side="right", fill="y")
        barra_h.pack(side="bottom", fill="x")
        self.lienzo.pack(side="left", fill="both", expand=True)

        # Rueda del ratón (Windows/macOS y Linux).
        self.lienzo.bind_all("<MouseWheel>",
                             lambda e: self.lienzo.yview_scroll(int(-e.delta / 120), "units"))
        self.lienzo.bind_all("<Button-4>", lambda e: self.lienzo.yview_scroll(-1, "units"))
        self.lienzo.bind_all("<Button-5>", lambda e: self.lienzo.yview_scroll(1, "units"))
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Prior>", lambda e: self.pagina_anterior())
        self.bind("<Next>", lambda e: self.pagina_siguiente())
        # Recentrar la página cuando cambia el tamaño de la ventana.
        self.lienzo.bind("<Configure>", lambda e: self._centrar_pagina())

    # -- Navegación y zoom ----------------------------------------------------
    def pagina_anterior(self):
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self._dibujar_pagina()

    def pagina_siguiente(self):
        if self.pagina_actual < self.documento.page_count - 1:
            self.pagina_actual += 1
            self._dibujar_pagina()

    def acercar(self):
        self.zoom = min(self.ZOOM_MAX, self.zoom + self.ZOOM_PASO)
        self._dibujar_pagina()

    def alejar(self):
        self.zoom = max(self.ZOOM_MIN, self.zoom - self.ZOOM_PASO)
        self._dibujar_pagina()

    # -- Renderizado ----------------------------------------------------------
    def _dibujar_pagina(self):
        pagina = self.documento.load_page(self.pagina_actual)
        matriz = fitz.Matrix(self.zoom * 2, self.zoom * 2)   # x2 = mejor nitidez
        pixmap = pagina.get_pixmap(matrix=matriz)

        if PILLOW_DISPONIBLE:
            imagen = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            imagen = imagen.resize((pixmap.width // 2, pixmap.height // 2),
                                   Image.Resampling.LANCZOS)
            self._imagen = ImageTk.PhotoImage(imagen)
        else:
            # Sin Pillow: Tk puede leer PPM directamente.
            self._imagen = tk.PhotoImage(data=pixmap.tobytes("ppm"))

        self.lienzo.delete("all")
        self._id_imagen = self.lienzo.create_image(0, 0, anchor="nw", image=self._imagen)
        self._centrar_pagina()
        self.lbl_pagina.config(
            text=f"Página {self.pagina_actual + 1} de {self.documento.page_count}"
                 f"   ·   Zoom {int(self.zoom * 100)}%")

    def _centrar_pagina(self):
        """Centra horizontalmente la página dentro del lienzo (y verticalmente
        si sobra espacio), para que el documento no quede pegado a la izquierda."""
        if self._imagen is None or not hasattr(self, "_id_imagen"):
            return
        ancho_lienzo = self.lienzo.winfo_width()
        alto_lienzo = self.lienzo.winfo_height()
        ancho_img = self._imagen.width()
        alto_img = self._imagen.height()

        x = max((ancho_lienzo - ancho_img) // 2, 0)
        y = max((alto_lienzo - alto_img) // 2, 0)
        self.lienzo.coords(self._id_imagen, x, y)
        # La región desplazable cubre al menos el lienzo completo, de modo que
        # la imagen centrada no "salte" al desplazarse.
        self.lienzo.configure(scrollregion=(
            0, 0, max(ancho_img, ancho_lienzo), max(alto_img, alto_lienzo)))

    def destroy(self):
        # Liberar los enlaces globales del ratón y cerrar el documento.
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                self.unbind_all(evento)
            except tk.TclError:
                pass
        try:
            self.documento.close()
        except Exception:
            pass
        super().destroy()


def abrir_visor(maestro, ruta_pdf, titulo="Respuesta del oficio") -> bool:
    """Abre el PDF dentro de la aplicación.

    Devuelve True si se mostró en la app; False si PyMuPDF no está instalado o
    el PDF no se pudo abrir (en ese caso, quien llama puede recurrir a
    `abrir_con_sistema`).
    """
    if not PYMUPDF_DISPONIBLE:
        return False
    try:
        VisorPDF(maestro, ruta_pdf, titulo)
        return True
    except Exception:
        return False
