# 🛒 Minimart POS

Sistema de Punto de Venta para tiendas de abarrotes y ferreterías pequeñas.  
Desarrollado con **Python + Streamlit**, almacenamiento en archivos **JSON**.

---

## 🚀 Funcionalidades

| Módulo | Descripción |
|---|---|
| 🔐 Login y Roles | 4 roles: Admin, Supervisor, Cajero, Almacenista |
| 🛒 Punto de Venta | Búsqueda de productos, carrito, cobro en efectivo/tarjeta |
| 📦 Inventario | CRUD de productos, alertas de stock bajo |
| 💰 Caja | Apertura, corte de caja, utilidad del día |
| 📱 Recargas | Registro de recargas telefónicas |
| 🏠 Dashboard | Resumen del día, métricas clave |
| ⚙️ Configuración | Datos de la tienda, usuarios |

---

## 📁 Estructura del proyecto

```
minimart-pos/
├── app.py                  # App principal (router + páginas)
├── requirements.txt        
├── .streamlit/
│   └── config.toml         # Tema visual
├── data/                   # Base de datos JSON
│   ├── usuarios.json
│   ├── productos.json
│   ├── ventas.json
│   ├── caja.json
│   ├── recargas.json
│   └── config_tienda.json
├── modules/                # Lógica de negocio
│   ├── auth.py             # Autenticación y usuarios
│   ├── inventario.py       # Gestión de productos
│   ├── ventas.py           # Registro de ventas
│   ├── caja.py             # Control de caja
│   └── recargas.py         # Recargas telefónicas
└── utils/
    └── db.py               # Lectura/escritura JSON
```

---

## ⚙️ Instalación local

```bash
# 1. Clonar el repo
git clone https://github.com/TU_USUARIO/minimart-pos.git
cd minimart-pos

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

---

## 🌐 Deploy en Streamlit Community Cloud

1. Sube el proyecto a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y `app.py` como archivo principal
5. ¡Listo! Tu app estará en línea en minutos

---

## 🔑 Acceso inicial

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |

> ⚠️ **Cambia la contraseña del admin** desde la sección de usuarios después de la primera vez.

---

## 👥 Roles del sistema

| Rol | Acceso |
|---|---|
| **Admin** | Todo: ventas, inventario, caja, usuarios, configuración |
| **Supervisor** | Ve todo pero no puede modificar |
| **Cajero** | Solo punto de venta y recargas |
| **Almacenista** | Solo inventario |

---

## 🗺️ Roadmap (versión completa)

- [ ] Base de datos Supabase (PostgreSQL)
- [ ] Dashboard con gráficas (ventas por día/semana/mes)
- [ ] Exportar reportes a Excel/PDF
- [ ] Impresión de tickets
- [ ] Gestión de proveedores y compras
- [ ] Historial de movimientos de inventario
- [ ] App móvil (PWA)

---

## 📄 Licencia

Uso privado. Todos los derechos reservados.
