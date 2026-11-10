# NetWatch – Network Monitoring System

NetWatch es una aplicación web desarrollada en Python que permite monitorear la conectividad de dispositivos dentro de una red mediante direcciones IP y solicitudes ICMP (Ping).

El sistema permite visualizar el estado de los dispositivos, consultar estadísticas generales y registrar eventos de conectividad mediante una base de datos SQLite.

## Características principales

- Monitoreo de dispositivos mediante Ping.
- Identificación de dispositivos en línea y fuera de línea.
- Panel web con estadísticas en tiempo real al actualizarse.
- Actualización automática cada 30 segundos.
- Registro de cambios de conectividad.
- Historial de los últimos 10 eventos.
- Almacenamiento de información mediante SQLite.
- Interfaz web desarrollada con HTML y CSS.

## Tecnologías utilizadas

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- ICMP / Ping

## Estructura del proyecto

```text
netwatch/
│
├── app.py
├── main.py
├── netwatch.db
├── historial.csv
├── requirements.txt
├── .gitignore
├── README.md
│
└── templates/
    └── index.html
```

## Instalación

1. Descargar o clonar el repositorio.
2. Instalar Python 3.
3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```bash
python app.py
```

5. Abrir el navegador en:

```text
http://127.0.0.1:5000
```

## Funcionamiento

NetWatch consulta la conectividad de los dispositivos registrados en su base de datos mediante solicitudes Ping.

Cuando detecta un cambio de estado, registra un evento en SQLite con el nombre del dispositivo, su dirección IP, el estado y la fecha y hora.

El panel web permite consultar los dispositivos monitoreados y los últimos eventos registrados.

## Objetivo del proyecto

Este proyecto fue desarrollado con fines educativos para aplicar conocimientos de programación en Python, administración de bases de datos, fundamentos de redes y desarrollo de aplicaciones web.

## Autor

Santiago Torres Cornejo

Proyecto personal de aprendizaje enfocado en redes y ciberseguridad.