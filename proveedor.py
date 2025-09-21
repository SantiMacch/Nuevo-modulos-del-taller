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

class Herramienta_Proveedor:
    def __init__(self, page: ft.Page, volver_menu_principal):
        self.page = page
        self.main_retroceder = volver_menu_principal
        self.conexion = conexiondb()
        self.cursor = self.conexion.cursor() if self.conexion else None
        self.proveedor_seleccionado = None
        self.mostrar_proveedores()

    def mostrar_proveedores(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Lista de Proveedores", size=20, weight="bold"),
                ft.ElevatedButton(text="Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        btn_agregar = ft.ElevatedButton(text="Agregar", on_click=self.abrir_formulario_agregar, icon=ft.Icons.ADD)
        btn_editar = ft.ElevatedButton(text="Editar", on_click=self.abrir_formulario_editar, icon=ft.Icons.EDIT)
        btn_eliminar = ft.ElevatedButton(text="Eliminar", on_click=self.eliminar_proveedor, icon=ft.Icons.DELETE)
        button_row = ft.Row(
            controls=[btn_agregar, btn_editar, btn_eliminar],
            spacing=10,
        )
        self.campo_busqueda = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Nombre"),
                ft.dropdown.Option("CUIT"),
            ],
            value="Nombre",
        )
        self.valor_busqueda = ft.TextField(label="Buscar", width=200)
        btn_buscar = ft.ElevatedButton(text="Buscar", on_click=self.buscar_proveedores, width=100)
        search_row = ft.Row(
            controls=[
                self.campo_busqueda,
                self.valor_busqueda,
                btn_buscar,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
        self.data_table = self.crear_tabla_proveedores()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        search_row,
                        button_row,
                        self.data_table,
                    ],
                    spacing=10,
                ),
                padding=20,
            )
        )

    def crear_tabla_proveedores(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute("""
                SELECT nombre, cuit, direccion, telefono
                FROM proveedor
                ORDER BY nombre
            """)
            datos_proveedores = self.cursor.fetchall()
            filas = []
            for proveedor in datos_proveedores:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(proveedor[0])),
                            ft.DataCell(ft.Text(str(proveedor[1]))),
                            ft.DataCell(ft.Text(proveedor[2])),
                            ft.DataCell(ft.Text(proveedor[3])),
                        ],
                        on_select_changed=lambda e, cuit=proveedor[1]: self.seleccionar_proveedor(e, cuit),
                    )
                )
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("CUIT")),
                    ft.DataColumn(ft.Text("Dirección")),
                    ft.DataColumn(ft.Text("Teléfono")),
                ],
                rows=filas,
            )
        except Exception as e:
            print(f"Error al crear la tabla de proveedores: {e}")
            return ft.Text(f"No se pudieron cargar los proveedores. Error: {e}")

    def seleccionar_proveedor(self, e, cuit):
        self.proveedor_seleccionado = cuit

    def abrir_formulario_agregar(self, e):
        self.txt_nombre = ft.TextField(label="Nombre")
        self.txt_cuit = ft.TextField(label="CUIT")
        self.txt_direccion = ft.TextField(label="Dirección")
        self.txt_telefono = ft.TextField(label="Teléfono")

        dialog = ft.AlertDialog(
            title=ft.Text("Agregar Proveedor"),
            content=ft.Column([
                self.txt_nombre,
                self.txt_cuit,
                self.txt_direccion,
                self.txt_telefono,
            ]),
            actions=[
                ft.ElevatedButton("Guardar", on_click=self.guardar_proveedor),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def guardar_proveedor(self, e):
        nombre = self.txt_nombre.value
        cuit = self.txt_cuit.value
        direccion = self.txt_direccion.value
        telefono = self.txt_telefono.value
        try:
            self.cursor.execute(
                "INSERT INTO proveedor (nombre, cuit, direccion, telefono) VALUES (%s, %s, %s, %s)",
                (nombre, cuit, direccion, telefono)
            )
            self.conexion.commit()
            self.mostrar_proveedores()
            self.cerrar_dialogo(self.page.dialog)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def abrir_formulario_editar(self, e):
        if not self.proveedor_seleccionado:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecciona un proveedor para editar"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        try:
            self.cursor.execute("""
                SELECT nombre, cuit, direccion, telefono
                FROM proveedor
                WHERE cuit = %s
            """, (self.proveedor_seleccionado,))
            proveedor = self.cursor.fetchone()

            self.txt_nombre = ft.TextField(label="Nombre", value=proveedor[0])
            self.txt_cuit = ft.TextField(label="CUIT", value=str(proveedor[1]), disabled=True)
            self.txt_direccion = ft.TextField(label="Dirección", value=proveedor[2])
            self.txt_telefono = ft.TextField(label="Teléfono", value=proveedor[3])

            dialog = ft.AlertDialog(
                title=ft.Text("Editar Proveedor"),
                content=ft.Column([
                    self.txt_nombre,
                    self.txt_cuit,
                    self.txt_direccion,
                    self.txt_telefono,
                ]),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=self.actualizar_proveedor),
                    ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al cargar datos: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_proveedor(self, e):
        nombre = self.txt_nombre.value
        cuit = self.txt_cuit.value
        direccion = self.txt_direccion.value
        telefono = self.txt_telefono.value
        try:
            self.cursor.execute("""
                UPDATE proveedor
                SET nombre = %s, direccion = %s, telefono = %s
                WHERE cuit = %s
            """, (nombre, direccion, telefono, cuit))
            self.conexion.commit()
            self.mostrar_proveedores()
            self.cerrar_dialogo(self.page.dialog)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def eliminar_proveedor(self, e):
        if not self.proveedor_seleccionado:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecciona un proveedor para eliminar"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        try:
            self.cursor.execute("DELETE FROM proveedor WHERE cuit = %s", (self.proveedor_seleccionado,))
            self.conexion.commit()
            self.mostrar_proveedores()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def buscar_proveedores(self, e):
        if not self.cursor:
            return
        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value
        try:
            consulta = f"""
                SELECT nombre, cuit, direccion, telefono
                FROM proveedor
                WHERE {campo} LIKE %s
                ORDER BY nombre
            """
            self.cursor.execute(consulta, (f"%{valor}%",))
            datos_proveedores = self.cursor.fetchall()
            filas = []
            for proveedor in datos_proveedores:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(proveedor[0])),
                            ft.DataCell(ft.Text(str(proveedor[1]))),
                            ft.DataCell(ft.Text(proveedor[2])),
                            ft.DataCell(ft.Text(proveedor[3])),
                        ],
                        on_select_changed=lambda e, cuit=proveedor[1]: self.seleccionar_proveedor(e, cuit),
                    )
                )
            self.page.controls[0].content.controls[3] = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("CUIT")),
                    ft.DataColumn(ft.Text("Dirección")),
                    ft.DataColumn(ft.Text("Teléfono")),
                ],
                rows=filas,
            )
            self.page.update()
        except Exception as e:
            print(f"Error al buscar proveedores: {e}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al buscar: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def cerrar_dialogo(self, dialog):
        dialog.open = False
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_retroceder(self.page)
