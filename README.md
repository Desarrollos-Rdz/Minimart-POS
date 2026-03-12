# 🛒 Minimart POS

Sistema de Punto de Venta para tiendas de abarrotes y ferreterías pequeñas.  
Desarrollado con **Python + Streamlit**, almacenamiento en archivos **JSON**.

---

## 🚀 Funcionalidades

| Módulo | Descripción |
|---|---|
| 🔐 Login y Roles | 4 roles: Admin, Supervisor, Cajero, Almacenista |
| 🛒 Punto de Venta | Búsqueda, carrito, cobro en efectivo/tarjeta/mixto |
| 📦 Inventario | CRUD de productos, alertas de stock bajo, dos secciones |
| 💰 Caja | Apertura, corte de caja, utilidad del día automática |
| 📱 Recargas | Registro de recargas por operadora con historial |
| 🏠 Dashboard | Métricas del día, desglose por pago, últimas ventas |
| 👥 Usuarios | Crear, activar/desactivar, cambiar contraseñas |
| ⚙️ Configuración | Datos de la tienda, cambiar contraseña propia |

---

## 📁 Estructura del proyecto

```
minimart-pos/
├── app.py                    # Punto de entrada + login + navegación
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml           # Tema visual
│
├── pages/                    # Una página por módulo (st.navigation)
│   ├── dashboard.py
│   ├── pos.py
│   ├── inventario.py
│   ├── caja.py
│   ├── recargas.py
│   ├── usuarios.py
│   └── configuracion.py
│
├── modules/                  # Lógica de negocio
│   ├── auth.py               # Autenticación, sesión, usuarios
│   ├── inventario.py         # CRUD de productos
│   ├── ventas.py             # Registro y consulta de ventas
│   ├── caja.py               # Apertura y cortes de caja
│   └── recargas.py           # Recargas telefónicas
│
├── utils/
│   └── db.py                 # Lectura/escritura JSON, utilidades
│
└── data/                     # Base de datos en archivos JSON
    ├── usuarios.json
    ├── productos.json
    ├── ventas.json
    ├── caja.json
    ├── recargas.json
    └── config_tienda.json
```

---

## ⚙️ Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/minimart-pos.git
cd minimart-pos

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la app
streamlit run app.py
```

---

## 🌐 Deploy en Streamlit Community Cloud

1. Sube el proyecto a un repositorio de **GitHub** (público o privado)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y pon `app.py` como archivo principal
5. ¡Listo! La app estará en línea en minutos sin costo alguno

> ⚠️ **Importante para deploy:** Los archivos `.json` de la carpeta `data/` deben estar en el repositorio para que la app funcione. Streamlit Community Cloud no persiste datos entre reinicios; para producción real se recomienda migrar a Supabase (versión futura).

---

## 🔑 Acceso inicial

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |

> ⚠️ **Cambia la contraseña del admin** desde Configuración después del primer acceso.

---

## 👥 Roles del sistema

| Rol | Color | Acceso |
|---|---|---|
| **Admin** | 🔴 | Todo: ventas, inventario, caja, usuarios, configuración |
| **Supervisor** | 🟡 | Ve todo, no puede modificar ni vender |
| **Cajero** | 🔵 | Solo punto de venta y recargas |
| **Almacenista** | 🟢 | Solo inventario |

---

## 🗺️ Roadmap v2.0 (versión completa con Supabase)

- [ ] Migración a base de datos Supabase (PostgreSQL)
- [ ] Dashboard con gráficas interactivas (ventas por día/semana/mes)
- [ ] Exportar reportes a Excel y PDF
- [ ] Impresión de tickets
- [ ] Gestión de proveedores y órdenes de compra
- [ ] Historial de movimientos de inventario (auditoría)
- [ ] Múltiples sucursales

---

## 📄 Licencia

Uso privado. Todos los derechos reservados.