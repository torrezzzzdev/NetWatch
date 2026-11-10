import subprocess
import platform
import csv
import sqlite3
import ipaddress
import time
from datetime import datetime


def inicializar_base_datos():
    with sqlite3.connect("netwatch.db") as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispositivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ip TEXT NOT NULL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM dispositivos")
        cantidad = cursor.fetchone()[0]

        if cantidad == 0:
            dispositivos_iniciales = [
                ("DNS Google", "8.8.8.8"),
                ("DNS Cloudflare", "1.1.1.1"),
                ("Router local", "192.168.1.1")
            ]

            cursor.executemany(
                "INSERT INTO dispositivos (nombre, ip) VALUES (?, ?)",
                dispositivos_iniciales
            )


def cargar_dispositivos():
    with sqlite3.connect("netwatch.db") as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, nombre, ip FROM dispositivos ORDER BY id"
        )

        registros = cursor.fetchall()

    return [
        {"id": registro[0], "nombre": registro[1], "ip": registro[2]}
        for registro in registros
    ]


def agregar_dispositivo():
    nombre = input("Nombre del dispositivo: ").strip()
    ip = input("Dirección IP del dispositivo: ").strip()

    if not nombre or not ip:
        print("Error: el nombre y la IP son obligatorios.")
        return

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print("Error: la dirección IP no es válida.")
        return

    try:
        with sqlite3.connect("netwatch.db") as conexion:
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT 1 FROM dispositivos WHERE ip = ?",
                (ip,)
            )

            if cursor.fetchone():
                print("Error: ya existe un dispositivo registrado con esa IP.")
                return

            cursor.execute(
                "INSERT INTO dispositivos (nombre, ip) VALUES (?, ?)",
                (nombre, ip)
            )

        print(f"Dispositivo '{nombre}' guardado correctamente.")

    except sqlite3.Error as error:
        print(f"No se pudo guardar el dispositivo: {error}")


def mostrar_dispositivos():
    dispositivos = cargar_dispositivos()

    print("\n========== INVENTARIO NETWATCH ==========")

    if not dispositivos:
        print("No hay dispositivos registrados.")
    else:
        for dispositivo in dispositivos:
            print(
                f"ID: {dispositivo['id']} | "
                f"Nombre: {dispositivo['nombre']} | "
                f"IP: {dispositivo['ip']}"
            )

    print("=========================================")


def guardar_resultado(nombre, ip, estado):
    try:
        try:
            with open("historial.csv", "r", encoding="utf-8-sig") as archivo:
                archivo_vacio = archivo.read(1) == ""
        except FileNotFoundError:
            archivo_vacio = True

        with open(
            "historial.csv",
            "a",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:
            escritor = csv.writer(archivo)

            if archivo_vacio:
                escritor.writerow([
                    "Fecha y hora",
                    "Dispositivo",
                    "IP",
                    "Estado"
                ])

            escritor.writerow([
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                nombre,
                ip,
                estado
            ])

    except OSError as error:
        print(f"No se pudo guardar el historial: {error}")


def comprobar_conectividad(ip):
    if platform.system() == "Windows":
        comando = ["ping", "-n", "1", "-w", "2000", ip]
    else:
        comando = ["ping", "-c", "1", ip]

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=5
        )

        return resultado.returncode == 0

    except (subprocess.TimeoutExpired, OSError):
        return False


def monitorear_dispositivos():
    dispositivos = cargar_dispositivos()

    if not dispositivos:
        print("No hay dispositivos registrados para monitorear.")
        return

    print("\n" + "=" * 75)
    print("             NETWATCH - MONITOREO CONTINUO")
    print("=" * 75)
    print(f"Dispositivos registrados: {len(dispositivos)}")
    print("Intervalo de monitoreo: 30 segundos")
    print("Presiona Ctrl + C para detener el monitoreo.")
    print("=" * 75)

    try:
        while True:
            print(f"\nFecha y hora: {datetime.now():%d/%m/%Y %H:%M:%S}")
            print("-" * 75)

            for dispositivo in dispositivos:
                nombre = dispositivo["nombre"]
                ip = dispositivo["ip"]

                disponible = comprobar_conectividad(ip)
                estado = "EN LINEA" if disponible else "SIN RESPUESTA"

                guardar_resultado(nombre, ip, estado)

                print(f"{nombre:20} | IP: {ip:15} | {estado}")

            print("-" * 75)
            print("Siguiente revisión en 30 segundos...")

            time.sleep(30)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
        print("Los resultados anteriores se conservaron en historial.csv.")


def mostrar_reporte():
    resumen = {}

    try:
        with open(
            "historial.csv",
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:

            lector = csv.DictReader(archivo)

            if not lector.fieldnames:
                print("El historial está vacío. Ejecuta primero el monitoreo.")
                return

            columnas = {"Dispositivo", "Estado"}

            if not columnas.issubset(lector.fieldnames):
                print("Error: el historial no tiene las columnas esperadas.")
                print("Encabezados encontrados:", lector.fieldnames)
                return

            for registro in lector:
                nombre = registro["Dispositivo"]
                estado = registro["Estado"]

                if nombre not in resumen:
                    resumen[nombre] = {
                        "total": 0,
                        "en_linea": 0,
                        "sin_respuesta": 0
                    }

                resumen[nombre]["total"] += 1

                if estado == "EN LINEA":
                    resumen[nombre]["en_linea"] += 1
                elif estado == "SIN RESPUESTA":
                    resumen[nombre]["sin_respuesta"] += 1

    except FileNotFoundError:
        print("Todavía no existe el archivo historial.csv.")
        return

    except OSError as error:
        print(f"No se pudo leer el historial: {error}")
        return

    if not resumen:
        print("No hay registros para generar el reporte.")
        return

    print("\n" + "=" * 75)
    print("          NETWATCH - REPORTE DE DISPONIBILIDAD")
    print("=" * 75)

    for nombre, datos in resumen.items():
        total = datos["total"]
        en_linea = datos["en_linea"]
        sin_respuesta = datos["sin_respuesta"]

        disponibilidad = (en_linea / total) * 100
        porcentaje_fallos = (sin_respuesta / total) * 100

        print(f"\nDispositivo: {nombre}")
        print(f"Total de revisiones: {total}")
        print(f"En línea: {en_linea}")
        print(f"Sin respuesta: {sin_respuesta}")
        print(f"Disponibilidad registrada: {disponibilidad:.2f}%")
        print(f"Porcentaje de fallos: {porcentaje_fallos:.2f}%")

        if porcentaje_fallos > 20:
            print(
                "ADVERTENCIA: El dispositivo presenta varios "
                "fallos de conexión."
            )
        elif porcentaje_fallos > 0:
            print(
                "AVISO: El dispositivo tuvo algunos fallos "
                "de conexión."
            )
        else:
            print(
                "ESTADO ESTABLE: El dispositivo respondió "
                "a todas las revisiones."
            )

    print("\n" + "=" * 75)


def menu_principal():
    while True:
        print("\n=========================================")
        print("       NETWATCH - MONITOREO DE RED")
        print("=========================================")
        print("1. Ver dispositivos")
        print("2. Agregar dispositivo")
        print("3. Iniciar monitoreo")
        print("4. Ver reporte de disponibilidad")
        print("5. Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            mostrar_dispositivos()
        elif opcion == "2":
            agregar_dispositivo()
        elif opcion == "3":
            monitorear_dispositivos()
        elif opcion == "4":
            mostrar_reporte()
        elif opcion == "5":
            print("Cerrando NetWatch...")
            break
        else:
            print("Opción no válida. Elige del 1 al 5.")


if __name__ == "__main__":
    inicializar_base_datos()
    menu_principal()