import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

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


class AplicacionPrincipal(ttk.Frame):
    def __init__(self, maestro, usuario_sesion):
        super().__init__(maestro, padding=10)
        self.maestro = maestro
        self.usuario = usuario_sesion
        self.empleados = almacen_empleados.cargar_empleados()

        # --- Configuración de la ventana ---
        maestro.title(f"Gestor de Oficios · {self.usuario['nombre']}")
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
        lbl_app = tk.Label(cabecera, text="Gestor de Oficios - Unidad de Cumplimiento",
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

        ttk.Label(marco, text="Fecha de recepción (AAAA-MM-DD)").grid(row=2, column=0, sticky="w", pady=4)
        self.entrada_fecha_recepcion = ttk.Entry(marco, width=20)
        self.entrada_fecha_recepcion.insert(0, date.today().isoformat())
        self.entrada_fecha_recepcion.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Fecha de oficio (AAAA-MM-DD)").grid(row=3, column=0, sticky="w", pady=4)
        self.entrada_fecha_oficio = ttk.Entry(marco, width=20)
        self.entrada_fecha_oficio.insert(0, date.today().isoformat())
        self.entrada_fecha_oficio.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(marco, text="Usuario / empleado responsable").grid(row=4, column=0, sticky="w", pady=4)
        self.combo_empleado = ttk.Combobox(marco, width=37, state="readonly", values=self._valores_empleados())
        self.combo_empleado.grid(row=4, column=1, sticky="w", pady=4)
        if not self.empleados:
            ttk.Label(marco, text="(No hay empleados. Cargue datos/empleados.csv)", foreground="#a00").grid(row=5, column=1, sticky="w")

        ttk.Label(marco, text="Estado").grid(row=6, column=0, sticky="w", pady=4)
        self.combo_estado = ttk.Combobox(marco, width=25, state="readonly", values=ESTADOS)
        self.combo_estado.current(0)
        self.combo_estado.grid(row=6, column=1, sticky="w", pady=4)

        btn = ttk.Button(marco, text="Registrar oficio", command=self._guardar_oficio)
        btn.grid(row=7, column=1, sticky="w", pady=18)
        # Estilo especial para el botón principal
        estilo = ttk.Style()
        estilo.configure("Accent.TButton", background=COLOR_AZUL, foreground=COLOR_BLANCO, font=("Helvetica", 10, "bold"))
        btn.config(style="Accent.TButton")

    # Los demás métodos (_guardar_oficio, _construir_listado, etc.) permanecen idénticos.
    # Para ahorrar espacio, los incluyo a continuación pero son los mismos que antes.

    def _guardar_oficio(self):
        if self.combo_empleado.current() < 0:
            messagebox.showwarning("Falta empleado", "Seleccione un empleado.")
            return
        empleado = self.empleados[self.combo_empleado.current()]
        try:
            referencia = oficios.registrar_oficio(
                self.entrada_codigo.get(), self.entrada_fecha_recepcion.get(),
                self.entrada_fecha_oficio.get(), empleado["idUsuario"],
                empleado["nombreEmpleado"], self.combo_estado.get(),
                self.usuario["usuario"],
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Registrado", f"Oficio registrado.\nReferencia: {referencia}")
        self.entrada_codigo.delete(0, "end")
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
        ttk.Label(barra, text="   Cambiar estado del seleccionado a:").pack(side="left")
        self.combo_nuevo_estado = ttk.Combobox(barra, width=18, state="readonly", values=ESTADOS)
        self.combo_nuevo_estado.current(0)
        self.combo_nuevo_estado.pack(side="left", padx=5)
        ttk.Button(barra, text="Aplicar", command=self._cambiar_estado).pack(side="left")
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

    def _cambiar_estado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un oficio en la lista.")
            return
        try:
            oficios.actualizar_estado(seleccion[0], self.combo_nuevo_estado.get(), self.usuario["usuario"])
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
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
    def __init__(self, maestro):
        # Heredamos de tk.Frame para poder usar bg
        tk.Frame.__init__(self, maestro, bg=COLOR_BLANCO)
        self.maestro = maestro
        self.pack(fill="both", expand=True, padx=30, pady=30)

        maestro.title("Gestor de Oficios · Ingreso")
        maestro.geometry("400x360")

        # Ícono
        if ARCHIVO_ICONO.exists():
            try:
                maestro.iconbitmap(str(ARCHIVO_ICONO))
            except tk.TclError:
                pass

        # Estilo para los labels (fondo blanco, texto azul)
        estilo = ttk.Style()
        estilo.configure("Login.TLabel", background=COLOR_BLANCO, foreground=COLOR_TEXTO)

        if autenticacion.existe_algun_usuario():
            self._formulario_ingreso()
        else:
            self._formulario_primer_uso()

    def _limpiar(self):
        for hijo in self.winfo_children():
            hijo.destroy()

    def _formulario_ingreso(self):
        self._limpiar()
        # El fondo ya es blanco por el __init__, pero lo reafirmamos
        self.configure(bg=COLOR_BLANCO)

        ttk.Label(self, text="Iniciar sesión", font=("Helvetica", 15, "bold"),
                  style="Login.TLabel").pack(pady=(0, 20))
        ttk.Label(self, text="Usuario", style="Login.TLabel").pack(anchor="w")
        self.entrada_usuario = ttk.Entry(self, width=30)
        self.entrada_usuario.pack(fill="x", pady=(0, 10))
        ttk.Label(self, text="Contraseña", style="Login.TLabel").pack(anchor="w")
        self.entrada_clave = ttk.Entry(self, width=30, show="•")
        self.entrada_clave.pack(fill="x")
        self.entrada_clave.bind("<Return>", lambda evento: self._ingresar())

        # Botón personalizado (tk.Button) con colores fijos
        btn = tk.Button(self, text="Ingresar", command=self._ingresar,
                        bg=COLOR_AZUL, fg=COLOR_BLANCO,
                        activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                        font=("Helvetica", 10, "bold"), relief="flat", padx=20, pady=8)
        btn.pack(pady=20)

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
        self._limpiar()
        self.configure(bg=COLOR_BLANCO)

        ttk.Label(self, text="Primer uso: crear administrador",
                  font=("Helvetica", 13, "bold"), style="Login.TLabel").pack(pady=(0, 15))
        ttk.Label(self, text="Usuario", style="Login.TLabel").pack(anchor="w")
        self.entrada_usuario = ttk.Entry(self, width=30)
        self.entrada_usuario.pack(fill="x", pady=(0, 5))
        ttk.Label(self, text="Nombre", style="Login.TLabel").pack(anchor="w")
        self.entrada_nombre = ttk.Entry(self, width=30)
        self.entrada_nombre.pack(fill="x", pady=(0, 5))
        ttk.Label(self, text="Contraseña", style="Login.TLabel").pack(anchor="w")
        self.entrada_clave = ttk.Entry(self, width=30, show="•")
        self.entrada_clave.pack(fill="x", pady=(0, 5))

        btn = tk.Button(self, text="Crear y continuar", command=self._crear_administrador,
                        bg=COLOR_AZUL, fg=COLOR_BLANCO,
                        activebackground="#1A2E5A", activeforeground=COLOR_BLANCO,
                        font=("Helvetica", 10, "bold"), relief="flat", padx=20, pady=8)
        btn.pack(pady=16)

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



