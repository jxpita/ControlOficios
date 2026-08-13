import calendar
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter import font as tkfont
from datetime import date, datetime
from pathlib import Path

import autenticacion
import configuracion
import almacen_oficios as oficios
import carga_masiva
import parametros
import tipos_accion
import respaldo
import visor_pdf
import metricas
from configuracion import (
    ESTADOS, ARCHIVO_LOGO, ARCHIVO_ICONO, PREFIJO_REFERENCIA,
    DIR_RESPALDOS, DIAS_RESPALDO_POR_DEFECTO,
    ROL_SUPERUSUARIO, ROL_ADMINISTRADOR, ROL_USUARIO,
    ROLES_GESTORES, INSTITUCIONES, PRIORIDADES, PRIORIDAD_POR_DEFECTO,
    TIPOS_IDENTIFICACION, TIPOS_IMPLICADO, VALORES_LCI,
    COLOR_AZUL, COLOR_BLANCO, COLOR_GRIS_CLARO, COLOR_TEXTO, COLOR_TEXTO_INV
)

try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# Tamaño por debajo del cual la ventana deja de encoger: es el punto en el que
# todavía caben las dos columnas de los formularios y las tablas completas.
TAMANO_MINIMO = (940, 620)

# Ancho máximo de la tarjeta de ingreso. Los formularios de una sola columna se
# vuelven incómodos de leer estirados de lado a lado de un monitor, así que la
# tarjeta se queda en este ancho y se centra.
ANCHO_TARJETA_INGRESO = 430


def maximizar_ventana(ventana):
    """Abre la ventana ocupando toda la pantalla, sin bloquear el redimensionado.

    No hay una forma única de maximizar entre sistemas: Windows entiende
    `state("zoomed")` y los gestores de ventanas de Linux usan el atributo
    "-zoomed". Si ninguna funciona (o no hay gestor de ventanas), se recurre a
    fijar el tamaño de la pantalla, que da el mismo resultado visible.

    Importante: NO se toca `resizable`, de modo que el botón de
    maximizar/restaurar sigue disponible y la ventana se puede reajustar.
    """
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    for intento in (lambda: ventana.state("zoomed"),
                    lambda: ventana.attributes("-zoomed", True)):
        try:
            intento()
        except tk.TclError:
            continue
        ventana.update_idletasks()
        if ventana.winfo_width() >= ancho_pantalla * 0.8:
            return
    ventana.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")


class SelectorFecha(tk.Frame):
    """Campo de fecha con calendario emergente. No requiere librerías externas.

    Muestra un cuadro de texto (AAAA-MM-DD) y un botón que abre un calendario
    para elegir la fecha con el ratón. También se puede escribir la fecha a mano.
    Se usa `.get()` para leer el texto y `.set(fecha)` para fijarlo.
    """
    DIAS_SEMANA = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    def __init__(self, maestro, fecha_inicial=None, permitir_vacio=False,
                 fecha_maxima=None):
        """`permitir_vacio=True` deja el campo en blanco y ofrece un botón
        "Limpiar" en el calendario (para fechas opcionales).

        `fecha_maxima` es la última fecha seleccionable; por omisión **hoy**,
        porque no se puede registrar algo que aún no ha ocurrido. Pásalo como
        `False` para no aplicar ningún tope."""
        super().__init__(maestro, background=COLOR_BLANCO)
        self.permitir_vacio = permitir_vacio
        if fecha_maxima is None:
            fecha_maxima = date.today()
        self.fecha_maxima = fecha_maxima or None   # False -> sin tope
        self.entrada = ttk.Entry(self, width=14)
        self.entrada.pack(side="left")
        self.boton = tk.Button(self, text="📅", command=self._alternar_calendario,
                               relief="flat", cursor="hand2", bg=COLOR_GRIS_CLARO,
                               activebackground="#DDE3EC", padx=6, takefocus=0)
        self.boton.pack(side="left", padx=(4, 0))
        self._popup = None
        if fecha_inicial is None and permitir_vacio:
            self.set("")
        else:
            self.set(fecha_inicial or date.today())

    # -- API pública ----------------------------------------------------------
    def get(self):
        return self.entrada.get().strip()

    def set(self, valor):
        if isinstance(valor, date):
            valor = valor.isoformat()
        self.entrada.delete(0, "end")
        self.entrada.insert(0, valor)

    # -- Interno --------------------------------------------------------------
    def _fecha_base(self):
        """Fecha desde la que se abre el calendario (la escrita, o hoy)."""
        try:
            return datetime.strptime(self.get(), "%Y-%m-%d").date()
        except ValueError:
            return date.today()

    def _alternar_calendario(self):
        if self._popup is not None and self._popup.winfo_exists():
            self._cerrar()
            return
        base = self._fecha_base()
        # No abrir el calendario en un mes posterior al tope.
        if self.fecha_maxima and base > self.fecha_maxima:
            base = self.fecha_maxima
        self._anio, self._mes = base.year, base.month

        self._popup = tk.Toplevel(self)
        self._popup.title("Seleccionar fecha")
        self._popup.configure(bg=COLOR_BLANCO)
        self._popup.resizable(False, False)
        self._popup.transient(self.winfo_toplevel())
        # Usar el mismo ícono del banco que la ventana principal.
        if ARCHIVO_ICONO.exists():
            try:
                self._popup.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass
        self._popup.bind("<Escape>", lambda e: self._cerrar())
        self._popup.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._dibujar_calendario()
        self._ubicar_popup()

    def _ubicar_popup(self):
        """Coloca el calendario junto al campo, abriéndose hacia ARRIBA si no
        cabe debajo, y sin salirse de los bordes de la pantalla."""
        popup = self._popup
        popup.update_idletasks()
        ancho, alto = popup.winfo_width(), popup.winfo_height()
        pantalla_ancho = popup.winfo_screenwidth()
        pantalla_alto = popup.winfo_screenheight()

        x = self.winfo_rootx()
        abajo = self.winfo_rooty() + self.winfo_height() + 2
        arriba = self.winfo_rooty() - alto - 2

        # Si no cabe debajo pero sí encima, se abre hacia arriba.
        if abajo + alto > pantalla_alto and arriba >= 0:
            y = arriba
        else:
            y = min(abajo, max(0, pantalla_alto - alto))

        # Evitar que se salga por los lados.
        x = max(0, min(x, pantalla_ancho - ancho))
        popup.geometry(f"+{int(x)}+{int(y)}")

    def _cerrar(self):
        if self._popup is not None:
            self._popup.destroy()
            self._popup = None

    def _cambiar_mes(self, delta):
        mes = self._mes - 1 + delta
        self._anio += mes // 12
        self._mes = mes % 12 + 1
        self._dibujar_calendario()

    def _dibujar_calendario(self):
        for hijo in self._popup.winfo_children():
            hijo.destroy()

        # Cabecera con navegación de mes.
        cabecera = tk.Frame(self._popup, bg=COLOR_AZUL)
        cabecera.pack(fill="x")
        tk.Button(cabecera, text="‹", command=lambda: self._cambiar_mes(-1),
                  bg=COLOR_AZUL, fg=COLOR_BLANCO, relief="flat", cursor="hand2",
                  activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                  font=("Helvetica", 12, "bold"), takefocus=0, width=3).pack(side="left")
        tk.Label(cabecera, text=f"{self.MESES[self._mes - 1]} {self._anio}",
                 bg=COLOR_AZUL, fg=COLOR_BLANCO, font=("Helvetica", 10, "bold")
                 ).pack(side="left", expand=True)
        # El botón "mes siguiente" se desactiva si ya se alcanzó el mes tope.
        hay_siguiente = not (self.fecha_maxima and
                             (self._anio, self._mes) >=
                             (self.fecha_maxima.year, self.fecha_maxima.month))
        tk.Button(cabecera, text="›",
                  command=(lambda: self._cambiar_mes(1)) if hay_siguiente else None,
                  bg=COLOR_AZUL, fg=COLOR_BLANCO if hay_siguiente else "#5A6B8C",
                  relief="flat", cursor="hand2" if hay_siguiente else "arrow",
                  activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                  state="normal" if hay_siguiente else "disabled",
                  disabledforeground="#5A6B8C",
                  font=("Helvetica", 12, "bold"), takefocus=0, width=3).pack(side="right")

        cuerpo = tk.Frame(self._popup, bg=COLOR_BLANCO, padx=6, pady=6)
        cuerpo.pack()
        for col, nombre in enumerate(self.DIAS_SEMANA):
            tk.Label(cuerpo, text=nombre, bg=COLOR_BLANCO, fg="#6B7280",
                     font=("Helvetica", 8, "bold"), width=3).grid(row=0, column=col, padx=1, pady=(0, 2))

        hoy = date.today()
        seleccion = self._fecha_base()
        semanas = calendar.Calendar(firstweekday=0).monthdayscalendar(self._anio, self._mes)
        for fila, semana in enumerate(semanas, start=1):
            for col, dia in enumerate(semana):
                if dia == 0:
                    continue
                actual = date(self._anio, self._mes, dia)
                # Las fechas posteriores al tope (hoy) no son seleccionables.
                bloqueada = bool(self.fecha_maxima) and actual > self.fecha_maxima
                if bloqueada:
                    fondo, texto = COLOR_BLANCO, "#C3C9D4"
                elif actual == seleccion:
                    fondo, texto = COLOR_AZUL, COLOR_BLANCO
                elif actual == hoy:
                    fondo, texto = COLOR_GRIS_CLARO, COLOR_AZUL
                else:
                    fondo, texto = COLOR_BLANCO, COLOR_TEXTO
                tk.Button(cuerpo, text=str(dia), width=3, relief="flat",
                          cursor="arrow" if bloqueada else "hand2",
                          bg=fondo, fg=texto,
                          activebackground=fondo if bloqueada else "#1A2E5A",
                          activeforeground=texto if bloqueada else COLOR_BLANCO,
                          state="disabled" if bloqueada else "normal",
                          disabledforeground="#C3C9D4",
                          font=("Helvetica", 9), takefocus=0,
                          command=None if bloqueada else (lambda d=actual: self._elegir(d))
                          ).grid(row=fila, column=col, padx=1, pady=1)

        pie = tk.Frame(self._popup, bg=COLOR_BLANCO, pady=4)
        pie.pack(fill="x")
        tk.Button(pie, text="Hoy", command=lambda: self._elegir(date.today()),
                  bg=COLOR_GRIS_CLARO, fg=COLOR_AZUL, relief="flat", cursor="hand2",
                  font=("Helvetica", 9, "bold"), takefocus=0).pack(side="left", expand=True)
        if self.permitir_vacio:
            tk.Button(pie, text="Limpiar", command=lambda: self._elegir(""),
                      bg=COLOR_GRIS_CLARO, fg=COLOR_AZUL, relief="flat", cursor="hand2",
                      font=("Helvetica", 9, "bold"), takefocus=0).pack(side="left", expand=True)

    def _elegir(self, fecha):
        self.set(fecha)
        self._cerrar()


class SelectorArchivo(ttk.Frame):
    """Campo para elegir un archivo: botón + nombre del archivo elegido.

    Guarda la ruta completa pero muestra solo el nombre, que es lo único que
    aporta información en el formulario.
    """

    def __init__(self, maestro, tipos, titulo="Seleccionar archivo", ancho=34):
        super().__init__(maestro)
        self._tipos = tipos
        self._titulo = titulo
        self._ruta = ""
        ttk.Button(self, text="Examinar", command=self._elegir).pack(side="left")
        self.etiqueta = ttk.Label(self, text="(ningún archivo)", width=ancho,
                                  foreground="#6B7280", font=("Helvetica", 8))
        self.etiqueta.pack(side="left", padx=6)
        self.btn_quitar = ttk.Button(self, text="Quitar", width=7,
                                     command=lambda: self.set(""))
        self.btn_quitar.pack(side="left")
        self._actualizar()

    def _elegir(self):
        ruta = filedialog.askopenfilename(title=self._titulo, filetypes=self._tipos)
        if ruta:
            self.set(ruta)

    def _actualizar(self):
        nombre = Path(self._ruta).name if self._ruta else ""
        self.etiqueta.config(text=nombre or "(ningún archivo)",
                             foreground=COLOR_TEXTO if nombre else "#6B7280")
        self.btn_quitar.state(["!disabled"] if nombre else ["disabled"])

    def get(self):
        return self._ruta

    def set(self, ruta):
        self._ruta = ruta or ""
        self._actualizar()


class AplicacionPrincipal(ttk.Frame):
    # Texto que representa "ningún responsable" en los desplegables.
    SIN_RESPONSABLE = "(Sin responsable)"

    def __init__(self, maestro, usuario_sesion):
        super().__init__(maestro, padding=10)
        self.maestro = maestro
        self.usuario = usuario_sesion

        # --- Configuración de la ventana ---
        maestro.title(f"Control de Oficios · {self.usuario['nombre']} "
                      f"({self.usuario.get('rol', ROL_USUARIO)})")
        # No se fija un tamaño: se conserva el que tenga la ventana (maximizado
        # al arrancar, o el que la persona haya elegido). Solo se garantiza el
        # mínimo por debajo del cual el contenido dejaría de caber.
        maestro.minsize(*TAMANO_MINIMO)
        maestro.resizable(True, True)
        if ARCHIVO_ICONO.exists():
            try:
                maestro.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        # --- Estilos personalizados ---
        self._configurar_estilos()

        # Áreas con desplazamiento vertical (pestañas Oficios y Tablero).
        self._lienzos_desplazables = set()

        # Oficio cargado en el panel de edición: evita recargarlo (y borrar lo
        # que se esté escribiendo) cuando el listado se refresca solo.
        self._referencia_en_edicion = None

        # Etiquetas de texto largo que se re-ajustan al ancho de la ventana.
        self._etiquetas_ajustables = []
        # Etiquetas de los campos de los formularios (ver `_campo`) y los
        # recuadros que las contienen, a cuyo tamaño se ajustan.
        self._etiquetas_campo = []
        self._grupos_con_etiquetas = []

        # --- Marco superior con logo ---
        self._crear_cabecera()

        # --- Cuaderno de pestañas ---
        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, pady=(10, 0))

        self.pestana_registro = ttk.Frame(self.cuaderno, padding=15)
        self.pestana_listado = ttk.Frame(self.cuaderno, padding=10)
        self.pestana_usuarios = ttk.Frame(self.cuaderno, padding=15)
        self.pestana_tablero = ttk.Frame(self.cuaderno, padding=15)
        self.pestana_configuracion = ttk.Frame(self.cuaderno, padding=15)

        self.cuaderno.add(self.pestana_registro, text="  Registrar oficio  ")
        self.cuaderno.add(self.pestana_listado, text="  Oficios  ")
        # La pestaña de usuarios solo está disponible para gestores.
        if self._puede_gestionar_usuarios():
            self.cuaderno.add(self.pestana_usuarios, text="  Usuarios  ")
        self.cuaderno.add(self.pestana_tablero, text="  Tablero  ")
        # La configuración del secuencial está disponible para los gestores.
        if self._puede_gestionar_usuarios():
            self.cuaderno.add(self.pestana_configuracion, text="  Configuración  ")

        self._construir_registro()
        self._construir_listado()
        if self._puede_gestionar_usuarios():
            self._construir_usuarios()
        self._construir_tablero()
        if self._puede_gestionar_usuarios():
            self._construir_configuracion()

        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)
        # Las etiquetas de los formularios se recortan al ancho de su recuadro.
        self.bind("<Configure>", self._ajustar_etiquetas_campo, add="+")
        self._ajustar_etiquetas_campo()

        # Rueda del ratón: un único manejador que decide qué desplazar según
        # dónde esté el puntero (Windows/macOS usan <MouseWheel>; Linux, los
        # botones 4 y 5).
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(evento, self._al_girar_rueda)

        # Al volver a la ventana se recargan los datos, por si otra persona los
        # modificó desde la carpeta compartida.
        self._ultimo_refresco = 0.0
        maestro.bind("<FocusIn>", self._al_recuperar_foco)

        # Copia de seguridad del día (la crea quien abra primero la aplicación).
        self._lanzar_respaldo_diario()

        self.pack(fill="both", expand=True)

    def _configurar_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        # Colores base
        estilo.configure("TFrame", background=COLOR_BLANCO)
        estilo.configure("TLabel", background=COLOR_BLANCO, foreground=COLOR_TEXTO, font=("Helvetica", 10))
        estilo.configure("TButton", font=("Helvetica", 10, "bold"), background=COLOR_AZUL, foreground=COLOR_BLANCO)
        estilo.map("TButton",
                   background=[("active", "#1A2E5A"), ("pressed", "#0F1F3A")],
                   foreground=[("active", COLOR_BLANCO), ("pressed", COLOR_BLANCO)])
        estilo.configure("TEntry", fieldbackground=COLOR_BLANCO, foreground=COLOR_TEXTO)
        estilo.configure("TCombobox", fieldbackground=COLOR_BLANCO, foreground=COLOR_TEXTO)
        estilo.configure("Treeview", background=COLOR_BLANCO, foreground=COLOR_TEXTO, rowheight=25)
        estilo.configure("Treeview.Heading", background=COLOR_AZUL,
                         foreground=COLOR_BLANCO, font=self.FUENTE_CABECERA,
                         padding=(6, 5))
        estilo.map("Treeview.Heading", background=[("active", "#1A2E5A")])
        # Los marcos con título (LabelFrame) deben compartir el fondo blanco de
        # las etiquetas; si no, se ven franjas grises alrededor de los textos.
        estilo.configure("TLabelframe", background=COLOR_BLANCO)
        estilo.configure("TLabelframe.Label", background=COLOR_BLANCO,
                         foreground=COLOR_TEXTO, font=("Helvetica", 9, "bold"))
        estilo.configure("TNotebook", background=COLOR_BLANCO)
        estilo.configure("TNotebook.Tab", background=COLOR_GRIS_CLARO, foreground=COLOR_TEXTO, padding=[10, 4])
        estilo.map("TNotebook.Tab", background=[("selected", COLOR_AZUL)], foreground=[("selected", COLOR_BLANCO)])

    def _crear_cabecera(self):
        """Marco superior con logo y título."""
        cabecera = tk.Frame(self, bg=COLOR_AZUL, height=90)
        cabecera.pack(fill="x", pady=(0, 10))
        cabecera.pack_propagate(False)  # fijar altura

        # Logo (si existe y Pillow está disponible)
        logo_img = None
        if ARCHIVO_LOGO.exists() and PILLOW_AVAILABLE:
            try:
                img = Image.open(ARCHIVO_LOGO)
                # Mantener relación de aspecto, ajustando al alto de la cabecera menos margen
                base_height = 60
                w_percent = base_height / float(img.size[1])
                new_width = int(float(img.size[0]) * w_percent)
                img = img.resize((new_width, base_height), Image.Resampling.LANCZOS)
                logo_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Error cargando logo:", e)
        if logo_img:
            lbl_logo = tk.Label(cabecera, image=logo_img, bg=COLOR_AZUL)
            lbl_logo.image = logo_img
            lbl_logo.pack(side="left", padx=3, pady=5)
        # else:
        # Texto alternativo si no hay logo
        lbl_titulo = tk.Label(cabecera, text="Banco del Pacífico", font=("Arial", 20, "bold"),
                                fg=COLOR_BLANCO, bg=COLOR_AZUL)
        lbl_titulo.pack(side="left", padx=3, pady=10)

        # Botón de cerrar sesión (extremo derecho). Relleno sólido en contraste
        # con la cabecera azul para que se lea claramente como un botón.
        btn_salir = tk.Button(cabecera, text="Cerrar sesión", command=self._cerrar_sesion,
                              bg=COLOR_BLANCO, fg=COLOR_AZUL, relief="flat", cursor="hand2",
                              activebackground="#DDE3EC", activeforeground=COLOR_AZUL,
                              font=("Helvetica", 10, "bold"), padx=14, pady=6,
                              bd=0, highlightthickness=0, takefocus=0)
        btn_salir.pack(side="right", padx=(6, 15), pady=10)
        btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg="#DDE3EC"))
        btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg=COLOR_BLANCO))

        # Cambiar la propia contraseña: disponible para cualquier rol.
        btn_clave = tk.Button(cabecera, text="Cambiar contraseña",
                              command=self._cambiar_clave_propia,
                              bg=COLOR_BLANCO, fg=COLOR_AZUL, relief="flat",
                              cursor="hand2", activebackground="#DDE3EC",
                              activeforeground=COLOR_AZUL,
                              font=("Helvetica", 10, "bold"), padx=14, pady=6,
                              bd=0, highlightthickness=0, takefocus=0)
        btn_clave.pack(side="right", pady=10)
        btn_clave.bind("<Enter>", lambda e: btn_clave.config(bg="#DDE3EC"))
        btn_clave.bind("<Leave>", lambda e: btn_clave.config(bg=COLOR_BLANCO))

        # Título de la aplicación
        self.lbl_app = tk.Label(cabecera, text=self._TITULO_LARGO,
                                font=("Arial", 14), fg=COLOR_BLANCO, bg=COLOR_AZUL)
        self.lbl_app.pack(side="right", padx=20, pady=10)

        # Widgets de ancho fijo de la cabecera: lo que quede es para el título.
        self._cabecera = cabecera
        self._cabecera_fijos = [w for w in (lbl_logo if logo_img else None,
                                            lbl_titulo, btn_salir, btn_clave)
                                if w is not None]
        cabecera.bind("<Configure>", self._ajustar_titulo_cabecera)

    # Título de la cabecera, en versión larga y corta.
    _TITULO_LARGO = "Control de Oficios — Unidad de Cumplimiento"
    _TITULO_CORTO = "Control de Oficios"

    def _ajustar_titulo_cabecera(self, evento=None):
        """Acorta el título de la cabecera cuando la ventana es estrecha.

        `pack` no encoge los widgets: al faltar sitio recorta el último, y el
        título acababa solapándose con el nombre del banco. Aquí se mide el
        espacio libre y se elige la versión más larga que quepa; si no cabe
        ninguna, el título se oculta y quedan el logo y los botones.
        """
        try:
            disponible = self._cabecera.winfo_width() - sum(
                w.winfo_reqwidth() for w in self._cabecera_fijos)
        except tk.TclError:
            return
        disponible -= 70          # separaciones de los pack (padx)
        fuente = tkfont.Font(font=self.lbl_app.cget("font"))
        for texto in (self._TITULO_LARGO, self._TITULO_CORTO, ""):
            if fuente.measure(texto) <= disponible:
                break
        # Solo se reconfigura si cambia: reconfigurar dispara otro <Configure>.
        if self.lbl_app.cget("text") != texto:
            self.lbl_app.config(text=texto)

    def _cambiar_clave_propia(self):
        """Diálogo para que el usuario en sesión cambie su propia contraseña.
        Disponible para cualquier rol; pide la contraseña actual."""
        dlg = tk.Toplevel(self)
        dlg.title("Cambiar contraseña")
        dlg.configure(bg=COLOR_BLANCO)
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        if ARCHIVO_ICONO.exists():
            try:
                dlg.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        cont = tk.Frame(dlg, bg=COLOR_BLANCO, padx=20, pady=16)
        cont.pack(fill="both", expand=True)
        tk.Label(cont, text="Cambiar mi contraseña", bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO, font=("Helvetica", 11, "bold")).pack(anchor="w")
        tk.Label(cont, text=f"{self.usuario['nombre']} ({self.usuario['usuario']})",
                 bg=COLOR_BLANCO, fg="#6B7280",
                 font=("Helvetica", 9)).pack(anchor="w", pady=(0, 12))

        campos = {}
        for clave, etiqueta in (("actual", "Contraseña actual"),
                                ("nueva", "Nueva contraseña"),
                                ("confirmar", "Confirmar nueva contraseña")):
            tk.Label(cont, text=etiqueta, bg=COLOR_BLANCO,
                     fg=COLOR_TEXTO).pack(anchor="w")
            entrada = ttk.Entry(cont, width=32, show="•")
            entrada.pack(fill="x", pady=(0, 8))
            campos[clave] = entrada

        var = tk.BooleanVar(value=False)

        def alternar():
            for entrada in campos.values():
                entrada.config(show="" if var.get() else "•")

        tk.Checkbutton(cont, text="Mostrar contraseñas", variable=var,
                       command=alternar, bg=COLOR_BLANCO, fg="#6B7280",
                       activebackground=COLOR_BLANCO, selectcolor=COLOR_BLANCO,
                       font=("Helvetica", 9), cursor="hand2", bd=0,
                       highlightthickness=0).pack(anchor="w", pady=(0, 12))

        def aceptar():
            if campos["nueva"].get() != campos["confirmar"].get():
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=dlg)
                return
            try:
                autenticacion.cambiar_clave_propia(
                    self.usuario["usuario"], campos["actual"].get(),
                    campos["nueva"].get())
            except ValueError as error:
                messagebox.showerror("Error", str(error), parent=dlg)
                return
            dlg.destroy()
            messagebox.showinfo("Listo", "Su contraseña se cambió correctamente.")

        barra = tk.Frame(cont, bg=COLOR_BLANCO)
        barra.pack(fill="x")
        tk.Button(barra, text="Cambiar", command=aceptar, bg=COLOR_AZUL,
                  fg=COLOR_BLANCO, activebackground="#1A2E5A",
                  activeforeground=COLOR_BLANCO, relief="flat", cursor="hand2",
                  font=("Helvetica", 10, "bold"), padx=12, pady=5).pack(side="right")
        tk.Button(barra, text="Cancelar", command=dlg.destroy, relief="flat",
                  cursor="hand2", font=("Helvetica", 10),
                  padx=12, pady=5).pack(side="right", padx=6)

        campos["actual"].bind("<Return>", lambda e: campos["nueva"].focus_set())
        campos["nueva"].bind("<Return>", lambda e: campos["confirmar"].focus_set())
        campos["confirmar"].bind("<Return>", lambda e: aceptar())
        dlg.update_idletasks()
        dlg.grab_set()
        campos["actual"].focus_set()

    def _cerrar_sesion(self):
        """Cierra la sesión actual y vuelve a la pantalla de ingreso."""
        if not messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la sesión actual?"):
            return
        autenticacion.cerrar_sesion(self.usuario["usuario"])
        self.destroy()
        # Restablecer la ventana a su tamaño de ingreso y mostrar el login.
        VentanaIngreso(self.maestro)

    # ---- Responsables: ahora son los usuarios del sistema (cualquier rol) ----
    def _usuarios_sistema(self):
        try:
            return autenticacion.listar_usuarios()
        except Exception:
            return []

    def _display_responsable(self, usuario, nombre):
        """Texto que se muestra en los desplegables para un responsable.
        Incluye el usuario entre paréntesis para evitar ambigüedad si dos
        personas comparten el mismo nombre."""
        if not usuario:
            return ""
        return f"{nombre} ({usuario})" if nombre else usuario

    def _valores_responsables(self):
        """Personas a las que se les puede asignar un oficio.

        Un administrador no puede asignar oficios a un superusuario, así que
        esas cuentas no aparecen en su desplegable. El superusuario ve a todos.
        """
        usuarios = self._usuarios_sistema()
        if self.usuario.get("rol") == ROL_ADMINISTRADOR:
            usuarios = [u for u in usuarios
                        if u.get("rol") != ROL_SUPERUSUARIO]
        return [self._display_responsable(u["usuario"], u["nombre"])
                for u in usuarios]

    def _responsable_por_display(self, display):
        """A partir del texto del desplegable devuelve (usuario, nombre).
        Para "(Sin responsable)" o vacío devuelve ("", "")."""
        if not display or display == self.SIN_RESPONSABLE:
            return "", ""
        for u in self._usuarios_sistema():
            if self._display_responsable(u["usuario"], u["nombre"]) == display:
                return u["usuario"], u["nombre"]
        return "", ""

    def _refrescar_responsables(self):
        """Repuebla los desplegables de responsable con los usuarios actuales."""
        valores = [self.SIN_RESPONSABLE] + self._valores_responsables()
        for atributo in ("combo_empleado", "combo_responsable_edicion"):
            combo = getattr(self, atributo, None)
            if combo is not None:
                try:
                    combo.config(values=valores)
                except tk.TclError:
                    pass

    def _abrir_implicados(self, evento=None):
        """Abre los implicados del oficio sobre el que se hizo doble clic."""
        fila = self.tabla.identify_row(evento.y) if evento else None
        referencia = fila or (self.tabla.selection() or [None])[0]
        if not referencia:
            return
        registro = self._oficio_por_referencia(referencia)
        if registro is None:
            return
        DialogoImplicados(self, self.usuario, registro)

    def _oficio_por_referencia(self, referencia):
        """Busca solo entre los oficios visibles para el usuario en sesión.

        Incluye los anulados cuando quien mira es un gestor: si no, al
        seleccionar uno con la casilla «Ver anulados» no se encontraría y no
        habría forma de reactivarlo.
        """
        for registro in oficios.listar_oficios_visibles(
                self.usuario["usuario"], self.usuario.get("rol"),
                incluir_anulados=True):
            if registro["referencia"] == referencia:
                return registro
        return None

    def _puede_gestionar_usuarios(self):
        """True si el usuario en sesión puede crear/editar/eliminar usuarios
        y reasignar/cambiar libremente el estado de los oficios (gestor)."""
        return self.usuario.get("rol") in ROLES_GESTORES

    def _es_superusuario(self):
        return self.usuario.get("rol") == ROL_SUPERUSUARIO

    def _lanzar_respaldo_diario(self):
        """Crea la copia del día en segundo plano.

        Va en un hilo aparte para que la ventana abra sin esperar, y usa la
        versión silenciosa: si el respaldo falla, queda en la bitácora pero
        nunca impide trabajar. Si otra persona ya creó la copia de hoy, no hace
        nada. El hilo solo toca archivos, nunca widgets de Tkinter.
        """
        if respaldo.existe_del_dia():
            return
        hilo = threading.Thread(
            target=respaldo.crear_respaldo_silencioso,
            args=(self.usuario["usuario"],), daemon=True)
        hilo.start()

    def _alcanza_a(self, usuario_objetivo, rol_objetivo):
        """¿El usuario en sesión puede gestionar a ese usuario? Se consulta
        antes de abrir el formulario para avisar cuanto antes."""
        return autenticacion.puede_gestionar_a(
            self.usuario["usuario"], self.usuario.get("rol"),
            usuario_objetivo, rol_objetivo)

    def _aviso_sin_alcance(self, usuario_objetivo, rol_objetivo, accion):
        """Muestra el motivo si no se puede gestionar. True = sin permisos."""
        if self._alcanza_a(usuario_objetivo, rol_objetivo):
            return False
        messagebox.showerror(
            "No permitido",
            f"Como administrador solo puede {accion} usuarios con rol "
            f"'{ROL_USUARIO}' (y su propia cuenta).\n\n"
            f"'{usuario_objetivo}' tiene rol '{rol_objetivo}': para eso se "
            "necesita un superusuario.")
        return True

    def _roles_asignables(self):
        """Roles que puede otorgar quien está en sesión (solo el superusuario
        puede crear otros superusuarios)."""
        return autenticacion.roles_asignables(self.usuario.get("rol"))

    # ---- Áreas con desplazamiento vertical ---------------------------------
    def _crear_area_desplazable(self, contenedor):
        """Convierte un contenedor en un área con scroll vertical.

        Devuelve (lienzo, marco_interno): el contenido se agrega al marco
        interno y el lienzo se encarga del desplazamiento. Se usa para que en
        resoluciones pequeñas no queden secciones fuera de la vista.
        """
        lienzo = tk.Canvas(contenedor, background=COLOR_BLANCO, highlightthickness=0)
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=lienzo.yview)
        lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        lienzo.pack(side="left", fill="both", expand=True)

        interno = ttk.Frame(lienzo)
        id_ventana = lienzo.create_window((0, 0), window=interno, anchor="nw")

        def al_cambiar_contenido(evento):
            lienzo.configure(scrollregion=lienzo.bbox("all"))

        def al_cambiar_lienzo(evento):
            # El contenido ocupa siempre todo el ancho disponible.
            lienzo.itemconfigure(id_ventana, width=evento.width)

        interno.bind("<Configure>", al_cambiar_contenido)
        lienzo.bind("<Configure>", al_cambiar_lienzo)
        self._lienzos_desplazables.add(lienzo)
        return lienzo, interno

    def _al_girar_rueda(self, evento):
        """Desplaza el área que está bajo el puntero.

        Si el cursor está sobre una tabla, se desplaza la tabla; si no, se
        busca un área desplazable entre los contenedores que la rodean.
        """
        if getattr(evento, "num", None) == 4:
            pasos = -1
        elif getattr(evento, "num", None) == 5:
            pasos = 1
        else:
            pasos = int(-evento.delta / 120) or (-1 if evento.delta > 0 else 1)

        widget = evento.widget
        if isinstance(widget, ttk.Treeview):
            widget.yview_scroll(pasos, "units")
            return
        while widget is not None:
            if widget in self._lienzos_desplazables:
                widget.yview_scroll(pasos, "units")
                return
            widget = getattr(widget, "master", None)

    def _tipos_accion(self):
        """Tipos de acción del catálogo, para los desplegables."""
        try:
            return tipos_accion.listar()
        except Exception:
            return []

    def _mostrar_proxima_referencia(self):
        """Adelanta la Referencia UDC que se asignará al oficio en curso.

        Depende de la institución elegida, porque cada una lleva su propia
        numeración."""
        institucion = self.combo_institucion.get()
        if not institucion:
            self.lbl_proxima_referencia.config(text="")
            return
        try:
            self.lbl_proxima_referencia.config(
                text=f"Referencia UDC que se asignará: "
                     f"{oficios.proxima_referencia(institucion)}")
        except ValueError:
            self.lbl_proxima_referencia.config(text="")

    @classmethod
    def _ancho_columna(cls, titulo, ancho_dato):
        """Ancho de una columna de tabla: el mayor entre lo que pide el dato y
        lo que ocupa su encabezado, medido con la fuente real.

        Los encabezados van **en una sola línea**, con el nombre completo del
        campo. Repartirlos en dos ahorraría ancho, pero no es fiable: hay
        versiones de Tk que dibujan solo la primera línea del encabezado de un
        `Treeview` —da igual que el corte se pida con un salto de línea o con
        `wraplength`— y el nombre del campo queda truncado («Fecha de»,
        «Cantidad de»), que es peor que una tabla ancha. Para el ancho está la
        barra de desplazamiento horizontal.
        """
        try:
            fuente = tkfont.Font(font=cls.FUENTE_CABECERA)
            return max(ancho_dato, fuente.measure(titulo) + 22)
        except tk.TclError:
            return ancho_dato

    def _campo(self, grupo, fila, etiqueta, widget, ayuda=None, estirar=True):
        """Coloca una etiqueta y su campo en una fila del grupo.

        Con `estirar` el campo ocupa todo el ancho disponible de la columna, de
        modo que el formulario aprovecha el espacio cuando la ventana crece.

        La etiqueta se registra en `_etiquetas_campo` para que
        `_ajustar_etiquetas_campo` le ponga un ancho de corte acorde al del
        recuadro: en una ventana estrecha se parte en dos líneas en vez de
        empujar al campo fuera de la vista.
        """
        # Espacio duro antes del asterisco: al partir la etiqueta en dos
        # líneas, el * de "obligatorio" no debe quedarse solo en la segunda.
        rotulo = ttk.Label(grupo, text=etiqueta.replace(" *", "\u00a0*"),
                           justify="left")
        rotulo.grid(row=fila, column=0, sticky="w", padx=(0, 8), pady=4)
        self._etiquetas_campo.append(rotulo)
        # El aviso de cambio de tamaño tiene que venir del propio recuadro: la
        # ventana deja de redimensionarse antes que sus hijos, así que atender
        # solo al <Configure> de la ventana dejaría anchos de corte antiguos.
        if grupo not in self._grupos_con_etiquetas:
            self._grupos_con_etiquetas.append(grupo)
            grupo.bind("<Configure>", self._ajustar_etiquetas_campo, add="+")
        widget.grid(row=fila, column=1, sticky="ew" if estirar else "w", pady=4)
        if ayuda:
            ttk.Label(grupo, text=ayuda, foreground="#6B7280",
                      font=("Helvetica", 8)).grid(row=fila + 1, column=1,
                                                  sticky="w", pady=(0, 2))
        return widget

    def _grupo(self, contenedor, titulo, fila, columna, columnspan=1):
        """Recuadro con título para agrupar campos afines."""
        grupo = ttk.LabelFrame(contenedor, text=f" {titulo} ", padding=(10, 6))
        grupo.grid(row=fila, column=columna, columnspan=columnspan,
                   sticky="nsew", padx=(0, 10) if columna == 0 else 0,
                   pady=(0, 10))
        grupo.columnconfigure(1, weight=1)      # el campo crece, la etiqueta no
        return grupo

    def _construir_registro(self):
        marco = self.pestana_registro

        # El botón se ancla ABAJO y fuera del área desplazable, así nunca queda
        # cortado ni fuera de la ventana por muy baja que sea la pantalla.
        pie = ttk.Frame(marco)
        pie.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Label(pie, text="* Campos obligatorios", foreground="#6B7280",
                  font=("Helvetica", 8)).pack(side="left")
        btn = ttk.Button(pie, text="Registrar", command=self._guardar_oficio)
        btn.pack(side="right")
        # Estilo especial para el botón principal
        estilo = ttk.Style()
        estilo.configure("Accent.TButton", background=COLOR_AZUL,
                         foreground=COLOR_BLANCO, font=("Helvetica", 10, "bold"))
        btn.config(style="Accent.TButton")

        # El resto del formulario va en un área con desplazamiento vertical.
        self.registro_lienzo, contenido = self._crear_area_desplazable(marco)

        ttk.Label(contenido, text="Registrar nuevo oficio",
                  font=("Helvetica", 13, "bold")).grid(
                      row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        # Las dos columnas se reparten el ancho por igual.
        contenido.columnconfigure(0, weight=1, uniform="formulario")
        contenido.columnconfigure(1, weight=1, uniform="formulario")

        # --- Columna izquierda: identificación del oficio --------------------
        datos = self._grupo(contenido, "Datos del oficio", 1, 0)
        # La institución no se muestra luego en el listado: solo determina la
        # nomenclatura de la Referencia UDC (REQ-UDC-SB-… o REQ-UDC-FGE-…).
        self.combo_institucion = ttk.Combobox(
            datos, state="readonly", values=list(INSTITUCIONES))
        self.combo_institucion.bind("<<ComboboxSelected>>",
                                    lambda e: self._mostrar_proxima_referencia())
        self._campo(datos, 0, "Institución del Estado *", self.combo_institucion)
        self.lbl_proxima_referencia = ttk.Label(
            datos, text="", foreground="#6B7280", font=("Helvetica", 8))
        self.lbl_proxima_referencia.grid(row=1, column=1, sticky="w", pady=(0, 2))

        self.entrada_codigo = self._campo(
            datos, 2, "Referencia oficio *", ttk.Entry(datos))
        self.combo_tipo_accion = ttk.Combobox(datos, state="readonly",
                                              values=self._tipos_accion())
        self._campo(datos, 3, "Tipo de acción *", self.combo_tipo_accion)
        self.entrada_causal = self._campo(
            datos, 4, "Causal oficio", ttk.Entry(datos))
        # Orden de fechas: oficio -> recepción.
        self.entrada_fecha_oficio = self._campo(
            datos, 5, "Fecha de oficio *", SelectorFecha(datos), estirar=False)
        self.entrada_fecha_recepcion = self._campo(
            datos, 6, "Fecha de recepción *", SelectorFecha(datos), estirar=False)

        # --- Columna derecha: asignación y seguimiento -----------------------
        gestion = self._grupo(contenido, "Asignación y seguimiento", 1, 1)
        if self._puede_gestionar_usuarios():
            # Gestores: pueden asignar el oficio a cualquier usuario.
            self.combo_empleado = ttk.Combobox(
                gestion, state="readonly",
                values=[self.SIN_RESPONSABLE] + self._valores_responsables())
            self.combo_empleado.current(0)  # por defecto: sin responsable
            self._campo(gestion, 0, "Usuario responsable", self.combo_empleado)
            estados_registro = ESTADOS
        else:
            # Usuario regular: los oficios que registra se le asignan a él.
            self.combo_empleado = None
            propio = ttk.Frame(gestion)
            ttk.Label(propio, text=self.usuario["nombre"],
                      font=("Helvetica", 10, "bold")).pack(side="left")
            ttk.Label(propio, text="(" + self.usuario["usuario"] + ")",
                      foreground="#6B7280", font=("Helvetica", 8)).pack(side="left")
            self._campo(gestion, 0, "Usuario responsable", propio, estirar=False)
            # Con responsable, "Por asignar" no aplica.
            estados_registro = ["En proceso", "Finalizado"]

        self.combo_estado = ttk.Combobox(gestion, state="readonly",
                                         values=estados_registro)
        self.combo_estado.current(0)
        self._campo(gestion, 1, "Estado *", self.combo_estado)
        self.entrada_fecha_asignacion = self._campo(
            gestion, 2, "Fecha de asignación",
            SelectorFecha(gestion, permitir_vacio=True), estirar=False)
        self.entrada_fecha_respuesta = self._campo(
            gestion, 3, "Fecha de respuesta",
            SelectorFecha(gestion, permitir_vacio=True), estirar=False)
        self.combo_prioridad = ttk.Combobox(gestion, state="readonly",
                                            values=PRIORIDADES)
        self.combo_prioridad.set(PRIORIDAD_POR_DEFECTO)
        self._campo(gestion, 4, "Prioridad", self.combo_prioridad)

        # --- Personas investigadas (ancho completo) --------------------------
        self._construir_implicados_registro(contenido, 2)

        # --- Documentos (ancho completo) -------------------------------------
        documentos = self._grupo(contenido, "Documentos", 3, 0, columnspan=2)
        # El documento del oficio es obligatorio: no se registra un oficio sin
        # su soporte digital.
        self.archivo_oficio = self._campo(
            documentos, 0, "Documento del oficio *",
            SelectorArchivo(documentos,
                            [("Documentos", "*.pdf *.docx"), ("PDF", "*.pdf"),
                             ("Word", "*.docx")],
                            "Seleccione el documento del oficio (PDF o Word)"),
            estirar=False)
        self.archivo_respuesta_registro = self._campo(
            documentos, 1, "Respuesta en PDF",
            SelectorArchivo(documentos, [("PDF", "*.pdf")],
                            "Seleccione la respuesta en PDF"),
            estirar=False)

        # --- Observación (ancho completo y elástica) -------------------------
        observacion = self._grupo(contenido, "Observación", 4, 0, columnspan=2)
        # Aquí no hay columna de etiqueta: la caja ocupa todo el recuadro. Se
        # anula el peso que _grupo() da a la columna 1 para que no se quede con
        # el espacio sobrante.
        observacion.columnconfigure(0, weight=1)
        observacion.columnconfigure(1, weight=0)
        self.texto_observacion = tk.Text(observacion, height=4, wrap="word",
                                         font=("Helvetica", 10),
                                         highlightthickness=1,
                                         highlightbackground="#CBD2DE",
                                         relief="flat")
        self.texto_observacion.grid(row=0, column=0, columnspan=2, sticky="ew")

    def _construir_implicados_registro(self, contenido, fila):
        """Personas investigadas que se anotan junto con el oficio.

        Se guardan en memoria y viajan con el alta, de modo que el oficio nace
        ya con su detalle y con la cantidad de investigados calculada.
        """
        self.implicados_registro = []
        grupo = self._grupo(contenido, "Personas investigadas", fila, 0,
                            columnspan=2)
        grupo.columnconfigure(0, weight=1)
        grupo.columnconfigure(1, weight=0)

        columnas = ("nombre", "tipo_id", "identificacion", "implicado", "lci")
        titulos = ("Nombre o razón social", "Tipo de identificación",
                   "Identificación", "Tipo de implicado", "LCI")
        anchos = (240, 120, 120, 130, 50)
        self.tabla_implicados_registro = ttk.Treeview(
            grupo, columns=columnas, show="headings", height=4)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tabla_implicados_registro.heading(columna, text=titulo)
            self.tabla_implicados_registro.column(
                columna, width=self._ancho_columna(titulo, ancho),
                minwidth=self._ancho_columna(titulo, ancho), anchor="w",
                stretch=columna == "nombre")
        self.tabla_implicados_registro.grid(row=0, column=0, columnspan=2,
                                            sticky="ew")

        formulario = ttk.Frame(grupo)
        formulario.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        def celda(fila_, columna, etiqueta, widget, columnspan=1, estirar=False):
            ttk.Label(formulario, text=etiqueta).grid(
                row=fila_, column=columna, sticky="w",
                padx=(0 if columna == 0 else 12, 6), pady=3)
            # Solo el nombre se estira: un desplegable de tres opciones tan
            # ancho como la ventana se ve raro.
            widget.grid(row=fila_, column=columna + 1, columnspan=columnspan,
                        sticky="ew" if estirar else "w", pady=3)

        self.implicado_nombre = ttk.Entry(formulario)
        celda(0, 0, "Nombre o razón social", self.implicado_nombre,
              columnspan=3, estirar=True)
        self.implicado_tipo_id = ttk.Combobox(
            formulario, state="readonly", width=16,
            values=[""] + TIPOS_IDENTIFICACION)
        celda(1, 0, "Tipo de identificación", self.implicado_tipo_id)
        self.implicado_identificacion = ttk.Entry(formulario, width=20)
        celda(1, 2, "Identificación", self.implicado_identificacion)
        self.implicado_tipo = ttk.Combobox(formulario, state="readonly",
                                           width=20, values=TIPOS_IMPLICADO)
        celda(2, 0, "Tipo de implicado", self.implicado_tipo)
        self.implicado_lci = ttk.Combobox(formulario, state="readonly", width=8,
                                          values=VALORES_LCI)
        self.implicado_lci.set("No")
        celda(2, 2, "LCI", self.implicado_lci)

        barra = ttk.Frame(grupo)
        barra.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(barra, text="Añadir persona",
                   command=self._anadir_implicado_registro).pack(side="left")
        ttk.Button(barra, text="Quitar",
                   command=self._quitar_implicado_registro).pack(side="left",
                                                                 padx=6)

    def _anadir_implicado_registro(self):
        """Suma una persona a la lista del oficio que se está registrando."""
        try:
            implicado = oficios.validar_implicado(
                self.implicado_nombre.get(), self.implicado_tipo_id.get(),
                self.implicado_identificacion.get(), self.implicado_tipo.get(),
                self.implicado_lci.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self.implicados_registro.append(implicado)
        self._refrescar_implicados_registro()
        self.implicado_nombre.delete(0, "end")
        self.implicado_identificacion.delete(0, "end")
        self.implicado_tipo_id.set("")
        self.implicado_tipo.set("")
        self.implicado_lci.set("No")
        self.implicado_nombre.focus_set()

    def _quitar_implicado_registro(self):
        seleccion = self.tabla_implicados_registro.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección",
                                   "Seleccione una persona de la lista.")
            return
        del self.implicados_registro[int(seleccion[0])]
        self._refrescar_implicados_registro()

    def _refrescar_implicados_registro(self):
        tabla = self.tabla_implicados_registro
        tabla.delete(*tabla.get_children())
        for indice, implicado in enumerate(self.implicados_registro):
            tabla.insert("", "end", iid=str(indice),
                         values=(implicado["nombre"],
                                 implicado["tipo_identificacion"],
                                 implicado["identificacion"],
                                 implicado["tipo_implicado"],
                                 implicado["lci"]))

    def _guardar_oficio(self):
        # Solo la referencia del oficio y las fechas de oficio/recepción son
        # obligatorias; el resto de campos son opcionales.
        if self.combo_empleado is not None:
            id_empleado, nombre_empleado = self._responsable_por_display(
                self.combo_empleado.get())
        else:
            # Usuario regular: el oficio se le asigna a sí mismo.
            id_empleado = self.usuario["usuario"]
            nombre_empleado = self.usuario["nombre"]
        try:
            referencia = oficios.registrar_oficio(
                self.entrada_codigo.get(), self.entrada_fecha_recepcion.get(),
                self.entrada_fecha_oficio.get(), id_empleado,
                nombre_empleado, self.combo_estado.get(),
                self.usuario["usuario"],
                fecha_respuesta=self.entrada_fecha_respuesta.get(),
                observacion=self.texto_observacion.get("1.0", "end"),
                causal_oficio=self.entrada_causal.get(),
                actor_rol=self.usuario.get("rol"),
                ruta_documento=self.archivo_oficio.get(),
                fecha_asignacion=self.entrada_fecha_asignacion.get(),
                ruta_respuesta=self.archivo_respuesta_registro.get(),
                institucion=self.combo_institucion.get(),
                tipo_accion=self.combo_tipo_accion.get(),
                prioridad=self.combo_prioridad.get(),
                implicados=self.implicados_registro,
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Registrado",
                            f"Oficio registrado.\nReferencia UDC: {referencia}")
        for entrada in (self.entrada_codigo, self.entrada_causal):
            entrada.delete(0, "end")
        self.entrada_fecha_asignacion.set("")
        self.entrada_fecha_respuesta.set("")
        self.archivo_oficio.set("")
        self.archivo_respuesta_registro.set("")
        self.texto_observacion.delete("1.0", "end")
        self.combo_institucion.set("")
        self.combo_tipo_accion.set("")
        self._mostrar_proxima_referencia()
        if self.combo_empleado is not None:
            self.combo_empleado.current(0)
        self.combo_estado.current(0)
        self.combo_prioridad.set(PRIORIDAD_POR_DEFECTO)
        self.implicados_registro = []
        self._refrescar_implicados_registro()
        self._refrescar_listado()

    # Primera opción de los desplegables de filtro: no filtra por ese campo.
    TODOS = "(Todos)"

    # Ancho máximo de la etiqueta de un campo antes de partirla en dos líneas.
    ANCHO_MAXIMO_ETIQUETA = 140

    FUENTE_CABECERA = ("Helvetica", 10, "bold")

    def _construir_filtros(self, marco):
        """Panel de búsqueda. Tres bloques que se acumulan entre sí:

        - por texto, sobre uno de los campos de `CAMPOS_BUSQUEDA`;
        - por institución, tipo de acción, causal, estado, prioridad y —solo
          para gestores— responsable, eligiendo de un desplegable;
        - por fecha única o rango de un mismo tipo.
        """
        panel = ttk.LabelFrame(marco, text=" Buscar oficios ", padding=(8, 4))
        panel.pack(fill="x", pady=(0, 4))

        # Fila 1: búsqueda por texto.
        fila1 = ttk.Frame(panel)
        fila1.pack(fill="x")
        ttk.Label(fila1, text="Buscar por").pack(side="left")
        self._etiquetas_busqueda = list(oficios.CAMPOS_BUSQUEDA.values())
        self.combo_campo_busqueda = ttk.Combobox(
            fila1, width=18, state="readonly", values=self._etiquetas_busqueda)
        self.combo_campo_busqueda.current(0)
        self.combo_campo_busqueda.pack(side="left", padx=6)
        self.entrada_busqueda = ttk.Entry(fila1, width=28)
        self.entrada_busqueda.pack(side="left", padx=(0, 16))
        self.entrada_busqueda.bind("<Return>", lambda e: self._refrescar_listado())

        # La institución va en esta fila, que tiene sitio de sobra, y no con
        # los otros desplegables: su nombre es largo y los estrecharía a todos.
        ttk.Label(fila1, text="Institución").pack(side="left")
        self.combo_filtro_institucion = ttk.Combobox(
            fila1, width=26, state="readonly",
            values=[self.TODOS] + list(INSTITUCIONES))
        self.combo_filtro_institucion.current(0)
        self.combo_filtro_institucion.pack(side="left", padx=(4, 0))
        self.combo_filtro_institucion.bind("<<ComboboxSelected>>",
                                           lambda e: self._refrescar_listado())


        # Fila 2: filtros de valor exacto, elegidos de un desplegable.
        #
        # Van en `grid` y no en `pack` a propósito: con el peso repartido entre
        # las columnas de los desplegables, al estrechar la ventana encogen
        # todos un poco en vez de quedar el último cortado.
        filtros = ttk.Frame(panel)
        filtros.pack(fill="x", pady=(4, 0))

        def desplegable(columna, etiqueta, valores=None):
            ttk.Label(filtros, text=etiqueta).grid(
                row=0, column=columna, sticky="w",
                padx=(0 if columna == 0 else 10, 4))
            combo = ttk.Combobox(filtros, width=14, state="readonly",
                                 values=valores or [])
            combo.grid(row=0, column=columna + 1, sticky="ew")
            filtros.columnconfigure(columna + 1, weight=1)
            combo.bind("<<ComboboxSelected>>",
                       lambda e: self._refrescar_listado())
            return combo

        self.combo_filtro_accion = desplegable(0, "Tipo de acción")
        self.combo_filtro_causal = desplegable(2, "Causal")
        self.combo_filtro_estado = desplegable(4, "Estado",
                                               [self.TODOS] + list(ESTADOS))
        self.combo_filtro_estado.current(0)
        self.combo_filtro_prioridad = desplegable(
            6, "Prioridad", [self.TODOS] + list(PRIORIDADES))
        self.combo_filtro_prioridad.current(0)
        if self._puede_gestionar_usuarios():
            # Un usuario regular solo ve sus propios oficios, así que filtrar
            # por responsable no le aportaría nada.
            self.combo_filtro_responsable = desplegable(8, "Responsable")
        else:
            self.combo_filtro_responsable = None
        self._refrescar_desplegables_filtro()

        # Fila 3: filtro por fecha (un solo tipo para ambos extremos).
        fila2 = ttk.Frame(panel)
        fila2.pack(fill="x", pady=(4, 0))
        ttk.Label(fila2, text="Fecha").pack(side="left")
        self._etiquetas_fecha = list(oficios.CAMPOS_FECHA.values())
        self.combo_campo_fecha = ttk.Combobox(
            fila2, width=18, state="readonly", values=self._etiquetas_fecha)
        self.combo_campo_fecha.current(0)
        self.combo_campo_fecha.pack(side="left", padx=6)
        ttk.Label(fila2, text="desde").pack(side="left")
        self.filtro_fecha_desde = SelectorFecha(fila2, permitir_vacio=True)
        self.filtro_fecha_desde.pack(side="left", padx=(4, 10))
        ttk.Label(fila2, text="hasta").pack(side="left")
        self.filtro_fecha_hasta = SelectorFecha(fila2, permitir_vacio=True)
        self.filtro_fecha_hasta.pack(side="left", padx=4)

        ttk.Button(fila2, text="Buscar",
                   command=self._refrescar_listado).pack(side="left", padx=(12, 4))
        ttk.Button(fila2, text="Limpiar filtros",
                   command=self._limpiar_filtros).pack(side="left")

        # Ayuda y contador de resultados comparten línea para no ocupar dos.
        fila3 = ttk.Frame(panel)
        fila3.pack(fill="x", pady=(3, 0))
        ttk.Label(fila3, text="Deje \"hasta\" vacío para buscar por fecha única",
                  foreground="#6B7280", font=("Helvetica", 8)).pack(side="left")
        if self._puede_gestionar_usuarios():
            # Los anulados están fuera de la operación diaria, pero un gestor
            # tiene que poder encontrarlos para revisarlos o reactivarlos.
            self.var_ver_anulados = tk.BooleanVar(value=False)
            ttk.Checkbutton(fila3, text="Ver anulados",
                            variable=self.var_ver_anulados,
                            command=self._refrescar_listado).pack(side="left",
                                                                  padx=(16, 0))
        else:
            self.var_ver_anulados = None
        self.lbl_resultados = ttk.Label(fila3, text="", foreground="#6B7280",
                                        font=("Helvetica", 8))
        self.lbl_resultados.pack(side="right")
        return panel

    def _refrescar_desplegables_filtro(self, registros=None):
        """Repuebla los desplegables de filtro conservando lo elegido.

        El tipo de acción sale del catálogo y el causal de lo que realmente
        haya registrado, que es texto libre. El responsable incluye a todos los
        usuarios: aquí no rige la restricción de asignación, porque un
        administrador sí puede *ver* los oficios de un superusuario.
        """
        def repoblar(combo, valores, todos):
            if combo is None:
                return
            elegido = combo.get()
            combo.config(values=[todos] + valores)
            combo.set(elegido if elegido in valores else todos)

        repoblar(self.combo_filtro_accion, self._tipos_accion(), self.TODOS)
        if registros is None:
            try:
                registros = oficios.listar_oficios_visibles(
                    self.usuario["usuario"], self.usuario.get("rol"))
            except Exception:
                registros = []
        repoblar(self.combo_filtro_causal,
                 oficios.causales_registradas(registros), "(Todas)")
        if self.combo_filtro_responsable is not None:
            repoblar(self.combo_filtro_responsable,
                     [self.SIN_RESPONSABLE] +
                     [self._display_responsable(u["usuario"], u["nombre"])
                      for u in self._usuarios_sistema()],
                     self.TODOS)

    def _valor_filtro(self, combo):
        """Valor elegido en un desplegable de filtro, o '' si es "(Todos)"."""
        if combo is None:
            return ""
        valor = combo.get()
        return "" if valor in (self.TODOS, "(Todas)", "") else valor

    def _limpiar_filtros(self):
        self.entrada_busqueda.delete(0, "end")
        self.combo_campo_busqueda.current(0)
        self.combo_campo_fecha.current(0)
        self.filtro_fecha_desde.set("")
        self.filtro_fecha_hasta.set("")
        self.combo_filtro_institucion.set(self.TODOS)
        self.combo_filtro_prioridad.set(self.TODOS)
        self.combo_filtro_accion.set(self.TODOS)
        self.combo_filtro_causal.set("(Todas)")
        self.combo_filtro_estado.set(self.TODOS)
        if self.combo_filtro_responsable is not None:
            self.combo_filtro_responsable.set(self.TODOS)
        self._refrescar_listado()

    def _clave_por_etiqueta(self, mapa, etiqueta):
        """Devuelve la clave interna a partir de la etiqueta mostrada."""
        for clave, valor in mapa.items():
            if valor == etiqueta:
                return clave
        return ""

    def _construir_listado(self):
        # Toda la pestaña va dentro de un lienzo con desplazamiento vertical:
        # así, en pantallas pequeñas, ninguna de las tres secciones (buscar,
        # listado y modificar) queda fuera de la vista.
        self.oficios_lienzo, marco = self._crear_area_desplazable(self.pestana_listado)
        es_gestor = self._puede_gestionar_usuarios()

        # --- 1) Filtros de búsqueda -----------------------------------------
        self._marco_filtros = self._construir_filtros(marco)

        # --- 2) Tabla de oficios (orden: oficio -> recepción -> respuesta) --
        columnas = ("referencia", "institucion", "codigo", "accion", "causal",
                    "oficio", "recepcion", "asignacion", "respuesta",
                    "investigados", "empleado", "estado", "prioridad", "pdf",
                    "observacion")
        # Encabezados con el nombre completo del campo, sin abreviar y en una
        # sola línea (ver `_ancho_columna`): la tabla queda más ancha, pero se
        # lee sin ambigüedad. Para el ancho está la barra horizontal.
        titulos = ("Referencia UDC", "Institución del Estado",
                   "Referencia oficio", "Tipo de acción",
                   "Causal oficio", "Fecha de oficio", "Fecha de recepción",
                   "Fecha de asignación", "Fecha de respuesta",
                   "Cantidad de investigados",
                   "Responsable", "Estado", "Prioridad", "PDF", "Observación")
        # Ancho que pide el DATO (p. ej. "REQ-UDC-FGE-2026-0001" o
        # "Superintendencia de Bancos"); si el título es más largo, manda él.
        anchos = (190, 215, 150, 120, 150, 90, 95, 90, 90, 60, 110, 90, 60, 40,
                  200)
        contenedor = ttk.Frame(marco)
        # Altura fija (no expand): dentro de un área desplazable la tabla debe
        # tener alto propio para que el panel inferior siga siendo alcanzable.
        contenedor.pack(fill="x", side="top")
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=10)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tabla.heading(columna, text=titulo)
            ancho = self._ancho_columna(titulo, ancho)
            self.tabla.column(columna, width=ancho, minwidth=ancho, anchor="w",
                              stretch=False)
        self.tabla.column("observacion", stretch=True)
        barra_v = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        barra_h = ttk.Scrollbar(contenedor, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
        # Los oficios anulados se ven apagados, para distinguirlos de un vistazo.
        self.tabla.tag_configure("anulado", foreground="#94A3B8")
        barra_v.pack(side="right", fill="y")
        barra_h.pack(side="bottom", fill="x")
        self.tabla.pack(fill="both", expand=True, side="left")

        # --- 3) Panel de edición del oficio seleccionado ---------------------
        # Disposición en una sola fila de campos + observación, para que la
        # pestaña no quede saturada y el calendario tenga espacio.
        panel = ttk.LabelFrame(marco, text=" Modificar oficio seleccionado ",
                               padding=(8, 4))
        panel.pack(fill="x", pady=(4, 0))
        self._panel_edicion = panel

        fila = ttk.Frame(panel)
        fila.pack(fill="x")

        if es_gestor:
            # La fecha de asignación acompaña al responsable, así que solo la
            # manejan quienes pueden reasignar.
            ttk.Label(fila, text="Fecha de asignación").pack(side="left")
            self.edicion_fecha_asignacion = SelectorFecha(fila, permitir_vacio=True)
            self.edicion_fecha_asignacion.pack(side="left", padx=(6, 16))
        else:
            self.edicion_fecha_asignacion = None

        ttk.Label(fila, text="Fecha de respuesta").pack(side="left")
        self.edicion_fecha_respuesta = SelectorFecha(fila, permitir_vacio=True)
        self.edicion_fecha_respuesta.pack(side="left", padx=(6, 16))

        # La cantidad de investigados no se edita aquí: la cuenta la lista de
        # implicados (doble clic sobre el oficio).
        ttk.Label(fila, text="Cantidad de investigados").pack(side="left")
        self.edicion_cantidad = ttk.Label(fila, text="—", width=4,
                                          anchor="center")
        self.edicion_cantidad.pack(side="left", padx=(6, 16))

        ttk.Label(fila, text="Tipo de acción").pack(side="left")
        self.combo_tipo_accion_edicion = ttk.Combobox(
            fila, width=20, state="readonly", values=self._tipos_accion())
        self.combo_tipo_accion_edicion.pack(side="left", padx=(6, 16))

        # La prioridad es parte del seguimiento: se corrige aquí, no en el
        # mantenimiento, que es para los datos que identifican al oficio.
        ttk.Label(fila, text="Prioridad").pack(side="left")
        self.combo_prioridad_edicion = ttk.Combobox(
            fila, width=10, state="readonly", values=PRIORIDADES)
        self.combo_prioridad_edicion.pack(side="left", padx=6)

        # Segunda fila: responsable y estado (así ninguna queda apretada).
        fila2 = ttk.Frame(panel)
        fila2.pack(fill="x", pady=(6, 0))

        if es_gestor:
            # Solo administrador / superusuario pueden reasignar responsable.
            ttk.Label(fila2, text="Responsable").pack(side="left")
            self.combo_responsable_edicion = ttk.Combobox(
                fila2, width=24, state="readonly",
                values=[self.SIN_RESPONSABLE] + self._valores_responsables())
            self.combo_responsable_edicion.current(0)
            self.combo_responsable_edicion.pack(side="left", padx=(6, 16))
            estados_disponibles = ESTADOS
        else:
            # El usuario solo alterna entre En proceso y Finalizado.
            estados_disponibles = ["En proceso", "Finalizado"]

        ttk.Label(fila2, text="Estado").pack(side="left")
        self.combo_nuevo_estado = ttk.Combobox(fila2, width=13, state="readonly",
                                               values=estados_disponibles)
        self.combo_nuevo_estado.current(0)
        self.combo_nuevo_estado.pack(side="left", padx=6)

        fila_obs = ttk.Frame(panel)
        fila_obs.pack(fill="x", pady=(6, 0))
        ttk.Label(fila_obs, text="Observación").pack(side="left", anchor="n")
        self.edicion_observacion = tk.Text(fila_obs, height=2, wrap="word",
                                           font=("Helvetica", 10), relief="flat",
                                           highlightthickness=1, highlightbackground="#CBD2DE")
        self.edicion_observacion.pack(side="left", fill="x", expand=True, padx=6)

        barra = ttk.Frame(panel)
        barra.pack(fill="x", pady=(6, 0))
        btn_guardar = ttk.Button(barra, text="Guardar cambios", command=self._aplicar_cambios)
        btn_guardar.pack(side="left")
        btn_guardar.config(style="Accent.TButton")
        ttk.Button(barra, text="Ver oficio",
                   command=self._ver_documento).pack(side="left", padx=6)
        ttk.Button(barra, text="Cambiar oficio",
                   command=self._cambiar_documento).pack(side="left")
        ttk.Button(barra, text="Adjuntar respuesta (PDF)",
                   command=self._adjuntar_respuesta).pack(side="left", padx=6)
        ttk.Button(barra, text="Ver respuesta (PDF)",
                   command=self._ver_respuesta).pack(side="left")
        ttk.Button(barra, text="Eliminar PDF",
                   command=self._eliminar_respuesta).pack(side="left", padx=6)
        if es_gestor:
            # Mantenimiento: corregir lo mal tecleado y retirar un oficio.
            ttk.Button(barra, text="Mantenimiento",
                       command=self._abrir_mantenimiento).pack(side="left")
        ttk.Button(barra, text="Exportar",
                   command=self._exportar_oficios).pack(side="right")

        # Al seleccionar un oficio, precargar sus valores actuales.
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_oficio)
        # Doble clic: implicados (personas investigadas) del oficio.
        self.tabla.bind("<Double-1>", self._abrir_implicados)
        # La tabla crece con la ventana: al maximizar se ven muchas más filas.
        self.oficios_lienzo.bind("<Configure>", self._ajustar_alto_tabla, add="+")
        self._refrescar_listado()

    def _ajustar_alto_tabla(self, evento=None):
        """Ajusta cuántas filas muestra la tabla de oficios al alto disponible.

        Dentro de un área desplazable la tabla no puede "expandirse" sola: el
        lienzo mide el contenido, no al revés. Así que se calcula cuántas filas
        caben entre el panel de filtros y el de edición, y se le fija ese alto.
        """
        alto_visible = self.oficios_lienzo.winfo_height()
        if alto_visible <= 1:
            return
        try:
            alto_fila = int(ttk.Style().lookup("Treeview", "rowheight") or 20)
        except (tk.TclError, ValueError):
            alto_fila = 20
        alto_fila = max(alto_fila, 16)
        # Lo que ocupan los paneles de arriba y de abajo, más los márgenes y la
        # barra horizontal de la tabla.
        ocupado = (self._marco_filtros.winfo_reqheight()
                   + self._panel_edicion.winfo_reqheight() + 70)
        filas = max(6, (alto_visible - ocupado) // alto_fila)
        if self.tabla.cget("height") != filas:
            self.tabla.config(height=filas)

    def _refrescar_listado(self):
        if not hasattr(self, "tabla"):
            return
        seleccion_previa = self.tabla.selection()
        self.tabla.delete(*self.tabla.get_children())
        try:
            # Un usuario regular solo ve sus oficios (registrados o asignados).
            ver_anulados = bool(getattr(self, "var_ver_anulados", None)
                                and self.var_ver_anulados.get())
            registros = oficios.listar_oficios_visibles(
                self.usuario["usuario"], self.usuario.get("rol"),
                incluir_anulados=ver_anulados)
            total_visibles = len(registros)
            # Filtros de búsqueda (si el panel ya está construido).
            if hasattr(self, "entrada_busqueda"):
                # Los desplegables se repueblan con lo que hay a la vista: el
                # causal es texto libre y cambia según lo registrado.
                self._refrescar_desplegables_filtro(registros)
                responsable = self._valor_filtro(self.combo_filtro_responsable)
                sin_responsable = responsable == self.SIN_RESPONSABLE
                id_responsable = "" if sin_responsable else \
                    self._responsable_por_display(responsable)[0]
                registros = oficios.filtrar_oficios(
                    registros,
                    self._clave_por_etiqueta(oficios.CAMPOS_BUSQUEDA,
                                             self.combo_campo_busqueda.get()),
                    self.entrada_busqueda.get(),
                    self._clave_por_etiqueta(oficios.CAMPOS_FECHA,
                                             self.combo_campo_fecha.get()),
                    self.filtro_fecha_desde.get(),
                    self.filtro_fecha_hasta.get(),
                    institucion=self._valor_filtro(
                        self.combo_filtro_institucion),
                    prioridad=self._valor_filtro(self.combo_filtro_prioridad),
                    tipo_accion=self._valor_filtro(self.combo_filtro_accion),
                    causal=self._valor_filtro(self.combo_filtro_causal),
                    estado=self._valor_filtro(self.combo_filtro_estado),
                    id_empleado=id_responsable,
                    solo_sin_responsable=sin_responsable)
            for registro in registros:
                observacion = " ".join(registro.get("observacion", "").split())
                if len(observacion) > 60:
                    observacion = observacion[:57] + "..."
                anulado = oficios.esta_anulado(registro)
                self.tabla.insert("", "end", iid=registro["referencia"],
                                  tags=("anulado",) if anulado else (), values=(
                    registro["referencia"],
                    registro.get("institucion", ""),
                    registro["codigo_oficio"],
                    registro.get("tipo_accion", ""),
                    registro.get("causal_oficio", ""),
                    registro["fecha_oficio"], registro["fecha_recepcion"],
                    registro.get("fecha_asignacion", ""),
                    registro.get("fecha_respuesta", ""),
                    registro.get("cantidad_investigados", ""),
                    # El usuario en vez del nombre completo: la tabla queda
                    # más compacta y sigue identificando sin ambigüedad.
                    registro.get("id_empleado", ""),
                    "ANULADO" if anulado else registro["estado"],
                    registro.get("prioridad", ""),
                    "Sí" if registro.get("archivo_respuesta") else "",
                    observacion))
        except ValueError as error:
            messagebox.showerror("Filtro no válido", str(error))
            return
        except Exception as e:
            messagebox.showerror("Error al cargar oficios", str(e))
            return
        if hasattr(self, "lbl_resultados"):
            self.lbl_resultados.config(
                text=f"Mostrando {len(registros)} de {total_visibles} oficios."
                if len(registros) != total_visibles else "")
        # Conservar la selección tras refrescar, si el oficio sigue existiendo.
        for referencia in seleccion_previa:
            if self.tabla.exists(referencia):
                self.tabla.selection_set(referencia)
        # La cantidad de investigados del panel se refresca siempre: no la
        # teclea nadie —la cuentan los implicados—, así que actualizarla no
        # puede pisar una edición a medias, y si acaban de añadir o quitar a
        # una persona tiene que verse al momento.
        if hasattr(self, "edicion_cantidad") and seleccion_previa:
            registro = self._oficio_por_referencia(seleccion_previa[0])
            if registro is not None:
                self.edicion_cantidad.config(
                    text=registro.get("cantidad_investigados", "") or "—")

    def _al_seleccionar_oficio(self, evento=None):
        """Precarga el panel de edición con los datos del oficio seleccionado.

        Solo recarga cuando cambia el oficio seleccionado. Es importante: al
        refrescar el listado se borran y reinsertan las filas, y Tk entrega el
        <<TreeviewSelect>> resultante MÁS TARDE, ya fuera de esta llamada. Si se
        recargara en cada aviso, ese evento diferido pisaría lo que la persona
        acabara de elegir en el panel (estado, fecha u observación) justo antes
        de pulsar "Guardar cambios".
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        if seleccion[0] == getattr(self, "_referencia_en_edicion", None):
            return          # mismo oficio: no pisar lo que se esté editando
        registro = self._oficio_por_referencia(seleccion[0])
        if registro is None:
            return
        self._referencia_en_edicion = seleccion[0]
        self.edicion_fecha_respuesta.set(registro.get("fecha_respuesta", ""))
        self.edicion_cantidad.config(
            text=registro.get("cantidad_investigados", "") or "—")
        self.combo_tipo_accion_edicion.config(values=self._tipos_accion())
        self.combo_tipo_accion_edicion.set(registro.get("tipo_accion", ""))
        self.combo_prioridad_edicion.set(registro.get("prioridad", ""))
        self.edicion_observacion.delete("1.0", "end")
        self.edicion_observacion.insert("1.0", registro.get("observacion", ""))

        if self._puede_gestionar_usuarios():
            self.edicion_fecha_asignacion.set(registro.get("fecha_asignacion", ""))
            display = self._display_responsable(
                registro.get("id_empleado", ""), registro.get("empleado", ""))
            valores = [self.SIN_RESPONSABLE] + self._valores_responsables()
            if display and display not in valores:
                # El oficio está asignado a alguien fuera del alcance de quien
                # mira (un administrador viendo un oficio de un superusuario):
                # se muestra para no perderlo al guardar, aunque no pueda
                # asignárselo a otro oficio.
                valores.append(display)
            self.combo_responsable_edicion.config(values=valores)
            self.combo_responsable_edicion.set(display or self.SIN_RESPONSABLE)
            if registro.get("estado") in ESTADOS:
                self.combo_nuevo_estado.set(registro["estado"])
        else:
            estado = registro.get("estado")
            if estado in ("En proceso", "Finalizado"):
                self.combo_nuevo_estado.set(estado)

    def _aplicar_cambios(self):
        """Guarda los cambios del panel según el rol: el gestor puede cambiar
        responsable, estado, fecha de respuesta y observación; el usuario
        regular solo fecha de respuesta, estado y observación de sus oficios."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        fecha_respuesta = self.edicion_fecha_respuesta.get()
        observacion = self.edicion_observacion.get("1.0", "end")
        try:
            if self._puede_gestionar_usuarios():
                id_empleado, nombre_empleado = self._responsable_por_display(
                    self.combo_responsable_edicion.get())
                estado_final = oficios.actualizar_oficio(
                    seleccion[0], self.combo_nuevo_estado.get(),
                    id_empleado, nombre_empleado, self.usuario["usuario"],
                    self.usuario.get("rol"), fecha_respuesta, observacion,
                    fecha_asignacion=self.edicion_fecha_asignacion.get(),
                    tipo_accion=self.combo_tipo_accion_edicion.get(),
                    prioridad=self.combo_prioridad_edicion.get())
            else:
                estado_final = oficios.actualizar_estado_asignado(
                    seleccion[0], self.usuario["usuario"],
                    self.combo_nuevo_estado.get(), fecha_respuesta, observacion,
                    tipo_accion=self.combo_tipo_accion_edicion.get(),
                    prioridad=self.combo_prioridad_edicion.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        # Si las reglas ajustaron el estado (p. ej. al asignar responsable),
        # reflejarlo en el desplegable.
        if estado_final in self.combo_nuevo_estado.cget("values"):
            self.combo_nuevo_estado.set(estado_final)
        self._refrescar_listado()

    # ---- Documento del oficio ------------------------------------------------
    def _ver_documento(self):
        """Abre el documento del oficio (PDF dentro de la aplicación; el Word,
        con el programa del sistema)."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        ruta = oficios.ruta_documento(seleccion[0])
        if ruta is None:
            messagebox.showinfo(
                "Sin documento",
                "Este oficio no tiene el documento adjunto.\n\n"
                "Los oficios registrados antes de esta versión pueden no "
                "tenerlo: use \"Cambiar oficio\" para adjuntarlo.")
            return
        if ruta.suffix.lower() != ".pdf":
            # Word: no hay visor integrado, lo abre el programa asociado.
            if not visor_pdf.abrir_con_sistema(ruta):
                messagebox.showerror("Error", "No se pudo abrir el documento.")
            return
        self._mostrar_pdf(ruta, f"Oficio {seleccion[0]}")

    def _cambiar_documento(self):
        """Sustituye el documento del oficio por si se cargó el equivocado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        ruta = filedialog.askopenfilename(
            title="Seleccione el documento del oficio (PDF o Word)",
            filetypes=[("Documentos", "*.pdf *.docx"), ("PDF", "*.pdf"),
                       ("Word", "*.docx")])
        if not ruta:
            return
        try:
            oficios.reemplazar_documento(seleccion[0], ruta,
                                         self.usuario["usuario"],
                                         self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "Documento del oficio actualizado.")
        self._refrescar_listado()

    # ---- Respuesta en PDF ---------------------------------------------------
    def _adjuntar_respuesta(self):
        """Carga un PDF con la respuesta del oficio seleccionado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        ruta = filedialog.askopenfilename(
            title="Seleccione la respuesta en PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")])
        if not ruta:
            return
        try:
            oficios.adjuntar_respuesta(seleccion[0], ruta, self.usuario["usuario"],
                                       self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "Respuesta en PDF adjuntada correctamente.")
        self._refrescar_listado()

    def _eliminar_respuesta(self):
        """Elimina el PDF adjunto (por si se cargó el archivo equivocado)."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        if not messagebox.askyesno(
                "Confirmar",
                "¿Eliminar la respuesta en PDF adjunta a este oficio?\n"
                "Podrá volver a adjuntar un archivo."):
            return
        try:
            oficios.eliminar_respuesta(seleccion[0], self.usuario["usuario"],
                                       self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "Respuesta en PDF eliminada.")
        self._refrescar_listado()

    def _ver_respuesta(self):
        """Muestra el PDF de respuesta dentro de la aplicación."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        ruta = oficios.ruta_respuesta(seleccion[0])
        if ruta is None:
            messagebox.showinfo("Sin respuesta",
                                "Este oficio no tiene una respuesta en PDF adjunta.")
            return
        self._mostrar_pdf(ruta, f"Respuesta · {seleccion[0]}")

    def _mostrar_pdf(self, ruta, titulo):
        """Abre un PDF en el visor integrado y, si no está disponible, ofrece
        el lector del sistema."""
        if visor_pdf.abrir_visor(self, ruta, titulo):
            return
        # Sin PyMuPDF instalado: ofrecer el lector del sistema.
        if messagebox.askyesno(
                "Visor no disponible",
                "Para ver el PDF dentro de la aplicación instale PyMuPDF:\n\n"
                "    pip install pymupdf\n\n"
                "¿Desea abrirlo con el lector de PDF del sistema?"):
            if not visor_pdf.abrir_con_sistema(ruta):
                messagebox.showerror("Error", "No se pudo abrir el PDF.")

    # ---- Mantenimiento -------------------------------------------------------
    def _abrir_mantenimiento(self):
        """Corrige los datos de identificación de un oficio, o lo retira."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        registro = self._oficio_por_referencia(seleccion[0])
        if registro is None:
            messagebox.showerror("Error", "No se encontró el oficio seleccionado.")
            return
        dialogo = DialogoMantenimiento(self, self.usuario, registro)
        self.wait_window(dialogo)
        self._referencia_en_edicion = None      # forzar la recarga del panel
        self._refrescar_listado()

    # ---- Exportación ---------------------------------------------------------
    def _exportar_oficios(self):
        """Exporta a CSV los oficios de una fecha o de un rango de fechas."""
        dialogo = DialogoExportar(self, self.usuario)
        self.wait_window(dialogo)

    def _construir_usuarios(self):
        marco = self.pestana_usuarios
        # Usuario que se está editando (None = se está creando uno nuevo).
        self._usuario_en_edicion = None

        # El formulario ocupa su ancho natural a la izquierda y la lista se
        # queda con todo el espacio restante, a lo ancho y a lo alto.
        marco.columnconfigure(0, weight=0)
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(0, weight=1)

        # --- Formulario de la cuenta ----------------------------------------
        # El título del recuadro es el que cambia entre crear y editar, así que
        # `lbl_form_usuario` apunta al propio recuadro.
        formulario = ttk.LabelFrame(marco, text="Crear usuario del sistema",
                                    padding=(12, 8))
        # "new" (sin sur): el recuadro se ajusta a su contenido en vez de
        # estirarse a lo alto dejando un hueco vacío debajo del botón.
        formulario.grid(row=0, column=0, sticky="new", padx=(0, 12))
        formulario.columnconfigure(1, weight=1)
        self.lbl_form_usuario = formulario

        self.entrada_usuario = self._campo(formulario, 0, "Usuario",
                                           ttk.Entry(formulario, width=28))
        self.entrada_nombre = self._campo(formulario, 1, "Nombre",
                                          ttk.Entry(formulario, width=28))
        self.combo_rol = ttk.Combobox(formulario, width=25, state="readonly",
                                      values=self._roles_asignables())
        self.combo_rol.current(0)
        self._campo(formulario, 2, "Rol", self.combo_rol)
        self.entrada_clave = self._campo(
            formulario, 3, "Contraseña", ttk.Entry(formulario, width=28, show="•"))
        self.entrada_clave2 = self._campo(
            formulario, 4, "Confirmar contraseña",
            ttk.Entry(formulario, width=28, show="•"))
        self.lbl_ayuda_clave = ttk.Label(formulario, text="", foreground="#6B7280",
                                         font=("Helvetica", 8), wraplength=260)
        self.lbl_ayuda_clave.grid(row=5, column=0, columnspan=2, sticky="w")

        # El botón principal cambia de texto entre crear y editar. "Nuevo" va a
        # su lado porque es la única salida del modo edición: sin él habría que
        # guardar los cambios para poder volver a crear una cuenta.
        barra_formulario = ttk.Frame(formulario)
        barra_formulario.grid(row=6, column=0, columnspan=2, sticky="ew",
                              pady=(12, 0))
        barra_formulario.columnconfigure(0, weight=1)
        self.btn_guardar_usuario = ttk.Button(barra_formulario,
                                              text="Crear usuario",
                                              command=self._guardar_usuario)
        self.btn_guardar_usuario.grid(row=0, column=0, sticky="ew")
        self.btn_guardar_usuario.config(style="Accent.TButton")
        ttk.Button(barra_formulario, text="Nuevo",
                   command=self._nuevo_usuario).grid(row=0, column=1,
                                                     sticky="e", padx=(6, 0))

        # --- Lista de cuentas (se queda con el espacio sobrante) -------------
        lista = ttk.LabelFrame(marco, text=" Usuarios existentes ", padding=(10, 6))
        lista.grid(row=0, column=1, sticky="nsew")
        lista.columnconfigure(0, weight=1)
        lista.rowconfigure(0, weight=1)

        # La lista va con barra de desplazamiento: el número de cuentas crece
        # con el tiempo y no debe quedar ninguna fuera de la vista.
        self.tabla_usuarios = ttk.Treeview(
            lista, columns=("usuario", "nombre", "rol"), show="headings", height=8)
        self.tabla_usuarios.heading("usuario", text="Usuario")
        self.tabla_usuarios.heading("nombre", text="Nombre")
        self.tabla_usuarios.heading("rol", text="Rol")
        # Las tres columnas crecen a la vez, así el ancho sobrante se reparte
        # en lugar de acumularse todo en una y dejar un hueco enorme.
        #
        # `stretch` solo REPARTE el espacio que sobra: nunca encoge una columna
        # por debajo de su `width`. Por eso los anchos de partida son modestos,
        # de forma que las tres caben con la ventana en su tamaño mínimo y se
        # ensanchan solas cuando hay sitio.
        self.tabla_usuarios.column("usuario", width=100, minwidth=90, stretch=True)
        self.tabla_usuarios.column("nombre", width=150, minwidth=140, stretch=True)
        self.tabla_usuarios.column("rol", width=105, minwidth=100, stretch=True)
        barra_usuarios = ttk.Scrollbar(lista, orient="vertical",
                                       command=self.tabla_usuarios.yview)
        # Barra horizontal por si el equipo usa una fuente mayor y las columnas
        # no llegan a caber: así "Rol" nunca queda inalcanzable.
        barra_usuarios_h = ttk.Scrollbar(lista, orient="horizontal",
                                         command=self.tabla_usuarios.xview)
        self.tabla_usuarios.configure(yscrollcommand=barra_usuarios.set,
                                      xscrollcommand=barra_usuarios_h.set)
        self.tabla_usuarios.grid(row=0, column=0, sticky="nsew")
        barra_usuarios.grid(row=0, column=1, sticky="ns")
        barra_usuarios_h.grid(row=1, column=0, sticky="ew")
        self.tabla_usuarios.bind("<<TreeviewSelect>>", self._al_seleccionar_usuario)

        # Los botones actúan sobre la fila seleccionada, que queda justo encima,
        # así que se etiquetan en corto para que las tres quepan aunque la
        # ventana esté en su tamaño mínimo.
        barra_tabla = ttk.Frame(lista)
        barra_tabla.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(barra_tabla, text="Editar",
                   command=self._editar_usuario_seleccionado).pack(side="left")
        ttk.Button(barra_tabla, text="Restablecer contraseña",
                   command=self._restablecer_clave_seleccionado).pack(side="left", padx=6)
        ttk.Button(barra_tabla, text="Eliminar",
                   command=self._eliminar_usuario_seleccionado).pack(side="left")

        self._nuevo_usuario()
        self._refrescar_usuarios()

    def _nuevo_usuario(self):
        """Restablece el formulario para crear un usuario nuevo."""
        self._usuario_en_edicion = None
        self.lbl_form_usuario.config(text="Crear usuario del sistema")
        self.btn_guardar_usuario.config(text="Crear usuario")
        self.lbl_ayuda_clave.config(text="")
        # Primero se rehabilita: al editar, el campo Usuario queda deshabilitado
        # y borrarlo entonces no surte efecto (Tk ignora la escritura), con lo
        # que el formulario arrastraría el nombre de la cuenta anterior.
        self.entrada_usuario.config(state="normal")
        for entrada in (self.entrada_usuario, self.entrada_nombre,
                        self.entrada_clave, self.entrada_clave2):
            entrada.delete(0, "end")
        self.combo_rol.config(state="readonly", values=self._roles_asignables())
        self.combo_rol.set(ROL_USUARIO)
        if self.tabla_usuarios.selection():
            self.tabla_usuarios.selection_remove(self.tabla_usuarios.selection())

    def _al_seleccionar_usuario(self, evento=None):
        pass  # la carga se hace explícitamente con "Editar seleccionado"

    def _editar_usuario_seleccionado(self):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un usuario de la lista.")
            return
        usuario, nombre, rol = self.tabla_usuarios.item(seleccion[0], "values")
        if self._aviso_sin_alcance(usuario, rol, "editar"):
            return
        self._usuario_en_edicion = usuario
        self.lbl_form_usuario.config(text=f"Editar usuario: {usuario}")
        self.btn_guardar_usuario.config(text="Guardar cambios")
        self.lbl_ayuda_clave.config(text="(Deje la contraseña vacía para no cambiarla)")

        self.entrada_usuario.config(state="normal")
        self.entrada_usuario.delete(0, "end")
        self.entrada_usuario.insert(0, usuario)
        self.entrada_usuario.config(state="disabled")  # el usuario es la clave, no se cambia
        self.entrada_nombre.delete(0, "end")
        self.entrada_nombre.insert(0, nombre)
        self.entrada_clave.delete(0, "end")
        self.entrada_clave2.delete(0, "end")

        posibles = self._roles_asignables()
        if rol not in posibles:
            # Por ejemplo, un administrador editando a un superusuario: se
            # muestra el rol actual pero no puede cambiarlo.
            self.combo_rol.config(state="readonly", values=[rol])
            self.combo_rol.set(rol)
            self.combo_rol.config(state="disabled")
        else:
            self.combo_rol.config(state="readonly", values=posibles)
            self.combo_rol.set(rol)

    def _guardar_usuario(self):
        if self.entrada_clave.get() != self.entrada_clave2.get():
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        actor = self.usuario["usuario"]
        actor_rol = self.usuario.get("rol")
        try:
            if self._usuario_en_edicion is None:
                # Crear usuario nuevo.
                rol = autenticacion.crear_usuario(
                    self.entrada_usuario.get(), self.entrada_nombre.get(),
                    self.entrada_clave.get(), self.combo_rol.get(), actor,
                    actor_rol)
                mensaje = f"Usuario creado correctamente (rol: {rol})."
            else:
                # Editar usuario existente. La contraseña vacía no se cambia.
                autenticacion.editar_usuario(
                    self._usuario_en_edicion, actor, actor_rol,
                    nombre=self.entrada_nombre.get(),
                    clave=self.entrada_clave.get() or None,
                    rol=self.combo_rol.get())
                mensaje = "Cambios guardados correctamente."
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", mensaje)
        self._nuevo_usuario()
        self._refrescar_usuarios()
        self._refrescar_responsables()

    def _eliminar_usuario_seleccionado(self):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un usuario de la lista.")
            return
        usuario, _, rol = self.tabla_usuarios.item(seleccion[0], "values")
        if self._aviso_sin_alcance(usuario, rol, "eliminar"):
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{usuario}'?"):
            return
        try:
            autenticacion.eliminar_usuario(usuario, self.usuario["usuario"],
                                           self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self._nuevo_usuario()
        self._refrescar_usuarios()
        self._refrescar_responsables()

    def _restablecer_clave_seleccionado(self):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un usuario de la lista.")
            return
        usuario, nombre, rol = self.tabla_usuarios.item(seleccion[0], "values")
        if self._aviso_sin_alcance(usuario, rol, "restablecer la contraseña de"):
            return
        nueva = self._pedir_nueva_clave(f"{nombre} ({usuario})")
        if nueva is None:  # cancelado
            return
        try:
            autenticacion.restablecer_clave(
                usuario, self.usuario["usuario"], self.usuario.get("rol"), nueva)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", f"Contraseña de '{usuario}' restablecida correctamente.")

    def _pedir_nueva_clave(self, usuario_texto):
        """Diálogo modal para escribir y confirmar una nueva contraseña.
        Devuelve la contraseña, o None si se cancela."""
        dlg = tk.Toplevel(self)
        dlg.title("Restablecer contraseña")
        dlg.configure(bg=COLOR_BLANCO)
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        if ARCHIVO_ICONO.exists():
            try:
                dlg.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        resultado = {"clave": None}
        cont = tk.Frame(dlg, bg=COLOR_BLANCO, padx=20, pady=16)
        cont.pack(fill="both", expand=True)
        tk.Label(cont, text=f"Nueva contraseña para:\n{usuario_texto}", bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO, justify="left", font=("Helvetica", 10, "bold")).pack(anchor="w")
        
        tk.Label(cont, text="Contraseña", bg=COLOR_BLANCO, fg=COLOR_TEXTO).pack(anchor="w")
        e1 = ttk.Entry(cont, width=30, show="•")
        e1.pack(fill="x", pady=(0, 8))
        tk.Label(cont, text="Confirmar contraseña", bg=COLOR_BLANCO, fg=COLOR_TEXTO).pack(anchor="w")
        e2 = ttk.Entry(cont, width=30, show="•")
        e2.pack(fill="x", pady=(0, 6))

        var = tk.BooleanVar(value=False)
        def alternar():
            e1.config(show="" if var.get() else "•")
            e2.config(show="" if var.get() else "•")
        tk.Checkbutton(cont, text="Mostrar contraseña", variable=var, command=alternar,
                       bg=COLOR_BLANCO, fg="#6B7280", activebackground=COLOR_BLANCO,
                       selectcolor=COLOR_BLANCO, font=("Helvetica", 9),
                       cursor="hand2", bd=0, highlightthickness=0).pack(anchor="w", pady=(0, 12))

        def aceptar():
            if e1.get() != e2.get():
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=dlg)
                return
            if not e1.get():
                messagebox.showerror("Error", "La contraseña no puede estar vacía.", parent=dlg)
                return
            resultado["clave"] = e1.get()
            dlg.destroy()

        barra = tk.Frame(cont, bg=COLOR_BLANCO)
        barra.pack(fill="x")
        tk.Button(barra, text="Restablecer", command=aceptar, bg=COLOR_AZUL, fg=COLOR_BLANCO,
                  activebackground="#1A2E5A", activeforeground=COLOR_BLANCO, relief="flat",
                  cursor="hand2", font=("Helvetica", 10, "bold"), padx=12, pady=5).pack(side="right")
        tk.Button(barra, text="Cancelar", command=dlg.destroy, relief="flat", cursor="hand2",
                  font=("Helvetica", 10), padx=12, pady=5).pack(side="right", padx=6)

        e1.bind("<Return>", lambda e: e2.focus_set())
        e2.bind("<Return>", lambda e: aceptar())
        dlg.update_idletasks()
        dlg.grab_set()
        e1.focus_set()
        dlg.wait_window()
        return resultado["clave"]

    def _refrescar_usuarios(self):
        self.tabla_usuarios.delete(*self.tabla_usuarios.get_children())
        for usu in autenticacion.listar_usuarios():
            self.tabla_usuarios.insert("", "end",
                                       values=(usu["usuario"], usu["nombre"], usu["rol"]))

    # ---- Configuración (superusuario y administradores) --------------------
    def _construir_configuracion(self):
        """Permite al superusuario o a un administrador indicar la última
        Referencia UDC registrada en el Excel anterior, para que el sistema
        continúe desde ahí."""
        # Toda la pestaña va en un área con desplazamiento: con varios paneles
        # (carpeta de datos, secuencial, carga masiva y copias de seguridad) los
        # botones de los últimos se salían de la ventana y no había forma de
        # alcanzarlos.
        self.configuracion_lienzo, marco = self._crear_area_desplazable(
            self.pestana_configuracion)

        ttk.Label(marco, text="Configuración del sistema",
                  font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(0, 8))

        # Diagnóstico: qué carpeta de datos se está usando realmente. Evita la
        # confusión de creer que se comparten los datos cuando en realidad cada
        # carpeta de versión está usando la suya.
        marco_ruta = ttk.LabelFrame(marco, text=" Carpeta de datos en uso ", padding=(12, 6))
        marco_ruta.pack(fill="x", pady=(0, 12))
        self._etiqueta_ajustable(marco_ruta, str(configuracion.DIR_DATOS),
                                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        if configuracion.DIR_DATOS.parent == configuracion.DIR_BASE:
            detalle = ("Se está usando la carpeta contigua al ejecutable. Para "
                       "compartir los datos entre versiones, cree junto al "
                       f"ejecutable un archivo '{configuracion.ARCHIVO_RUTA_DATOS}' "
                       "con la ruta de la carpeta compartida.")
            color = "#b45309"
        else:
            detalle = "Carpeta configurada fuera del ejecutable (uso compartido)."
            color = "#15803d"
        self._etiqueta_ajustable(marco_ruta, detalle, foreground=color,
                                 font=("Helvetica", 8)).pack(anchor="w", pady=(2, 0))

        panel = ttk.LabelFrame(marco, text=" Secuencial inicial de la Referencia UDC ",
                               padding=12)
        panel.pack(fill="x")

        ejemplo_sigla = list(INSTITUCIONES.values())[0]
        self._etiqueta_ajustable(
            panel,
            "Indique, por institución, la ÚLTIMA Referencia UDC utilizada "
            "antes del sistema.\n"
            f"Formato: {PREFIJO_REFERENCIA}-SIGLA-AAAA-NNNN  "
            f"(por ejemplo {PREFIJO_REFERENCIA}-{ejemplo_sigla}-"
            f"{parametros.anio_vigente()}-0241)."
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Label(panel, text="Institución").grid(row=1, column=0, sticky="w", pady=4)
        self.combo_institucion_secuencial = ttk.Combobox(
            panel, width=30, state="readonly", values=list(INSTITUCIONES))
        self.combo_institucion_secuencial.current(0)
        self.combo_institucion_secuencial.bind(
            "<<ComboboxSelected>>", lambda e: self._refrescar_configuracion())
        self.combo_institucion_secuencial.grid(row=1, column=1, sticky="w",
                                               padx=6, pady=4)

        ttk.Label(panel, text="Última Referencia UDC utilizada").grid(
            row=2, column=0, sticky="w", pady=4)
        self.entrada_secuencial = ttk.Entry(panel, width=28)
        self.entrada_secuencial.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        btn = ttk.Button(panel, text="Guardar", command=self._guardar_secuencial)
        btn.grid(row=3, column=1, sticky="w", padx=6, pady=(8, 4))
        btn.config(style="Accent.TButton")

        self.lbl_secuencial = ttk.Label(panel, text="", font=("Helvetica", 9))
        self.lbl_secuencial.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self._etiqueta_ajustable(
            panel,
            "El formato de los códigos corren de forma continua. Solo el "
            "superusuario y los administradores pueden modificar este valor.",
            foreground="#6B7280", font=("Helvetica", 8)
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))

        # --- Catálogo de tipos de acción (gestores) --------------------------
        self._construir_panel_tipos_accion(marco)

        # --- Carga masiva de oficios (gestores) ------------------------------
        self._construir_panel_carga_masiva(marco)

        # --- Copias de seguridad: EXCLUSIVO del superusuario -----------------
        if self._es_superusuario():
            self._construir_panel_respaldos(marco)

        # Los textos largos se re-ajustan al ancho de la pestaña.
        self.configuracion_lienzo.bind("<Configure>", self._ajustar_etiquetas,
                                       add="+")
        self._refrescar_configuracion()

    def _etiqueta_ajustable(self, contenedor, texto, **kw):
        """Etiqueta de texto largo cuyo ancho de corte sigue al de la ventana.

        Con un `wraplength` fijo el texto se corta siempre a la misma anchura y
        deja media pestaña vacía cuando la ventana está maximizada.
        """
        etiqueta = ttk.Label(contenedor, text=texto, justify="left", **kw)
        self._etiquetas_ajustables.append(etiqueta)
        return etiqueta

    def _ajustar_etiquetas_campo(self, evento=None):
        """Ancho de corte de las etiquetas de los formularios.

        El corte es el 45 % del recuadro que las contiene, con un TOPE de
        `ANCHO_MAXIMO_ETIQUETA`: la columna de etiquetas nunca se come la del
        campo y las etiquetas largas —«Institución del Estado», «Confirmar
        contraseña»— se reparten en dos líneas también con la ventana ancha,
        que es donde antes se estiraban a lo largo.
        """
        for etiqueta in self._etiquetas_campo:
            try:
                ancho = min(self.ANCHO_MAXIMO_ETIQUETA,
                            max(90, int(etiqueta.master.winfo_width() * 0.45) - 16))
                if str(etiqueta.cget("wraplength")).strip() != str(ancho):
                    etiqueta.config(wraplength=ancho)
            except tk.TclError:
                pass          # la etiqueta ya no existe

    def _ajustar_etiquetas(self, evento=None):
        ancho = self.configuracion_lienzo.winfo_width() - 90
        if ancho < 200:
            return
        for etiqueta in self._etiquetas_ajustables:
            try:
                # Una etiqueta sin wraplength devuelve cadena vacía, no 0.
                actual = str(etiqueta.cget("wraplength")).strip()
                if actual != str(ancho):
                    etiqueta.config(wraplength=ancho)
            except tk.TclError:
                pass          # la etiqueta ya no existe

    def _construir_panel_tipos_accion(self, marco):
        """Catálogo de tipos de acción, mantenible por los gestores."""
        panel = ttk.LabelFrame(marco, text=" Tipos de acción ", padding=12)
        panel.pack(fill="x", pady=(14, 0))

        self._etiqueta_ajustable(
            panel,
            "Opciones disponibles en el campo «Tipo de acción» del oficio. "
            "Entre paréntesis, cuántos oficios usan cada una."
        ).pack(anchor="w", pady=(0, 8))

        cuerpo = ttk.Frame(panel)
        cuerpo.pack(fill="x")
        contenedor = ttk.Frame(cuerpo)
        contenedor.pack(side="left")
        self.lista_tipos_accion = tk.Listbox(contenedor, height=7, width=42,
                                             activestyle="none",
                                             highlightthickness=1,
                                             highlightbackground="#CBD2DE",
                                             relief="flat")
        barra = ttk.Scrollbar(contenedor, orient="vertical",
                              command=self.lista_tipos_accion.yview)
        self.lista_tipos_accion.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lista_tipos_accion.pack(side="left", fill="both", expand=True)

        botones = ttk.Frame(cuerpo)
        botones.pack(side="left", padx=12, anchor="n")
        btn = ttk.Button(botones, text="Agregar", width=14,
                         command=self._agregar_tipo_accion)
        btn.pack(pady=(0, 6))
        btn.config(style="Accent.TButton")
        ttk.Button(botones, text="Renombrar", width=14,
                   command=self._renombrar_tipo_accion).pack(pady=(0, 6))
        ttk.Button(botones, text="Eliminar", width=14,
                   command=self._eliminar_tipo_accion).pack()

        self._etiqueta_ajustable(
            panel,
            "Un tipo en uso no se puede eliminar, pero sí renombrar: el cambio "
            "se aplica a los oficios que lo tuvieran.",
            foreground="#6B7280", font=("Helvetica", 8)
        ).pack(anchor="w", pady=(8, 0))

    def _refrescar_tipos_accion(self):
        if not hasattr(self, "lista_tipos_accion"):
            return
        self.lista_tipos_accion.delete(0, "end")
        try:
            uso = tipos_accion.uso_actual()
        except ValueError as error:
            self.lista_tipos_accion.insert("end", str(error))
            return
        for tipo, cantidad in uso.items():
            self.lista_tipos_accion.insert("end", f"{tipo}   ({cantidad})")
        self._refrescar_desplegables_accion()

    def _refrescar_desplegables_accion(self):
        """Repuebla los desplegables de tipo de acción tras cambiar el catálogo."""
        valores = self._tipos_accion()
        for atributo in ("combo_tipo_accion", "combo_tipo_accion_edicion"):
            combo = getattr(self, atributo, None)
            if combo is not None:
                try:
                    combo.config(values=valores)
                except tk.TclError:
                    pass

    def _tipo_accion_seleccionado(self):
        """Nombre del tipo elegido en la lista, sin el contador."""
        seleccion = self.lista_tipos_accion.curselection()
        if not seleccion:
            messagebox.showwarning("Sin selección",
                                   "Seleccione un tipo de acción de la lista.")
            return None
        texto = self.lista_tipos_accion.get(seleccion[0])
        return texto.rsplit("   (", 1)[0]

    def _agregar_tipo_accion(self):
        nuevo = simpledialog.askstring(
            "Nuevo tipo de acción", "Nombre del tipo de acción:", parent=self)
        if nuevo is None:
            return
        try:
            tipos_accion.agregar(nuevo, self.usuario["usuario"],
                                 self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self._refrescar_tipos_accion()

    def _renombrar_tipo_accion(self):
        actual = self._tipo_accion_seleccionado()
        if actual is None:
            return
        nuevo = simpledialog.askstring(
            "Renombrar tipo de acción",
            f"Nuevo nombre para «{actual}»:", initialvalue=actual, parent=self)
        if nuevo is None:
            return
        try:
            afectados = tipos_accion.renombrar(actual, nuevo,
                                               self.usuario["usuario"],
                                               self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        if afectados:
            messagebox.showinfo(
                "Renombrado",
                f"Se actualizaron {afectados} oficio(s) que usaban «{actual}».")
        self._refrescar_tipos_accion()
        self._refrescar_listado()

    def _eliminar_tipo_accion(self):
        tipo = self._tipo_accion_seleccionado()
        if tipo is None:
            return
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar el tipo de acción «{tipo}»?"):
            return
        try:
            tipos_accion.eliminar(tipo, self.usuario["usuario"],
                                  self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self._refrescar_tipos_accion()

    def _construir_panel_carga_masiva(self, marco):
        """Panel para volcar de una vez el histórico de la matriz de Excel."""
        panel = ttk.LabelFrame(marco, text=" Carga masiva de oficios ", padding=12)
        panel.pack(fill="x", pady=(14, 0))

        self._etiqueta_ajustable(
            panel,
            "Permite dar de alta de una sola vez los oficios que se venían "
            "llevando en la matriz de Excel. Se admite la propia matriz "
            "(.xlsx) o un CSV con la misma cabecera."
        ).pack(anchor="w", pady=(0, 8))

        btn = ttk.Button(panel, text="Cargar archivo",
                         command=self._abrir_carga_masiva)
        btn.pack(anchor="w")
        btn.config(style="Accent.TButton")

        self._etiqueta_ajustable(
            panel,
            "Los oficios importados no llevan el documento del oficio ni la "
            "respuesta en PDF; se pueden adjuntar después desde la pestaña "
            "Oficios.",
            foreground="#6B7280", font=("Helvetica", 8)
        ).pack(anchor="w", pady=(8, 0))

    def _abrir_carga_masiva(self):
        ruta = filedialog.askopenfilename(
            title="Seleccione la matriz de oficios",
            filetypes=[("Matriz de oficios", "*.xlsx *.xlsm *.csv"),
                       ("Excel", "*.xlsx *.xlsm"), ("CSV", "*.csv")])
        if not ruta:
            return
        try:
            resumen = carga_masiva.preparar(ruta, autenticacion.listar_usuarios())
        except ValueError as error:
            messagebox.showerror("No se pudo leer el archivo", str(error))
            return
        if not resumen["filas"]:
            messagebox.showinfo(
                "Sin oficios",
                "El archivo no contiene ninguna fila con datos de oficios.")
            return
        dialogo = DialogoCargaMasiva(self, self.usuario, resumen)
        self.wait_window(dialogo)
        self._refrescar_listado()

    def _construir_panel_respaldos(self, marco):
        """Panel de copias de seguridad. Solo lo ve el superusuario."""
        panel = ttk.LabelFrame(marco, text=" Copias de seguridad ", padding=12)
        panel.pack(fill="x", pady=(14, 0))

        self._etiqueta_ajustable(
            panel,
            "La aplicación crea automáticamente una copia al día, la primera "
            "vez que alguien la abre. Se guardan en datos\\respaldos y se "
            f"conservan los últimos {DIAS_RESPALDO_POR_DEFECTO} días.\n"
            "No se incluyen los PDF de respuesta."
        ).pack(anchor="w", pady=(0, 8))

        self.lbl_respaldos = ttk.Label(panel, text="", font=("Helvetica", 9))
        self.lbl_respaldos.pack(anchor="w")

        barra = ttk.Frame(panel)
        barra.pack(anchor="w", pady=(10, 0))
        btn = ttk.Button(barra, text="Crear copia ahora",
                         command=self._crear_respaldo_manual)
        btn.pack(side="left")
        btn.config(style="Accent.TButton")
        ttk.Button(barra, text="Abrir carpeta de copias",
                   command=self._abrir_carpeta_respaldos).pack(side="left", padx=6)

    def _refrescar_panel_respaldos(self):
        if not hasattr(self, "lbl_respaldos"):
            return
        copias = respaldo.listar_respaldos()
        if not copias:
            self.lbl_respaldos.config(text="Todavía no hay copias.", foreground="#a00")
            return
        ultima = copias[0]
        tamano = ultima.stat().st_size / 1024
        self.lbl_respaldos.config(
            text=f"Última copia: {ultima.name}  ({tamano:.0f} KB)    ·    "
                 f"{len(copias)} copia(s) guardada(s)",
            foreground=COLOR_TEXTO)

    def _crear_respaldo_manual(self):
        try:
            archivo = respaldo.crear_respaldo(self.usuario["usuario"], forzar=True)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self._refrescar_panel_respaldos()
        messagebox.showinfo("Listo", f"Copia creada:\n{archivo.name}")

    def _abrir_carpeta_respaldos(self):
        if not visor_pdf.abrir_con_sistema(DIR_RESPALDOS):
            messagebox.showinfo("Carpeta de copias", f"Ruta: {DIR_RESPALDOS}")

    def _refrescar_configuracion(self):
        self._refrescar_panel_respaldos()
        self._refrescar_tipos_accion()
        institucion = self.combo_institucion_secuencial.get()
        try:
            actual = parametros.obtener_referencia_inicial(institucion)
            proxima = oficios.proxima_referencia(institucion)
        except ValueError as error:
            self.lbl_secuencial.config(text=str(error), foreground="#a00")
            return
        if actual:
            texto = (f"{institucion} · configurado: {actual}.    "
                     f"Próxima Referencia UDC: {proxima}")
        else:
            texto = (f"{institucion} · sin configurar.    "
                     f"Próxima Referencia UDC: {proxima}")
        self.lbl_secuencial.config(text=texto, foreground=COLOR_TEXTO)

    def _guardar_secuencial(self):
        valor = self.entrada_secuencial.get().strip()
        if not valor:
            messagebox.showwarning("Falta el dato",
                                   "Ingrese la última Referencia UDC registrada.")
            return
        institucion = self.combo_institucion_secuencial.get()
        if parametros.esta_configurado(institucion) and not messagebox.askyesno(
                "Confirmar",
                f"El secuencial de {institucion} ya está configurado como "
                f"{parametros.obtener_referencia_inicial(institucion)}.\n\n"
                "¿Desea reemplazarlo?"):
            return
        try:
            normalizada = parametros.definir_secuencial_inicial(
                valor, self.usuario["usuario"], self.usuario.get("rol"),
                institucion)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self.entrada_secuencial.delete(0, "end")
        self._refrescar_configuracion()
        messagebox.showinfo(
            "Listo",
            f"Secuencial de {institucion} configurado en {normalizada}.\n"
            f"La próxima Referencia UDC será "
            f"{oficios.proxima_referencia(institucion)}.")

    # ---- Tablero (dashboard) -----------------------------------------------
    # Paleta de los estados, reutilizada en tarjetas y gráficos.
    COLOR_POR_ASIGNAR = "#b45309"
    COLOR_EN_PROCESO = "#1d4ed8"
    COLOR_FINALIZADO = "#15803d"

    def _construir_tablero(self):
        """Tablero con scroll vertical: tarjetas de indicadores y gráficos."""
        self.tablero_lienzo, self.tablero = self._crear_area_desplazable(
            self.pestana_tablero)

        ttk.Label(self.tablero, text="Tablero de oficios",
                  font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(0, 2))
        self.lbl_alcance = ttk.Label(self.tablero, text="", foreground="#6B7280",
                                     font=("Helvetica", 8))
        self.lbl_alcance.pack(anchor="w")

        # Dos filas de tarjetas de indicadores.
        self.marco_tarjetas = ttk.Frame(self.tablero)
        self.marco_tarjetas.pack(fill="x", pady=(10, 4))
        self.marco_tarjetas2 = ttk.Frame(self.tablero)
        self.marco_tarjetas2.pack(fill="x", pady=(0, 8))

        # Gráfico 1: recepciones por día.
        self.lienzo = self._crear_lienzo(self.tablero, 210)
        # Gráficos 2 y 3, lado a lado: estados (anillo) y responsables (barras).
        fila = ttk.Frame(self.tablero)
        fila.pack(fill="x", pady=6)
        self.lienzo_estados = self._crear_lienzo(fila, 240, lado="left", expandir=True)
        self.lienzo_responsables = self._crear_lienzo(fila, 240, lado="left", expandir=True)
        # Gráfico 4: recepciones por mes.
        self.lienzo_meses = self._crear_lienzo(self.tablero, 210)

    def _crear_lienzo(self, contenedor, alto, lado=None, expandir=False):
        lienzo = tk.Canvas(contenedor, height=alto, background=COLOR_BLANCO,
                           highlightthickness=1, highlightbackground="#DDE3EC")
        if lado:
            lienzo.pack(side=lado, fill="both", expand=expandir, padx=(0, 6))
        else:
            lienzo.pack(fill="x", pady=6)
        return lienzo

    def _tarjeta(self, contenedor, titulo, valor, color):
        marco = tk.Frame(contenedor, bg=color, padx=12, pady=8)
        marco.pack(side="left", padx=4)
        tk.Label(marco, text=str(valor), bg=color, fg=COLOR_BLANCO,
                 font=("Helvetica", 17, "bold")).pack()
        tk.Label(marco, text=titulo, bg=color, fg=COLOR_BLANCO,
                 font=("Helvetica", 9)).pack()

    def _refrescar_tablero(self):
        for contenedor in (self.marco_tarjetas, self.marco_tarjetas2):
            for hijo in contenedor.winfo_children():
                hijo.destroy()

        # El tablero refleja únicamente los oficios que el usuario puede ver.
        # Los anulados quedan fuera de las métricas: no son trabajo real.
        registros = oficios.listar_oficios_visibles(
            self.usuario["usuario"], self.usuario.get("rol"))
        datos = metricas.resumen(registros)
        self.lbl_alcance.config(
            text="Todos los oficios" if self._puede_gestionar_usuarios()
            else "Solo sus oficios (registrados o asignados a usted)")

        # Fila 1: volumen y estados.
        self._tarjeta(self.marco_tarjetas, "Total", datos["total"], COLOR_AZUL)
        self._tarjeta(self.marco_tarjetas, "Por asignar",
                      datos["por_estado"]["Por asignar"], self.COLOR_POR_ASIGNAR)
        self._tarjeta(self.marco_tarjetas, "En proceso",
                      datos["por_estado"]["En proceso"], self.COLOR_EN_PROCESO)
        self._tarjeta(self.marco_tarjetas, "Finalizados",
                      datos["finalizados"], self.COLOR_FINALIZADO)
        self._tarjeta(self.marco_tarjetas, "% finalizados",
                      f"{datos['porcentaje_finalizados']}%", "#0f766e")
        promedio = datos["dias_promedio_respuesta"]
        self._tarjeta(self.marco_tarjetas, "Días prom. respuesta",
                      promedio if promedio is not None else "—", "#334155")

        # Fila 2: recepción reciente y seguimiento de respuestas.
        self._tarjeta(self.marco_tarjetas2, "Hoy", datos["recibidos_hoy"], "#0f766e")
        self._tarjeta(self.marco_tarjetas2, "Semana", datos["recibidos_semana"], "#7c3aed")
        self._tarjeta(self.marco_tarjetas2, "Mes", datos["recibidos_mes"], "#be123c")
        self._tarjeta(self.marco_tarjetas2, "Con respuesta", datos["con_respuesta"], "#15803d")
        self._tarjeta(self.marco_tarjetas2, "Sin respuesta", datos["sin_respuesta"], "#b45309")
        self._tarjeta(self.marco_tarjetas2, "Con PDF", datos["con_pdf"], "#1d4ed8")
        self._tarjeta(self.marco_tarjetas2, "Sin responsable",
                      datos["sin_responsable"], "#64748b")

        # Gráficos.
        self._dibujar_barras(metricas.serie_por_dia(14, registros))
        self._dibujar_anillo_estados(metricas.distribucion_estados(registros))
        self._dibujar_barras_horizontales(metricas.por_responsable(registros))
        self._dibujar_barras_meses(metricas.serie_por_mes(6, registros))
        self.tablero_lienzo.configure(scrollregion=self.tablero_lienzo.bbox("all"))

    # Fuentes de los gráficos: el título, la cifra que corona cada barra y la
    # etiqueta del eje.
    FUENTE_TITULO_GRAFICO = ("Helvetica", 9, "bold")
    FUENTE_VALOR_GRAFICO = ("Helvetica", 8)

    @classmethod
    def _medidas_grafico(cls):
        """(y del título, margen superior) medidos con las fuentes de verdad.

        La barra más alta siempre llega justo hasta el margen superior —la
        escala se normaliza con el valor máximo—, así que la cifra que la
        corona se dibuja siempre a la misma altura por muy grandes que sean los
        valores. Lo que sí cambia de un equipo a otro es el TAMAÑO del texto,
        de modo que el margen se calcula a partir de él y no con un número
        fijo: título + separación + cifra.
        """
        try:
            alto_titulo = tkfont.Font(
                font=cls.FUENTE_TITULO_GRAFICO).metrics("linespace")
            alto_valor = tkfont.Font(
                font=cls.FUENTE_VALOR_GRAFICO).metrics("linespace")
        except tk.TclError:
            alto_titulo, alto_valor = 14, 12
        y_titulo = 4 + alto_titulo / 2
        return y_titulo, int(4 + alto_titulo + 8 + alto_valor)

    def _dibujar_barras(self, serie):
        """Barras verticales: oficios recibidos por día."""
        lienzo = self.lienzo
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho_lienzo = lienzo.winfo_width() or 800
        alto_lienzo = 210
        y_titulo, margen_sup = self._medidas_grafico()
        margen_izq, margen_inf = 30, 30
        valor_max = max([valor for _, valor in serie] + [1])
        cantidad = len(serie)
        ancho_barra = (ancho_lienzo - margen_izq - 10) / cantidad
        lienzo.create_text(margen_izq, y_titulo,
                           text="Oficios recibidos por día (14 días)",
                           anchor="w", font=self.FUENTE_TITULO_GRAFICO,
                           fill=COLOR_TEXTO)
        for indice, (dia, valor) in enumerate(serie):
            x0 = margen_izq + indice * ancho_barra + 4
            x1 = x0 + ancho_barra - 8
            altura = (alto_lienzo - margen_inf - margen_sup) * (valor / valor_max)
            y1 = alto_lienzo - margen_inf
            y0 = y1 - altura
            lienzo.create_rectangle(x0, y0, x1, y1, fill=COLOR_AZUL, outline="")
            if valor:
                lienzo.create_text((x0 + x1) / 2, y0 - 8, text=str(valor),
                                   font=self.FUENTE_VALOR_GRAFICO)
            lienzo.create_text((x0 + x1) / 2, y1 + 12, text=dia[5:],
                               font=("Helvetica", 7))

    def _dibujar_barras_meses(self, serie):
        """Barras verticales: oficios recibidos por mes."""
        lienzo = self.lienzo_meses
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho_lienzo = lienzo.winfo_width() or 800
        alto_lienzo = 210
        y_titulo, margen_sup = self._medidas_grafico()
        margen_izq, margen_inf = 30, 30
        valor_max = max([valor for _, valor in serie] + [1])
        ancho_barra = (ancho_lienzo - margen_izq - 10) / max(len(serie), 1)
        lienzo.create_text(margen_izq, y_titulo,
                           text="Oficios recibidos por mes (6 meses)",
                           anchor="w", font=self.FUENTE_TITULO_GRAFICO,
                           fill=COLOR_TEXTO)
        for indice, (mes, valor) in enumerate(serie):
            x0 = margen_izq + indice * ancho_barra + 12
            x1 = x0 + ancho_barra - 24
            altura = (alto_lienzo - margen_inf - margen_sup) * (valor / valor_max)
            y1 = alto_lienzo - margen_inf
            y0 = y1 - altura
            lienzo.create_rectangle(x0, y0, x1, y1, fill="#7c3aed", outline="")
            lienzo.create_text((x0 + x1) / 2, y0 - 8, text=str(valor),
                               font=self.FUENTE_VALOR_GRAFICO)
            lienzo.create_text((x0 + x1) / 2, y1 + 12, text=mes,
                               font=("Helvetica", 7))

    def _dibujar_anillo_estados(self, distribucion):
        """Gráfico de anillo con la distribución por estado."""
        lienzo = self.lienzo_estados
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho = lienzo.winfo_width() or 380
        alto = 240
        lienzo.create_text(16, 12, text="Distribución por estado", anchor="w",
                           font=("Helvetica", 9, "bold"), fill=COLOR_TEXTO)

        total = sum(valor for _, valor in distribucion)
        colores = {"Por asignar": self.COLOR_POR_ASIGNAR,
                   "En proceso": self.COLOR_EN_PROCESO,
                   "Finalizado": self.COLOR_FINALIZADO}
        # Círculo a la izquierda, leyenda a la derecha.
        diametro = min(alto - 70, 140)
        x0, y0 = 30, 46
        x1, y1 = x0 + diametro, y0 + diametro

        if not total:
            lienzo.create_oval(x0, y0, x1, y1, outline="#DDE3EC", width=18)
            lienzo.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="Sin datos",
                               font=("Helvetica", 9), fill="#6B7280")
            return

        inicio = 90.0
        for estado, valor in distribucion:
            if not valor:
                continue
            extension = -360.0 * valor / total
            # 'arc' con ancho grueso da el efecto de anillo sin rellenar el centro.
            lienzo.create_arc(x0, y0, x1, y1, start=inicio, extent=extension,
                              style="arc", width=22, outline=colores.get(estado, COLOR_AZUL))
            inicio += extension
        lienzo.create_text((x0 + x1) / 2, (y0 + y1) / 2 - 8, text=str(total),
                           font=("Helvetica", 16, "bold"), fill=COLOR_TEXTO)
        lienzo.create_text((x0 + x1) / 2, (y0 + y1) / 2 + 12, text="oficios",
                           font=("Helvetica", 8), fill="#6B7280")

        # Leyenda.
        leyenda_x = x1 + 24
        leyenda_y = y0 + 10
        for estado, valor in distribucion:
            porcentaje = round(valor * 100 / total) if total else 0
            lienzo.create_rectangle(leyenda_x, leyenda_y, leyenda_x + 12, leyenda_y + 12,
                                    fill=colores.get(estado, COLOR_AZUL), outline="")
            lienzo.create_text(leyenda_x + 20, leyenda_y + 6, anchor="w",
                               text=f"{estado}: {valor} ({porcentaje}%)",
                               font=("Helvetica", 9), fill=COLOR_TEXTO)
            leyenda_y += 26

    def _dibujar_barras_horizontales(self, datos):
        """Barras horizontales: cantidad de oficios por responsable."""
        lienzo = self.lienzo_responsables
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho = lienzo.winfo_width() or 380
        lienzo.create_text(16, 12, text="Oficios por responsable", anchor="w",
                           font=("Helvetica", 9, "bold"), fill=COLOR_TEXTO)
        if not datos:
            lienzo.create_text(ancho / 2, 120, text="Sin datos",
                               font=("Helvetica", 9), fill="#6B7280")
            return

        margen_izq = 130          # espacio para el nombre
        margen_der = 40           # espacio para el valor
        ancho_util = max(ancho - margen_izq - margen_der, 40)
        valor_max = max(valor for _, valor in datos)
        alto_fila = min(26, max(16, int((240 - 50) / max(len(datos), 1))))
        y = 42
        for nombre, valor in datos:
            etiqueta = nombre if len(nombre) <= 18 else nombre[:17] + "…"
            lienzo.create_text(margen_izq - 8, y + alto_fila / 2, text=etiqueta,
                               anchor="e", font=("Helvetica", 8), fill=COLOR_TEXTO)
            largo = ancho_util * (valor / valor_max)
            lienzo.create_rectangle(margen_izq, y + 3, margen_izq + max(largo, 2),
                                    y + alto_fila - 3, fill=COLOR_AZUL, outline="")
            lienzo.create_text(margen_izq + largo + 8, y + alto_fila / 2,
                               text=str(valor), anchor="w", font=("Helvetica", 8))
            y += alto_fila

    def _al_cambiar_pestana(self, evento):
        # Se identifica la pestaña por su widget (no por índice), porque la
        # pestaña "Usuarios" puede o no estar presente según el rol.
        try:
            actual = evento.widget.nametowidget(evento.widget.select())
        except (tk.TclError, KeyError):
            return
        if actual is self.pestana_registro:
            self._refrescar_responsables()
        elif actual is self.pestana_configuracion:
            if self._puede_gestionar_usuarios():
                self._refrescar_configuracion()
        elif actual is self.pestana_listado:
            self._refrescar_responsables()
            self._refrescar_listado()
        elif actual is self.pestana_tablero:
            self._refrescar_tablero()

    def _al_recuperar_foco(self, evento):
        """Refresca la vista al volver a la ventana.

        Con varias personas usando la misma carpeta compartida, lo que se ve en
        pantalla puede haber quedado desactualizado. Refrescar al recuperar el
        foco mantiene los datos al día sin botones ni recargas periódicas.
        """
        # <FocusIn> también llega desde los widgets hijos: solo interesa cuando
        # es la ventana entera la que recupera el foco.
        if evento.widget is not self.maestro:
            return
        ahora = time.monotonic()
        if ahora - self._ultimo_refresco < 2.0:
            return                      # evitar ráfagas al alternar ventanas
        self._ultimo_refresco = ahora
        try:
            actual = self.cuaderno.nametowidget(self.cuaderno.select())
        except (tk.TclError, KeyError):
            return
        if actual is self.pestana_listado:
            self._refrescar_responsables()
            self._refrescar_listado()
        elif actual is self.pestana_tablero:
            self._refrescar_tablero()
        elif actual is self.pestana_usuarios and self._puede_gestionar_usuarios():
            self._refrescar_usuarios()


# ============================================================================
#  MANTENIMIENTO DE OFICIOS
# ============================================================================
class DialogoMantenimiento(tk.Toplevel):
    """Corrige los datos de identificación de un oficio y permite retirarlo.

    Son los campos que el panel normal no deja tocar porque identifican al
    oficio; cuando se teclean mal no había forma de arreglarlos. Está reservado
    a administradores y al superusuario, y todo cambio queda en la bitácora.
    """

    def __init__(self, aplicacion, usuario, registro):
        super().__init__(aplicacion)
        self.aplicacion = aplicacion
        self.usuario = usuario
        self.registro = registro
        self.referencia = registro["referencia"]
        self.anulado = oficios.esta_anulado(registro)
        self.title(f"Mantenimiento · {self.referencia}")
        self.configure(bg=COLOR_BLANCO)
        self.resizable(False, False)
        self.transient(aplicacion.winfo_toplevel())
        self.grab_set()

        marco = tk.Frame(self, bg=COLOR_BLANCO, padx=18, pady=16)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(1, weight=1)

        tk.Label(marco, text=f"Oficio {self.referencia}", bg=COLOR_BLANCO,
                 fg=COLOR_AZUL, font=("Helvetica", 12, "bold")).grid(
                     row=0, column=0, columnspan=2, sticky="w")
        tk.Label(marco, bg=COLOR_BLANCO, fg="#6B7280", font=("Helvetica", 8),
                 justify="left", wraplength=430,
                 text="Corrija aquí los datos que identifican al oficio. El "
                      "resto del trámite se cambia en la pestaña Oficios.").grid(
                          row=1, column=0, columnspan=2, sticky="w", pady=(2, 12))

        self.campos = {}
        filas = [
            ("codigo_oficio", "Referencia oficio *", False),
            ("causal_oficio", "Causal oficio", False),
            ("fecha_oficio", "Fecha de oficio *", True),
            ("fecha_recepcion", "Fecha de recepción *", True),
        ]
        for indice, (campo, etiqueta, es_fecha) in enumerate(filas, start=2):
            tk.Label(marco, text=etiqueta, bg=COLOR_BLANCO,
                     fg=COLOR_TEXTO).grid(row=indice, column=0, sticky="w", pady=4)
            if es_fecha:
                widget = SelectorFecha(marco)
                widget.set(registro.get(campo, ""))
            else:
                widget = ttk.Entry(marco, width=34)
                widget.insert(0, registro.get(campo, ""))
            widget.grid(row=indice, column=1, sticky="w", padx=(10, 0), pady=4)
            self.campos[campo] = widget

        barra = tk.Frame(marco, bg=COLOR_BLANCO)
        barra.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Button(barra, text="Cerrar", command=self.destroy).pack(side="right")
        btn = ttk.Button(barra, text="Guardar correcciones",
                         command=self._guardar)
        btn.pack(side="right", padx=6)
        btn.config(style="Accent.TButton")
        if self.anulado:
            ttk.Button(barra, text="Reactivar oficio",
                       command=self._reactivar).pack(side="left")
        else:
            ttk.Button(barra, text="Anular oficio",
                       command=self._anular).pack(side="left")

        estado = tk.Frame(marco, bg=COLOR_BLANCO)
        estado.grid(row=9, column=0, columnspan=2, sticky="w", pady=(12, 0))
        if self.anulado:
            tk.Label(estado, bg=COLOR_BLANCO, fg="#b45309",
                     font=("Helvetica", 8, "bold"), justify="left", wraplength=430,
                     text=f"ANULADO por {registro.get('anulado_por', '?')} · "
                          f"{registro.get('motivo_anulacion', '')}").pack(anchor="w")
        else:
            tk.Label(estado, bg=COLOR_BLANCO, fg="#6B7280",
                     font=("Helvetica", 8), justify="left", wraplength=430,
                     text="Anular retira el oficio del listado y de las "
                          "métricas, pero lo conserva: la Referencia UDC no se "
                          "reutiliza y queda constancia de quién lo anuló y por "
                          "qué. Se puede reactivar.").pack(anchor="w")

    def _guardar(self):
        valores = {campo: widget.get().strip()
                   for campo, widget in self.campos.items()}
        try:
            cambios = oficios.corregir_oficio(
                self.referencia, self.usuario["usuario"],
                self.usuario.get("rol"), **valores)
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        if not cambios:
            messagebox.showinfo("Sin cambios", "No se modificó ningún dato.",
                                parent=self)
            return
        messagebox.showinfo("Corregido",
                            "Cambios aplicados:\n\n" + "\n".join(cambios),
                            parent=self)
        self.destroy()

    def _anular(self):
        motivo = simpledialog.askstring(
            "Anular oficio",
            f"Motivo por el que se retira el oficio {self.referencia}:",
            parent=self)
        if motivo is None:
            return
        try:
            oficios.anular_oficio(self.referencia, motivo,
                                  self.usuario["usuario"], self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        messagebox.showinfo(
            "Anulado",
            f"El oficio {self.referencia} queda fuera del listado y de las "
            "métricas.\nPuede volver a verlo con la casilla «Ver anulados».",
            parent=self)
        self.destroy()

    def _reactivar(self):
        if not messagebox.askyesno(
                "Reactivar",
                f"¿Devolver el oficio {self.referencia} a la operación?",
                parent=self):
            return
        try:
            oficios.reactivar_oficio(self.referencia, self.usuario["usuario"],
                                     self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        messagebox.showinfo("Reactivado", "El oficio vuelve a estar activo.",
                            parent=self)
        self.destroy()


# ============================================================================
#  IMPLICADOS DE UN OFICIO
# ============================================================================
class DialogoImplicados(tk.Toplevel):
    """Personas investigadas en un oficio: verlas, añadirlas y corregirlas.

    Se abre con doble clic sobre el oficio en la pestaña *Oficios*. La lista
    de arriba muestra a los implicados y el formulario de abajo sirve tanto
    para añadir uno nuevo como para modificar el que esté seleccionado.

    Mientras el oficio tenga implicados anotados, la *Cantidad de
    investigados* la cuenta esta lista: no tendría sentido que dijeran cosas
    distintas.
    """

    def __init__(self, aplicacion, usuario, registro):
        super().__init__(aplicacion)
        self.aplicacion = aplicacion
        self.usuario = usuario
        self.referencia = registro["referencia"]
        self.anulado = oficios.esta_anulado(registro)
        # Un usuario regular solo puede tocar los oficios asignados a él; el
        # resto los ve, pero en modo lectura.
        self.editable = (not self.anulado) and (
            usuario.get("rol") in ROLES_GESTORES
            or (registro.get("id_empleado", "") or "").strip().lower()
            == (usuario["usuario"] or "").strip().lower())
        self.id_en_edicion = None

        self.title(f"Implicados · {self.referencia}")
        self.configure(bg=COLOR_BLANCO)
        self.transient(aplicacion.winfo_toplevel())
        self.grab_set()
        self.minsize(720, 480)

        marco = tk.Frame(self, bg=COLOR_BLANCO, padx=18, pady=16)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(2, weight=1)

        tk.Label(marco, text=f"Oficio {self.referencia}", bg=COLOR_BLANCO,
                 fg=COLOR_AZUL, font=("Helvetica", 12, "bold")).grid(
                     row=0, column=0, sticky="w")
        detalle = registro.get("codigo_oficio", "")
        if registro.get("institucion"):
            detalle += f"   ·   {registro['institucion']}"
        if self.anulado:
            detalle += "   ·   ANULADO (solo lectura)"
        elif not self.editable:
            detalle += "   ·   solo lectura"
        tk.Label(marco, text=detalle, bg=COLOR_BLANCO, fg="#6B7280",
                 font=("Helvetica", 9)).grid(row=1, column=0, sticky="w",
                                             pady=(2, 10))

        # --- Lista de implicados --------------------------------------------
        lista = ttk.LabelFrame(marco, text=" Personas investigadas ",
                               padding=(10, 6))
        lista.grid(row=2, column=0, sticky="nsew")
        lista.columnconfigure(0, weight=1)
        lista.rowconfigure(0, weight=1)

        columnas = ("nombre", "tipo_id", "identificacion", "implicado", "lci")
        # Aquí no aprieta el ancho: los títulos van completos.
        titulos = ("Nombre o razón social", "Tipo de identificación",
                   "Identificación", "Tipo de implicado", "LCI")
        anchos = (250, 120, 120, 130, 50)
        self.tabla = ttk.Treeview(lista, columns=columnas, show="headings",
                                  height=8)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tabla.heading(columna, text=titulo)
            ancho = AplicacionPrincipal._ancho_columna(titulo, ancho)
            self.tabla.column(columna, width=ancho, minwidth=ancho, anchor="w",
                              stretch=columna == "nombre")
        barra = ttk.Scrollbar(lista, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        botones_lista = ttk.Frame(lista)
        botones_lista.grid(row=1, column=0, columnspan=2, sticky="w",
                           pady=(8, 0))
        self.btn_eliminar = ttk.Button(botones_lista, text="Eliminar",
                                       command=self._eliminar)
        self.btn_eliminar.pack(side="left")
        self.lbl_total = ttk.Label(botones_lista, text="",
                                   foreground="#6B7280", font=("Helvetica", 8))
        self.lbl_total.pack(side="left", padx=12)

        # --- Formulario -----------------------------------------------------
        self.formulario = ttk.LabelFrame(marco, text=" Datos del implicado ",
                                         padding=(10, 6))
        self.formulario.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        self.formulario.columnconfigure(1, weight=1)
        self.formulario.columnconfigure(3, weight=1)

        self.entrada_nombre = ttk.Entry(self.formulario)
        self._fila(0, 0, "Nombre o razón social *", self.entrada_nombre,
                   columnspan=3)
        self.combo_tipo_id = ttk.Combobox(self.formulario, state="readonly",
                                          width=16,
                                          values=[""] + TIPOS_IDENTIFICACION)
        self._fila(1, 0, "Tipo de identificación", self.combo_tipo_id)
        self.entrada_identificacion = ttk.Entry(self.formulario, width=20)
        self._fila(1, 2, "Identificación", self.entrada_identificacion)
        self.combo_tipo_implicado = ttk.Combobox(self.formulario,
                                                 state="readonly", width=20,
                                                 values=TIPOS_IMPLICADO)
        self._fila(2, 0, "Tipo de implicado *", self.combo_tipo_implicado)
        self.combo_lci = ttk.Combobox(self.formulario, state="readonly",
                                      width=8, values=VALORES_LCI)
        self.combo_lci.set("No")
        self._fila(2, 2, "LCI", self.combo_lci)
        ttk.Label(self.formulario,
                  text="LCI: Lista de Control Interno.",
                  foreground="#6B7280", font=("Helvetica", 8)).grid(
                      row=3, column=0, columnspan=4, sticky="w", pady=(4, 0))

        barra_form = ttk.Frame(marco)
        barra_form.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        self.btn_guardar = ttk.Button(barra_form, text="Añadir",
                                      command=self._guardar)
        self.btn_guardar.pack(side="left")
        self.btn_guardar.config(style="Accent.TButton")
        ttk.Button(barra_form, text="Nuevo",
                   command=self._nuevo).pack(side="left", padx=6)
        ttk.Button(barra_form, text="Cerrar",
                   command=self.destroy).pack(side="right")

        if not self.editable:
            for widget in (self.entrada_nombre, self.combo_tipo_id,
                           self.entrada_identificacion,
                           self.combo_tipo_implicado, self.combo_lci,
                           self.btn_guardar, self.btn_eliminar):
                widget.config(state="disabled")

        self._refrescar()
        self.entrada_nombre.focus_set()

    def _fila(self, fila, columna, etiqueta, widget, columnspan=1):
        ttk.Label(self.formulario, text=etiqueta).grid(
            row=fila, column=columna, sticky="w",
            padx=(0 if columna == 0 else 12, 6), pady=4)
        widget.grid(row=fila, column=columna + 1, columnspan=columnspan,
                    sticky="ew", pady=4)

    # ---- Datos --------------------------------------------------------------
    def _refrescar(self):
        seleccion = self.id_en_edicion
        self.tabla.delete(*self.tabla.get_children())
        implicados = oficios.listar_implicados(self.referencia)
        for implicado in implicados:
            self.tabla.insert("", "end", iid=str(implicado.get("id", "")),
                              values=(implicado.get("nombre", ""),
                                      implicado.get("tipo_identificacion", ""),
                                      implicado.get("identificacion", ""),
                                      implicado.get("tipo_implicado", ""),
                                      implicado.get("lci", "")))
        self.lbl_total.config(
            text=f"{len(implicados)} implicado(s) · la cantidad de "
                 f"investigados del oficio sigue a esta lista" if implicados
                 else "Sin implicados anotados")
        if seleccion is not None and self.tabla.exists(str(seleccion)):
            self.tabla.selection_set(str(seleccion))
        # La pestaña de oficios refleja el nuevo número de investigados.
        self.aplicacion._refrescar_listado()

    def _al_seleccionar(self, evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        id_implicado = int(seleccion[0])
        implicado = next((i for i in oficios.listar_implicados(self.referencia)
                          if int(i.get("id", 0)) == id_implicado), None)
        if implicado is None:
            return
        self.id_en_edicion = id_implicado
        self.formulario.config(text=" Modificar implicado ")
        self.btn_guardar.config(text="Guardar cambios")
        self.entrada_nombre.delete(0, "end")
        self.entrada_nombre.insert(0, implicado.get("nombre", ""))
        self.combo_tipo_id.set(implicado.get("tipo_identificacion", ""))
        self.entrada_identificacion.delete(0, "end")
        self.entrada_identificacion.insert(0, implicado.get("identificacion", ""))
        self.combo_tipo_implicado.set(implicado.get("tipo_implicado", ""))
        self.combo_lci.set(implicado.get("lci", "No"))

    def _nuevo(self):
        """Deja el formulario en blanco para añadir a otra persona."""
        self.id_en_edicion = None
        self.formulario.config(text=" Datos del implicado ")
        self.btn_guardar.config(text="Añadir")
        self.entrada_nombre.delete(0, "end")
        self.entrada_identificacion.delete(0, "end")
        self.combo_tipo_id.set("")
        self.combo_tipo_implicado.set("")
        self.combo_lci.set("No")
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())
        self.entrada_nombre.focus_set()

    def _guardar(self):
        datos = dict(nombre=self.entrada_nombre.get(),
                     tipo_identificacion=self.combo_tipo_id.get(),
                     identificacion=self.entrada_identificacion.get(),
                     tipo_implicado=self.combo_tipo_implicado.get(),
                     lci=self.combo_lci.get())
        try:
            if self.id_en_edicion is None:
                oficios.agregar_implicado(
                    self.referencia, self.usuario["usuario"],
                    self.usuario.get("rol"), **datos)
            else:
                oficios.actualizar_implicado(
                    self.referencia, self.id_en_edicion,
                    self.usuario["usuario"], self.usuario.get("rol"), **datos)
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        self._nuevo()
        self._refrescar()

    def _eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección",
                                   "Seleccione un implicado de la lista.",
                                   parent=self)
            return
        nombre = self.tabla.item(seleccion[0], "values")[0]
        if not messagebox.askyesno("Eliminar",
                                   f"¿Quitar a «{nombre}» de este oficio?",
                                   parent=self):
            return
        try:
            oficios.eliminar_implicado(self.referencia, int(seleccion[0]),
                                       self.usuario["usuario"],
                                       self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        self._nuevo()
        self._refrescar()


# ============================================================================
#  CARGA MASIVA DE OFICIOS
# ============================================================================
class DialogoCargaMasiva(tk.Toplevel):
    """Muestra qué se va a importar y, si se confirma, lo guarda.

    La carga no se hace a ciegas: primero se ve cuántos oficios entran, qué
    filas se descartan y por qué, y con qué responsables se han emparejado.
    """

    def __init__(self, aplicacion, usuario, resumen):
        super().__init__(aplicacion)
        self.aplicacion = aplicacion
        self.usuario = usuario
        self.resumen = resumen
        self.title("Carga masiva de oficios")
        self.configure(bg=COLOR_BLANCO)
        self.transient(aplicacion.winfo_toplevel())
        self.grab_set()
        self.minsize(720, 520)

        marco = tk.Frame(self, bg=COLOR_BLANCO, padx=18, pady=16)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(2, weight=1)

        filas = resumen["filas"]
        tk.Label(marco, text=f"Se importarán {len(filas)} oficios",
                 bg=COLOR_BLANCO, fg=COLOR_AZUL,
                 font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")

        avisos = self._texto_avisos(resumen)
        tk.Label(marco, text=avisos, bg=COLOR_BLANCO, fg="#6B7280",
                 font=("Helvetica", 8), justify="left", wraplength=680).grid(
                     row=1, column=0, sticky="w", pady=(4, 10))

        # Vista previa de lo que se va a guardar.
        contenedor = ttk.Frame(marco)
        contenedor.grid(row=2, column=0, sticky="nsew")
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(0, weight=1)
        columnas = ("institucion", "codigo", "accion", "oficio", "recepcion",
                    "asignacion", "respuesta", "investigados", "responsable",
                    "estado")
        titulos = ("Institución", "Referencia oficio", "Tipo de acción",
                   "Fecha de oficio", "Fecha de recepción",
                   "Fecha de asignación", "Fecha de respuesta",
                   "Investigados", "Responsable", "Estado")
        tabla = ttk.Treeview(contenedor, columns=columnas, show="headings",
                             height=12)
        for columna, titulo in zip(columnas, titulos):
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=110, minwidth=80, stretch=True)
        for fila in filas:
            tabla.insert("", "end", values=(
                fila.get("institucion", "") or "(no reconocida)",
                fila.get("codigo_oficio", ""),
                fila.get("tipo_accion", "") or "(no reconocido)",
                fila.get("fecha_oficio", ""), fila.get("fecha_recepcion", ""),
                fila.get("fecha_asignacion", ""), fila.get("fecha_respuesta", ""),
                fila.get("cantidad_investigados", ""),
                fila.get("empleado", "") or "(sin responsable)",
                fila.get("estado", "")))
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
        barra_h = ttk.Scrollbar(contenedor, orient="horizontal", command=tabla.xview)
        tabla.configure(yscrollcommand=barra.set, xscrollcommand=barra_h.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")

        botones = tk.Frame(marco, bg=COLOR_BLANCO)
        botones.grid(row=3, column=0, sticky="e", pady=(14, 0))
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="right")
        btn = ttk.Button(botones, text=f"Importar {len(filas)} oficios",
                         command=self._importar)
        btn.pack(side="right", padx=6)
        btn.config(style="Accent.TButton")

    def _texto_avisos(self, resumen):
        """Resume en pocas líneas lo que conviene saber antes de confirmar."""
        lineas = []
        if resumen["errores"]:
            lineas.append(
                f"{len(resumen['errores'])} filas se descartan por datos "
                f"incorrectos: {resumen['errores'][0]}"
                + (" …" if len(resumen["errores"]) > 1 else ""))
        if resumen["responsables_sin_identificar"]:
            nombres = ", ".join(resumen["responsables_sin_identificar"][:6])
            lineas.append(
                "No se encontró cuenta para estos nombres de la matriz: "
                f"{nombres}.")
        if resumen.get("responsables_ambiguos"):
            nombres = ", ".join(resumen["responsables_ambiguos"][:6])
            lineas.append(
                f"Estos nombres coinciden con más de una cuenta: {nombres}. No "
                "se asignan, para no atribuir el oficio a quien no fue.")
        cantidad = resumen.get("puestos_por_asignar") or 0
        if cantidad:
            lineas.append(
                f"{cantidad} oficio(s) entran como «Por asignar» por no tener "
                "responsable identificado; se les retira la fecha de respuesta "
                "hasta que un gestor los asigne.")
        if resumen.get("instituciones_desconocidas"):
            nombres = ", ".join(resumen["instituciones_desconocidas"][:6])
            lineas.append(
                f"Institución no reconocida en {nombres}. Esas filas no se "
                "pueden importar: la institución decide la nomenclatura de la "
                "Referencia UDC.")
        if resumen.get("tipos_accion_desconocidos"):
            nombres = ", ".join(resumen["tipos_accion_desconocidos"][:6])
            lineas.append(
                f"Tipo de acción no reconocido: {nombres}. Añádalos al "
                "catálogo de tipos de acción y vuelva a cargar el archivo.")
        no_validas = resumen.get("identificaciones_no_validas") or []
        if no_validas:
            muestra = ", ".join(no_validas[:5])
            lineas.append(
                f"{len(no_validas)} identificación(es) no cumplen su formato "
                f"(cédula de 10 dígitos, RUC de 13, pasaporte alfanumérico): "
                f"{muestra}. Esas personas entran sin identificación; puede "
                "completarla después en el detalle del oficio.")
        if resumen["columnas_ignoradas"]:
            lineas.append(
                "Columnas de la matriz sin equivalente en la aplicación (se "
                "ignoran): " + ", ".join(resumen["columnas_ignoradas"]) + ".")
        lineas.append(
            "Los oficios ya finalizados en la matriz se importan como tales, "
            "sin exigir la respuesta en PDF.")
        return "\n".join(lineas)

    def _importar(self):
        try:
            resultado = oficios.importar_oficios(
                self.resumen["filas"], self.usuario["usuario"],
                self.usuario.get("rol"))
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        detalle = [f"Oficios importados: {len(resultado['importados'])}"]
        if resultado["omitidos"]:
            detalle.append(
                f"Omitidos por estar ya registrados: {len(resultado['omitidos'])}")
        if resultado["fallidos"]:
            detalle.append(f"Descartados por datos incorrectos: "
                           f"{len(resultado['fallidos'])}")
            detalle.append("")
            detalle.extend(resultado["fallidos"][:10])
            if len(resultado["fallidos"]) > 10:
                detalle.append("…")
        messagebox.showinfo("Carga masiva", "\n".join(detalle), parent=self)
        self.destroy()


# ============================================================================
#  EXPORTACIÓN DE OFICIOS
# ============================================================================
class DialogoExportar(tk.Toplevel):
    """Exporta los oficios, con o sin acotarlos por fecha.

    Sin fechas se exporta **todo** lo que el usuario alcanza a ver. Si se
    indica solo "desde", esa fecha única; con las dos, el rango entre ambas.

    El archivo lleva una fila por implicado, con todos los datos del oficio
    repetidos a la izquierda (ver `almacen_oficios.filas_exportacion`).
    """

    def __init__(self, aplicacion, usuario):
        super().__init__(aplicacion)
        self.aplicacion = aplicacion
        self.usuario = usuario
        self.title("Exportar oficios")
        self.configure(bg=COLOR_BLANCO)
        self.resizable(False, False)
        self.transient(aplicacion.winfo_toplevel())
        self.grab_set()

        marco = tk.Frame(self, bg=COLOR_BLANCO, padx=18, pady=16)
        marco.pack(fill="both", expand=True)

        tk.Label(marco, text="Exportar oficios", bg=COLOR_BLANCO,
                 fg=COLOR_AZUL, font=("Helvetica", 12, "bold")).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        tk.Label(marco, text="Tipo de fecha", bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO).grid(row=1, column=0, sticky="w", pady=4)
        self._etiquetas = list(oficios.CAMPOS_FECHA.values())
        self.combo_campo = ttk.Combobox(marco, width=22, state="readonly",
                                        values=self._etiquetas)
        self.combo_campo.current(1)      # por defecto, fecha de recepción
        self.combo_campo.grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(marco, text="Desde", bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO).grid(row=2, column=0, sticky="w", pady=4)
        self.fecha_desde = SelectorFecha(marco, permitir_vacio=True)
        self.fecha_desde.grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(marco, text="Hasta", bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO).grid(row=3, column=0, sticky="w", pady=4)
        self.fecha_hasta = SelectorFecha(marco, permitir_vacio=True)
        self.fecha_hasta.grid(row=3, column=1, sticky="w", pady=4)

        tk.Label(marco,
                 text="Deje las dos fechas vacías para exportar todos los "
                      "oficios,\ny solo \"hasta\" vacía para exportar una fecha "
                      "única.",
                 bg=COLOR_BLANCO, fg="#6B7280", font=("Helvetica", 8),
                 justify="left").grid(row=4, column=1, sticky="w")

        tk.Label(marco, text="Formato", bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO).grid(row=5, column=0, sticky="w", pady=(10, 4))
        self._formatos = list(oficios.FORMATOS_EXPORTACION)
        self.combo_formato = ttk.Combobox(marco, width=22, state="readonly",
                                          values=self._formatos)
        self.combo_formato.current(0)      # por defecto, Excel
        self.combo_formato.grid(row=5, column=1, sticky="w", pady=(10, 4))
        if not oficios.hay_soporte_xlsx():
            # Sin openpyxl no se puede generar el .xlsx: se deja el CSV, que no
            # necesita ninguna librería externa.
            self.combo_formato.set("CSV (.csv)")

        barra = tk.Frame(marco, bg=COLOR_BLANCO)
        barra.grid(row=6, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(barra, text="Cancelar", command=self.destroy).pack(side="right")
        btn = ttk.Button(barra, text="Exportar", command=self._exportar)
        btn.pack(side="right", padx=6)
        btn.config(style="Accent.TButton")

    def _exportar(self):
        desde = self.fecha_desde.get()
        hasta = self.fecha_hasta.get()
        campo = self.aplicacion._clave_por_etiqueta(
            oficios.CAMPOS_FECHA, self.combo_campo.get())
        try:
            registros = oficios.listar_oficios_visibles(
                self.usuario["usuario"], self.usuario.get("rol"))
            # Sin fechas no se filtra: salen todos los oficios visibles.
            if desde or hasta:
                registros = oficios.filtrar_oficios(
                    registros, campo_fecha=campo, desde=desde, hasta=hasta)
        except ValueError as error:
            messagebox.showerror("Filtro no válido", str(error), parent=self)
            return
        if not registros:
            messagebox.showinfo(
                "Sin resultados",
                "No hay oficios que exportar con ese criterio." if (desde or hasta)
                else "Todavía no hay oficios registrados.", parent=self)
            return

        etiqueta_formato = self.combo_formato.get()
        extension = oficios.FORMATOS_EXPORTACION[etiqueta_formato]
        if not desde and not hasta:
            sufijo = "todos"
        elif not hasta:
            sufijo = desde
        else:
            sufijo = f"{desde or 'inicio'}_a_{hasta}"
        ruta = filedialog.asksaveasfilename(
            parent=self, title="Guardar la exportación",
            defaultextension=extension,
            initialfile=f"oficios_{sufijo}{extension}",
            filetypes=[(etiqueta_formato, f"*{extension}")])
        if not ruta:
            return
        try:
            cantidad = oficios.exportar_oficios(
                registros, ruta, extension, self.usuario["usuario"],
                (f"{self.combo_campo.get()} {desde or ''}"
                 + (f"..{hasta}" if hasta else "")) if (desde or hasta)
                else "todos los oficios")
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        messagebox.showinfo(
            "Exportado",
            f"Se exportaron {cantidad} oficios a:\n{ruta}", parent=self)
        self.destroy()


# ============================================================================
#  INGRESO / PRIMER USO (con colores corporativos)
# ============================================================================
class VentanaIngreso(tk.Frame):
    # Colores de apoyo para la pantalla de ingreso.
    COLOR_FONDO = COLOR_GRIS_CLARO
    COLOR_BORDE = "#E1E5EC"
    COLOR_CAMPO = "#F7F8FA"
    COLOR_BORDE_CAMPO = "#CBD2DE"
    COLOR_SUBTITULO = "#C7D2E6"
    COLOR_TENUE = "#6B7280"
    COLOR_AZUL_HOVER = "#1A2E5A"

    def __init__(self, maestro):
        # Heredamos de tk.Frame para poder usar bg
        tk.Frame.__init__(self, maestro, bg=self.COLOR_FONDO)
        self.maestro = maestro
        self.pack(fill="both", expand=True)

        maestro.title("Control de Oficios · Ingreso")
        # La ventana de ingreso comparte la ventana principal, así que conserva
        # su tamaño y sigue siendo redimensionable. La tarjeta se centra y no
        # se estira (ver `_construir_marco`).
        maestro.minsize(*TAMANO_MINIMO)
        maestro.resizable(True, True)

        # Ícono
        if ARCHIVO_ICONO.exists():
            try:
                maestro.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        self._configurar_estilos()

        if autenticacion.existe_algun_usuario():
            self._formulario_ingreso()
        else:
            self._formulario_primer_uso()

    def _configurar_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Login.TLabel", background=COLOR_BLANCO, foreground=COLOR_TEXTO)
        # Campos de texto con borde suave que se resalta al enfocar.
        estilo.configure(
            "Login.TEntry", fieldbackground=self.COLOR_CAMPO,
            foreground=COLOR_TEXTO, bordercolor=self.COLOR_BORDE_CAMPO,
            lightcolor=self.COLOR_BORDE_CAMPO, darkcolor=self.COLOR_BORDE_CAMPO,
            relief="flat", padding=6)
        estilo.map(
            "Login.TEntry",
            bordercolor=[("focus", COLOR_AZUL)],
            lightcolor=[("focus", COLOR_AZUL)],
            darkcolor=[("focus", COLOR_AZUL)],
            fieldbackground=[("focus", COLOR_BLANCO)])

    def _limpiar(self):
        for hijo in self.winfo_children():
            hijo.destroy()

    # ---- Componentes reutilizables -----------------------------------------
    def _construir_marco(self):
        """Crea el banner corporativo y la tarjeta central. Devuelve el
        contenedor interno (con fondo blanco) donde va cada formulario."""
        self._limpiar()

        # Banner superior con identidad corporativa.
        banner = tk.Frame(self, bg=COLOR_AZUL, height=150)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        # Fila con el ícono a la izquierda del texto "Banco del Pacífico".
        fila = tk.Frame(banner, bg=COLOR_AZUL)
        fila.pack(pady=(26, 0))
        logo_img = self._cargar_logo(46)
        if logo_img:
            lbl_logo = tk.Label(fila, image=logo_img, bg=COLOR_AZUL)
            lbl_logo.image = logo_img
            lbl_logo.pack(side="left", padx=(0, 10))
        tk.Label(fila, text="Banco del Pacífico", bg=COLOR_AZUL, fg=COLOR_BLANCO,
                 font=("Arial", 16, "bold")).pack(side="left")

        # Subtítulo y sub-subtítulo.
        tk.Label(banner, text="Unidad de Cumplimiento", bg=COLOR_AZUL,
                 fg=self.COLOR_SUBTITULO, font=("Helvetica", 10, "bold")
                 ).pack(pady=(8, 0))
        tk.Label(banner, text="Uso Interno", bg=COLOR_AZUL,
                 fg=self.COLOR_SUBTITULO, font=("Helvetica", 8)).pack(pady=(1, 0))

        # Cuerpo con la tarjeta centrada y de ancho acotado. Las columnas de los
        # lados absorben el espacio sobrante, así que al maximizar la ventana la
        # tarjeta no se estira: se queda centrada y con un ancho cómodo de leer.
        cuerpo = tk.Frame(self, bg=self.COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=1, uniform="lados")
        cuerpo.columnconfigure(1, weight=0, minsize=ANCHO_TARJETA_INGRESO)
        cuerpo.columnconfigure(2, weight=1, uniform="lados")
        cuerpo.rowconfigure(0, weight=1)

        tarjeta = tk.Frame(cuerpo, bg=COLOR_BLANCO,
                           highlightbackground=self.COLOR_BORDE,
                           highlightthickness=1)
        # "ew": ocupa el ancho de su columna y se ajusta a su contenido a lo
        # alto, quedando centrada verticalmente en vez de estirarse hasta el
        # borde inferior de la pantalla.
        tarjeta.grid(row=0, column=1, sticky="ew", pady=28)

        interno = tk.Frame(tarjeta, bg=COLOR_BLANCO)
        interno.pack(fill="both", expand=True, padx=30, pady=26)
        return interno

    def _cargar_logo(self, alto):
        if not (ARCHIVO_LOGO.exists() and PILLOW_AVAILABLE):
            return None
        try:
            img = Image.open(ARCHIVO_LOGO)
            ancho = int(img.size[0] * (alto / float(img.size[1])))
            img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _etiqueta_campo(self, contenedor, texto):
        tk.Label(contenedor, text=texto, bg=COLOR_BLANCO, fg=COLOR_TEXTO,
                 font=("Helvetica", 9, "bold")).pack(anchor="w")

    def _campo(self, contenedor, oculto=False):
        entrada = ttk.Entry(contenedor, style="Login.TEntry",
                            font=("Helvetica", 11), show="•" if oculto else "")
        entrada.pack(fill="x", ipady=4, pady=(4, 14))
        return entrada

    def _boton_principal(self, contenedor, texto, comando):
        btn = tk.Button(contenedor, text=texto, command=comando,
                        bg=COLOR_AZUL, fg=COLOR_BLANCO,
                        activebackground=self.COLOR_AZUL_HOVER,
                        activeforeground=COLOR_BLANCO,
                        font=("Helvetica", 11, "bold"), relief="flat",
                        cursor="hand2", pady=9)
        btn.pack(fill="x", pady=(8, 0))
        btn.bind("<Enter>", lambda e: btn.config(bg=self.COLOR_AZUL_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_AZUL))
        return btn

    def _casilla_mostrar_clave(self, contenedor):
        self.var_mostrar = tk.BooleanVar(value=False)

        def alternar():
            self.entrada_clave.config(show="" if self.var_mostrar.get() else "•")

        tk.Checkbutton(
            contenedor, text="Mostrar contraseña", variable=self.var_mostrar,
            command=alternar, bg=COLOR_BLANCO, fg=self.COLOR_TENUE,
            activebackground=COLOR_BLANCO, activeforeground=self.COLOR_TENUE,
            selectcolor=COLOR_BLANCO, font=("Helvetica", 9),
            cursor="hand2", bd=0, highlightthickness=0
        ).pack(anchor="w", pady=(0, 16))

    # ---- Formularios --------------------------------------------------------
    def _formulario_ingreso(self):
        cont = self._construir_marco()

        tk.Label(cont, text="Iniciar sesión", bg=COLOR_BLANCO, fg=COLOR_TEXTO,
                 font=("Helvetica", 17, "bold")).pack(anchor="w")
        tk.Label(cont, text="Ingrese sus credenciales para continuar",
                 bg=COLOR_BLANCO, fg=self.COLOR_TENUE,
                 font=("Helvetica", 9)).pack(anchor="w", pady=(2, 20))

        self._etiqueta_campo(cont, "Usuario")
        self.entrada_usuario = self._campo(cont)
        self._etiqueta_campo(cont, "Contraseña")
        self.entrada_clave = self._campo(cont, oculto=True)
        self.entrada_clave.bind("<Return>", lambda evento: self._ingresar())
        self.entrada_usuario.bind("<Return>", lambda evento: self.entrada_clave.focus_set())

        self._casilla_mostrar_clave(cont)
        self._boton_principal(cont, "Ingresar", self._ingresar)
        self.entrada_usuario.focus_set()

    def _ingresar(self):
        try:
            sesion = autenticacion.validar_acceso(self.entrada_usuario.get(), self.entrada_clave.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        if not sesion:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            return
        self.destroy()
        AplicacionPrincipal(self.maestro, sesion)

    def _formulario_primer_uso(self):
        cont = self._construir_marco()

        tk.Label(cont, text="Primer uso", bg=COLOR_BLANCO, fg=COLOR_TEXTO,
                 font=("Helvetica", 17, "bold")).pack(anchor="w")
        tk.Label(cont, text="Cree la cuenta de superusuario para comenzar",
                 bg=COLOR_BLANCO, fg=self.COLOR_TENUE,
                 font=("Helvetica", 9)).pack(anchor="w", pady=(2, 18))

        self._etiqueta_campo(cont, "Usuario")
        self.entrada_usuario = self._campo(cont)
        self._etiqueta_campo(cont, "Nombre")
        self.entrada_nombre = self._campo(cont)
        self._etiqueta_campo(cont, "Contraseña")
        self.entrada_clave = self._campo(cont, oculto=True)
        self.entrada_clave.bind("<Return>", lambda evento: self._crear_administrador())

        self._casilla_mostrar_clave(cont)
        self._boton_principal(cont, "Crear y continuar", self._crear_administrador)
        self.entrada_usuario.focus_set()

    def _crear_administrador(self):
        try:
            # El primer usuario del sistema se crea como superusuario.
            autenticacion.crear_usuario(self.entrada_usuario.get(),
                                        self.entrada_nombre.get(),
                                        self.entrada_clave.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "Superusuario creado. Inicie sesión.")
        self._formulario_ingreso()


def iniciar():
    raiz = tk.Tk()
    # Si la carpeta de datos no está accesible (unidad de red caída o ruta mal
    # indicada en datos.ruta), se avisa con un mensaje claro en vez de dejar
    # que la aplicación falle con un error técnico.
    if configuracion.ERROR_DATOS:
        raiz.withdraw()
        messagebox.showerror("No se puede acceder a los datos",
                             configuracion.ERROR_DATOS)
        raiz.destroy()
        return
    # La aplicación abre maximizada, pero la ventana queda redimensionable: el
    # botón de maximizar/restaurar sigue operativo y cada persona la deja como
    # prefiera. Solo se maximiza aquí, al arrancar; después de ingresar o de
    # cerrar sesión se respeta el tamaño que tenga en ese momento.
    raiz.minsize(*TAMANO_MINIMO)
    raiz.resizable(True, True)
    maximizar_ventana(raiz)
    VentanaIngreso(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar()



