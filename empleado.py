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

class Herramienta_Empleado:
    def __init__(self, pagina: ft.Page, volver_menu_principal):
        self.pagina = pagina
        self.volver_menu_principal = volver_menu_principal
        self.conexion = conexiondb()
        self.cursor = self.conexion.cursor() if self.conexion else None
        self.mostrar_empleados()

    def mostrar_empleados(self):
        self.pagina.clean()
        self.pagina.title = "Gestión de Empleados"

        barra_superior = ft.Row(
            controls=[
                ft.Text("Lista de Empleados", size=20, weight="bold"),
                ft.ElevatedButton("Volver al Menú", on_click=lambda e: self.volver_menu_principal(self.pagina)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.campo_busqueda = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Apellido"),
                ft.dropdown.Option("Nombre"),
                ft.dropdown.Option("DNI"),
                ft.dropdown.Option("Puesto"),
            ],
            value="Apellido",
        )

        self.valor_busqueda = ft.TextField(label="Buscar", width=200)
        boton_buscar = ft.ElevatedButton("Buscar", on_click=self.buscar_empleados, width=100)

        fila_busqueda = ft.Row(
            controls=[
                self.campo_busqueda,
                self.valor_busqueda,
                boton_buscar,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        self.tabla_empleados = self.crear_tabla_empleados()

        contenido_principal = ft.Column(
            controls=[
                barra_superior,
                fila_busqueda,
                self.tabla_empleados,
            ],
            spacing=10,
            expand=True
        )

        self.pagina.add(contenido_principal)

    def crear_tabla_empleados(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        try:
            self.cursor.execute("""
                SELECT p.apellido, p.nombre, p.dni, e.cod_empleado, e.puesto
                FROM persona p
                INNER JOIN empleado e ON p.dni = e.dni
                ORDER BY p.apellido
            """)
            datos_empleados = self.cursor.fetchall()
            filas = []
            for empleado in datos_empleados:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(empleado[0])),
                            ft.DataCell(ft.Text(empleado[1])),
                            ft.DataCell(ft.Text(str(empleado[2]))),
                            ft.DataCell(ft.Text(str(empleado[3]))),
                            ft.DataCell(ft.Text(empleado[4])),
                        ]
                    )
                )
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Apellido")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("DNI")),
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Puesto")),
                ],
                rows=filas,
            )
        except Exception as e:
            print(f"Error al crear la tabla de empleados: {e}")
            return ft.Text(f"No se pudieron cargar los empleados. Error: {e}")

    def buscar_empleados(self, e):
        if not self.cursor:
            return

        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value

        try:
            consulta = f"""
                SELECT p.apellido, p.nombre, p.dni, e.cod_empleado, e.puesto
                FROM persona p
                INNER JOIN empleado e ON p.dni = e.dni
                WHERE {campo} LIKE %s
                ORDER BY p.apellido
            """
            self.cursor.execute(consulta, (f"%{valor}%",))
            datos_empleados = self.cursor.fetchall()

            filas = []
            for empleado in datos_empleados:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(empleado[0])),
                            ft.DataCell(ft.Text(empleado[1])),
                            ft.DataCell(ft.Text(str(empleado[2]))),
                            ft.DataCell(ft.Text(str(empleado[3]))),
                            ft.DataCell(ft.Text(empleado[4])),
                        ]
                    )
                )

            self.pagina.controls[0].content.controls[2] = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Apellido")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("DNI")),
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Puesto")),
                ],
                rows=filas,
            )
            self.pagina.update()
        except Exception as e:
            print(f"Error al buscar empleados: {e}")
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al buscar: {e}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
