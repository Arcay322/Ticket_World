# 🎟️ Ticket World

**Ticket World** es una plataforma web para la venta y gestión de boletos para eventos como conciertos, festivales, arte, deportes, y más. Permite a usuarios registrarse, comprar entradas y a proveedores gestionar sus propios eventos.

---

## 🛠️ Tecnologías utilizadas

- **Back-end**: Django (Python)
- **Front-end**: HTML, CSS, JavaScript
- **Base de Datos**: PostgreSQL
- **Autenticación**: Sistema de registro y login con roles (cliente, proveedor, administrador)
- **Control de versiones**: Git + GitHub

---

## 📌 Funcionalidades

### Usuarios:
- Registro e inicio de sesión con validación de correo electrónico
- Visualización de eventos disponibles
- Compra de entradas

### Proveedores:
- Solicitud para convertirse en proveedor
- Gestión de sus eventos (crear, editar, eliminar)
- Ver reportes de ventas

### Administrador:
- Aprobación o rechazo de solicitudes de proveedores
- Gestión general del sistema

---

## 🧪 Instalación local

Requisitos Previos
Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu sistema:

Git: Para clonar el repositorio. Puedes descargarlo desde git-scm.com.
Python 3.13.x: El lenguaje de programación principal del proyecto. Descárgalo desde python.org.
Importante en Windows: Durante la instalación de Python, asegúrate de marcar la casilla "Add Python to PATH" (Añadir Python al PATH) para evitar problemas con los comandos python y pip en la terminal.

Configuración y Ejecución Local
Sigue estos pasos detallados para configurar y poner en marcha el proyecto en tu entorno de desarrollo local.

1. Clonar el Repositorio
Abre tu terminal (PowerShell, CMD, o la terminal integrada de VS Code) y clona el repositorio a tu máquina local. Luego, navega a la carpeta del proyecto:

Bash

git clone https://github.com/Arcay322/Ticket_World.git
cd Ticket_World

2. Crear y Activar el Entorno Virtual
Es fundamental el uso de un entorno virtual para aislar las dependencias del proyecto de tu instalación global de Python.

python -m venv venv

Luego, activa el entorno virtual en tu terminal:

En Windows:

venv\Scripts\activate


En macOS/Linux:

source venv/bin/activate


Tu prompt de la terminal debería mostrar (venv) al principio, indicando que el entorno virtual está activo.

3. Instalar las Dependencias
Con el entorno virtual activado, instala todas las librerías de Python requeridas por el proyecto. Estas están listadas en el archivo requirements.txt:

python -m pip install -r requirements.txt

4. Configurar Variables de Entorno (¡IMPORTANTE!)
Este proyecto utiliza variables de entorno para almacenar configuraciones sensibles y específicas del entorno, como las credenciales de la base de datos de Supabase y la SECRET_KEY de Django.

Crea un archivo llamado .env en la raíz de tu proyecto (dentro de la carpeta Ticket_World/). Este archivo DEBE ser ignorado por Git (está en .gitignore) para prevenir que las credenciales sensibles sean subidas al repositorio público.

Crea un archivo llamado .gitignore y dentro agrega la linea : .env "IMPORTANTE"

Dentro de tu archivo .env, añade las siguientes variables. Necesitarás obtener los valores de DATABASE_URL y SUPABASE_API_KEY del propietario del proyecto o de un administrador de Supabase.

5. Aplicar Migraciones de Base de Datos
Una vez que la conexión a la base de datos esté configurada en tu archivo .env, aplica las migraciones de Django para crear las tablas necesarias en tu base de datos de Supabase:

python manage.py migrate


6. Crear un Superusuario (Opcional, pero recomendado)
Para acceder al panel de administración de Django y gestionar la aplicación, puedes crear una cuenta de superusuario:

python manage.py createsuperuser


Sigue las instrucciones en la terminal para definir el nombre de usuario, la dirección de correo electrónico y la contraseña.

7. Ejecutar el Servidor de Desarrollo
Finalmente, inicia el servidor de desarrollo de Django para ver tu aplicación en acción:

python manage.py runserver

La aplicación estará accesible en tu navegador web, generalmente en la siguiente dirección: http://127.0.0.1:8000/.

Consideraciones Adicionales
.gitignore: Asegúrate de que el archivo .gitignore en la raíz del proyecto contenga la línea / .env para garantizar que este archivo crítico no sea rastreado por Git.