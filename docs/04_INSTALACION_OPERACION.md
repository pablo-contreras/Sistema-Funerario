# 04 - Instalación y Operación

Este documento resume cómo instalar y operar el sistema en el servidor Ubuntu.

La guía larga original está en:

```text
INSTALACION_SERVIDOR.md
```

Este documento se concentra en el uso diario y mantenimiento.

## Requisitos del Servidor

Servidor usado:

```text
Dell PowerEdge T150
```

Sistema recomendado:

```text
Ubuntu Server 24.04.4 LTS
```

Distribución elegida:

```text
SSD: sistema operativo, Docker, PostgreSQL, documentos activos.
HDD: respaldos versionados.
```

## Carpetas Importantes

Código del sistema:

```text
/opt/sistema-funerario
```

Datos activos:

```text
/srv/funeraria/data
```

Base PostgreSQL:

```text
/srv/funeraria/data/postgres
```

Documentos subidos:

```text
/srv/funeraria/data/media
```

Respaldos:

```text
/mnt/funeraria-backups
```

## Instalación Inicial

### 1. Preparar sistema

```bash
sudo apt update
sudo apt full-upgrade -y
sudo timedatectl set-timezone America/Santiago
sudo hostnamectl set-hostname servidor-funeraria
sudo reboot
```

### 2. Instalar Docker

```bash
sudo apt install -y docker.io docker-compose-v2 git curl ufw unzip
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Después de `usermod`, cierre sesión y vuelva a entrar.

### 3. Crear carpetas

```bash
sudo mkdir -p /opt/sistema-funerario
sudo mkdir -p /srv/funeraria/data
sudo mkdir -p /mnt/funeraria-backups
sudo chown -R "$USER":"$USER" /opt/sistema-funerario /srv/funeraria /mnt/funeraria-backups
```

### 4. Copiar el código

Copie esta carpeta completa al servidor:

```text
/opt/sistema-funerario
```

Debe quedar así:

```text
/opt/sistema-funerario/manage.py
/opt/sistema-funerario/docker-compose.yml
/opt/sistema-funerario/clientes/
/opt/sistema-funerario/funeraria/
```

### 5. Crear `.env`

```bash
cd /opt/sistema-funerario
cp .env.example .env
nano .env
```

Valores mínimos que debe cambiar:

```text
DJANGO_SECRET_KEY
POSTGRES_PASSWORD
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
```

Para generar claves:

```bash
openssl rand -hex 32
openssl rand -hex 24
```

Ejemplo de `.env` para red local:

```text
DJANGO_SECRET_KEY=clave-larga-generada
DJANGO_DEBUG=False
DJANGO_SECURE_COOKIES=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.22
DJANGO_CSRF_TRUSTED_ORIGINS=
POSTGRES_DB=funeraria
POSTGRES_USER=funeraria
POSTGRES_PASSWORD=clave-postgres-generada
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATA_DIR=/srv/funeraria/data
BACKUP_DIR=/mnt/funeraria-backups
```

Ejemplo agregando Tailscale:

```text
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.22,servidor-funeraria.taild7534a.ts.net
DJANGO_CSRF_TRUSTED_ORIGINS=https://servidor-funeraria.taild7534a.ts.net
```

## Levantar el Sistema

```bash
cd /opt/sistema-funerario
sudo docker compose up -d --build
```

Ver estado:

```bash
sudo docker compose ps
```

Debe aparecer algo parecido a:

```text
db       Up healthy
web      Up
nginx    Up
```

## Crear Usuario Administrador

```bash
sudo docker compose exec web python manage.py createsuperuser
```

Ese usuario permite:

- entrar al sistema;
- entrar a `/admin/`;
- crear otros usuarios.

## Abrir en Chrome

En red local:

```text
http://192.168.0.22:8080
```

Por Tailscale:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

## Comandos de Operación Diaria

### Ver contenedores

```bash
cd /opt/sistema-funerario
sudo docker compose ps
```

### Ver logs de la aplicación

```bash
sudo docker compose logs -f web
```

### Ver logs de Nginx

```bash
sudo docker compose logs -f nginx
```

### Ver logs de PostgreSQL

```bash
sudo docker compose logs -f db
```

### Reiniciar todo

```bash
sudo docker compose restart
```

### Reiniciar solo web

```bash
sudo docker compose restart web
```

### Apagar sistema

```bash
sudo docker compose down
```

Esto apaga contenedores, pero no borra datos.

### Volver a levantar

```bash
sudo docker compose up -d
```

## Actualizar Código

Cuando copie una versión nueva del sistema:

```bash
cd /opt/sistema-funerario
sudo docker compose up -d --build
```

El contenedor `web` aplicará migraciones automáticamente al iniciar.

## Revisar Espacio en Disco

```bash
df -h
df -h /srv/funeraria/data
df -h /mnt/funeraria-backups
```

Ver tamaño de datos:

```bash
sudo du -sh /srv/funeraria/data
sudo du -sh /mnt/funeraria-backups
```

## Revisar IP del Servidor

```bash
hostname -I
```

## Revisar Montaje del HDD

```bash
findmnt /mnt/funeraria-backups
df -h /mnt/funeraria-backups
```

Si no aparece montado, revise:

```bash
cat /etc/fstab
sudo mount -a
```

## Panel Administrativo

URL:

```text
http://192.168.0.22:8080/admin/
```

Desde ahí se puede:

- crear usuarios;
- cambiar contraseñas;
- revisar clientes;
- revisar pagos;
- revisar documentos.

Recomendación:

- crear una cuenta por persona;
- no compartir el usuario administrador;
- usar contraseñas largas;
- desactivar usuarios que ya no trabajen en la funeraria.

## Variables de Entorno Importantes

| Variable | Valor recomendado |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECURE_COOKIES` | `True` si se usa solo HTTPS |
| `DATA_DIR` | `/srv/funeraria/data` |
| `BACKUP_DIR` | `/mnt/funeraria-backups` |
| `POSTGRES_HOST` | `db` |

## Errores Comunes

### Página sin estilos

Ejecutar:

```bash
sudo docker compose exec web python manage.py collectstatic --noinput
sudo docker compose restart nginx
```

### Error 502 por Tailscale

Revisar que Nginx esté arriba:

```bash
sudo docker compose ps
curl -I http://127.0.0.1:8080
```

Luego reiniciar Tailscale Serve:

```bash
sudo tailscale serve --bg http://127.0.0.1:8080
```

### No deja iniciar sesión

Crear o resetear usuario:

```bash
sudo docker compose exec web python manage.py createsuperuser
sudo docker compose exec web python manage.py changepassword nombre_usuario
```

### Error CSRF por Tailscale

Editar `.env`:

```text
DJANGO_CSRF_TRUSTED_ORIGINS=https://servidor-funeraria.taild7534a.ts.net
```

Luego:

```bash
sudo docker compose up -d
```

## Checklist Después de Reiniciar el Servidor

```bash
cd /opt/sistema-funerario
sudo docker compose ps
findmnt /mnt/funeraria-backups
curl -I http://127.0.0.1:8080
tailscale status
```

Abrir en Chrome:

```text
http://192.168.0.22:8080
```
