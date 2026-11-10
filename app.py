from datetime import datetime
from flask import Flask, render_template
import sqlite3
import platform
import subprocess
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "netwatch.db"


def cargar_dispositivos():
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, nombre, ip FROM dispositivos ORDER BY id"
        )

        registros = cursor.fetchall()

    return [
        {"id": registro[0], "nombre": registro[1], "ip": registro[2]}
        for registro in registros
    ]


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


def inicializar_historial():
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_conectividad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_id INTEGER,
                nombre TEXT,
                ip TEXT,
                estado TEXT,
                fecha TEXT
            )
        """)


def registrar_estado(dispositivo):
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT estado
            FROM historial_conectividad
            WHERE dispositivo_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (dispositivo["id"],))

        ultimo_registro = cursor.fetchone()

        estado_actual = dispositivo["estado"]

        if ultimo_registro is None or ultimo_registro[0] != estado_actual:

            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            cursor.execute("""
                INSERT INTO historial_conectividad
                (dispositivo_id, nombre, ip, estado, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (
                dispositivo["id"],
                dispositivo["nombre"],
                dispositivo["ip"],
                estado_actual,
                fecha
            ))


def cargar_historial():
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT nombre, ip, estado, fecha
            FROM historial_conectividad
            ORDER BY id DESC
            LIMIT 10
        """)

        registros = cursor.fetchall()

    return [
        {
            "nombre": registro[0],
            "ip": registro[1],
            "estado": registro[2],
            "fecha": registro[3]
        }
        for registro in registros
    ]


@app.route("/")
def inicio():

    inicializar_historial()

    dispositivos = cargar_dispositivos()

    for dispositivo in dispositivos:

        if comprobar_conectividad(dispositivo["ip"]):
            dispositivo["estado"] = "En línea"
        else:
            dispositivo["estado"] = "Fuera de línea"

        registrar_estado(dispositivo)

    total_dispositivos = len(dispositivos)

    en_linea = sum(
        1 for dispositivo in dispositivos
        if dispositivo["estado"] == "En línea"
    )

    fuera_linea = total_dispositivos - en_linea

    ultima_actualizacion = datetime.now().strftime("%H:%M:%S")

    historial = cargar_historial()

    return render_template(
        "index.html",
        dispositivos=dispositivos,
        ultima_actualizacion=ultima_actualizacion,
        total_dispositivos=total_dispositivos,
        en_linea=en_linea,
        fuera_linea=fuera_linea,
        historial=historial
    )


if __name__ == "__main__":
    app.run(debug=True)