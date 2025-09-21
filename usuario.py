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
        self.usuario_seleccionado = None
        self.mostrar_usuarios()

    def mostrar_usuarios(self):
        self.pagina.clean()
        self.pagina.title = "Gestión de Usuarios"
        btn_agregar = ft.ElevatedButton(text="Agregar", on_click=self.abrir_formulario_agregar, icon=ft.Icons.ADD)
        btn_editar = ft.ElevatedButton(text="Editar", on_click=self.abrir_formulario_editar, icon=ft.Icons.EDIT)
        btn_eliminar = ft.ElevatedButton(text="Eliminar", on_click=self.eliminar_usuario, icon=ft.Icons.DELETE)
        button_row = ft.Row(
            controls=[btn_agregar, btn_editar, btn_eliminar],
            spacing=10,
        )
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
                button_row,
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
                            ft.DataCell(ft.Text(str(usuario[2]))),
                            ft.DataCell(ft.Text(usuario[0])),
                            ft.DataCell(ft.Text(usuario[1])),
                        ],
                        on_select_changed=lambda e, id=usuario[2]: self.seleccionar_usuario(e, id),
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

    def seleccionar_usuario(self, e, id):
        self.usuario_seleccionado = id

    def abrir_formulario_agregar(self, e):
        self.txt_usuario = ft.TextField(label="Usuario")
        self.txt_contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
        self.txt_rol = ft.TextField(label="Rol")

        dialog = ft.AlertDialog(
            title=ft.Text("Agregar Usuario"),
            content=ft.Column([
                self.txt_usuario,
                self.txt_contrasena,
                self.txt_rol,
            ]),
            actions=[
                ft.ElevatedButton("Guardar", on_click=self.guardar_usuario),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
            ],
        )
        self.pagina.dialog = dialog
        dialog.open = True
        self.pagina.update()

    def guardar_usuario(self, e):
        usuario = self.txt_usuario.value
        contrasena = self.txt_contrasena.value
        rol = self.txt_rol.value
        try:
            self.cursor.execute(
                "INSERT INTO detalle_usuario (usuario, contrasena, rol) VALUES (%s, %s, %s)",
                (usuario, contrasena, rol)
            )
            self.conexion.commit()
            self.mostrar_usuarios()
            self.cerrar_dialogo(self.pagina.dialog)
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def abrir_formulario_editar(self, e):
        if not self.usuario_seleccionado:
            self.pagina.snack_bar = ft.SnackBar(ft.Text("Selecciona un usuario para editar"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return
        try:
            self.cursor.execute("""
                SELECT usuario, rol, contrasena
                FROM detalle_usuario
                WHERE id = %s
            """, (self.usuario_seleccionado,))
            usuario = self.cursor.fetchone()

            self.txt_usuario = ft.TextField(label="Usuario", value=usuario[0])
            self.txt_contrasena = ft.TextField(label="Contraseña", value=usuario[2], password=True, can_reveal_password=True)
            self.txt_rol = ft.TextField(label="Rol", value=usuario[1])

            dialog = ft.AlertDialog(
                title=ft.Text("Editar Usuario"),
                content=ft.Column([
                    self.txt_usuario,
                    self.txt_contrasena,
                    self.txt_rol,
                ]),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=self.actualizar_usuario),
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

    def actualizar_usuario(self, e):
        usuario = self.txt_usuario.value
        contrasena = self.txt_contrasena.value
        rol = self.txt_rol.value
        try:
            self.cursor.execute("""
                UPDATE detalle_usuario
                SET usuario = %s, contrasena = %s, rol = %s
                WHERE id = %s
            """, (usuario, contrasena, rol, self.usuario_seleccionado))
            self.conexion.commit()
            self.mostrar_usuarios()
            self.cerrar_dialogo(self.pagina.dialog)
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def eliminar_usuario(self, e):
        if not self.usuario_seleccionado:
            self.pagina.snack_bar = ft.SnackBar(ft.Text("Selecciona un usuario para eliminar"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return
        try:
            self.cursor.execute("DELETE FROM detalle_usuario WHERE id = %s", (self.usuario_seleccionado,))
            self.conexion.commit()
            self.mostrar_usuarios()
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

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
                            ft.DataCell(ft.Text(str(usuario[2]))),
                            ft.DataCell(ft.Text(usuario[0])),
                            ft.DataCell(ft.Text(usuario[1])),
                        ],
                        on_select_changed=lambda e, id=usuario[2]: self.seleccionar_usuario(e, id),
                    )
                )
            self.pagina.controls[0].content.controls[3] = ft.DataTable(
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

    def cerrar_dialogo(self, dialog):
        dialog.open = False
        self.pagina.update()
