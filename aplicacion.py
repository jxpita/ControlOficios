import calendar
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime

import autenticacion
import almacen_oficios as oficios
import visor_pdf
import metricas
from configuracion import (
    ESTADOS, ARCHIVO_LOGO, ARCHIVO_ICONO,
    ROL_SUPERUSUARIO, ROL_ADMINISTRADOR, ROL_USUARIO,
    ROLES_ASIGNABLES, ROLES_GESTORES,
    COLOR_AZUL, COLOR_BLANCO, COLOR_GRIS_CLARO, COLOR_TEXTO, COLOR_TEXTO_INV
)

try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


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
        maestro.geometry("1060x720")
        maestro.minsize(940, 620)
        maestro.resizable(True, True)
        if ARCHIVO_ICONO.exists():
            try:
                maestro.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        # --- Estilos personalizados ---
        self._configurar_estilos()

        # --- Marco superior con logo ---
        self._crear_cabecera()

        # --- Cuaderno de pestañas ---
        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, pady=(10, 0))

        self.pestana_registro = ttk.Frame(self.cuaderno, padding=15)
        self.pestana_listado = ttk.Frame(self.cuaderno, padding=10)
        self.pestana_usuarios = ttk.Frame(self.cuaderno, padding=15)
        self.pestana_tablero = ttk.Frame(self.cuaderno, padding=15)

        self.cuaderno.add(self.pestana_registro, text="  Registrar oficio  ")
        self.cuaderno.add(self.pestana_listado, text="  Oficios  ")
        # La pestaña de usuarios solo está disponible para gestores.
        if self._puede_gestionar_usuarios():
            self.cuaderno.add(self.pestana_usuarios, text="  Usuarios  ")
        self.cuaderno.add(self.pestana_tablero, text="  Tablero  ")

        self._construir_registro()
        self._construir_listado()
        if self._puede_gestionar_usuarios():
            self._construir_usuarios()
        self._construir_tablero()

        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)

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
        estilo.configure("Treeview.Heading", background=COLOR_AZUL, foreground=COLOR_BLANCO, font=("Helvetica", 10, "bold"))
        estilo.map("Treeview.Heading", background=[("active", "#1A2E5A")])
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

        # Botón de cerrar sesión (extremo derecho).
        btn_salir = tk.Button(cabecera, text="Cerrar sesión", command=self._cerrar_sesion,
                              bg=COLOR_AZUL, fg=COLOR_BLANCO, relief="flat", cursor="hand2",
                              activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                              font=("Helvetica", 10, "bold"), padx=12, pady=6,
                              highlightbackground=COLOR_BLANCO, highlightthickness=1,
                              takefocus=0)
        btn_salir.pack(side="right", padx=15, pady=10)
        btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg="#1A2E5A"))
        btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg=COLOR_AZUL))

        # Título de la aplicación
        lbl_app = tk.Label(cabecera, text="Control de Oficios — Unidad de Cumplimiento",
                           font=("Arial", 14), fg=COLOR_BLANCO, bg=COLOR_AZUL)
        lbl_app.pack(side="right", padx=20, pady=10)

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
        return [self._display_responsable(u["usuario"], u["nombre"])
                for u in self._usuarios_sistema()]

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

    def _oficio_por_referencia(self, referencia):
        """Busca solo entre los oficios visibles para el usuario en sesión."""
        for registro in oficios.listar_oficios_visibles(
                self.usuario["usuario"], self.usuario.get("rol")):
            if registro["referencia"] == referencia:
                return registro
        return None

    def _puede_gestionar_usuarios(self):
        """True si el usuario en sesión puede crear/editar/eliminar usuarios
        y reasignar/cambiar libremente el estado de los oficios (gestor)."""
        return self.usuario.get("rol") in ROLES_GESTORES

    def _construir_registro(self):
        marco = self.pestana_registro
        # Aplicar fondo blanco a todos los hijos
        for child in marco.winfo_children():
            child.configure(background=COLOR_BLANCO) if isinstance(child, tk.Widget) else None

        ttk.Label(marco, text="Registrar nuevo oficio",
                  font=("Helvetica", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Los campos obligatorios se marcan con un asterisco (*).
        ttk.Label(marco, text="Código de oficio o circular *").grid(row=1, column=0, sticky="w", pady=4)
        self.entrada_codigo = ttk.Entry(marco, width=40)
        self.entrada_codigo.grid(row=1, column=1, sticky="w", pady=4)

        # Orden de fechas: oficio -> recepción -> respuesta.
        ttk.Label(marco, text="Fecha de oficio *").grid(row=2, column=0, sticky="w", pady=4)
        self.entrada_fecha_oficio = SelectorFecha(marco)
        self.entrada_fecha_oficio.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Fecha de recepción *").grid(row=3, column=0, sticky="w", pady=4)
        self.entrada_fecha_recepcion = SelectorFecha(marco)
        self.entrada_fecha_recepcion.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Fecha de respuesta").grid(row=4, column=0, sticky="w", pady=4)
        self.entrada_fecha_respuesta = SelectorFecha(marco, permitir_vacio=True)
        self.entrada_fecha_respuesta.grid(row=4, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Usuario responsable").grid(row=5, column=0, sticky="w", pady=4)
        self.combo_empleado = ttk.Combobox(
            marco, width=37, state="readonly",
            values=[self.SIN_RESPONSABLE] + self._valores_responsables())
        self.combo_empleado.current(0)  # por defecto: sin responsable
        self.combo_empleado.grid(row=5, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Estado *").grid(row=6, column=0, sticky="w", pady=4)
        self.combo_estado = ttk.Combobox(marco, width=25, state="readonly", values=ESTADOS)
        self.combo_estado.current(0)
        self.combo_estado.grid(row=6, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Observación").grid(row=7, column=0, sticky="nw", pady=4)
        self.texto_observacion = tk.Text(marco, width=44, height=4, wrap="word",
                                         font=("Helvetica", 10),
                                         highlightthickness=1, highlightbackground="#CBD2DE",
                                         relief="flat")
        self.texto_observacion.grid(row=7, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="* Campos obligatorios", foreground="#6B7280",
                  font=("Helvetica", 8)).grid(row=8, column=1, sticky="w")

        btn = ttk.Button(marco, text="Registrar oficio", command=self._guardar_oficio)
        btn.grid(row=9, column=1, sticky="w", pady=14)
        # Estilo especial para el botón principal
        estilo = ttk.Style()
        estilo.configure("Accent.TButton", background=COLOR_AZUL, foreground=COLOR_BLANCO, font=("Helvetica", 10, "bold"))
        btn.config(style="Accent.TButton")

    def _guardar_oficio(self):
        # El responsable, la fecha de respuesta y la observación son opcionales.
        id_empleado, nombre_empleado = self._responsable_por_display(self.combo_empleado.get())
        try:
            referencia = oficios.registrar_oficio(
                self.entrada_codigo.get(), self.entrada_fecha_recepcion.get(),
                self.entrada_fecha_oficio.get(), id_empleado,
                nombre_empleado, self.combo_estado.get(),
                self.usuario["usuario"],
                self.entrada_fecha_respuesta.get(),
                self.texto_observacion.get("1.0", "end"),
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Registrado", f"Oficio registrado.\nReferencia: {referencia}")
        self.entrada_codigo.delete(0, "end")
        self.entrada_fecha_respuesta.set("")
        self.texto_observacion.delete("1.0", "end")
        self.combo_empleado.current(0)
        self.combo_estado.current(0)
        self._refrescar_listado()

    def _construir_listado(self):
        marco = self.pestana_listado
        es_gestor = self._puede_gestionar_usuarios()

        # --- Tabla de oficios (orden: oficio -> recepción -> respuesta) ------
        columnas = ("referencia", "codigo", "oficio", "recepcion", "respuesta",
                    "empleado", "estado", "pdf", "observacion")
        titulos = ("Referencia", "Código oficio", "F. oficio", "F. recepción",
                   "F. respuesta", "Responsable", "Estado", "PDF", "Observación")
        anchos = (145, 110, 85, 90, 90, 150, 85, 40, 180)
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True, side="top")
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=8)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor="w", stretch=False)
        self.tabla.column("observacion", stretch=True)
        barra_v = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        barra_h = ttk.Scrollbar(contenedor, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
        barra_v.pack(side="right", fill="y")
        barra_h.pack(side="bottom", fill="x")
        self.tabla.pack(fill="both", expand=True, side="left")

        # --- Panel de edición del oficio seleccionado ------------------------
        # Disposición en una sola fila de campos + observación, para que la
        # pestaña no quede saturada y el calendario tenga espacio.
        panel = ttk.LabelFrame(marco, text=" Modificar oficio seleccionado ", padding=8)
        panel.pack(fill="x", pady=(6, 0))

        fila = ttk.Frame(panel)
        fila.pack(fill="x")

        ttk.Label(fila, text="F. respuesta").pack(side="left")
        self.edicion_fecha_respuesta = SelectorFecha(fila, permitir_vacio=True)
        self.edicion_fecha_respuesta.pack(side="left", padx=(6, 16))

        if es_gestor:
            # Solo administrador / superusuario pueden reasignar responsable.
            ttk.Label(fila, text="Responsable").pack(side="left")
            self.combo_responsable_edicion = ttk.Combobox(
                fila, width=24, state="readonly",
                values=[self.SIN_RESPONSABLE] + self._valores_responsables())
            self.combo_responsable_edicion.current(0)
            self.combo_responsable_edicion.pack(side="left", padx=(6, 16))
            estados_disponibles = ESTADOS
        else:
            # El usuario solo alterna entre En proceso y Finalizado.
            estados_disponibles = ["En proceso", "Finalizado"]

        ttk.Label(fila, text="Estado").pack(side="left")
        self.combo_nuevo_estado = ttk.Combobox(fila, width=13, state="readonly",
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
        barra.pack(fill="x", pady=(8, 0))
        btn_guardar = ttk.Button(barra, text="Guardar cambios", command=self._aplicar_cambios)
        btn_guardar.pack(side="left")
        btn_guardar.config(style="Accent.TButton")
        ttk.Button(barra, text="Adjuntar respuesta (PDF)",
                   command=self._adjuntar_respuesta).pack(side="left", padx=6)
        ttk.Button(barra, text="Ver respuesta (PDF)",
                   command=self._ver_respuesta).pack(side="left")
        ttk.Button(barra, text="Eliminar PDF",
                   command=self._eliminar_respuesta).pack(side="left", padx=6)

        # Al seleccionar un oficio, precargar sus valores actuales.
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_oficio)
        self._refrescar_listado()

    def _refrescar_listado(self):
        if not hasattr(self, "tabla"):
            return
        seleccion_previa = self.tabla.selection()
        self.tabla.delete(*self.tabla.get_children())
        try:
            # Un usuario regular solo ve sus oficios (registrados o asignados).
            for registro in oficios.listar_oficios_visibles(
                    self.usuario["usuario"], self.usuario.get("rol")):
                observacion = " ".join(registro.get("observacion", "").split())
                if len(observacion) > 60:
                    observacion = observacion[:57] + "..."
                self.tabla.insert("", "end", iid=registro["referencia"], values=(
                    registro["referencia"], registro["codigo_oficio"],
                    registro["fecha_oficio"], registro["fecha_recepcion"],
                    registro.get("fecha_respuesta", ""),
                    registro.get("empleado", ""), registro["estado"],
                    "Sí" if registro.get("archivo_respuesta") else "",
                    observacion))
        except Exception as e:
            messagebox.showerror("Error al cargar oficios", str(e))
            return
        # Conservar la selección tras refrescar, si el oficio sigue existiendo.
        for referencia in seleccion_previa:
            if self.tabla.exists(referencia):
                self.tabla.selection_set(referencia)

    def _al_seleccionar_oficio(self, evento=None):
        """Precarga el panel de edición con los datos del oficio seleccionado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        registro = self._oficio_por_referencia(seleccion[0])
        if registro is None:
            return
        self.edicion_fecha_respuesta.set(registro.get("fecha_respuesta", ""))
        self.edicion_observacion.delete("1.0", "end")
        self.edicion_observacion.insert("1.0", registro.get("observacion", ""))

        if self._puede_gestionar_usuarios():
            display = self._display_responsable(
                registro.get("id_empleado", ""), registro.get("empleado", ""))
            if display and display in self._valores_responsables():
                self.combo_responsable_edicion.set(display)
            else:
                self.combo_responsable_edicion.set(self.SIN_RESPONSABLE)
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
                    self.usuario.get("rol"), fecha_respuesta, observacion)
            else:
                estado_final = oficios.actualizar_estado_asignado(
                    seleccion[0], self.usuario["usuario"],
                    self.combo_nuevo_estado.get(), fecha_respuesta, observacion)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        # Si las reglas ajustaron el estado (p. ej. al asignar responsable),
        # reflejarlo en el desplegable.
        if estado_final in self.combo_nuevo_estado.cget("values"):
            self.combo_nuevo_estado.set(estado_final)
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
                "Podrá volver a adjuntar el archivo correcto."):
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
        if visor_pdf.abrir_visor(self, ruta, f"Respuesta · {seleccion[0]}"):
            return
        # Sin PyMuPDF instalado: ofrecer el lector del sistema.
        if messagebox.askyesno(
                "Visor no disponible",
                "Para ver el PDF dentro de la aplicación instale PyMuPDF:\n\n"
                "    pip install pymupdf\n\n"
                "¿Desea abrirlo con el lector de PDF del sistema?"):
            if not visor_pdf.abrir_con_sistema(ruta):
                messagebox.showerror("Error", "No se pudo abrir el PDF.")

    def _construir_usuarios(self):
        marco = self.pestana_usuarios
        # Usuario que se está editando (None = se está creando uno nuevo).
        self._usuario_en_edicion = None

        self.lbl_form_usuario = ttk.Label(
            marco, text="Crear usuario del sistema", font=("Helvetica", 13, "bold"))
        self.lbl_form_usuario.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        ttk.Label(marco, text="Usuario").grid(row=1, column=0, sticky="w", pady=4)
        self.entrada_usuario = ttk.Entry(marco, width=30)
        self.entrada_usuario.grid(row=1, column=1, sticky="w")
        ttk.Label(marco, text="Nombre").grid(row=2, column=0, sticky="w", pady=4)
        self.entrada_nombre = ttk.Entry(marco, width=30)
        self.entrada_nombre.grid(row=2, column=1, sticky="w")
        ttk.Label(marco, text="Rol").grid(row=3, column=0, sticky="w", pady=4)
        self.combo_rol = ttk.Combobox(marco, width=27, state="readonly", values=ROLES_ASIGNABLES)
        self.combo_rol.current(0)
        self.combo_rol.grid(row=3, column=1, sticky="w")
        ttk.Label(marco, text="Contraseña").grid(row=4, column=0, sticky="w", pady=4)
        self.entrada_clave = ttk.Entry(marco, width=30, show="•")
        self.entrada_clave.grid(row=4, column=1, sticky="w")
        ttk.Label(marco, text="Confirmar contraseña").grid(row=5, column=0, sticky="w", pady=4)
        self.entrada_clave2 = ttk.Entry(marco, width=30, show="•")
        self.entrada_clave2.grid(row=5, column=1, sticky="w")
        self.lbl_ayuda_clave = ttk.Label(marco, text="", foreground="#6B7280", font=("Helvetica", 8))
        self.lbl_ayuda_clave.grid(row=6, column=1, sticky="w")

        barra_form = ttk.Frame(marco)
        barra_form.grid(row=7, column=1, sticky="w", pady=12)
        self.btn_guardar_usuario = ttk.Button(barra_form, text="Crear usuario",
                                               command=self._guardar_usuario)
        self.btn_guardar_usuario.pack(side="left")
        self.btn_guardar_usuario.config(style="Accent.TButton")
        ttk.Button(barra_form, text="Nuevo",
                   command=self._nuevo_usuario).pack(side="left", padx=6)

        ttk.Label(marco, text="Usuarios existentes:").grid(row=8, column=0, sticky="w", pady=(6, 0))
        self.tabla_usuarios = ttk.Treeview(
            marco, columns=("usuario", "nombre", "rol"), show="headings", height=8)
        self.tabla_usuarios.heading("usuario", text="Usuario")
        self.tabla_usuarios.heading("nombre", text="Nombre")
        self.tabla_usuarios.heading("rol", text="Rol")
        self.tabla_usuarios.column("usuario", width=130)
        self.tabla_usuarios.column("nombre", width=220)
        self.tabla_usuarios.column("rol", width=120)
        self.tabla_usuarios.grid(row=9, column=0, columnspan=2, sticky="w", pady=6)
        self.tabla_usuarios.bind("<<TreeviewSelect>>", self._al_seleccionar_usuario)

        barra_tabla = ttk.Frame(marco)
        barra_tabla.grid(row=10, column=0, columnspan=2, sticky="w")
        ttk.Button(barra_tabla, text="Editar seleccionado",
                   command=self._editar_usuario_seleccionado).pack(side="left")
        ttk.Button(barra_tabla, text="Restablecer contraseña",
                   command=self._restablecer_clave_seleccionado).pack(side="left", padx=6)
        ttk.Button(barra_tabla, text="Eliminar seleccionado",
                   command=self._eliminar_usuario_seleccionado).pack(side="left", padx=6)

        self._nuevo_usuario()
        self._refrescar_usuarios()

    def _nuevo_usuario(self):
        """Restablece el formulario para crear un usuario nuevo."""
        self._usuario_en_edicion = None
        self.lbl_form_usuario.config(text="Crear usuario del sistema")
        self.btn_guardar_usuario.config(text="Crear usuario")
        self.lbl_ayuda_clave.config(text="")
        for entrada in (self.entrada_usuario, self.entrada_nombre,
                        self.entrada_clave, self.entrada_clave2):
            entrada.delete(0, "end")
        self.entrada_usuario.config(state="normal")
        self.combo_rol.config(state="readonly", values=ROLES_ASIGNABLES)
        self.combo_rol.current(0)
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

        if rol == ROL_SUPERUSUARIO:
            # El rol del superusuario no puede cambiarse.
            self.combo_rol.config(state="readonly", values=[ROL_SUPERUSUARIO])
            self.combo_rol.set(ROL_SUPERUSUARIO)
            self.combo_rol.config(state="disabled")
        else:
            self.combo_rol.config(state="readonly", values=ROLES_ASIGNABLES)
            self.combo_rol.set(rol if rol in ROLES_ASIGNABLES else ROL_USUARIO)

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
                    self.entrada_clave.get(), self.combo_rol.get(), actor)
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
        if rol == ROL_SUPERUSUARIO:
            messagebox.showerror("No permitido", "El superusuario no puede eliminarse.")
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
        """El gestor selecciona un usuario y le cede el teclado para que escriba
        su nueva contraseña (recuperación de contraseña)."""
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un usuario de la lista.")
            return
        usuario, nombre, _ = self.tabla_usuarios.item(seleccion[0], "values")
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
        tk.Label(cont, text="Cédale el teclado al usuario para que la escriba.",
                 bg=COLOR_BLANCO, fg="#6B7280", font=("Helvetica", 8)).pack(anchor="w", pady=(0, 10))

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

    # ---- Tablero (dashboard) -----------------------------------------------
    # Paleta de los estados, reutilizada en tarjetas y gráficos.
    COLOR_POR_ASIGNAR = "#b45309"
    COLOR_EN_PROCESO = "#1d4ed8"
    COLOR_FINALIZADO = "#15803d"

    def _construir_tablero(self):
        """Tablero con scroll vertical: tarjetas de indicadores y gráficos."""
        marco = self.pestana_tablero

        # Lienzo desplazable que contiene todo el tablero.
        self.tablero_lienzo = tk.Canvas(marco, background=COLOR_BLANCO,
                                        highlightthickness=0)
        barra = ttk.Scrollbar(marco, orient="vertical",
                              command=self.tablero_lienzo.yview)
        self.tablero_lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.tablero_lienzo.pack(side="left", fill="both", expand=True)

        self.tablero = ttk.Frame(self.tablero_lienzo)
        self._id_tablero = self.tablero_lienzo.create_window(
            (0, 0), window=self.tablero, anchor="nw")

        def al_redimensionar_contenido(evento):
            self.tablero_lienzo.configure(
                scrollregion=self.tablero_lienzo.bbox("all"))

        def al_redimensionar_lienzo(evento):
            # El contenido ocupa siempre todo el ancho disponible.
            self.tablero_lienzo.itemconfigure(self._id_tablero, width=evento.width)

        self.tablero.bind("<Configure>", al_redimensionar_contenido)
        self.tablero_lienzo.bind("<Configure>", al_redimensionar_lienzo)
        self.tablero_lienzo.bind("<Enter>", lambda e: self._activar_rueda(True))
        self.tablero_lienzo.bind("<Leave>", lambda e: self._activar_rueda(False))

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

    def _activar_rueda(self, activar):
        """Activa la rueda del ratón solo mientras el cursor está en el tablero."""
        if activar:
            self.tablero_lienzo.bind_all(
                "<MouseWheel>",
                lambda e: self.tablero_lienzo.yview_scroll(int(-e.delta / 120), "units"))
            self.tablero_lienzo.bind_all(
                "<Button-4>", lambda e: self.tablero_lienzo.yview_scroll(-1, "units"))
            self.tablero_lienzo.bind_all(
                "<Button-5>", lambda e: self.tablero_lienzo.yview_scroll(1, "units"))
        else:
            for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                try:
                    self.tablero_lienzo.unbind_all(evento)
                except tk.TclError:
                    pass

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

    def _dibujar_barras(self, serie):
        """Barras verticales: oficios recibidos por día."""
        lienzo = self.lienzo
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho_lienzo = lienzo.winfo_width() or 800
        alto_lienzo = 210
        margen_izq, margen_inf, margen_sup = 30, 30, 26
        valor_max = max([valor for _, valor in serie] + [1])
        cantidad = len(serie)
        ancho_barra = (ancho_lienzo - margen_izq - 10) / cantidad
        lienzo.create_text(margen_izq, 12, text="Oficios recibidos por día (14 días)",
                           anchor="w", font=("Helvetica", 9, "bold"), fill=COLOR_TEXTO)
        for indice, (dia, valor) in enumerate(serie):
            x0 = margen_izq + indice * ancho_barra + 4
            x1 = x0 + ancho_barra - 8
            altura = (alto_lienzo - margen_inf - margen_sup) * (valor / valor_max)
            y1 = alto_lienzo - margen_inf
            y0 = y1 - altura
            lienzo.create_rectangle(x0, y0, x1, y1, fill=COLOR_AZUL, outline="")
            if valor:
                lienzo.create_text((x0 + x1) / 2, y0 - 8, text=str(valor),
                                   font=("Helvetica", 8))
            lienzo.create_text((x0 + x1) / 2, y1 + 12, text=dia[5:],
                               font=("Helvetica", 7))

    def _dibujar_barras_meses(self, serie):
        """Barras verticales: oficios recibidos por mes."""
        lienzo = self.lienzo_meses
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho_lienzo = lienzo.winfo_width() or 800
        alto_lienzo = 210
        margen_izq, margen_inf, margen_sup = 30, 30, 26
        valor_max = max([valor for _, valor in serie] + [1])
        ancho_barra = (ancho_lienzo - margen_izq - 10) / max(len(serie), 1)
        lienzo.create_text(margen_izq, 12, text="Oficios recibidos por mes (6 meses)",
                           anchor="w", font=("Helvetica", 9, "bold"), fill=COLOR_TEXTO)
        for indice, (mes, valor) in enumerate(serie):
            x0 = margen_izq + indice * ancho_barra + 12
            x1 = x0 + ancho_barra - 24
            altura = (alto_lienzo - margen_inf - margen_sup) * (valor / valor_max)
            y1 = alto_lienzo - margen_inf
            y0 = y1 - altura
            lienzo.create_rectangle(x0, y0, x1, y1, fill="#7c3aed", outline="")
            lienzo.create_text((x0 + x1) / 2, y0 - 8, text=str(valor),
                               font=("Helvetica", 8))
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
        elif actual is self.pestana_listado:
            self._refrescar_responsables()
            self._refrescar_listado()
        elif actual is self.pestana_tablero:
            self._refrescar_tablero()


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
        self._centrar(440, 600)
        try:
            maestro.resizable(False, False)
        except tk.TclError:
            pass

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

    def _centrar(self, ancho, alto):
        """Centra la ventana en la pantalla."""
        self.maestro.update_idletasks()
        x = (self.maestro.winfo_screenwidth() - ancho) // 2
        y = (self.maestro.winfo_screenheight() - alto) // 3
        self.maestro.geometry(f"{ancho}x{alto}+{x}+{max(y, 0)}")

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

        # Cuerpo con tarjeta.
        cuerpo = tk.Frame(self, bg=self.COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True)
        tarjeta = tk.Frame(cuerpo, bg=COLOR_BLANCO,
                           highlightbackground=self.COLOR_BORDE,
                           highlightthickness=1)
        tarjeta.pack(fill="both", expand=True, padx=34, pady=28)

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
    VentanaIngreso(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar()



