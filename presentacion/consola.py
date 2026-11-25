from maskpass import askpass

from auxiliares.mensajes import CREDENCIALES_INVALIDAS
from auxiliares.validaciones import entero_no_negativo
from negocio import taller, usuarios

NOMBRES_ENTIDADES = {
    "taller": "Talleres",
    "cliente": "Clientes",
    "mecanico": "Mecánicos",
    "vehiculo": "Vehículos",
    "automovil": "Automóviles",
    "camioneta": "Camionetas",
    "proveedor": "Proveedores",
    "repuesto": "Repuestos",
    "mantencion": "Mantenciones",
    "detalle_mantencion": "Repuestos usados en mantenciones",
    "factura": "Facturas",
    "usuario": "Usuarios",
}


def leer_contrasena(mensaje):
    return askpass(prompt=mensaje, mask="*")


def leer_datos_usuario(actual=None):
    sugerencia = f" [{actual['nombre_usuario']}]" if actual else ""
    nombre = input(f"Nombre de usuario{sugerencia}: ").strip()
    if actual and not nombre:
        nombre = actual["nombre_usuario"]
    mensaje = "Contraseña (Enter para conservarla): " if actual else "Contraseña: "
    contrasena = leer_contrasena(mensaje)
    if contrasena and contrasena != leer_contrasena("Confirma la contraseña: "):
        raise ValueError("Las contraseñas no coinciden.")
    return nombre, contrasena


def login():
    while not usuarios.hay_usuarios():
        print("\nCrea la primera cuenta.")
        try:
            usuarios.guardar_usuario(*leer_datos_usuario())
        except ValueError as error:
            print(error)
    while True:
        print("\nInicio de sesión")
        nombre = input("Usuario (Enter para salir): ").strip()
        if not nombre:
            return None
        id_usuario = usuarios.autenticar(nombre, leer_contrasena("Contraseña: "))
        if id_usuario is not None:
            return id_usuario
        print(CREDENCIALES_INVALIDAS)


def mostrar_registro(registro):
    for nombre, valor in registro.items():
        print(f"  {nombre.replace('_', ' ')}: {valor if valor is not None else '(vacío)'}")


def mostrar_listado(registros):
    if not registros:
        print("Todavía no hay registros.")
    for registro in registros:
        print()
        mostrar_registro(registro)


def leer_id():
    return entero_no_negativo(input("ID del registro: "), "El ID")


def leer_datos(entidad, actual=None):
    datos = {}
    for nombre, etiqueta in taller.campos_formulario(entidad).items():
        valor_actual = None if actual is None else actual.get(nombre, actual.get(f"{nombre}_id"))
        if isinstance(valor_actual, bool):
            valor_actual = "s" if valor_actual else "n"
        sugerencia = ""
        if actual is not None:
            visible = valor_actual if valor_actual is not None else "vacío"
            sugerencia = f" [{visible}]"
        valor = input(f"{etiqueta}{sugerencia}: ").strip()
        if actual is None or valor:
            datos[nombre] = "" if actual is not None and valor == "-" else valor
    return datos


def operar_entidad(entidad, opcion):
    if opcion == "1":
        id_registro = taller.guardar(entidad, leer_datos(entidad))
        print(f"Registro creado con ID {id_registro}.")
    elif opcion == "2":
        mostrar_listado(taller.listar(entidad))
    elif opcion == "3":
        mostrar_registro(taller.buscar(entidad, leer_id()))
    elif opcion == "4":
        id_registro = leer_id()
        actual = taller.buscar(entidad, id_registro)
        print("Enter conserva el valor. Escribe - para vaciar un campo opcional.")
        taller.guardar(entidad, leer_datos(entidad, actual), id_registro)
        print("Registro actualizado.")
    elif opcion == "5":
        id_registro = leer_id()
        if input("¿Eliminar el registro? (s/n): ").strip().lower() == "s":
            taller.eliminar(entidad, id_registro)
            print("Registro eliminado.")


def operar_usuarios(opcion, id_usuario_actual):
    if opcion == "1":
        usuarios.guardar_usuario(*leer_datos_usuario())
        print("Usuario creado.")
    elif opcion == "2":
        mostrar_listado(usuarios.listar_usuarios())
    elif opcion == "3":
        mostrar_registro(usuarios.buscar_usuario(leer_id()))
    elif opcion == "4":
        id_usuario = leer_id()
        actual = usuarios.buscar_usuario(id_usuario)
        usuarios.guardar_usuario(*leer_datos_usuario(actual), id_usuario)
        print("Usuario actualizado.")
    elif opcion == "5":
        id_usuario = leer_id()
        if input("¿Eliminar el usuario? (s/n): ").strip().lower() == "s":
            usuarios.eliminar_usuario(id_usuario, id_usuario_actual)
            print("Usuario eliminado.")


def menu_entidad(entidad, id_usuario_actual):
    while True:
        print(f"\n{NOMBRES_ENTIDADES[entidad]}")
        print("1. Crear\n2. Listar\n3. Buscar por ID\n4. Modificar\n5. Eliminar\n0. Volver")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        if opcion not in ("1", "2", "3", "4", "5"):
            print("Opción inválida.")
            continue
        try:
            if entidad == "usuario":
                operar_usuarios(opcion, id_usuario_actual)
            else:
                operar_entidad(entidad, opcion)
        except ValueError as error:
            print(error)


def menu_principal(id_usuario_actual):
    entidades = list(NOMBRES_ENTIDADES)
    while True:
        print("\nTaller mecánico")
        for numero, entidad in enumerate(entidades, start=1):
            print(f"{numero}. {NOMBRES_ENTIDADES[entidad]}")
        print("0. Salir")
        try:
            opcion = entero_no_negativo(input("Opción: "), "La opción")
            if opcion == 0:
                return
            if opcion > len(entidades):
                raise ValueError("Opción inválida.")
            menu_entidad(entidades[opcion - 1], id_usuario_actual)
        except ValueError as error:
            print(error)


def ejecutar():
    try:
        taller.iniciar_base_datos()
        id_usuario = login()
        if id_usuario is not None:
            menu_principal(id_usuario)
    except RuntimeError as error:
        print(error)
    except (KeyboardInterrupt, EOFError):
        print("\nAplicación cerrada.")
    finally:
        taller.cerrar_base_datos()
