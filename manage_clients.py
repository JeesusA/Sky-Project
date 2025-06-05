from json import dump, load, JSONDecodeError
from os import path, makedirs, listdir, remove
from re import match
from logging import basicConfig, INFO, info, error
from datetime import datetime

# Configuracion del logging para trazabilidad
basicConfig(
    level = INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename = 'gestion_clientes.log'
)

# Directorio para almacenar los datos de los clientes
CLIENTES_DIR = "sky_clientes"
CONTADOR_FILE = path.join(CLIENTES_DIR, "contador.txt")
if not path.exists(CLIENTES_DIR):
    makedirs(CLIENTES_DIR)

# Diccionario en memoria para almacenar clientes guardados
clientes = {}

def validate_phone(phone: str) -> bool:
    """
    Valida que el número de télefono tenga exactamente 10 dígitos

    Args:
        phone (str): Número de telefono a validar.

    Returns:
        bool: True si el número es válido, False de lo contrario.
    """
    return bool(match(r'^\d{10}$', phone))

def validate_email(email: str) -> bool:
    """
    Valida que el correo electrónico tenga un formato estándar.

    Args:
        email (str): Correo electrónico a validar.

    Returns:
        bool: True si el correo es válido, False de lo contrario.
    """
    return bool(match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))

def generate_unique_id(nombre: str, apellido: str) -> str:
    """
    Genera un ID único basado en las iniciales del nombre y apellido
    y la fecha de registro

    Args:
        nombre (str): Nombre del cliente.
        apellido (str): Apellido del cliente.

    Returns:
        str: ID único en el formato INICIALES_FECHA (ejemplo: JPD_20250602).
    """

    # Obtiene las inicilaes del nombre y apellido
    iniciales = (nombre[0] + (apellido[0] if apellido else '')).upper()
    # Obtiene la fecha actual en formato AAAAMMDD
    fecha = datetime.now().strftime('%Y%m%d')
    # Combina iniciales y fecha
    base_id = f"{iniciales}_{fecha}"

    # Verifica si el ID ya existe, y añade un sufijo númerico si es necesario
    counter = 1
    unique_id = base_id
    while path.exists(path.join(CLIENTES_DIR, f"cliente_{unique_id}.json")):
        unique_id = f"{base_id}_{counter}"
        counter += 1
    
    return unique_id

def generate_cliente_number() -> str:
    """
    Genera un número de cliente secuencial (ejemplo: C001, C002).
    
    Returns:
        str: Número de cliente en formato CXXX.
    """
    global CONTADOR_CLIENTE
    CONTADOR_CLIENTE += 1
    with open(CONTADOR_FILE, 'w') as f:
        f.write(str(CONTADOR_CLIENTE))
    return f"C{CONTADOR_CLIENTE:03d}"

def guardar_cliente(cliente_id: str, cliente_data: dict) -> None:
    """
    Guarda los datos de un cliente en un archivo JSON.

    Args:
        cliente_id (str): ID único del cliente
        cliente_data (dict): Datos del cliente a guardar.

    Raises:
        IOError: Si hay un error al escribir el archivo.
    """
    try:
        archivo = path.join(CLIENTES_DIR, f"cliente_{cliente_id}.json")
        with open(archivo, 'w') as f:
            dump(cliente_data, f, indent=4)
        info(f"Cliente {cliente_id} guardado exitosamente en {archivo}")
        print(f"Cliente {cliente_id} guardado exitosamente.")
    except IOError as e:
        error(f"Error al guardar cliente {cliente_id}: {e}")
        print(f"Error al guadar al cliente: {e}")

def cargar_cliente(cliente_id: str) -> dict:
    """
    Carga los datos de un cliente desde un archivo JSON.

    Args:
        cliente_id (str): ID del cliente a cargar.

    Returns:
        dict: Datos del cliente, o None si no se encuentra
    """
    try:
        archivo = path.join(CLIENTES_DIR, f"cliente_{cliente_id}.json")
        if path.exists(archivo):
            with open(archivo, 'r') as f:
                return load(f)
    except (IOError, JSONDecodeError) as e:
        error(f"Error al cargar cliente {cliente_id}: {e}")
        return None

def buscar_clientes(criterio: str, valor: str) -> list:
    """
    Buscar clientes por ID o nombre (parcial o completo).

    Args:
        criterio (str): 'numero' para buscar por numero de cliente, 'id' para buscar por ID, 
        'nombre' para buscar por nombre.
        valor (str): Valor a buscar (ID o parte del nombre).

    Returns:
        list: Lista de clientes que coinciden con el criterio
    """
    resultados = []
    for archivo in listdir(CLIENTES_DIR):
        if (archivo.startswith("cliente_") and archivo.endswith(".json")):
            cliente_id = archivo.replace("cliente_", "").replace(".json", "")
            cliente = cargar_cliente(cliente_id)
            if cliente:
                if criterio == 'numero' and cliente.get('numero_cliente', '').lower() == valor.lower():
                    resultados.append((cliente_id, cliente))
                elif criterio == 'id' and cliente_id == valor:
                    resultados.append((cliente_id, cliente))
                elif criterio == 'nombre' and valor.lower() in f"{cliente['nombre']} {cliente['apellido']}".lower():
                    resultados.append((cliente_id, cliente))
    return resultados

def crear_cliente() -> None:
    """
    Crear un nuevo cliente, generando un ID único y validando el contacto.
    """
    try:
        nombre = input("Ingresa el nombre: ").strip()
        if not nombre:
            print("El nombre no puede estar vacío.")
            return
        apellido = input("Ingrese el apellido: ").strip()
        if not apellido:
            print("El apellido no puede estar vacío.")
            return
        
        # Genera un ID único
        cliente_id = generate_unique_id(nombre, apellido)

        tipo = input ("Ingrese el tipo (Persona/Negocio): ").strip().capitalize()
        if tipo not in ["Persona", "Negocio"]:
            print("Tipo inválido. Debe ser 'Persona' o 'Negocio'.")
            return
        
        contacto = input("Ingrese el contacto (teléfono o email): ").strip()
        if validate_phone(contacto):
            info(f"Contacto validado como teléfono: {contacto}")
        elif validate_email(contacto):
            info(f"Contacto validado como email: {contacto}")

        else:
            print("Contacto inválido. El teléfono de tener 10 dígitos o el email debe ser válido.")
            return
        
        numero_cliente = generate_cliente_number()
        # Crea el registro del cliente
        clientes[cliente_id] = {
            "nombre": nombre,
            "apellido": apellido,
            "tipo": tipo, 
            "contacto": contacto, 
            "servicios": [],
            "fecha_registro": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "numero_cliente": numero_cliente
        }
        guardar_cliente(cliente_id, clientes[cliente_id])
        print(f"Cliente creado con ID: {cliente_id} y Número de Cliente: {numero_cliente}")

    except Exception as e:
        error(f"Error al crear cliente: {e}")
        print(f"Error al crear el cliente: {e}")

def leer_cliente() -> None:
    """
    Muestra la información de un cliente existente.
    """
    criterio = input("Buscar por (1) Número de Cliente, (2) ID o (3) Nombre (1/2/3): ").strip()
    if criterio == "1":
        numero_buscar = input("Ingrese el Número de Cliente (ej. C001): ").strip()
        clientes_encontrados = buscar_clientes('numero', numero_buscar)
    elif criterio == "2":
        cliente_id = input("Ingrese el ID del cliente a consultar: ").strip()
        clientes_encontrados = buscar_clientes('id', cliente_id)
    elif criterio == "3":
        nombre_buscar = input("Ingrese el nombre o parte del nombre a consultar:").strip()
        clientes_encontrados = buscar_clientes('nombre', nombre_buscar)
    else:
        print("Opción inválida. Use 1 para ID o 2 para nombre.")
        return

    if clientes_encontrados:
        for cliente_id, cliente in clientes_encontrados:
            print(f"ID: {cliente_id}, Número: {cliente['numero_cliente']}, Nombre: {cliente['nombre']} {cliente['apellido']}, "
                  f"Tipo: {cliente['tipo']}, Contacto: {cliente['contacto']}, "
                  f"Servicios: {cliente['servicios']}, Fecha Registro: {cliente['fecha_registro']}")
    else:
        print("No se encontraron clientes con ese criterio.")

def modificar_cliente() -> None:
    """
    Modifica un cliente existente, permitiendo agregar un servicio.
    """
    criterio = input ("Modificar por (1) Número de Cliente, (2) ID O (3) Nombre (1/2/3): ").strip()
    clientes_encontrados = []
    if criterio == "1":
        numero_buscar = input("Ingrese el Número de Cliente (ej. C001): ").strip()
        clientes_encontrados = buscar_clientes('numero', numero_buscar)
    elif criterio == "2":
        cliente_id = input("Ingrese el ID del cliente a modificar: ").strip()
        clientes_encontrados = buscar_clientes('id', cliente_id)
    elif criterio == "3":
        nombre_buscar = input("Ingrese el nombre o parte del nombre a modificar: ").strip()
        clientes_encontrados = buscar_clientes('nombre', nombre_buscar)
    else:
        print("Opción no válida. Use 1 para Número, 2 para ID o 3 para nombre.")
        return
    
    if not clientes_encontrados:
        print("No se encontraron clientes con ese criterio.")
        return
    elif len(clientes_encontrados) > 1:
        print("Multiples clientes encontrados. Por favor, use el Número de Cliente o ID para mayor precisión:")
        for cliente_id, cliente, in clientes_encontrados:
            print(f"ID: {cliente_id}, Número: {cliente['numero_cliente']}")
        return
    
    cliente_id, cliente = clientes_encontrados[0]
    servicio = input("Ingrese el nuevo servicio a agregar: ").strip()
    if not servicio:
        print("El servicio no puede estar vacío.")
        return
    cliente["servicios"].append(servicio)
    guardar_cliente(cliente_id, cliente)
    print(f"Servicio {servicio} agregado al cliente {cliente_id} (Nombre y Número: {cliente['nombre']} | {cliente['numero_cliente']}.)")

def eliminar_cliente() -> None:
    """
    Elimina un cliente buscando por número, ID o nombre.
    """
    criterio = input("Eliminar por (1) Número de Cliente, (2) ID o (3) Nombre (1/2/3): ").strip()
    clientes_encontrados = []
    if criterio == "1":
        numero_buscar = input("Ingrese el Número de Cliente (ej. C001): ").strip()
        clientes_encontrados = buscar_clientes('numero', numero_buscar)
    elif criterio == "2":
        cliente_id = input("Ingrese el ID del cliente a eliminar: ").strip()
        clientes_encontrados = buscar_clientes('id', cliente_id)
    elif criterio == "3":
        nombre_buscar = input("Ingrese el nombre o parte del nombre a eliminar: ").strip()
        clientes_encontrados = buscar_clientes('nombre', nombre_buscar)
    else:
        print("Opción no válida. Use 1 para Número, 2 para ID o 3 para nombre.")
        return

    if not clientes_encontrados:
        print("No se encontraron clientes con ese criterio.")
        return
    elif len(clientes_encontrados) > 1:
        print("Múltiples clientes encontrados. Por favor, use el Número de Cliente o ID para mayor precisión:")
        for cliente_id, cliente in clientes_encontrados:
            print(f"ID: {cliente_id}, Número: {cliente['numero_cliente']}")
        return

    cliente_id, _ = clientes_encontrados[0]
    archivo = path.join(CLIENTES_DIR, f"cliente_{cliente_id}.json")
    if path.exists(archivo):
        try:
            remove(archivo)
            if cliente_id in clientes:
                del clientes[cliente_id]
            info(f"Cliente {cliente_id} eliminado exitosamente. Contador actualizado a {CONTADOR_CLIENTE}")
            print(f"Cliente {cliente_id} (Número: {clientes_encontrados[0][1]['numero_cliente']}) eliminado.")
        except OSError as e:
            error(f"Error al eliminar cliente {cliente_id}: {e}")
            print(f"Error al eliminar el cliente: {e}")
    else:
        print("Cliente no encontrado.")

def menu() -> None:
    """
    Muestra el menú principal y maneja las opciones del usuario.
    """
    while True:
        print("\n=== Gestión de Clientes Sky ===")
        print("1. Crear cliente")
        print("2. Leer cliente (por Número, ID o Nombre)")
        print("3. Modificar cliente (agregar servicio)")
        print("4. Eliminar cliente")
        print("5. Listar todos los clientes.")
        print("6. Salir")
        opcion = input("Seleccione una opción (1-6): ").strip()
        if opcion == "1":
            crear_cliente()
        elif opcion == "2":
            leer_cliente()
        elif opcion == "3":
            modificar_cliente()
        elif opcion == "4":
            eliminar_cliente()
        elif opcion == "5":
            listar_clientes()
        elif opcion == "6":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción entre 1 y 5.")

def listar_clientes() -> None:
    """
    Lista todos los clientes registrados.
    """
    if not listdir(CLIENTES_DIR):
        print("No hay clientes registrados.")
        return
    for archivo in listdir(CLIENTES_DIR):
        if archivo.startswith("cliente_") and archivo.endswith(".json"):
            cliente_id = archivo.replace("cliente_", "").replace(".json", "")
            cliente = cargar_cliente(cliente_id)
            if cliente:
                print(f"ID: {cliente_id}, Número: {cliente['numero_cliente']}, Nombre: {cliente['nombre']} {cliente['apellido']}, "
                      f"Tipo: {cliente['tipo']}, Contacto: {cliente['contacto']}, Servicios: {cliente['servicios']}")

# Carga o inicializa el contador de clientes
if path.exists(CONTADOR_FILE):
    with open(CONTADOR_FILE, 'r') as f:
        CONTADOR_CLIENTE = int(f.read().strip())
else:
    # Encuentra el número más alto de clientes existentes
    max_num = 0
    for f in listdir(CLIENTES_DIR):
        if f.startswith("cliente_") and f.endswith(".json"):
            cliente = cargar_cliente(f.replace("cliente_", "").replace(".json", ""))
            if cliente and 'numero_cliente' in cliente:
                num = int(cliente['numero_cliente'].replace("C", ""))
                max_num = max(max_num, num)
    CONTADOR_CLIENTE = max_num
    with open(CONTADOR_FILE, 'w') as f:
        f.write(str(CONTADOR_CLIENTE))

if __name__ == "__main__":
    info("Iniciando la aplicación Gestión de Clientes Sky")
    menu()