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

class Herramienta_Cliente:
    def __init__(self, page: ft.Page, volver_menu_principal):
        self.page = page
        self.main_retroceder = volver_menu_principal
        self.connection = conexiondb()
        self.cursor = self.connection.cursor() if self.connection else None
        self.cliente_seleccionado = None
        self.mostrar_clientes()

    def mostrar_clientes(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Lista de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.campo_busqueda = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Apellido"),
                ft.dropdown.Option("Nombre"),
                ft.dropdown.Option("DNI"),
            ],
            value="Apellido",
        )
        self.valor_busqueda = ft.TextField(label="Buscar", width=200)
        btn_buscar = ft.ElevatedButton(text="Buscar", on_click=self.buscar_clientes, width=100)
        search_row = ft.Row(
            controls=[
                self.campo_busqueda,
                self.valor_busqueda,
                btn_buscar,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
        btn_agregar = ft.ElevatedButton(text="Agregar", on_click=self.abrir_formulario_agregar, icon=ft.Icons.ADD)
        btn_editar = ft.ElevatedButton(text="Editar", on_click=self.abrir_formulario_editar, icon=ft.Icons.EDIT)
        btn_eliminar = ft.ElevatedButton(text="Eliminar", on_click=self.eliminar_cliente, icon=ft.Icons.DELETE)
        button_row = ft.Row(
            controls=[btn_agregar, btn_editar, btn_eliminar],
            spacing=10,
        )
        self.data_table = self.crear_tabla_clientes()
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

    def crear_tabla_clientes(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute("""
                SELECT per.apellido, per.nombre, per.dni, per.direccion, per.tele_contac, c.cod_cliente
                FROM persona per
                INNER JOIN cliente c ON per.dni = c.dni
                ORDER BY per.apellido
            """)
            datos_clientes = self.cursor.fetchall()
            rows = []
            for cliente in datos_clientes:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(cliente[0])),
                            ft.DataCell(ft.Text(cliente[1])),
                            ft.DataCell(ft.Text(str(cliente[2]))),
                            ft.DataCell(ft.Text(cliente[3])),
                            ft.DataCell(ft.Text(cliente[4])),
                            ft.DataCell(ft.Text(str(cliente[5]))),
                        ],
                        on_select_changed=lambda e, dni=cliente[2]: self.seleccionar_cliente(e, dni),
                    )
                )
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Apellido")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("DNI")),
                    ft.DataColumn(ft.Text("Dirección")),
                    ft.DataColumn(ft.Text("Teléfono")),
                    ft.DataColumn(ft.Text("Código")),
                ],
                rows=rows,
            )
        except Exception as e:
            print(f"Error al crear la tabla de clientes: {e}")
            return ft.Text(f"No se pudieron cargar los clientes. Error: {e}")

    def seleccionar_cliente(self, e, dni):
        self.cliente_seleccionado = dni

    def abrir_formulario_agregar(self, e):
        self.txt_nombre = ft.TextField(label="Nombre")
        self.txt_apellido = ft.TextField(label="Apellido")
        self.txt_dni = ft.TextField(label="DNI")
        self.txt_direccion = ft.TextField(label="Dirección")
        self.txt_telefono = ft.TextField(label="Teléfono")

        dialog = ft.AlertDialog(
            title=ft.Text("Agregar Cliente"),
            content=ft.Column([
                self.txt_nombre,
                self.txt_apellido,
                self.txt_dni,
                self.txt_direccion,
                self.txt_telefono,
            ]),
            actions=[
                ft.ElevatedButton("Guardar", on_click=self.guardar_cliente),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def guardar_cliente(self, e):
        nombre = self.txt_nombre.value
        apellido = self.txt_apellido.value
        dni = self.txt_dni.value
        direccion = self.txt_direccion.value
        telefono = self.txt_telefono.value
        try:
            self.cursor.execute(
                "INSERT INTO persona (nombre, apellido, dni, direccion, tele_contac) VALUES (%s, %s, %s, %s, %s)",
                (nombre, apellido, dni, direccion, telefono)
            )
            self.cursor.execute(
                "INSERT INTO cliente (dni) VALUES (%s)",
                (dni,)
            )
            self.connection.commit()
            self.mostrar_clientes()
            self.cerrar_dialogo(self.page.dialog)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def abrir_formulario_editar(self, e):
        if not self.cliente_seleccionado:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecciona un cliente para editar"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        try:
            self.cursor.execute("""
                SELECT per.nombre, per.apellido, per.dni, per.direccion, per.tele_contac
                FROM persona per
                WHERE per.dni = %s
            """, (self.cliente_seleccionado,))
            cliente = self.cursor.fetchone()

            self.txt_nombre = ft.TextField(label="Nombre", value=cliente[0])
            self.txt_apellido = ft.TextField(label="Apellido", value=cliente[1])
            self.txt_dni = ft.TextField(label="DNI", value=str(cliente[2]), disabled=True)
            self.txt_direccion = ft.TextField(label="Dirección", value=cliente[3])
            self.txt_telefono = ft.TextField(label="Teléfono", value=cliente[4])

            dialog = ft.AlertDialog(
                title=ft.Text("Editar Cliente"),
                content=ft.Column([
                    self.txt_nombre,
                    self.txt_apellido,
                    self.txt_dni,
                    self.txt_direccion,
                    self.txt_telefono,
                ]),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=self.actualizar_cliente),
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

    def actualizar_cliente(self, e):
        nombre = self.txt_nombre.value
        apellido = self.txt_apellido.value
        dni = self.txt_dni.value
        direccion = self.txt_direccion.value
        telefono = self.txt_telefono.value
        try:
            self.cursor.execute("""
                UPDATE persona
                SET nombre = %s, apellido = %s, direccion = %s, tele_contac = %s
                WHERE dni = %s
            """, (nombre, apellido, direccion, telefono, dni))
            self.connection.commit()
            self.mostrar_clientes()
            self.cerrar_dialogo(self.page.dialog)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def eliminar_cliente(self, e):
        if not self.cliente_seleccionado:
            self.page.snack_bar = ft.SnackBar(ft.Text("Selecciona un cliente para eliminar"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        try:
            self.cursor.execute("DELETE FROM cliente WHERE dni = %s", (self.cliente_seleccionado,))
            self.cursor.execute("DELETE FROM persona WHERE dni = %s", (self.cliente_seleccionado,))
            self.connection.commit()
            self.mostrar_clientes()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def buscar_clientes(self, e):
        if not self.cursor:
            return
        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value
        try:
            consulta = f"""
                SELECT per.apellido, per.nombre, per.dni, per.direccion, per.tele_contac, c.cod_cliente
                FROM persona per
                INNER JOIN cliente c ON per.dni = c.dni
                WHERE {campo} LIKE %s
                ORDER BY per.apellido
            """
            self.cursor.execute(consulta, (f"%{valor}%",))
            datos_clientes = self.cursor.fetchall()
            rows = []
            for cliente in datos_clientes:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(cliente[0])),
                            ft.DataCell(ft.Text(cliente[1])),
                            ft.DataCell(ft.Text(str(cliente[2]))),
                            ft.DataCell(ft.Text(cliente[3])),
                            ft.DataCell(ft.Text(cliente[4])),
                            ft.DataCell(ft.Text(str(cliente[5]))),
                        ],
                        on_select_changed=lambda e, dni=cliente[2]: self.seleccionar_cliente(e, dni),
                    )
                )
            self.page.controls[0].content.controls[3] = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Apellido")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("DNI")),
                    ft.DataColumn(ft.Text("Dirección")),
                    ft.DataColumn(ft.Text("Teléfono")),
                    ft.DataColumn(ft.Text("Código")),
                ],
                rows=rows,
            )
            self.page.update()
        except Exception as e:
            print(f"Error al buscar clientes: {e}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al buscar: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def cerrar_dialogo(self, dialog):
        dialog.open = False
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_retroceder(self.page)
