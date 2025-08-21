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
        self.connection = conexiondb()
        self.cursor = self.connection.cursor() if self.connection else None
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

        # Dropdown y campo de búsqueda
        self.campo_busqueda = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Nombre"),
                ft.dropdown.Option("CUIT"),
            ],
            value="Nombre",
        )

        self.valor_busqueda = ft.TextField(label="Buscar", width=200, on_change=self.buscar_proveedores)
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

        # DataTable para mostrar proveedores
        self.data_table = self.crear_tabla_proveedores()

        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        search_row,
                        self.data_table,
                    ],
                    spacing=10,
                ),
                padding=20,
            )
        )

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_retroceder(self.page)

    def crear_tabla_proveedores(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        self.cursor.execute("""
            SELECT nombre, cuit, direccion, telefono
            FROM proveedor
            ORDER BY nombre
        """)
        datos_proveedores = self.cursor.fetchall()
        rows = []
        for proveedor in datos_proveedores:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proveedor[0])),
                        ft.DataCell(ft.Text(str(proveedor[1]))),
                        ft.DataCell(ft.Text(proveedor[2])),
                        ft.DataCell(ft.Text(proveedor[3])),
                    ]
                )
            )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("CUIT")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
            ],
            rows=rows,
        )

    def buscar_proveedores(self, e):
        if not self.cursor:
            return

        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value

        consulta = f"""
            SELECT nombre, cuit, direccion, telefono
            FROM proveedor
            WHERE {campo} LIKE %s
            ORDER BY nombre
        """
        self.cursor.execute(consulta, (f"%{valor}%",))
        datos_proveedores = self.cursor.fetchall()

        rows = []
        for proveedor in datos_proveedores:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proveedor[0])),
                        ft.DataCell(ft.Text(str(proveedor[1]))),
                        ft.DataCell(ft.Text(proveedor[2])),
                        ft.DataCell(ft.Text(proveedor[3])),
                    ]
                )
            )

        self.page.controls[0].content.controls[2] = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("CUIT")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
            ],
            rows=rows,
        )
        self.page.update()
