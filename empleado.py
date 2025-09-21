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
        self.empleado_seleccionado = None
        self.mostrar_empleados()

    def mostrar_empleados(self):
        self.pagina.clean()
        self.pagina.title = "Gestión de Empleados"
        btn_agregar = ft.ElevatedButton(text="Agregar", on_click=self.abrir_formulario_agregar, icon=ft.Icons.ADD)
        btn_editar = ft.ElevatedButton(text="Editar", on_click=self.abrir_formulario_editar, icon=ft.Icons.EDIT)
        btn_eliminar = ft.ElevatedButton(text="Eliminar", on_click=self.eliminar_empleado, icon=ft.Icons.DELETE)
        barra_superior = ft.Row(
            controls=[
                ft.Text("Lista de Empleados", size=20, weight="bold"),
                ft.ElevatedButton("Volver al Menú", on_click=lambda e: self.volver_menu_principal(self.pagina)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        fila_botones = ft.Row(
            controls=[btn_agregar, btn_editar, btn_eliminar],
            spacing=10,
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
                fila_botones,
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
                        ],
                        on_select_changed=lambda e, dni=empleado[2]: self.seleccionar_empleado(e, dni),
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

    def seleccionar_empleado(self, e, dni):
        self.empleado_seleccionado = dni

    def abrir_formulario_agregar(self, e):
        self.txt_nombre = ft.TextField(label="Nombre")
        self.txt_apellido = ft.TextField(label="Apellido")
        self.txt_dni = ft.TextField(label="DNI")
        self.txt_direccion = ft.TextField(label="Dirección")
        self.txt_telefono = ft.TextField(label="Teléfono")
        self.txt_puesto = ft.TextField(label="Puesto")

        dialog = ft.AlertDialog(
            title=ft.Text("Agregar Empleado"),
            content=ft.Column([
                self.txt_nombre,
                self.txt_apellido,
                self.txt_dni,
                self.txt_direccion,
                self.txt_telefono,
                self.txt_puesto,
            ]),
            actions=[
                ft.ElevatedButton("Guardar", on_click=self.guardar_empleado),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.cerrar_dialogo(dialog)),
            ],
        )
        self.pagina.dialog = dialog
        dialog.open = True
        self.pagina.update()

    def guardar_empleado(self, e):
        nombre = self.txt_nombre.value
        apellido = self.txt_apellido.value
        dni = self.txt_dni.value
        direccion = self.txt_direccion.value
        telefono = self.txt_telefono.value
        puesto = self.txt_puesto.value
        try:
            self.cursor.execute(
                "INSERT INTO persona (nombre, apellido, dni, direccion, tele_contac) VALUES (%s, %s, %s, %s, %s)",
                (nombre, apellido, dni, direccion, telefono)
            )
            self.cursor.execute(
                "INSERT INTO empleado (dni, puesto) VALUES (%s, %s)",
                (dni, puesto)
            )
            self.conexion.commit()
            self.mostrar_empleados()
            self.cerrar_dialogo(self.pagina.dialog)
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def abrir_formulario_editar(self, e):
        if not self.empleado_seleccionado:
            self.pagina.snack_bar = ft.SnackBar(ft.Text("Selecciona un empleado para editar"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return
        try:
            self.cursor.execute("""
                SELECT p.nombre, p.apellido, p.dni, p.direccion, p.tele_contac, e.puesto
                FROM persona p
                INNER JOIN empleado e ON p.dni = e.dni
                WHERE p.dni = %s
            """, (self.empleado_seleccionado,))
            empleado = self.cursor.fetchone()

            self.txt_nombre = ft.TextField(label="Nombre", value=empleado[0])
            self.txt_apellido = ft.TextField(label="Apellido", value=empleado[1])
            self.txt_dni = ft.TextField(label="DNI", value=str(empleado[2]), disabled=True)
            self.txt_direccion = ft.TextField(label="Dirección", value=empleado[3])
            self.txt_telefono = ft.TextField(label="Teléfono", value=empleado[4])
            self.txt_puesto = ft.TextField(label="Puesto", value=empleado[5])

            dialog = ft.AlertDialog(
                title=ft.Text("Editar Empleado"),
                content=ft.Column([
                    self.txt_nombre,
                    self.txt_apellido,
                    self.txt_dni,
                    self.txt_direccion,
                    self.txt_telefono,
                    self.txt_puesto,
                ]),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=self.actualizar_empleado),
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

    def actualizar_empleado(self, e):
        nombre = self.txt_nombre.value
        apellido = self.txt_apellido.value
        dni = self.txt_dni.value
        direccion = self.txt_direccion.value
        telefono = self.txt_telefono.value
        puesto = self.txt_puesto.value
        try:
            self.cursor.execute("""
                UPDATE persona
                SET nombre = %s, apellido = %s, direccion = %s, tele_contac = %s
                WHERE dni = %s
            """, (nombre, apellido, direccion, telefono, dni))
            self.cursor.execute("""
                UPDATE empleado
                SET puesto = %s
                WHERE dni = %s
            """, (puesto, dni))
            self.conexion.commit()
            self.mostrar_empleados()
            self.cerrar_dialogo(self.pagina.dialog)
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def eliminar_empleado(self, e):
        if not self.empleado_seleccionado:
            self.pagina.snack_bar = ft.SnackBar(ft.Text("Selecciona un empleado para eliminar"))
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return
        try:
            self.cursor.execute("DELETE FROM empleado WHERE dni = %s", (self.empleado_seleccionado,))
            self.cursor.execute("DELETE FROM persona WHERE dni = %s", (self.empleado_seleccionado,))
            self.conexion.commit()
            self.mostrar_empleados()
        except Exception as ex:
            self.pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.pagina.snack_bar.open = True
            self.pagina.update()

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
                        ],
                        on_select_changed=lambda e, dni=empleado[2]: self.seleccionar_empleado(e, dni),
                    )
                )
            self.pagina.controls[0].content.controls[3] = ft.DataTable(
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

    def cerrar_dialogo(self, dialog):
        dialog.open = False
        self.pagina.update()
