import flet as ft
import mysql.connector
from cliente import Herramienta_Cliente
from usuario import Herramienta_Usuario
from proveedor import Herramienta_Proveedor
from repuesto import Herramienta_Repuesto
from empleado import Herramienta_Empleado

def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            database='Taller_Mecanico',
            ssl_disabled=True
        )
        if conexion.is_connected():
            print('Conexión exitosa a la base de datos')
            return conexion
    except Exception as error:
        print('Error de conexión:', error)
        return None

conexion_base_datos = conectar_base_datos()
if conexion_base_datos is None:
    print("No se pudo conectar a la base de datos. Verifica las credenciales.")
else:
    cursor = conexion_base_datos.cursor()

def pantalla_identificacion(pagina: ft.Page):
    pagina.clean()
    pagina.title = "Login - Taller Mecánico"
    pagina.window.maximized = True
    pagina.window_resizable = False
    pagina.window_center = True

    campo_usuario = ft.TextField(label="Usuario", width=200)
    campo_contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=200)

    def iniciar_sesion(evento):
        if not campo_usuario.value or not campo_contrasena.value:
            pagina.snack_bar = ft.SnackBar(ft.Text("Usuario y contraseña son obligatorios!"))
            pagina.snack_bar.open = True
            pagina.update()
            return
        try:
            consulta = "SELECT usuario, contrasena FROM detalle_usuario WHERE usuario=%s AND contrasena=%s"
            cursor.execute(consulta, (campo_usuario.value, campo_contrasena.value))
            datos_usuario = cursor.fetchone()
            if datos_usuario:
                pagina.clean()
                pantalla_menu_principal(pagina)
            else:
                pagina.snack_bar = ft.SnackBar(ft.Text("Usuario o contraseña incorrectos!"))
                pagina.snack_bar.open = True
                pagina.update()
        except Exception as ex:
            print(f"Error al iniciar sesión: {ex}")
            pagina.snack_bar = ft.SnackBar(ft.Text(f"Error al iniciar sesión: {ex}"))
            pagina.snack_bar.open = True
            pagina.update()

    boton_iniciar_sesion = ft.ElevatedButton(text="Iniciar sesión", on_click=iniciar_sesion, width=200)

    contenido_formulario = ft.Column(
        controls=[
            ft.Text("Iniciar Sesión", size=20, weight=ft.FontWeight.BOLD),
            campo_usuario,
            campo_contrasena,
            boton_iniciar_sesion,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
        expand=True
    )

    contenedor_principal = ft.Container(
        content=contenido_formulario,
        alignment=ft.alignment.center,
        expand=True,
    )

    pagina.add(contenedor_principal)

def pantalla_menu_principal(pagina: ft.Page):
    pagina.clean()
    pagina.window.maximized = True
    pagina.title = "Administración de Taller Mecánico"

    icono_cliente = ft.Icons.PEOPLE
    icono_proveedor = ft.Icons.BUSINESS
    icono_repuesto = ft.Icons.BUILD
    icono_empleado = ft.Icons.WORK
    icono_usuario = ft.Icons.PERSON
    icono_ficha_tecnica = ft.Icons.DESCRIPTION
    icono_presupuesto = ft.Icons.RECEIPT
    icono_salir = ft.Icons.EXIT_TO_APP

    menu_archivo = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Salir", icon=icono_salir, on_click=lambda evento: pantalla_identificacion(pagina)),
        ],
        content=ft.Text("Archivo"),
        tooltip="Archivo"
    )

    menu_herramientas = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Clientes", icon=icono_cliente, on_click=lambda evento: abrir_modulo_cliente(evento, pagina)),
            ft.PopupMenuItem(text="Proveedores", icon=icono_proveedor, on_click=lambda evento: abrir_modulo_proveedor(evento, pagina)),
            ft.PopupMenuItem(text="Repuestos", icon=icono_repuesto, on_click=lambda evento: abrir_modulo_repuesto(evento, pagina)),
            ft.PopupMenuItem(text="Empleados", icon=icono_empleado, on_click=lambda evento: abrir_modulo_empleado(evento, pagina)),
            ft.PopupMenuItem(text="Usuarios", icon=icono_usuario, on_click=lambda evento: abrir_modulo_usuario(evento, pagina)),
        ],
        content=ft.Text("Herramientas"),
        tooltip="Administrador de archivos maestros"
    )

    menu_administracion = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Ficha Técnica", icon=icono_ficha_tecnica),
            ft.PopupMenuItem(text="Presupuesto", icon=icono_presupuesto),
        ],
        content=ft.Text("Administración"),
        tooltip="Administración de presupuesto y ficha técnica"
    )

    boton_cliente = ft.IconButton(icon=icono_cliente, tooltip="Clientes", on_click=lambda evento: abrir_modulo_cliente(evento, pagina))
    boton_proveedor = ft.IconButton(icon=icono_proveedor, tooltip="Proveedores", on_click=lambda evento: abrir_modulo_proveedor(evento, pagina))
    boton_repuesto = ft.IconButton(icon=icono_repuesto, tooltip="Repuestos", on_click=lambda evento: abrir_modulo_repuesto(evento, pagina))
    boton_empleado = ft.IconButton(icon=icono_empleado, tooltip="Empleados", on_click=lambda evento: abrir_modulo_empleado(evento, pagina))
    boton_usuario = ft.IconButton(icon=icono_usuario, tooltip="Usuarios", on_click=lambda evento: abrir_modulo_usuario(evento, pagina))

    contenido_principal = ft.Column(
        controls=[
            ft.Row(
                controls=[menu_archivo, menu_administracion, menu_herramientas],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Row(
                controls=[boton_cliente, boton_proveedor, boton_repuesto, boton_empleado, boton_usuario],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text("Seleccione una opción del menú", size=16),
        ],
        spacing=20,
        expand=True
    )

    pagina.add(contenido_principal)
    pagina.update()

def abrir_modulo_cliente(evento, pagina):
    pagina.clean()
    Herramienta_Cliente(pagina, pantalla_menu_principal)

def abrir_modulo_proveedor(evento, pagina):
    pagina.clean()
    Herramienta_Proveedor(pagina, pantalla_menu_principal)

def abrir_modulo_repuesto(evento, pagina):
    pagina.clean()
    Herramienta_Repuesto(pagina, pantalla_menu_principal)

def abrir_modulo_empleado(evento, pagina):
    pagina.clean()
    Herramienta_Empleado(pagina, pantalla_menu_principal)

def abrir_modulo_usuario(evento, pagina):
    pagina.clean()
    Herramienta_Usuario(pagina, pantalla_menu_principal)

def main(pagina: ft.Page):
    pantalla_identificacion(pagina)

ft.app(target=main)
