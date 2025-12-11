import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
import os


DB_NAME = "estudiantes.db"


class EstudianteDB:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._crear_tabla()

    def _conectar(self):
        return sqlite3.connect(self.db_name)

    def _crear_tabla(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS estudiantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    carrera TEXT NOT NULL,
                    email TEXT
                )
                """
            )
            conn.commit()

    def insertar(self, nombre, apellido, edad, carrera, email):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO estudiantes (nombre, apellido, edad, carrera, email) VALUES (?, ?, ?, ?, ?)",
                (nombre, apellido, edad, carrera, email),
            )
            conn.commit()

    def listar(self, filtro=""):
        with self._conectar() as conn:
            cursor = conn.cursor()
            if filtro:
                filtro_like = f"%{filtro}%"
                cursor.execute(
                    """
                    SELECT id, nombre, apellido, edad, carrera, email
                    FROM estudiantes
                    WHERE nombre LIKE ? OR apellido LIKE ? OR carrera LIKE ? OR email LIKE ?
                    ORDER BY id DESC
                    """,
                    (filtro_like, filtro_like, filtro_like, filtro_like),
                )
            else:
                cursor.execute(
                    "SELECT id, nombre, apellido, edad, carrera, email FROM estudiantes ORDER BY id DESC"
                )
            return cursor.fetchall()

    def actualizar(self, id_est, nombre, apellido, edad, carrera, email):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE estudiantes
                SET nombre = ?, apellido = ?, edad = ?, carrera = ?, email = ?
                WHERE id = ?
                """,
                (nombre, apellido, edad, carrera, email, id_est),
            )
            conn.commit()

    def eliminar(self, id_est):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM estudiantes WHERE id = ?", (id_est,))
            conn.commit()


class GestionEstudiantesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Estudiantes")
        self.geometry("900x500")
        self.minsize(900, 500)
        self.resizable(True, True)

        # Centrar ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.db = EstudianteDB()

        # Variables de formulario
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_edad = tk.StringVar()
        self.var_carrera = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_buscar = tk.StringVar()

        self._configurar_estilo()
        self._crear_widgets()
        self.cargar_estudiantes()

    def _configurar_estilo(self):
        style = ttk.Style()
        # En Windows suele ser "vista", en otros "clam"
        try:
            style.theme_use("vista")
        except tk.TclError:
            style.theme_use("clam")

        style.configure(
            "TFrame",
            background="#f5f5f5",
        )
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 16, "bold"),
            background="#f5f5f5",
        )
        style.configure(
            "Field.TLabel",
            font=("Segoe UI", 10),
            background="#f5f5f5",
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=4,
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
        )

    def _crear_widgets(self):
        # Frame principal
        contenedor = ttk.Frame(self, padding=10)
        contenedor.pack(fill="both", expand=True)

        # ----- Izquierda: Formulario -----
        frame_form = ttk.Frame(contenedor)
        frame_form.pack(side="left", fill="y", padx=(0, 10))

        lbl_titulo = ttk.Label(
            frame_form,
            text="Gestión de Estudiantes",
            style="Title.TLabel",
        )
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # Campo ID (solo lectura)
        ttk.Label(frame_form, text="ID:", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=2
        )
        entry_id = ttk.Entry(frame_form, textvariable=self.var_id, state="readonly", width=10)
        entry_id.grid(row=1, column=1, sticky="w", pady=2)

        # Nombre
        ttk.Label(frame_form, text="Nombre *:", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=2
        )
        entry_nombre = ttk.Entry(frame_form, textvariable=self.var_nombre, width=30)
        entry_nombre.grid(row=2, column=1, sticky="w", pady=2)

        # Apellido
        ttk.Label(frame_form, text="Apellido *:", style="Field.TLabel").grid(
            row=3, column=0, sticky="w", pady=2
        )
        entry_apellido = ttk.Entry(frame_form, textvariable=self.var_apellido, width=30)
        entry_apellido.grid(row=3, column=1, sticky="w", pady=2)

        # Edad
        ttk.Label(frame_form, text="Edad *:", style="Field.TLabel").grid(
            row=4, column=0, sticky="w", pady=2
        )
        entry_edad = ttk.Entry(frame_form, textvariable=self.var_edad, width=10)
        entry_edad.grid(row=4, column=1, sticky="w", pady=2)

        # Carrera
        ttk.Label(frame_form, text="Carrera *:", style="Field.TLabel").grid(
            row=5, column=0, sticky="w", pady=2
        )
        entry_carrera = ttk.Entry(frame_form, textvariable=self.var_carrera, width=30)
        entry_carrera.grid(row=5, column=1, sticky="w", pady=2)

        # Email
        ttk.Label(frame_form, text="Email:", style="Field.TLabel").grid(
            row=6, column=0, sticky="w", pady=2
        )
        entry_email = ttk.Entry(frame_form, textvariable=self.var_email, width=30)
        entry_email.grid(row=6, column=1, sticky="w", pady=2)

        # Botones CRUD
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="w")

        btn_nuevo = ttk.Button(
            frame_botones,
            text="Nuevo",
            command=self.limpiar_formulario,
        )
        btn_nuevo.grid(row=0, column=0, padx=2)

        btn_guardar = ttk.Button(
            frame_botones,
            text="Guardar",
            style="Accent.TButton",
            command=self.guardar_estudiante,
        )
        btn_guardar.grid(row=0, column=1, padx=2)

        btn_actualizar = ttk.Button(
            frame_botones,
            text="Actualizar",
            command=self.actualizar_estudiante,
        )
        btn_actualizar.grid(row=0, column=2, padx=2)

        btn_eliminar = ttk.Button(
            frame_botones,
            text="Eliminar",
            command=self.eliminar_estudiante,
        )
        btn_eliminar.grid(row=0, column=3, padx=2)

        # Nota campos obligatorios
        lbl_obligatorio = ttk.Label(
            frame_form,
            text="* Campos obligatorios",
            style="Field.TLabel",
            foreground="#666666",
        )
        lbl_obligatorio.grid(row=8, column=0, columnspan=2, pady=(10, 0), sticky="w")

        # Expandir filas
        for i in range(9):
            frame_form.rowconfigure(i, weight=0)
        frame_form.rowconfigure(9, weight=1)

        # ----- Derecha: Panel de búsqueda y tabla -----
        frame_derecha = ttk.Frame(contenedor)
        frame_derecha.pack(side="left", fill="both", expand=True)

        frame_busqueda = ttk.Frame(frame_derecha)
        frame_busqueda.pack(fill="x")

        ttk.Label(frame_busqueda, text="Buscar:", style="Field.TLabel").pack(
            side="left", padx=(0, 5)
        )
        entry_buscar = ttk.Entry(
            frame_busqueda, textvariable=self.var_buscar, width=40
        )
        entry_buscar.pack(side="left", padx=(0, 5))
        entry_buscar.bind("<Return>", lambda event: self.cargar_estudiantes())

        btn_buscar = ttk.Button(
            frame_busqueda, text="Filtrar", command=self.cargar_estudiantes
        )
        btn_buscar.pack(side="left", padx=(0, 5))

        btn_limpiar_busqueda = ttk.Button(
            frame_busqueda, text="Limpiar filtro", command=self.limpiar_busqueda
        )
        btn_limpiar_busqueda.pack(side="left")

        # Treeview
        frame_tabla = ttk.Frame(frame_derecha)
        frame_tabla.pack(fill="both", expand=True, pady=(10, 0))

        columnas = ("id", "nombre", "apellido", "edad", "carrera", "email")
        self.tree = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            selectmode="browse",
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("edad", text="Edad")
        self.tree.heading("carrera", text="Carrera")
        self.tree.heading("email", text="Email")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=120)
        self.tree.column("apellido", width=120)
        self.tree.column("edad", width=50, anchor="center")
        self.tree.column("carrera", width=150)
        self.tree.column("email", width=180)

        # Scrollbars
        scroll_y = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree.yview
        )
        scroll_x = ttk.Scrollbar(
            frame_tabla, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        # Evento: seleccionar fila
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

    # ================== LÓGICA CRUD ==================

    def validar_formulario(self):
        nombre = self.var_nombre.get().strip()
        apellido = self.var_apellido.get().strip()
        edad = self.var_edad.get().strip()
        carrera = self.var_carrera.get().strip()
        email = self.var_email.get().strip()

        if not nombre or not apellido or not edad or not carrera:
            messagebox.showwarning(
                "Validación",
                "Por favor completa todos los campos obligatorios marcados con *.",
                parent=self,
            )
            return False

        if not edad.isdigit() or int(edad) <= 0:
            messagebox.showwarning(
                "Validación",
                "La edad debe ser un número entero positivo.",
                parent=self,
            )
            return False

        if email:
            patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(patron_email, email):
                messagebox.showwarning(
                    "Validación",
                    "El email no tiene un formato válido.",
                    parent=self,
                )
                return False

        return True

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_nombre.set("")
        self.var_apellido.set("")
        self.var_edad.set("")
        self.var_carrera.set("")
        self.var_email.set("")
        self.tree.selection_remove(self.tree.selection())

    def limpiar_busqueda(self):
        self.var_buscar.set("")
        self.cargar_estudiantes()

    def guardar_estudiante(self):
        if not self.validar_formulario():
            return

        try:
            self.db.insertar(
                self.var_nombre.get().strip(),
                self.var_apellido.get().strip(),
                int(self.var_edad.get().strip()),
                self.var_carrera.get().strip(),
                self.var_email.get().strip(),
            )
            messagebox.showinfo(
                "Éxito", "Estudiante registrado correctamente.", parent=self
            )
            self.limpiar_formulario()
            self.cargar_estudiantes()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al guardar el estudiante:\n{e}", parent=self
            )

    def cargar_estudiantes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro = self.var_buscar.get().strip()
        try:
            registros = self.db.listar(filtro=filtro)
            for fila in registros:
                self.tree.insert("", "end", values=fila)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al cargar los estudiantes:\n{e}", parent=self
            )

    def on_tree_select(self, event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        item = self.tree.item(seleccion[0])
        id_est, nombre, apellido, edad, carrera, email = item["values"]

        self.var_id.set(id_est)
        self.var_nombre.set(nombre)
        self.var_apellido.set(apellido)
        self.var_edad.set(str(edad))
        self.var_carrera.set(carrera)
        self.var_email.set(email)

    def on_tree_double_click(self, event=None):
        # Doble clic: cargar datos en el formulario (ya lo hace on_tree_select) y enfocar nombre
        self.on_tree_select()
        self.focus_force()

    def actualizar_estudiante(self):
        if not self.var_id.get():
            messagebox.showwarning(
                "Actualizar",
                "Selecciona primero un estudiante de la tabla para actualizar.",
                parent=self,
            )
            return

        if not self.validar_formulario():
            return

        resp = messagebox.askyesno(
            "Confirmar actualización",
            "¿Seguro que deseas actualizar este registro?",
            parent=self,
        )
        if not resp:
            return

        try:
            self.db.actualizar(
                int(self.var_id.get()),
                self.var_nombre.get().strip(),
                self.var_apellido.get().strip(),
                int(self.var_edad.get().strip()),
                self.var_carrera.get().strip(),
                self.var_email.get().strip(),
            )
            messagebox.showinfo(
                "Éxito", "Estudiante actualizado correctamente.", parent=self
            )
            self.cargar_estudiantes()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al actualizar el estudiante:\n{e}", parent=self
            )

    def eliminar_estudiante(self):
        if not self.var_id.get():
            messagebox.showwarning(
                "Eliminar",
                "Selecciona primero un estudiante de la tabla para eliminar.",
                parent=self,
            )
            return

        resp = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Seguro que deseas eliminar este registro? Esta acción no se puede deshacer.",
            parent=self,
        )
        if not resp:
            return

        try:
            self.db.eliminar(int(self.var_id.get()))
            messagebox.showinfo(
                "Éxito", "Estudiante eliminado correctamente.", parent=self
            )
            self.limpiar_formulario()
            self.cargar_estudiantes()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al eliminar el estudiante:\n{e}", parent=self
            )


if __name__ == "__main__":
    # Crear DB en el mismo directorio si no existe
    if not os.path.exists(DB_NAME):
        open(DB_NAME, "a").close()
    app = GestionEstudiantesApp()
    app.mainloop()