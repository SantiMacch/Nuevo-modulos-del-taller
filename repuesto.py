import flet as ft
import mysql.connector

def conexiondb():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            database='Taller_Mecanico',
            ssl_disabled=True
        )
        if connection.is_connected():
            print('Conexión exitosa a la base de datos')
            return connection
    except Exception as ex:
        print('Error de conexión:', ex)
        return None

class Herramienta_Repuesto:
    def __init__(self, pagina: ft.Page, volver_menu_principal):
        self.pagina = pagina
        self.volver_menu_principal = volver_menu_principal
        self.conexion = conexiondb()
        self.cursor = self.conexion.cursor() if self.conexion else None
        self.repuesto_seleccionado = None
        self.mostrar_repuestos()

    def mostrar_repuestos(self):
        self.pagina.clean()
        self.pagina.title = "Gestión de Repuestos"
        btn_agregar = ft.ElevatedButton(text="Agregar", on_click=self.abrir_formulario_agregar, icon=ft.Icons.ADD)
        btn_editar = ft.ElevatedButton(text="Editar", on_click=self.abrir_formulario_editar, icon=ft.Icons.EDIT)
        btn_eliminar = ft.ElevatedButton(text="Eliminar", on_click=self.eliminar_repuesto, icon=ft.Icons.DELETE)
        button_row = ft.Row(
            controls=[btn_agregar, btn_editar, btn_eliminar],
            spacing=10,
        )
        barra_superior = ft.Row(
            controls=[
                ft.Text("Lista de Repuestos", size=20, weight="bold"),
                ft.ElevatedButton(
                    "Volver al Menú",
                    on_click=lambda e: self.volver_menu_principal(self.pagina),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.campo_busqueda = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Nombre"),
                ft.dropdown.Option("Código"),
            ],
            value="Nombre",
        )
        self.valor_busqueda = ft.TextField(label="Buscar", width=200)
        boton_buscar = ft.ElevatedButton("Buscar", on_click=self.buscar_repuestos, width=100)
        fila_busqueda = ft.Row(
            controls=[
                self.campo_busqueda,
                self.valor_busqueda,
                boton_buscar,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
        self.tabla_repuestos = self.crear_tabla_repuestos()
        contenido_principal = ft.Column(
            controls=[
                barra_superior,
                fila_busqueda,
                button_row,
                self.tabla_repuestos,
            ],
            spacing=10,
            expand=True
        )
        self.pagina.add(contenido_principal)

    def crear_tabla_repuestos(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute("""
                SELECT cod_repuesto, nombre, stock, precio
                FROM repuesto
                ORDER BY nombre
            """)
            datos_repuestos = self.cursor.fetchall()
            filas = []
            for repuesto in datos_repuestos:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(repuesto[0]))),
                            ft.DataCell(ft.Text(repuesto[1])),
                            ft.DataCell(ft.Text(str(repuesto[2]))),
                            ft.DataCell(ft.Text(f"$ {repuesto[3]:.2f}")),
                        ],
                        on_select_changed=lambda e, cod=repuesto[0]: self.seleccionar_repuesto(e, cod),
                    )
                )
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Stock")),
                    ft.DataColumn(ft.Text("Precio")),
                ],
                rows=filas,
            )
        except Exception as e:
            print(f"Error al crear la tabla de repuestos: {e}")
            return ft.Text(f"No se pudieron cargar los repuestos. Error: {e}")

    def seleccionar_repuesto(self, e, cod_repuesto):
        self.repuesto_seleccionado = cod_repuesto

    def abrir_formulario_agregar(self, e):
        self.txt_nombre = ft.TextField(label="Nombre")
        self.txt_stock = ft.TextField(label="Stock", input_filter=ft.NumbersOnlyInputFilter())
        self.txt_precio = ft.TextField(label="Precio", input_filter=ft.NumbersOnlyInputFilter())

        dialog = ft.AlertDialog(
            title=ft.Text("Agregar Repuesto"),
            content=ft.Column([
                self.txt_nombre,
                self.txt_stock,
                self.txt_precio,
            ]),
            actions=[
                ft.ElevatedButton("Guardar", on_click=self.guardar_repuesto),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
            ],
        )
        self.pagina.dialog = dialog
        dialog.open = True
        self.pagina.update()

    def guardar_repuesto(self, e):
        nombre = self.txt_nombre.value
        stock = self.txt_stock.value
        precio = self.txt_precio.value
        try:
            self.cursor.execute(
                "INSERT INTO repuesto (nombre, stock, precio) VALUES (%s, %s, %s)",
                (nombre, stock, precio)
            )
            self.conexion.commit()
            self.mostrar_repuestos()
            self.cerrar_dialogo(self.pagina.dialog)
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def abrir_formulario_editar(self, e):
        if not self.repuesto_seleccionado:
            self.pagina.snack_bar = ft.SnackBar(ft.Text("Selecciona un repuesto para editar"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return
        try:
            self.cursor.execute("""
                SELECT nombre, stock, precio
                FROM repuesto
                WHERE cod_repuesto = %s
            """, (self.repuesto_seleccionado,))
            repuesto = self.cursor.fetchone()

            self.txt_nombre = ft.TextField(label="Nombre", value=repuesto[0])
            self.txt_stock = ft.TextField(label="Stock", value=str(repuesto[1]), input_filter=ft.NumbersOnlyInputFilter())
            self.txt_precio = ft.TextField(label="Precio", value=str(repuesto[2]), input_filter=ft.NumbersOnlyInputFilter())

            dialog = ft.AlertDialog(
                title=ft.Text("Editar Repuesto"),
                content=ft.Column([
                    self.txt_nombre,
                    self.txt_stock,
                    self.txt_precio,
                ]),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=self.actualizar_repuesto),
                    ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
                ],
            )
            self.pagina.dialog = dialog
            dialog.open = True
            self.pagina.update()
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al cargar datos: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def actualizar_repuesto(self, e):
        nombre = self.txt_nombre.value
        stock = self.txt_stock.value
        precio = self.txt_precio.value
        try:
            self.cursor.execute("""
                UPDATE repuesto
                SET nombre = %s, stock = %s, precio = %s
                WHERE cod_repuesto = %s
            """, (nombre, stock, precio, self.repuesto_seleccionado))
            self.conexion.commit()
            self.mostrar_repuestos()
            self.cerrar_dialogo(self.pagina.dialog)
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def eliminar_repuesto(self, e):
        if not self.repuesto_seleccionado:
            self.pagina.snack_bar = ft.SnackBar(ft.Text("Selecciona un repuesto para eliminar"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return
        try:
            self.cursor.execute("DELETE FROM repuesto WHERE cod_repuesto = %s", (self.repuesto_seleccionado,))
            self.conexion.commit()
            self.mostrar_repuestos()
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def buscar_repuestos(self, e):
        if not self.cursor:
            return
        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value
        try:
            consulta = f"""
                SELECT cod_repuesto, nombre, stock, precio
                FROM repuesto
                WHERE {campo} LIKE %s
                ORDER BY nombre
            """
            self.cursor.execute(consulta, (f"%{valor}%",))
            datos_repuestos = self.cursor.fetchall()
            filas = []
            for repuesto in datos_repuestos:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(repuesto[0]))),
                            ft.DataCell(ft.Text(repuesto[1])),
                            ft.DataCell(ft.Text(str(repuesto[2]))),
                            ft.DataCell(ft.Text(f"$ {repuesto[3]:.2f}")),
                        ],
                        on_select_changed=lambda e, cod=repuesto[0]: self.seleccionar_repuesto(e, cod),
                    )
                )
            self.pagina.controls[0].content.controls[3] = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Stock")),
                    ft.DataColumn(ft.Text("Precio")),
                ],
                rows=filas,
            )
            self.pagina.update()
        except Exception as e:
            print(f"Error al buscar repuestos: {e}")
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al buscar: {e}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def cerrar_dialogo(self, dialog):
        dialog.open = False
        self.pagina.update()
