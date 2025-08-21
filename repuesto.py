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
        self.mostrar_repuestos()

    def mostrar_repuestos(self):
        self.pagina.clean()
        self.pagina.title = "Gestión de Repuestos"

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
                        ]
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
                        ]
                    )
                )

            self.pagina.controls[0].content.controls[2] = ft.DataTable(
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