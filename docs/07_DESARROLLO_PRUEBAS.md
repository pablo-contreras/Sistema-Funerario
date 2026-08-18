# 07 - Desarrollo y Pruebas

Este documento explica cómo modificar, probar y mantener el código.

## Tecnología Usada

El sistema usa:

- Python 3.12 en producción Docker;
- Django 5.2 LTS;
- PostgreSQL 16;
- Gunicorn;
- Nginx;
- Docker Compose;
- ReportLab;
- WeasyPrint;
- Pillow;
- WhiteNoise.

## Probar en Windows

Desde esta carpeta:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000
```

En Windows, si no define `POSTGRES_HOST`, el sistema usa SQLite.

Esto permite probar sin instalar PostgreSQL.

## Probar con Docker

Crear `.env`:

```bash
cp .env.example .env
```

Levantar:

```bash
docker compose up -d --build
```

Crear superusuario:

```bash
docker compose exec web python manage.py createsuperuser
```

Abrir:

```text
http://127.0.0.1:8080
```

## Ejecutar Pruebas

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar:

```bash
python manage.py test
```

O con pytest si está instalado:

```bash
pytest
```

## Pruebas Incluidas

Archivo:

```text
tests/test_system.py
```

### `test_client_only_requires_name_and_rut`

Verifica que se pueda crear una ficha usando solo:

- nombre;
- RUT;
- IVA.

También confirma que:

- el RUT queda normalizado;
- el folio se genera automáticamente.

### `test_searches_by_name_and_rut`

Verifica que la búsqueda encuentre clientes por:

- nombre;
- RUT con puntos y guion.

### `test_payments_update_balance`

Verifica que:

- el total del servicio incluya IVA;
- el pago se sume;
- el saldo sea correcto.

Ejemplo:

```text
neto: 100.000
IVA 19%: 19.000
total: 119.000
pago: 30.000
saldo: 89.000
```

### `test_document_is_stored_in_client_folder`

Verifica que un documento subido quede dentro de la carpeta del cliente.

### `test_rut_normalization`

Verifica:

```text
12.345.678-5 -> 12345678-5
```

### `test_contract_pdf_download`

Verifica que la descarga del contrato devuelva un PDF válido.

## Cómo Agregar un Campo Nuevo a Cliente

Ejemplo: agregar `numero_causa`.

### 1. Editar modelo

Archivo:

```text
clientes/models.py
```

Agregar campo:

```python
numero_causa = models.CharField("Número de causa", max_length=80, blank=True)
```

### 2. Agregar al formulario visual

Archivo:

```text
clientes/templates/clientes/client_form.html
```

Agregar:

```django
{% include 'clientes/_field.html' with field=form.numero_causa span='span-3' %}
```

### 3. Agregar al detalle o contrato si corresponde

Archivos posibles:

```text
clientes/templates/clientes/client_detail.html
clientes/templates/clientes/contract_print.html
clientes/pdf_fallback.py
```

### 4. Crear migración

```bash
python manage.py makemigrations clientes
```

### 5. Aplicar migración

```bash
python manage.py migrate
```

En Docker producción:

```bash
sudo docker compose up -d --build
```

El entrypoint ejecuta `migrate` automáticamente.

## Cómo Cambiar el Diseño

Archivo principal:

```text
clientes/static/clientes/app.css
```

Plantillas:

```text
clientes/templates/clientes/base.html
clientes/templates/clientes/client_list.html
clientes/templates/clientes/client_form.html
clientes/templates/clientes/client_detail.html
clientes/templates/clientes/contract_print.html
```

Después de modificar CSS en Docker:

```bash
sudo docker compose exec web python manage.py collectstatic --noinput
sudo docker compose restart nginx
```

Si se reconstruye:

```bash
sudo docker compose up -d --build
```

## Cómo Cambiar el Contrato

El contrato HTML está en:

```text
clientes/templates/clientes/contract_print.html
```

Ese contrato se usa para:

- imprimir desde Chrome;
- generar PDF con WeasyPrint en Linux.

El fallback PDF está en:

```text
clientes/pdf_fallback.py
```

Si cambia mucho el contrato, conviene actualizar ambos:

1. plantilla HTML;
2. fallback ReportLab.

## Cómo Cambiar Reglas de Pago

Modelos:

```text
clientes/models.py
```

Vista:

```text
clientes/views.py
```

Plantillas:

```text
clientes/templates/clientes/client_detail.html
clientes/templates/clientes/contract_print.html
```

Reglas actuales:

```text
total servicio = neto + IVA
saldo = total servicio - suma pagos
```

## Cómo Cambiar Tipos de Documento

Archivo:

```text
clientes/models.py
```

Editar:

```python
CATEGORY_CHOICES = [
    ("contrato", "Contrato físico"),
    ("certificado", "Certificado"),
    ("comprobante", "Comprobante"),
    ("otro", "Otro"),
]
```

Si solo cambia etiquetas, no siempre hace falta migración. Si cambia valores internos, cree migración.

## Cómo Cambiar Extensiones Permitidas

Archivo:

```text
clientes/models.py
```

Editar:

```python
FileExtensionValidator(["pdf", "jpg", "jpeg", "png", "webp", "doc", "docx", "xls", "xlsx"])
```

Archivo:

```text
clientes/forms.py
```

Editar:

```python
self.fields["file"].widget.attrs["accept"] = ".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx,.xls,.xlsx"
```

## Cómo Crear Migraciones

Después de cambiar modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

Ver migraciones pendientes:

```bash
python manage.py showmigrations
```

## Buenas Prácticas Antes de Cambiar Producción

1. Crear respaldo:

```bash
sudo ./deploy/scripts/backup.sh
```

2. Probar cambios localmente.
3. Ejecutar pruebas.
4. Copiar código al servidor.
5. Reconstruir Docker.
6. Revisar logs.
7. Probar login, cliente, pago, documento y PDF.

## Checklist de Prueba Manual

Después de cualquier cambio importante:

```text
[ ] Login funciona.
[ ] Lista de clientes carga.
[ ] Búsqueda por nombre funciona.
[ ] Búsqueda por RUT funciona.
[ ] Se puede crear cliente con nombre y RUT.
[ ] Se puede editar cliente.
[ ] Se puede registrar pago.
[ ] El saldo se actualiza.
[ ] Se puede subir documento.
[ ] Se puede descargar documento.
[ ] Contrato imprimible abre.
[ ] Contrato PDF descarga.
[ ] Panel /admin/ abre.
[ ] Logs no muestran errores.
[ ] Respaldo manual funciona.
```

## Logs Útiles

Aplicación:

```bash
sudo docker compose logs -f web
```

Nginx:

```bash
sudo docker compose logs -f nginx
```

Base de datos:

```bash
sudo docker compose logs -f db
```

## Comandos Django Útiles

Entrar al shell:

```bash
sudo docker compose exec web python manage.py shell
```

Crear superusuario:

```bash
sudo docker compose exec web python manage.py createsuperuser
```

Cambiar contraseña:

```bash
sudo docker compose exec web python manage.py changepassword usuario
```

Aplicar migraciones:

```bash
sudo docker compose exec web python manage.py migrate
```

Recolectar estáticos:

```bash
sudo docker compose exec web python manage.py collectstatic --noinput
```

## Archivos Que No Deben Subirse Públicamente

No publicar:

```text
.env
db.sqlite3
media/
data/
staticfiles/
respaldos reales
```

Sí se puede compartir:

```text
.env.example
código fuente
documentación
Dockerfile
docker-compose.yml
requirements.txt
```

## Recomendación Final

Antes de tocar producción:

```text
respaldo primero, cambio después.
```

Es una regla simple, pero salva sistemas.
