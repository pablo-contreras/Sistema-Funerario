# 02 - Módulos del Código

Este documento explica qué hace cada módulo y archivo relevante del sistema.

## Vista General

El proyecto es una aplicación Django. La estructura principal es:

```text
clientes/      Aplicación de negocio: clientes, pagos, documentos y contratos.
funeraria/     Configuración global del proyecto Django.
deploy/        Archivos de despliegue, Nginx, backup y restore.
static/        Archivos estáticos globales.
tests/         Pruebas automáticas.
```

## `manage.py`

Archivo estándar de Django para ejecutar comandos administrativos.

Ejemplos:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py test
```

En Docker se usa principalmente para:

- aplicar migraciones;
- recolectar archivos estáticos;
- crear el usuario administrador;
- ejecutar comandos de mantenimiento.

## Carpeta `funeraria/`

Contiene la configuración global del proyecto Django.

### `funeraria/settings.py`

Archivo central de configuración.

Responsabilidades principales:

- definir `BASE_DIR`;
- leer variables de entorno;
- definir `SECRET_KEY`;
- activar o desactivar `DEBUG`;
- configurar `ALLOWED_HOSTS`;
- configurar `CSRF_TRUSTED_ORIGINS`;
- registrar aplicaciones instaladas;
- configurar middleware;
- configurar plantillas;
- elegir base de datos;
- configurar idioma y zona horaria;
- configurar archivos estáticos;
- configurar archivos subidos;
- configurar login/logout;
- configurar cookies seguras.

#### Base de datos

Si existe `POSTGRES_HOST`, Django usa PostgreSQL:

```python
if os.getenv("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            ...
        }
    }
```

Si no existe `POSTGRES_HOST`, usa SQLite local:

```python
default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
```

Esto permite:

- usar PostgreSQL en producción;
- probar localmente en Windows sin instalar PostgreSQL.

#### Archivos estáticos

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

Django recolecta los estáticos en `staticfiles`. Nginx los sirve desde ahí.

#### Archivos subidos

```python
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))
```

En Docker, `DJANGO_MEDIA_ROOT` queda como:

```text
/app/media
```

Esa carpeta se conecta al servidor con un volumen persistente.

#### Seguridad

Configuraciones relevantes:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

Cuando el sistema se use solo por HTTPS de Tailscale, conviene activar:

```text
DJANGO_SECURE_COOKIES=True
```

### `funeraria/urls.py`

Define las rutas globales del proyecto.

Rutas:

```text
/admin/       Panel administrativo de Django.
/ingresar/    Login.
/salir/       Logout.
/             Rutas de la aplicación clientes.
```

La línea:

```python
path("", include("clientes.urls"))
```

envía la raíz del sitio a la aplicación `clientes`.

### `funeraria/wsgi.py`

Punto de entrada para Gunicorn en producción.

El `Dockerfile` ejecuta:

```bash
gunicorn funeraria.wsgi:application
```

### `funeraria/asgi.py`

Punto de entrada ASGI estándar de Django.

Actualmente no se usa para WebSockets ni tareas asíncronas, pero queda disponible si en el futuro se necesita.

## Carpeta `clientes/`

Es la aplicación principal del sistema.

Aquí vive casi toda la lógica de negocio.

### `clientes/apps.py`

Declara la aplicación Django:

```python
class ClientesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clientes"
```

Django usa este archivo para registrar la app.

### `clientes/models.py`

Define las tablas principales del sistema.

Modelos:

- `Client`;
- `Payment`;
- `ClientDocument`.

También define:

- ruta de documentos por cliente;
- generación automática de folio;
- generación automática de carpeta del cliente;
- cálculo de IVA;
- cálculo de total del servicio;
- cálculo de total pagado;
- cálculo de saldo;
- eliminación física del archivo cuando se borra un documento.

#### Función `client_document_path`

```python
def client_document_path(instance, filename):
    folder = instance.client.document_folder or f"cliente-{instance.client_id}"
    return str(Path("clientes") / folder / filename)
```

Construye la ruta donde se guardará un archivo subido.

Ejemplo:

```text
clientes/juan-perez-12345678_5/contrato.pdf
```

#### Modelo `Client`

Representa la ficha principal del cliente.

Campos importantes:

| Campo | Función |
|---|---|
| `name` | Nombre del contratante. Obligatorio. |
| `rut` | RUT del contratante. Obligatorio, único y validado. |
| `folio` | Folio automático del contrato. |
| `address`, `phone`, `email` | Datos de contacto. |
| `deceased_name` | Nombre del fallecido. |
| `death_date`, `death_time`, `death_place` | Datos de fallecimiento. |
| `urn_type`, `wake_place`, `church` | Datos del servicio. |
| `service_net` | Valor neto del servicio. |
| `vat_rate` | Porcentaje de IVA. Por defecto 19%. |
| `document_folder` | Carpeta donde se guardan documentos. |
| `created_by` | Usuario que creó la ficha. |
| `created_at`, `updated_at` | Fechas automáticas de auditoría. |

Solo `name` y `rut` son obligatorios porque los demás campos tienen `blank=True` o `null=True`.

#### Método `Client.save`

Antes o después de guardar:

1. normaliza el RUT;
2. guarda el registro;
3. si no hay folio, crea uno;
4. si no hay carpeta, crea una carpeta con nombre y RUT.

Formato de folio:

```text
FUN-2026-00001
```

Formato de carpeta:

```text
nombre-cliente-12345678_5
```

#### Propiedad `vat_amount`

Calcula el IVA:

```text
service_net * vat_rate / 100
```

Si no hay valor neto, devuelve `None`.

#### Propiedad `service_total`

Calcula:

```text
valor neto + IVA
```

Si no hay valor neto, devuelve `0`.

#### Propiedad `paid_total`

Suma todos los pagos asociados al cliente.

Si la vista ya anotó `paid_amount`, usa ese valor para evitar consultas extra.

#### Propiedad `balance`

Calcula:

```text
total servicio - total pagado
```

#### Modelo `Payment`

Representa un pago o abono.

Campos:

| Campo | Función |
|---|---|
| `client` | Cliente al que pertenece el pago. |
| `payment_date` | Fecha del abono. |
| `amount` | Monto del pago. |
| `receipt_number` | Número de recibo. |
| `notes` | Detalle opcional. |
| `created_at` | Fecha de creación. |

Los pagos se ordenan por fecha y creación:

```python
ordering = ["payment_date", "created_at"]
```

#### Modelo `ClientDocument`

Representa un archivo subido para un cliente.

Categorías permitidas:

- contrato físico;
- certificado;
- comprobante;
- otro.

Extensiones permitidas:

```text
pdf, jpg, jpeg, png, webp, doc, docx, xls, xlsx
```

Campos:

| Campo | Función |
|---|---|
| `client` | Cliente dueño del archivo. |
| `category` | Tipo de documento. |
| `file` | Archivo físico. |
| `original_name` | Nombre original del archivo. |
| `uploaded_at` | Fecha de subida. |
| `uploaded_by` | Usuario que subió el archivo. |

#### Señal `delete_document_file`

Cuando se borra un `ClientDocument`, también borra el archivo físico del disco:

```python
@receiver(post_delete, sender=ClientDocument)
def delete_document_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
```

Esto evita que queden archivos huérfanos ocupando espacio.

### `clientes/validators.py`

Contiene validaciones del RUT chileno.

#### `normalize_rut`

Convierte un RUT a formato interno uniforme.

Ejemplo:

```text
12.345.678-5 -> 12345678-5
```

Esto evita duplicados escritos de formas distintas.

#### `validate_rut`

Verifica:

- que el RUT tenga cuerpo numérico;
- que tenga dígito verificador;
- que el dígito verificador sea correcto.

Usa el algoritmo módulo 11.

Si el RUT no es válido, lanza:

```python
ValidationError
```

### `clientes/forms.py`

Define formularios HTML y reglas de limpieza.

#### `DateInput`

Hace que los campos de fecha usen selector nativo del navegador:

```html
<input type="date">
```

#### `TimeInput`

Hace que los campos de hora usen:

```html
<input type="time">
```

#### `ClientForm`

Formulario principal de ficha.

Características:

- usa el modelo `Client`;
- excluye campos automáticos;
- reduce alto de áreas de texto;
- agrega clase CSS `form-control`;
- enfoca automáticamente el campo `name`;
- normaliza el RUT antes de guardar.

Campos excluidos:

```python
["folio", "document_folder", "created_by", "created_at", "updated_at"]
```

Estos campos no deben ser editados manualmente.

#### `PaymentForm`

Formulario para registrar pagos.

Campos:

```python
["payment_date", "amount", "receipt_number", "notes"]
```

#### `DocumentForm`

Formulario para subir documentos.

Valida:

- categoría;
- archivo;
- extensión;
- tamaño máximo de 20 MB.

También agrega el atributo `accept` para que Chrome sugiera solo formatos permitidos.

### `clientes/views.py`

Contiene las vistas que atienden las solicitudes del navegador.

Todas las vistas principales usan:

```python
@login_required
```

Eso significa que el usuario debe iniciar sesión.

#### `contract_context`

Prepara datos para el contrato imprimible y PDF.

Calcula el saldo después de cada pago:

```text
saldo inicial = total servicio
saldo después de cada pago = saldo anterior - pago
```

Entrega a la plantilla:

- cliente;
- pagos con saldo;
- modo PDF;
- request;
- ruta del logo.

#### `client_list`

Muestra la lista de clientes.

Permite buscar por:

- nombre;
- RUT;
- nombre del fallecido;
- folio.

También normaliza la búsqueda de RUT para encontrar resultados aunque se escriba con puntos o guion.

Limita la lista visible a 100 registros:

```python
clients[:100]
```

#### `client_create`

Crea una nueva ficha.

Flujo:

1. muestra formulario vacío;
2. recibe POST;
3. valida datos;
4. asocia `created_by` al usuario actual;
5. guarda;
6. muestra mensaje de éxito;
7. redirige al detalle del cliente.

#### `client_update`

Edita una ficha existente.

Flujo:

1. busca cliente por `pk`;
2. muestra formulario cargado;
3. recibe cambios;
4. valida;
5. guarda;
6. vuelve al detalle.

#### `client_detail`

Muestra una ficha completa.

Incluye:

- resumen de cliente;
- total del servicio;
- total pagado;
- saldo;
- formulario de pago;
- tabla de pagos;
- formulario de subida de documentos;
- lista de documentos;
- botones de imprimir y PDF.

Usa `prefetch_related` para cargar pagos y documentos eficientemente.

#### `client_delete`

Elimina una ficha.

Como `Payment` y `ClientDocument` dependen de `Client`, también se eliminan sus pagos y documentos asociados.

#### `payment_create`

Registra un pago.

Flujo:

1. busca cliente;
2. valida formulario;
3. asigna el cliente al pago;
4. guarda;
5. vuelve al detalle en la sección `#pagos`.

#### `payment_delete`

Elimina un pago específico.

Después redirige a la ficha del cliente.

#### `document_upload`

Sube un archivo para el cliente.

Flujo:

1. busca cliente;
2. valida formulario y archivo;
3. asigna cliente;
4. asigna usuario que subió;
5. guarda nombre original;
6. guarda archivo físico;
7. vuelve a la sección `#archivos`.

#### `document_download`

Descarga un archivo.

Si el archivo ya no existe físicamente, devuelve error 404.

#### `document_delete`

Elimina un documento.

La señal del modelo borra también el archivo físico.

#### `contract_print`

Muestra el contrato HTML en formato A4, listo para imprimir desde Chrome.

#### `contract_pdf`

Genera un PDF del contrato.

Intenta usar WeasyPrint en Linux:

```python
from weasyprint import HTML
```

Si no está disponible o se ejecuta en Windows, usa ReportLab mediante:

```python
from .pdf_fallback import generate_contract_pdf
```

Esto permite que la descarga PDF funcione también en entornos de prueba.

### `clientes/urls.py`

Define las rutas de la aplicación `clientes`.

Rutas principales:

| Ruta | Vista | Función |
|---|---|---|
| `/` | `client_list` | Lista y búsqueda |
| `/clientes/nuevo/` | `client_create` | Nueva ficha |
| `/clientes/<pk>/` | `client_detail` | Detalle |
| `/clientes/<pk>/editar/` | `client_update` | Editar |
| `/clientes/<pk>/eliminar/` | `client_delete` | Eliminar |
| `/clientes/<pk>/pagos/nuevo/` | `payment_create` | Registrar pago |
| `/pagos/<pk>/eliminar/` | `payment_delete` | Eliminar pago |
| `/clientes/<pk>/documentos/subir/` | `document_upload` | Subir documento |
| `/documentos/<pk>/descargar/` | `document_download` | Descargar documento |
| `/documentos/<pk>/eliminar/` | `document_delete` | Eliminar documento |
| `/clientes/<pk>/contrato/` | `contract_print` | Imprimir contrato |
| `/clientes/<pk>/contrato.pdf` | `contract_pdf` | Descargar PDF |

### `clientes/admin.py`

Configura el panel `/admin/`.

Incluye:

- pagos en línea dentro del cliente;
- documentos en línea dentro del cliente;
- búsqueda por nombre, RUT y fallecido;
- campos de solo lectura para folio y carpeta;
- listado con folio, nombre, RUT, teléfono y fecha.

### `clientes/pdf_fallback.py`

Genera PDF usando ReportLab.

Se usa cuando:

- el sistema está en Windows;
- WeasyPrint no está disponible;
- ocurre un error de dependencias gráficas.

Funciones principales:

- `money`: formatea valores en pesos chilenos;
- `value`: muestra texto o línea en blanco;
- `section`: crea bloques de datos;
- `header`: crea encabezado con logo, folio y fecha;
- `generate_contract_pdf`: arma el PDF completo.

Este módulo no depende de HTML. Construye el PDF con tablas y párrafos directamente.

### `clientes/templatetags/client_tags.py`

Filtros personalizados para plantillas.

#### `clp`

Formatea valores como pesos chilenos.

Ejemplo:

```text
119000 -> $119.000
```

#### `value_or_line`

Si hay valor, lo muestra.

Si está vacío, muestra:

```text
________________
```

Esto se usa en el contrato para simular líneas de documento físico.

### `clientes/templates/`

Contiene las pantallas HTML.

#### `clientes/templates/registration/login.html`

Pantalla de ingreso.

Incluye:

- logo;
- usuario;
- contraseña;
- mensaje de error si falla login.

#### `clientes/templates/clientes/base.html`

Plantilla base del sistema autenticado.

Define:

- estructura general;
- barra lateral;
- navegación;
- mensajes;
- enlace a clientes;
- enlace a nueva ficha;
- enlace a administración si el usuario es staff;
- botón de cerrar sesión.

#### `clientes/templates/clientes/client_list.html`

Lista de clientes.

Muestra:

- total de fichas;
- buscador;
- tabla de clientes;
- folio;
- contratante;
- RUT;
- fallecido;
- total;
- saldo;
- enlaces a ver y editar.

#### `clientes/templates/clientes/client_form.html`

Formulario de creación y edición.

Se divide en secciones:

- datos del contratante;
- datos del fallecido;
- servicio y ceremonia;
- entrega de documentos.

Usa `_field.html` para no repetir código de campos.

#### `clientes/templates/clientes/_field.html`

Fragmento reutilizable para renderizar un campo.

Se encarga de:

- mostrar etiqueta;
- mostrar asterisco si el campo es obligatorio;
- mostrar widget;
- mostrar errores del campo.

#### `clientes/templates/clientes/client_detail.html`

Pantalla de detalle de una ficha.

Incluye:

- resumen general;
- tarjetas de total, pagado, saldo y archivos;
- botones de editar, imprimir y descargar PDF;
- formulario de pagos;
- tabla de pagos;
- formulario de subida de documentos;
- lista de documentos;
- zona de eliminación de cliente.

#### `clientes/templates/clientes/contract_print.html`

Contrato imprimible.

Características:

- formato A4;
- botón para imprimir en Chrome;
- botón para descargar PDF;
- primera página con datos del contrato;
- segunda página con entrega de documentos y pagos;
- modo especial `pdf_mode` para que el logo se lea correctamente al generar PDF.

### `clientes/static/clientes/app.css`

Estilos visuales del sistema.

Define:

- colores;
- layout lateral;
- tarjetas;
- tablas;
- formularios compactos;
- pantalla de login;
- responsive para pantallas pequeñas;
- botones;
- mensajes;
- vista de documentos;
- zona de peligro para eliminar.

## Carpeta `static/`

Contiene archivos estáticos globales.

### `static/img/logo.png`

Logo usado en:

- login;
- barra lateral;
- contrato imprimible;
- PDF.

## Carpeta `deploy/`

Contiene todo lo necesario para producción.

### `deploy/nginx/default.conf`

Configuración de Nginx.

Responsabilidades:

- escuchar en puerto 80 dentro del contenedor;
- servir `/static/`;
- reenviar el resto a `web:8000`;
- permitir subida de archivos hasta 25 MB;
- conservar headers importantes.

### `deploy/scripts/entrypoint.sh`

Script que se ejecuta al iniciar el contenedor web.

Hace:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec "$@"
```

Esto significa:

1. aplica migraciones pendientes;
2. recolecta archivos estáticos;
3. arranca Gunicorn.

### `deploy/scripts/backup.sh`

Crea respaldo.

Incluye:

- dump de PostgreSQL en formato custom;
- compresión de documentos subidos;
- copia de `.env`;
- archivo `SHA256SUMS` para verificar integridad;
- eliminación de respaldos antiguos mayores a 30 días.

Genera una carpeta:

```text
/mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS
```

### `deploy/scripts/restore.sh`

Restaura un respaldo.

Hace:

1. valida parámetro;
2. verifica que exista `base-datos.dump`;
3. verifica `SHA256SUMS`;
4. elimina y recrea base de datos;
5. restaura dump;
6. restaura documentos si existe `documentos.tar.gz`;
7. reinicia el contenedor web.

### `deploy/funeraria-backup.service`

Servicio systemd que ejecuta el respaldo.

### `deploy/funeraria-backup.timer`

Timer systemd que agenda el respaldo automático.

## Archivos Docker

### `Dockerfile`

Construye la imagen de la aplicación.

Hace:

1. parte desde `python:3.12-slim`;
2. instala librerías necesarias para WeasyPrint;
3. copia `requirements.txt`;
4. instala dependencias Python;
5. copia el proyecto;
6. da permiso al entrypoint;
7. arranca Gunicorn.

### `docker-compose.yml`

Orquesta tres servicios:

- `db`;
- `web`;
- `nginx`.

Define:

- variables de entorno;
- volúmenes persistentes;
- healthcheck de PostgreSQL;
- puerto `8080:80`;
- dependencia de `web` respecto a `db`.

## Archivos de Configuración

### `.env.example`

Plantilla de variables para producción.

Debe copiarse como:

```bash
cp .env.example .env
```

Y editarse antes de levantar el sistema.

Variables importantes:

| Variable | Función |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django. Debe ser aleatoria. |
| `DJANGO_DEBUG` | En producción debe ser `False`. |
| `DJANGO_SECURE_COOKIES` | Usar `True` si se accede solo por HTTPS. |
| `DJANGO_ALLOWED_HOSTS` | Hosts/IP permitidos. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS permitidos para formularios. |
| `POSTGRES_DB` | Nombre de base de datos. |
| `POSTGRES_USER` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Contraseña PostgreSQL. |
| `DATA_DIR` | Carpeta persistente del sistema. |
| `BACKUP_DIR` | Carpeta de respaldos. |

### `requirements.txt`

Dependencias Python:

- Django;
- dj-database-url;
- gunicorn;
- Pillow;
- psycopg;
- reportlab;
- weasyprint;
- whitenoise.

### `pytest.ini`

Configura pytest para usar:

```text
DJANGO_SETTINGS_MODULE=funeraria.settings
```

## Carpeta `tests/`

Contiene pruebas automáticas.

### `tests/test_system.py`

Pruebas incluidas:

- solo nombre y RUT son obligatorios;
- búsqueda por nombre y RUT;
- pagos actualizan saldo;
- documentos se guardan en carpeta del cliente;
- normalización de RUT;
- descarga de contrato PDF.

Estas pruebas son útiles antes de modificar el sistema.
