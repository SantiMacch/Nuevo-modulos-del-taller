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

        # Dropdown y campo de búsqueda
        self.campo_busqueda = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Apellido"),
                ft.dropdown.Option("Nombre"),
                ft.dropdown.Option("DNI"),
            ],
            value="Apellido",
        )

        self.valor_busqueda = ft.TextField(label="Buscar", width=200, on_change=self.buscar_clientes)
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

        # DataTable para mostrar clientes
        self.data_table = self.crear_tabla_clientes()

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

    def crear_tabla_clientes(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

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
                    ]
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

    def buscar_clientes(self, e):
        if not self.cursor:
            return

        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value

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
                    ]
                )
            )

        self.page.controls[0].content.controls[2] = ft.DataTable(
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
