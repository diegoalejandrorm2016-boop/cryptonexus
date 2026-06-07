# 🚀 CryptoNexus — Django Trading Platform

App web de trading de criptomonedas migrada a **Django 5**, con datos en tiempo real de Binance.

## Características
- ✅ Página de inicio con precios en vivo (actualización cada 10s)
- ✅ Registro e inicio de sesión (modelo de usuario personalizado)
- ✅ Base de datos SQLite (fácilmente migrable a PostgreSQL)
- ✅ 16 criptomonedas en tiempo real via Binance API pública
- ✅ Gráficas de velas por día / semana / mes / año (ApexCharts)
- ✅ Compra y venta con balance demo ($10,000 USD)
- ✅ Notificaciones por email al realizar operaciones
- ✅ Portafolio con P&L en tiempo real
- ✅ Historial paginado de transacciones
- ✅ Panel de administración Django (`/admin/`)

## Instalación

```bash
# 1. Entrar al directorio
cd cryptonexus

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tu correo y contraseña de Gmail

# 5. Crear la base de datos
python manage.py migrate

# 6. (Opcional) Crear superusuario para el admin
python manage.py createsuperuser

# 7. Ejecutar
python manage.py runserver
```

Abre http://127.0.0.1:8000

## Equivalencias Flask → Django

| Flask                        | Django                              |
|------------------------------|-------------------------------------|
| `Flask(__name__)`            | `django-admin startproject`         |
| `Blueprint`                  | `App` + `urls.py`                   |
| `SQLAlchemy` models          | `django.db.models.Model`            |
| `flask-login`                | `django.contrib.auth`               |
| `flask-mail`                 | `django.core.mail`                  |
| `flask-wtf`                  | `django.forms`                      |
| `render_template`            | `render(request, 'template.html')`  |
| `redirect(url_for(...))`     | `redirect('nombre_url')`            |
| `flash()`                    | `messages.success/error/info()`     |
| `@login_required`            | `@login_required` (mismo decorador) |
| `db.create_all()`            | `python manage.py migrate`          |

## Estructura del proyecto

```
cryptonexus/
├── manage.py
├── requirements.txt
├── .env.example
├── cryptonexus/               # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── trading/                   # App principal
│   ├── models.py              # User, Portfolio, Transaction
│   ├── forms.py               # RegisterForm, LoginForm
│   ├── urls.py                # Todas las rutas
│   ├── admin.py
│   ├── views/
│   │   ├── auth.py            # login, register, logout
│   │   ├── dashboard.py       # dashboard, history
│   │   ├── trading.py         # trade, buy, sell
│   │   └── api.py             # API REST → Binance proxy
│   └── utils/
│       └── email.py           # Envío de emails
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth/login.html
│   ├── auth/register.html
│   ├── dashboard/dashboard.html
│   ├── dashboard/history.html
│   ├── trading/trade.html
│   └── emails/trade_confirmation.html
└── static/
    ├── css/main.css
    └── js/main.js
```

## URLs disponibles

| URL                        | Vista            |
|----------------------------|------------------|
| `/`                        | Inicio           |
| `/auth/login/`             | Iniciar sesión   |
| `/auth/register/`          | Registro         |
| `/auth/logout/`            | Cerrar sesión    |
| `/dashboard/`              | Dashboard        |
| `/dashboard/history/`      | Historial        |
| `/trading/?symbol=BTCUSDT` | Trading          |
| `/trading/buy/`            | Ejecutar compra  |
| `/trading/sell/`           | Ejecutar venta   |
| `/api/prices/`             | Precios JSON     |
| `/api/price/<symbol>/`     | Precio individual|
| `/api/klines/<symbol>/`    | Velas OHLCV      |
| `/admin/`                  | Panel admin      |

## Configurar Gmail para notificaciones

1. Google → Seguridad → Verificación en dos pasos (activar)
2. Contraseñas de aplicaciones → Generar para "Correo"
3. Copiar la contraseña en `.env` como `MAIL_PASSWORD`

## Producción (Gunicorn + PostgreSQL)

```bash
# Cambiar la base de datos en settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cryptonexus',
        'USER': 'postgres',
        'PASSWORD': 'tu-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

pip install psycopg2-binary
python manage.py collectstatic
gunicorn -w 4 -b 0.0.0.0:8000 cryptonexus.wsgi:application
```
