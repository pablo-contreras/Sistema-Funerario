# Sistema de Gestión Funeraria

<p align="center">
  <img src="static/img/logo.png" alt="Sistema de Gestión Funeraria" width="180">
</p>

<p align="center">
  Sistema web para la administración integral de clientes, servicios funerarios, pagos, contratos y documentación.
</p>

---

## Descripción del proyecto

El **Sistema de Gestión Funeraria** es una aplicación web desarrollada para centralizar y facilitar la administración de información asociada a los servicios de una empresa funeraria.

La plataforma permite gestionar fichas de clientes, información del fallecido, antecedentes del servicio, contratos, pagos, documentos y saldos pendientes desde una interfaz centralizada.

El sistema fue diseñado con una arquitectura preparada para funcionar tanto en un entorno local como en un servidor de producción, utilizando tecnologías de desarrollo web, base de datos relacional, contenedores y servidor proxy.

---

## Características principales

### Gestión de clientes

* Creación de fichas de clientes.
* Edición y eliminación de registros.
* Validación y normalización de RUT.
* Generación automática de folio.
* Registro de datos personales y de contacto.
* Búsqueda por nombre, RUT, fallecido o folio.
* Registro del usuario responsable de crear cada ficha.

### Información del fallecido

Permite registrar antecedentes como:

* nombre;
* RUT;
* domicilio;
* lugar de nacimiento;
* edad;
* estado civil;
* estudios;
* previsión;
* fecha de nacimiento;
* fecha y hora de fallecimiento;
* lugar de fallecimiento;
* lugar de inscripción;
* información de los padres.

### Gestión del servicio funerario

El sistema permite registrar información relacionada con la prestación del servicio, incluyendo:

* tipo de urna;
* traslado al cementerio;
* lugar de velación;
* fecha y hora de misa;
* iglesia;
* automóvil;
* microbús;
* descripción del servicio;
* vendedor responsable;
* lugar y fecha del contrato.

### Gestión financiera

* Registro del valor neto del servicio.
* Cálculo automático de IVA.
* Cálculo del valor total.
* Registro de múltiples pagos o abonos.
* Número de recibo por pago.
* Historial de pagos.
* Cálculo automático del total pagado.
* Cálculo del saldo pendiente.

### Gestión documental

Cada cliente dispone de una carpeta documental independiente.

El sistema permite almacenar documentos asociados a diferentes categorías:

* contratos;
* certificados;
* comprobantes;
* imágenes;
* otros documentos administrativos.

Formatos admitidos:

```text
PDF
JPG / JPEG
PNG
WEBP
DOC / DOCX
XLS / XLSX
```

### Contratos y documentos PDF

* Visualización de información contractual.
* Formato preparado para impresión desde el navegador.
* Generación y descarga del contrato en PDF.
* Presentación estructurada de los datos del cliente y del servicio.

### Usuarios y autenticación

* Inicio de sesión mediante el sistema de autenticación de Django.
* Gestión administrativa de usuarios.
* Control de acceso a las funciones del sistema.
* Panel administrativo independiente.
* Validación de contraseñas mediante las políticas de seguridad de Django.

### Respaldos

El proyecto incluye herramientas para realizar respaldos de:

* base de datos PostgreSQL;
* documentos almacenados;
* configuración del sistema.

Los respaldos incorporan verificación mediante sumas `SHA256`.

También se incluyen scripts para:

* generar respaldos;
* restaurar respaldos;
* automatizar respaldos mediante `systemd`.

---

## Tecnologías utilizadas

### Backend

* **Python**
* **Django 5.2**
* **Gunicorn**

### Base de datos

* **PostgreSQL 16** para producción.
* **SQLite** como alternativa para entornos locales de desarrollo.

### Frontend

* HTML5
* CSS3
* Django Templates

### Infraestructura

* Docker
* Docker Compose
* Nginx
* Ubuntu Server
* systemd

### Generación de documentos

* ReportLab
* WeasyPrint

### Seguridad y acceso remoto

* Autenticación Django
* Protección CSRF
* Cookies configurables para HTTPS
* Nginx como proxy inverso
* Tailscale como alternativa de acceso remoto privado

---

## Arquitectura

La solución utiliza una arquitectura basada en contenedores.

```text
                         USUARIO
                            │
                            ▼
                      Navegador Web
                            │
                            ▼
                         Nginx
                            │
                            ▼
                    Django + Gunicorn
                       │          │
                       │          └────────► Documentos
                       │
                       ▼
                    PostgreSQL
```

En producción, Docker Compose administra los principales servicios:

```text
┌────────────────────────────────────┐
│          Docker Compose            │
│                                    │
│   ┌──────────┐                     │
│   │  Nginx   │                     │
│   └────┬─────┘                     │
│        │                            │
│        ▼                            │
│   ┌──────────┐     ┌────────────┐  │
│   │  Django  │────►│ PostgreSQL │  │
│   │ Gunicorn │     │            │  │
│   └──────────┘     └────────────┘  │
│                                    │
└────────────────────────────────────┘
```

Nginx recibe las solicitudes HTTP y las deriva a la aplicación Django ejecutada mediante Gunicorn.

Django administra la lógica del sistema y se comunica con PostgreSQL para almacenar la información persistente.

---

## Estructura del proyecto

```text
sistema-funerario-final/
│
├── clientes/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── templatetags/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── pdf_fallback.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
│
├── funeraria/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── deploy/
│   ├── nginx/
│   ├── scripts/
│   │   ├── backup.sh
│   │   ├── entrypoint.sh
│   │   └── restore.sh
│   ├── funeraria-backup.service
│   └── funeraria-backup.timer
│
├── docs/
│   ├── 00_INDICE.md
│   ├── 01_ARQUITECTURA.md
│   ├── 02_MODULOS_DEL_CODIGO.md
│   ├── 03_FLUJOS_DEL_SISTEMA.md
│   ├── 04_INSTALACION_OPERACION.md
│   ├── 05_RESPALDOS_RESTAURACION.md
│   ├── 06_SEGURIDAD_ACCESO_REMOTO.md
│   ├── 07_DESARROLLO_PRUEBAS.md
│   ├── 08_RESPALDOS_Y_FALLA_CRITICA.md
│   ├── MANUAL_TECNICO_PROGRAMADOR_ADMINISTRADOR.md
│   └── MANUAL_USUARIO_COMUN.md
│
├── static/
│   └── img/
│       └── logo.png
│
├── tests/
│   └── test_system.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── INSTALACION_SERVIDOR.md
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Instalación

### Requisitos

Para un despliegue mediante contenedores se requiere:

* Docker;
* Docker Compose;
* Git;
* sistema operativo compatible con Docker.

Para desarrollo local también es posible utilizar Python directamente.

---

## Instalación con Docker

### 1. Clonar el repositorio

```bash
git clone https://github.com/pablo-contreras/Sistema-Funerario.git
```

Ingresar al proyecto:

```bash
cd Sistema-Funerario
```

### 2. Crear archivo de configuración

Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Editar `.env` y establecer valores propios para el entorno.

Ejemplo:

```env
DJANGO_SECRET_KEY=CLAVE-SEGURA-PARA-PRODUCCION
DJANGO_DEBUG=False

POSTGRES_DB=funeraria
POSTGRES_USER=funeraria
POSTGRES_PASSWORD=CAMBIE_ESTA_CLAVE

POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> El archivo `.env` contiene información sensible y no debe almacenarse en el repositorio.

### 3. Construir e iniciar los contenedores

```bash
docker compose up -d --build
```

### 4. Comprobar los servicios

```bash
docker compose ps
```

### 5. Crear usuario administrador

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acceder al sistema

El despliegue predeterminado publica el servicio mediante:

```text
http://localhost:8080
```

En una instalación dentro de una red local puede utilizarse:

```text
http://IP-DEL-SERVIDOR:8080
```

---

## Configuración

Las principales variables de entorno se encuentran documentadas en:

```text
.env.example
```

Variables principales:

| Variable                      | Descripción                              |
| ----------------------------- | ---------------------------------------- |
| `DJANGO_SECRET_KEY`           | Clave criptográfica utilizada por Django |
| `DJANGO_DEBUG`                | Activa o desactiva el modo de depuración |
| `DJANGO_ALLOWED_HOSTS`        | Hosts autorizados                        |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS de confianza              |
| `POSTGRES_DB`                 | Nombre de la base de datos               |
| `POSTGRES_USER`               | Usuario de PostgreSQL                    |
| `POSTGRES_PASSWORD`           | Contraseña de PostgreSQL                 |
| `POSTGRES_HOST`               | Servidor de PostgreSQL                   |
| `POSTGRES_PORT`               | Puerto de PostgreSQL                     |
| `DATA_DIR`                    | Directorio de datos persistentes         |
| `BACKUP_DIR`                  | Directorio destinado a respaldos         |

---

## Uso

Una vez iniciado el sistema, el usuario debe autenticarse mediante la pantalla de inicio de sesión.

Desde la aplicación puede:

1. consultar el listado de clientes;
2. buscar registros;
3. crear una nueva ficha;
4. ingresar antecedentes del contratante;
5. ingresar antecedentes del fallecido;
6. registrar detalles del servicio;
7. registrar información contractual;
8. agregar pagos;
9. consultar el saldo pendiente;
10. adjuntar documentos;
11. imprimir o generar el contrato;
12. actualizar información existente.

El panel administrativo de Django se encuentra disponible en:

```text
/admin/
```

Su utilización debe reservarse a usuarios autorizados.

---

## Seguridad

El proyecto incorpora diferentes medidas de seguridad.

### Autenticación

Las funciones del sistema requieren autenticación de usuario.

### Contraseñas

Se utilizan los validadores integrados de Django para impedir contraseñas excesivamente débiles.

### Protección CSRF

Django protege las operaciones realizadas mediante formularios contra ataques de tipo Cross-Site Request Forgery.

### Protección contra Clickjacking

El sistema utiliza:

```text
X_FRAME_OPTIONS = "DENY"
```

### Protección del contenido

También se encuentra habilitada:

```text
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Variables sensibles

Las contraseñas, claves y parámetros privados deben almacenarse en `.env`.

El archivo real:

```text
.env
```

está excluido del control de versiones mediante `.gitignore`.

### Acceso remoto

Para una instalación real no se recomienda publicar directamente el puerto de la aplicación hacia Internet.

Cuando se requiere acceso remoto privado puede utilizarse una solución VPN como Tailscale.

---

## Respaldos y restauración

El sistema incorpora:

```text
deploy/scripts/backup.sh
deploy/scripts/restore.sh
```

### Crear respaldo manual

```bash
sudo ./deploy/scripts/backup.sh
```

El respaldo puede contener:

```text
base-datos.dump
documentos.tar.gz
configuracion.env
SHA256SUMS
```

### Verificación de integridad

Los respaldos utilizan hashes SHA256 para comprobar que los archivos no hayan sido modificados o dañados.

### Restaurar

```bash
sudo ./deploy/scripts/restore.sh /ruta/del/respaldo
```

> Antes de realizar una restauración se recomienda generar un respaldo del estado actual.

---

## Pruebas

El proyecto incluye pruebas automatizadas.

Para ejecutarlas:

```bash
pytest
```

También pueden ejecutarse dentro del contenedor:

```bash
docker compose exec web pytest
```

La configuración de pytest se encuentra en:

```text
pytest.ini
```

---

## Documentación

El repositorio incluye documentación técnica y de usuario.

### Arquitectura

[docs/01_ARQUITECTURA.md](docs/01_ARQUITECTURA.md)

Descripción de la arquitectura general y comunicación entre los diferentes componentes.

### Módulos del código

[docs/02_MODULOS_DEL_CODIGO.md](docs/02_MODULOS_DEL_CODIGO.md)

Descripción de los principales archivos y módulos del proyecto.

### Flujos del sistema

[docs/03_FLUJOS_DEL_SISTEMA.md](docs/03_FLUJOS_DEL_SISTEMA.md)

Explicación de los principales procesos realizados por los usuarios.

### Instalación y operación

[docs/04_INSTALACION_OPERACION.md](docs/04_INSTALACION_OPERACION.md)

Procedimientos para instalar, iniciar, detener y mantener el sistema.

### Respaldos y restauración

[docs/05_RESPALDOS_RESTAURACION.md](docs/05_RESPALDOS_RESTAURACION.md)

Funcionamiento de los mecanismos de respaldo y recuperación.

### Seguridad y acceso remoto

[docs/06_SEGURIDAD_ACCESO_REMOTO.md](docs/06_SEGURIDAD_ACCESO_REMOTO.md)

Medidas de seguridad recomendadas para la operación del sistema.

### Desarrollo y pruebas

[docs/07_DESARROLLO_PRUEBAS.md](docs/07_DESARROLLO_PRUEBAS.md)

Información para continuar desarrollando y probando la aplicación.

### Recuperación ante fallas

[docs/08_RESPALDOS_Y_FALLA_CRITICA.md](docs/08_RESPALDOS_Y_FALLA_CRITICA.md)

Procedimientos para responder ante fallas críticas.

### Manual técnico

[docs/MANUAL_TECNICO_PROGRAMADOR_ADMINISTRADOR.md](docs/MANUAL_TECNICO_PROGRAMADOR_ADMINISTRADOR.md)

Manual destinado a desarrolladores y administradores.

También disponible en formato PDF:

[docs/manual_tecnico_programador_administrador.pdf](docs/manual_tecnico_programador_administrador.pdf)

### Manual de usuario

[docs/MANUAL_USUARIO_COMUN.md](docs/MANUAL_USUARIO_COMUN.md)

Guía de utilización destinada al usuario final.

También disponible en formato PDF:

[docs/manual_usuario_comun.pdf](docs/manual_usuario_comun.pdf)

---

## Operación del sistema

### Estado de los contenedores

```bash
docker compose ps
```

### Logs de Django

```bash
docker compose logs -f web
```

### Logs de Nginx

```bash
docker compose logs -f nginx
```

### Logs de PostgreSQL

```bash
docker compose logs -f db
```

### Reiniciar servicios

```bash
docker compose restart
```

### Reconstruir después de una actualización

```bash
docker compose up -d --build
```

---

## Persistencia de datos

Los datos de producción se mantienen fuera de los contenedores.

Esto permite reconstruir o actualizar los servicios sin perder:

* registros de clientes;
* pagos;
* usuarios;
* documentos;
* información administrativa.

PostgreSQL mantiene su información en almacenamiento persistente y los documentos se almacenan en un directorio independiente.

---

## Objetivos del proyecto

El proyecto busca:

* digitalizar el registro de servicios funerarios;
* centralizar información que normalmente se encuentra distribuida;
* facilitar la consulta de antecedentes;
* disminuir errores de registro;
* mantener un historial de pagos;
* automatizar cálculos financieros;
* ordenar la documentación de cada cliente;
* disponer de mecanismos de respaldo y recuperación;
* proporcionar una plataforma administrable y escalable.

---

## Estado del proyecto

**Versión estable inicial.**

El sistema dispone actualmente de:

* gestión de clientes;
* gestión de información funeraria;
* gestión de pagos;
* cálculo de saldos;
* gestión documental;
* generación de contratos;
* generación de PDF;
* autenticación;
* administración de usuarios;
* PostgreSQL;
* despliegue con Docker;
* proxy inverso mediante Nginx;
* respaldos y restauración;
* documentación técnica;
* manual de usuario;
* pruebas automatizadas.

---

## Autor

**Pablo Contreras**

Proyecto desarrollado como solución para la digitalización y administración de procesos asociados a la gestión funeraria.

---

## Aviso

Este repositorio no contiene contraseñas, claves privadas ni credenciales reales de producción.

Los valores incluidos en `.env.example` son únicamente ejemplos de configuración y deben ser reemplazados antes de utilizar el sistema en un entorno real.

