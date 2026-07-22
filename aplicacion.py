import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import autenticacion
import almacen_empleados
import almacen_oficios as oficios
import metricas
from configuracion import (
    ESTADOS, ARCHIVO_LOGO, ARCHIVO_ICONO,
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

    def __init__(self, maestro, fecha_inicial=None):
        super().__init__(maestro, background=COLOR_BLANCO)
        self.entrada = ttk.Entry(self, width=14)
        self.entrada.pack(side="left")
        self.boton = tk.Button(self, text="📅", command=self._alternar_calendario,
                               relief="flat", cursor="hand2", bg=COLOR_GRIS_CLARO,
                               activebackground="#DDE3EC", padx=6, takefocus=0)
        self.boton.pack(side="left", padx=(4, 0))
        self._popup = None
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
        self._anio, self._mes = base.year, base.month

        self._popup = tk.Toplevel(self)
        self._popup.title("Seleccionar fecha")
        self._popup.configure(bg=COLOR_BLANCO)
        self._popup.resizable(False, False)
        self._popup.transient(self.winfo_toplevel())
        # Posicionar justo debajo del campo.
        self._popup.geometry(
            f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height() + 2}")
        self._popup.bind("<Escape>", lambda e: self._cerrar())
        self._popup.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._dibujar_calendario()

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
        tk.Button(cabecera, text="›", command=lambda: self._cambiar_mes(1),
                  bg=COLOR_AZUL, fg=COLOR_BLANCO, relief="flat", cursor="hand2",
                  activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
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
                if actual == seleccion:
                    fondo, texto = COLOR_AZUL, COLOR_BLANCO
                elif actual == hoy:
                    fondo, texto = COLOR_GRIS_CLARO, COLOR_AZUL
                else:
                    fondo, texto = COLOR_BLANCO, COLOR_TEXTO
                tk.Button(cuerpo, text=str(dia), width=3, relief="flat",
                          cursor="hand2", bg=fondo, fg=texto,
                          activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                          font=("Helvetica", 9), takefocus=0,
                          command=lambda d=actual: self._elegir(d)
                          ).grid(row=fila, column=col, padx=1, pady=1)

        pie = tk.Frame(self._popup, bg=COLOR_BLANCO, pady=4)
        pie.pack(fill="x")
        tk.Button(pie, text="Hoy", command=lambda: self._elegir(date.today()),
                  bg=COLOR_GRIS_CLARO, fg=COLOR_AZUL, relief="flat", cursor="hand2",
                  font=("Helvetica", 9, "bold"), takefocus=0).pack()

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
        self.empleados = almacen_empleados.cargar_empleados()

        # --- Configuración de la ventana ---
        maestro.title(f"Control de Oficios · {self.usuario['nombre']}")
        maestro.geometry("950x650")
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
        self.cuaderno.add(self.pestana_usuarios, text="  Usuarios  ")
        self.cuaderno.add(self.pestana_tablero, text="  Tablero  ")

        self._construir_registro()
        self._construir_listado()
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

        # Título de la aplicación
        lbl_app = tk.Label(cabecera, text="Control de Oficios — Unidad de Cumplimiento",
                           font=("Arial", 14), fg=COLOR_BLANCO, bg=COLOR_AZUL)
        lbl_app.pack(side="right", padx=20, pady=10)

    # ---- Métodos de las pestañas (sin cambios, solo se ajustan los colores) ----
    def _valores_empleados(self):
        return [empleado["nombreEmpleado"] for empleado in self.empleados]

    def _construir_registro(self):
        marco = self.pestana_registro
        # Aplicar fondo blanco a todos los hijos
        for child in marco.winfo_children():
            child.configure(background=COLOR_BLANCO) if isinstance(child, tk.Widget) else None

        ttk.Label(marco, text="Registrar nuevo oficio",
                  font=("Helvetica", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        ttk.Label(marco, text="Ingrese código de oficio o circular").grid(row=1, column=0, sticky="w", pady=4)
        self.entrada_codigo = ttk.Entry(marco, width=40)
        self.entrada_codigo.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Fecha de recepción").grid(row=2, column=0, sticky="w", pady=4)
        self.entrada_fecha_recepcion = SelectorFecha(marco)
        self.entrada_fecha_recepcion.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Fecha de oficio").grid(row=3, column=0, sticky="w", pady=4)
        self.entrada_fecha_oficio = SelectorFecha(marco)
        self.entrada_fecha_oficio.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Usuario / empleado responsable (opcional)").grid(row=4, column=0, sticky="w", pady=4)
        self.combo_empleado = ttk.Combobox(
            marco, width=37, state="readonly",
            values=[self.SIN_RESPONSABLE] + self._valores_empleados())
        self.combo_empleado.current(0)  # por defecto: sin responsable
        self.combo_empleado.grid(row=4, column=1, sticky="w", pady=4)
        if not self.empleados:
            ttk.Label(marco, text="(No hay empleados. Cargue datos/empleados.csv)", foreground="#a00").grid(row=5, column=1, sticky="w")

        ttk.Label(marco, text="Estado").grid(row=6, column=0, sticky="w", pady=4)
        self.combo_estado = ttk.Combobox(marco, width=25, state="readonly", values=ESTADOS)
        self.combo_estado.current(0)
        self.combo_estado.grid(row=6, column=1, sticky="w", pady=4)

        ttk.Label(
            marco,
            text="Sin responsable el oficio queda \"Por asignar\". Al asignar un\n"
                 "responsable pasa automáticamente a \"En proceso\".",
            foreground="#6B7280", font=("Helvetica", 8),
        ).grid(row=7, column=1, sticky="w", pady=(2, 0))

        btn = ttk.Button(marco, text="Registrar oficio", command=self._guardar_oficio)
        btn.grid(row=8, column=1, sticky="w", pady=18)
        # Estilo especial para el botón principal
        estilo = ttk.Style()
        estilo.configure("Accent.TButton", background=COLOR_AZUL, foreground=COLOR_BLANCO, font=("Helvetica", 10, "bold"))
        btn.config(style="Accent.TButton")

    # Los demás métodos (_guardar_oficio, _construir_listado, etc.) permanecen idénticos.
    # Para ahorrar espacio, los incluyo a continuación pero son los mismos que antes.

    def _empleado_por_nombre(self, nombre):
        """Devuelve (id_empleado, nombre_empleado) a partir del texto elegido
        en un desplegable. Para "(Sin responsable)" o vacío devuelve ("", "")."""
        if not nombre or nombre == self.SIN_RESPONSABLE:
            return "", ""
        for empleado in self.empleados:
            if empleado["nombreEmpleado"] == nombre:
                return empleado["idUsuario"], empleado["nombreEmpleado"]
        return "", nombre

    def _guardar_oficio(self):
        # El responsable es opcional: "(Sin responsable)" => sin asignar.
        id_empleado, nombre_empleado = self._empleado_por_nombre(self.combo_empleado.get())
        try:
            referencia = oficios.registrar_oficio(
                self.entrada_codigo.get(), self.entrada_fecha_recepcion.get(),
                self.entrada_fecha_oficio.get(), id_empleado,
                nombre_empleado, self.combo_estado.get(),
                self.usuario["usuario"],
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Registrado", f"Oficio registrado.\nReferencia: {referencia}")
        self.entrada_codigo.delete(0, "end")
        self.combo_empleado.current(0)
        self.combo_estado.current(0)
        self._refrescar_listado()

    def _construir_listado(self):
        marco = self.pestana_listado
        columnas = ("referencia", "codigo", "recepcion", "oficio", "empleado", "estado")
        titulos = ("Referencia", "Código oficio", "F. recepción", "F. oficio", "Empleado", "Estado")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=16)
        for columna, titulo in zip(columnas, titulos):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=140 if columna == "referencia" else 110, anchor="w")
        self.tabla.column("empleado", width=150)
        self.tabla.pack(fill="both", expand=True, side="top")

        barra = ttk.Frame(marco)
        barra.pack(fill="x", pady=8)
        ttk.Button(barra, text="Actualizar lista", command=self._refrescar_listado).pack(side="left")

        ttk.Label(barra, text="   Responsable:").pack(side="left")
        self.combo_responsable_edicion = ttk.Combobox(
            barra, width=20, state="readonly",
            values=[self.SIN_RESPONSABLE] + self._valores_empleados())
        self.combo_responsable_edicion.current(0)
        self.combo_responsable_edicion.pack(side="left", padx=5)

        ttk.Label(barra, text="Estado:").pack(side="left")
        self.combo_nuevo_estado = ttk.Combobox(barra, width=14, state="readonly", values=ESTADOS)
        self.combo_nuevo_estado.current(0)
        self.combo_nuevo_estado.pack(side="left", padx=5)

        ttk.Button(barra, text="Aplicar cambios", command=self._aplicar_cambios).pack(side="left", padx=5)

        # Al seleccionar un oficio, precargar sus valores actuales.
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_oficio)
        self._refrescar_listado()

    def _refrescar_listado(self):
        if not hasattr(self, "tabla"):
            return
        self.tabla.delete(*self.tabla.get_children())
        try:
            for registro in oficios.listar_oficios():
                self.tabla.insert("", "end", iid=registro["referencia"], values=(
                    registro["referencia"], registro["codigo_oficio"],
                    registro["fecha_recepcion"], registro["fecha_oficio"],
                    registro.get("empleado", ""), registro["estado"]))
        except Exception as e:
            messagebox.showerror("Error al cargar oficios", str(e))

    def _al_seleccionar_oficio(self, evento=None):
        """Precarga los desplegables con el responsable y estado del oficio
        seleccionado en la tabla."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        empleado_actual = valores[4] if len(valores) > 4 else ""
        estado_actual = valores[5] if len(valores) > 5 else ""
        if empleado_actual and empleado_actual in self._valores_empleados():
            self.combo_responsable_edicion.set(empleado_actual)
        else:
            self.combo_responsable_edicion.set(self.SIN_RESPONSABLE)
        if estado_actual in ESTADOS:
            self.combo_nuevo_estado.set(estado_actual)

    def _aplicar_cambios(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        id_empleado, nombre_empleado = self._empleado_por_nombre(
            self.combo_responsable_edicion.get())
        try:
            estado_final = oficios.actualizar_oficio(
                seleccion[0], self.combo_nuevo_estado.get(),
                id_empleado, nombre_empleado, self.usuario["usuario"])
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        # Si las reglas ajustaron el estado (p. ej. al asignar responsable),
        # reflejarlo en el desplegable.
        if estado_final in ESTADOS:
            self.combo_nuevo_estado.set(estado_final)
        self._refrescar_listado()

    def _construir_usuarios(self):
        marco = self.pestana_usuarios
        ttk.Label(marco, text="Crear usuario del sistema",
                  font=("Helvetica", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        ttk.Label(marco, text="Usuario").grid(row=1, column=0, sticky="w", pady=4)
        self.entrada_usuario = ttk.Entry(marco, width=30)
        self.entrada_usuario.grid(row=1, column=1, sticky="w")
        ttk.Label(marco, text="Nombre").grid(row=2, column=0, sticky="w", pady=4)
        self.entrada_nombre = ttk.Entry(marco, width=30)
        self.entrada_nombre.grid(row=2, column=1, sticky="w")
        ttk.Label(marco, text="Contraseña").grid(row=3, column=0, sticky="w", pady=4)
        self.entrada_clave = ttk.Entry(marco, width=30, show="•")
        self.entrada_clave.grid(row=3, column=1, sticky="w")
        ttk.Label(marco, text="Confirmar contraseña").grid(row=4, column=0, sticky="w", pady=4)
        self.entrada_clave2 = ttk.Entry(marco, width=30, show="•")
        self.entrada_clave2.grid(row=4, column=1, sticky="w")
        btn = ttk.Button(marco, text="Crear usuario", command=self._crear_usuario)
        btn.grid(row=5, column=1, sticky="w", pady=14)
        btn.config(style="Accent.TButton")

        ttk.Label(marco, text="Usuarios existentes:").grid(row=6, column=0, sticky="w")
        self.tabla_usuarios = ttk.Treeview(marco, columns=("usuario", "nombre"), show="headings", height=8)
        self.tabla_usuarios.heading("usuario", text="Usuario")
        self.tabla_usuarios.heading("nombre", text="Nombre")
        self.tabla_usuarios.column("usuario", width=140)
        self.tabla_usuarios.column("nombre", width=220)
        self.tabla_usuarios.grid(row=7, column=0, columnspan=2, sticky="w", pady=6)
        self._refrescar_usuarios()

    def _crear_usuario(self):
        if self.entrada_clave.get() != self.entrada_clave2.get():
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        try:
            autenticacion.crear_usuario(self.entrada_usuario.get(),
                                        self.entrada_nombre.get(),
                                        self.entrada_clave.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "Usuario creado correctamente.")
        for entrada in (self.entrada_usuario, self.entrada_nombre,
                        self.entrada_clave, self.entrada_clave2):
            entrada.delete(0, "end")
        self._refrescar_usuarios()

    def _refrescar_usuarios(self):
        self.tabla_usuarios.delete(*self.tabla_usuarios.get_children())
        for usu in autenticacion.listar_usuarios():
            self.tabla_usuarios.insert("", "end", values=(usu["usuario"], usu["nombre"]))

    def _construir_tablero(self):
        marco = self.pestana_tablero
        ttk.Label(marco, text="Tablero de oficios",
                  font=("Helvetica", 13, "bold")).pack(anchor="w")
        self.marco_tarjetas = ttk.Frame(marco)
        self.marco_tarjetas.pack(fill="x", pady=12)
        self.lienzo = tk.Canvas(marco, height=220, background=COLOR_BLANCO,
                                highlightthickness=1, highlightbackground="#ccc")
        self.lienzo.pack(fill="x", pady=8)
        ttk.Button(marco, text="Actualizar métricas", command=self._refrescar_tablero).pack(anchor="w")

    def _tarjeta(self, contenedor, titulo, valor, color):
        marco = tk.Frame(contenedor, bg=color, padx=14, pady=10)
        marco.pack(side="left", padx=6)
        tk.Label(marco, text=str(valor), bg=color, fg=COLOR_BLANCO,
                 font=("Helvetica", 18, "bold")).pack()
        tk.Label(marco, text=titulo, bg=color, fg=COLOR_BLANCO,
                 font=("Helvetica", 9)).pack()

    def _refrescar_tablero(self):
        for hijo in self.marco_tarjetas.winfo_children():
            hijo.destroy()
        datos = metricas.resumen()
        self._tarjeta(self.marco_tarjetas, "Total", datos["total"], COLOR_AZUL)
        self._tarjeta(self.marco_tarjetas, "Por asignar", datos["por_estado"]["Por asignar"], "#b45309")
        self._tarjeta(self.marco_tarjetas, "En proceso", datos["por_estado"]["En proceso"], "#1d4ed8")
        self._tarjeta(self.marco_tarjetas, "Finalizados", datos["finalizados"], "#15803d")
        self._tarjeta(self.marco_tarjetas, "Hoy", datos["recibidos_hoy"], "#0f766e")
        self._tarjeta(self.marco_tarjetas, "Semana", datos["recibidos_semana"], "#7c3aed")
        self._tarjeta(self.marco_tarjetas, "Mes", datos["recibidos_mes"], "#be123c")
        self._dibujar_barras(metricas.serie_por_dia(14))

    def _dibujar_barras(self, serie):
        lienzo = self.lienzo
        lienzo.delete("all")
        lienzo.update_idletasks()
        ancho_lienzo = lienzo.winfo_width() or 800
        alto_lienzo = 220
        margen_izq, margen_inf, margen_sup = 30, 30, 20
        valor_max = max([valor for _, valor in serie] + [1])
        cantidad = len(serie)
        ancho_barra = (ancho_lienzo - margen_izq - 10) / cantidad
        lienzo.create_text(margen_izq, margen_sup - 8,
                           text="Oficios recibidos por día (14 días)",
                           anchor="w", font=("Helvetica", 9, "bold"))
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

    def _al_cambiar_pestana(self, evento):
        indice = evento.widget.index("current")
        if indice == 1:
            self._refrescar_listado()
        elif indice == 3:
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
        tk.Label(cont, text="Cree la cuenta de administrador para comenzar",
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
            autenticacion.crear_usuario(self.entrada_usuario.get(),
                                        self.entrada_nombre.get(),
                                        self.entrada_clave.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "Administrador creado. Inicie sesión.")
        self._formulario_ingreso()


def iniciar():
    raiz = tk.Tk()
    VentanaIngreso(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar()



