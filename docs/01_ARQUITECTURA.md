# 01 - Arquitectura del Sistema

Este documento explica la arquitectura general del sistema funerario: qué componentes lo forman, para qué sirve cada uno y cómo viajan los datos desde el navegador hasta la base de datos y los respaldos.

## Objetivo del Sistema

El sistema reemplaza el contrato HTML estático por una aplicación web local que guarda fichas reales de clientes. La aplicación queda pensada para una oficina funeraria que necesita:

- registrar datos del contratante;
- registrar datos del fallecido;
- registrar datos del servicio funerario;
- registrar pagos y saldos;
- guardar documentos asociados al cliente;
- imprimir o descargar el contrato;
- trabajar desde computadores de la red local;
- acceder de forma privada desde fuera de la red;
- respaldar base de datos y archivos.

## Capas Principales

El sistema está dividido en cuatro capas:

```text
Chrome / navegador
        |
        v
Nginx - puerto 8080
        |
        v
Django + Gunicorn
        |
        v
PostgreSQL + archivos en disco
```

### 1. Navegador

El usuario entra con Chrome, desde la red local o por Tailscale.

Desde el navegador puede:

- iniciar sesión;
- ver la lista de clientes;
- buscar por nombre o RUT;
- crear una ficha;
- editar una ficha;
- registrar pagos;
- subir documentos;
- imprimir contratos;
- descargar contratos en PDF.

### 2. Nginx

Nginx es el servidor web que queda escuchando en el puerto `8080`.

Sus tareas son:

- recibir las conexiones HTTP;
- entregar archivos estáticos como CSS y logo;
- pasar las solicitudes dinámicas a Django;
- limitar tamaño de subida de archivos;
- conservar encabezados de proxy para que Django sepa el host y protocolo original.

Archivo principal:

```text
deploy/nginx/default.conf
```

### 3. Django + Gunicorn

Django es el framework principal de la aplicación.

Gunicorn ejecuta Django dentro del contenedor `web`.

Django se encarga de:

- validar formularios;
- guardar clientes, pagos y documentos;
- proteger páginas con inicio de sesión;
- generar vistas HTML;
- generar o descargar contratos PDF;
- servir el panel administrativo;
- definir reglas de negocio como saldo pendiente, folio y carpeta del cliente.

Archivos principales:

```text
funeraria/settings.py
funeraria/urls.py
clientes/models.py
clientes/forms.py
clientes/views.py
clientes/urls.py
```

### 4. PostgreSQL

PostgreSQL guarda los datos estructurados:

- clientes;
- pagos;
- documentos subidos;
- usuarios del sistema;
- permisos;
- sesiones administrativas.

El contenedor se llama `db` y usa la imagen:

```text
postgres:16-bookworm
```

Los datos físicos se guardan en:

```text
${DATA_DIR}/postgres
```

En el servidor real se configuró `DATA_DIR` como:

```text
/srv/funeraria/data
```

### 5. Archivos Subidos

Los documentos asociados a los clientes no se guardan dentro de PostgreSQL. Se guardan como archivos físicos en disco.

La base de datos solo guarda la referencia al archivo.

Ruta dentro del contenedor:

```text
/app/media
```

Ruta en el servidor:

```text
/srv/funeraria/data/media
```

Cada archivo queda en una ruta similar a:

```text
clientes/nombre-cliente-rut/contrato.pdf
```

La carpeta se calcula a partir del nombre y RUT del cliente.

## Contenedores Docker

El archivo `docker-compose.yml` levanta tres servicios.

### Servicio `db`

Base de datos PostgreSQL.

Responsabilidades:

- almacenar datos persistentes;
- validar disponibilidad mediante `pg_isready`;
- guardar la base en un volumen/directorio persistente.

### Servicio `web`

Aplicación Django ejecutada con Gunicorn.

Responsabilidades:

- aplicar migraciones al iniciar;
- recolectar archivos estáticos;
- atender la lógica de negocio;
- conectarse a PostgreSQL;
- usar `/app/media` para documentos subidos.

### Servicio `nginx`

Servidor frontal.

Responsabilidades:

- publicar el sistema en `http://servidor:8080`;
- servir `/static/`;
- reenviar el resto a `web:8000`.

## Flujo de una Solicitud

Ejemplo: abrir la lista de clientes.

```text
1. Usuario abre Chrome.
2. Chrome solicita http://192.168.0.22:8080/
3. Nginx recibe la solicitud.
4. Nginx la envía a Django/Gunicorn.
5. Django verifica si el usuario inició sesión.
6. Django consulta PostgreSQL.
7. Django renderiza la plantilla client_list.html.
8. Nginx devuelve la respuesta al navegador.
```

## Persistencia de Datos

Los datos persistentes están fuera de los contenedores. Eso es clave: si se reconstruyen los contenedores, los datos no se pierden.

```text
/srv/funeraria/data/postgres  Base de datos PostgreSQL
/srv/funeraria/data/media     Documentos subidos
```

Los respaldos se copian al disco mecánico:

```text
/mnt/funeraria-backups
```

## Por Qué No Se Usó RAID 1 Entre SSD y HDD

El servidor tenía un SSD y un disco mecánico. No conviene hacer espejo entre discos tan distintos porque:

- el HDD reduce el rendimiento del SSD;
- un borrado accidental también se replica al espejo;
- una corrupción de datos también se replica;
- un espejo no permite volver a una versión anterior;
- no reemplaza una estrategia real de respaldos.

Por eso se eligió:

- SSD: sistema operativo, Docker, PostgreSQL y documentos activos;
- HDD: respaldos versionados cada cierto tiempo.

## Acceso Local y Acceso Remoto

### Red local

En red local se usa:

```text
http://192.168.0.22:8080
```

### Fuera de la red

Para acceso remoto se usa Tailscale Serve:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

Tailscale Serve es privado para dispositivos autorizados en la cuenta de Tailscale. No es lo mismo que Tailscale Funnel, que publicaría el servicio hacia Internet.

## Seguridad Básica

El sistema aplica estas defensas:

- todas las vistas principales requieren login;
- Django protege formularios con CSRF;
- las contraseñas se manejan con el sistema de usuarios de Django;
- Nginx limita subida de archivos a `25m`;
- Django limita archivos a 20 MB en el formulario;
- archivos permitidos: PDF, imágenes, Word y Excel;
- `ALLOWED_HOSTS` limita desde qué nombres/IP responde Django;
- `CSRF_TRUSTED_ORIGINS` permite usar HTTPS por Tailscale;
- se recomienda firewall local con UFW.

## Resumen de Componentes

| Componente | Archivo o servicio | Función |
|---|---|---|
| Django | `clientes/`, `funeraria/` | Aplicación web y reglas del negocio |
| PostgreSQL | servicio `db` | Base de datos |
| Gunicorn | comando del `Dockerfile` | Servidor Python de producción |
| Nginx | servicio `nginx` | Proxy y archivos estáticos |
| Docker Compose | `docker-compose.yml` | Levanta todos los servicios |
| Backup | `deploy/scripts/backup.sh` | Crea respaldo de base y documentos |
| Restore | `deploy/scripts/restore.sh` | Restaura un respaldo |
| Tailscale | servicio externo | Acceso remoto privado |
