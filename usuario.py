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

class Herramienta_Usuario:
    def __init__(self, pagina: ft.Page, volver_menu_principal):
        self.pagina = pagina
        self.volver_menu_principal = volver_menu_principal
        self.conexion = conexiondb()
        self.cursor = self.conexion.cursor() if self.conexion else None
        self.mostrar_usuarios()

    def mostrar_usuarios(self):
        self.pagina.clean()
        self.pagina.title = "Gestión de Usuarios"
        barra_superior = ft.Row(
            controls=[
                ft.Text("Lista de Usuarios", size=20, weight="bold"),
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
                ft.dropdown.Option("Usuario"),
                ft.dropdown.Option("Rol"),
            ],
            value="Usuario",
        )
        self.valor_busqueda = ft.TextField(label="Buscar", width=200)
        boton_buscar = ft.ElevatedButton("Buscar", on_click=self.buscar_usuarios, width=100)
        fila_busqueda = ft.Row(
            controls=[
                self.campo_busqueda,
                self.valor_busqueda,
                boton_buscar,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
        self.tabla_usuarios = self.crear_tabla_usuarios()
        contenido_principal = ft.Column(
            controls=[
                barra_superior,
                fila_busqueda,
                self.tabla_usuarios,
            ],
            spacing=10,
            expand=True
        )
        self.pagina.add(contenido_principal)

    def crear_tabla_usuarios(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute("""
                SELECT usuario, rol, id
                FROM detalle_usuario
                ORDER BY usuario
            """)
            datos_usuarios = self.cursor.fetchall()
            filas = []
            for usuario in datos_usuarios:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(usuario[2]))),  # ID
                            ft.DataCell(ft.Text(usuario[0])),      # Usuario
                            ft.DataCell(ft.Text(usuario[1])),      # Rol
                        ]
                    )
                )
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Usuario")),
                    ft.DataColumn(ft.Text("Rol")),
                ],
                rows=filas,
            )
        except Exception as e:
            print(f"Error al crear la tabla de usuarios: {e}")
            return ft.Text(f"No se pudieron cargar los usuarios. Error: {e}")

    def buscar_usuarios(self, e):
        if not self.cursor:
            return
        campo = self.campo_busqueda.value
        valor = self.valor_busqueda.value
        try:
            consulta = f"""
                SELECT usuario, rol, id
                FROM detalle_usuario
                WHERE {campo} LIKE %s
                ORDER BY usuario
            """
            self.cursor.execute(consulta, (f"%{valor}%",))
            datos_usuarios = self.cursor.fetchall()
            filas = []
            for usuario in datos_usuarios:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(usuario[2]))),  # ID
                            ft.DataCell(ft.Text(usuario[0])),      # Usuario
                            ft.DataCell(ft.Text(usuario[1])),      # Rol
                        ]
                    )
                )
            self.pagina.controls[0].content.controls[2] = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Usuario")),
                    ft.DataColumn(ft.Text("Rol")),
                ],
                rows=filas,
            )
            self.pagina.update()
        except Exception as e:
            print(f"Error al buscar usuarios: {e}")
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al buscar: {e}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
