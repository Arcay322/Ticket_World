# 🎟️ Ticket World

**Ticket World** es una plataforma web para la venta y gestión de boletos para eventos como conciertos, festivales, arte, deportes, y más. Permite a usuarios registrarse, comprar entradas y a proveedores gestionar sus propios eventos.

---

## 🛠️ Tecnologías utilizadas

- **Back-end**: Django (Python)
- **Front-end**: HTML, CSS, JavaScript
- **Base de Datos**: MySQL
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

1. Clona el repositorio:

```bash
git clone https://github.com/Arcay322/Ticket_World.git
cd Ticket_World

2. Crea y activa el entorno virutal
python -m venv venv
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En macOS/Linux

3. Instala las dependencias:

pip install -r requirements.txt

4.Aplica migraciones 

python manage.py migrate

5. Crea un superusuario

python manage.py createsuperuser

#estructura del proyecto :
Ticket_World/
├── usuarios/            # App de gestión de usuarios y proveedores
├── eventos/             # App de gestión de eventos
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos (CSS, imágenes, JS)
├── manage.py
└── requirements.txt
