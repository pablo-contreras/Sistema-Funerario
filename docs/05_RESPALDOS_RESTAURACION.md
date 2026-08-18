# 05 - Respaldos y Restauración

Este documento explica cómo funciona el respaldo del sistema funerario y cómo restaurarlo.

## Idea Principal

El sistema separa:

```text
SSD: datos activos
HDD: respaldos versionados
```

Datos activos:

```text
/srv/funeraria/data
```

Respaldos:

```text
/mnt/funeraria-backups
```

## Qué Se Respalda

El script `deploy/scripts/backup.sh` respalda:

1. base de datos PostgreSQL;
2. documentos subidos;
3. archivo `.env`;
4. sumas SHA256 para validar integridad.

Cada respaldo queda en una carpeta con fecha:

```text
/mnt/funeraria-backups/2026-06-14_18-30-00
```

Contenido típico:

```text
base-datos.dump
documentos.tar.gz
configuracion.env
SHA256SUMS
```

## Archivo `base-datos.dump`

Contiene la base de datos PostgreSQL.

Incluye:

- clientes;
- pagos;
- referencias a documentos;
- usuarios;
- permisos;
- sesiones;
- datos administrativos de Django.

Se crea con:

```bash
pg_dump --format custom
```

Ese formato permite restaurar con `pg_restore`.

## Archivo `documentos.tar.gz`

Contiene los archivos subidos por los usuarios.

Ejemplos:

- contratos físicos escaneados;
- certificados;
- comprobantes;
- imágenes;
- documentos Word o Excel.

No todos los documentos viven en la base de datos. Por eso es obligatorio respaldar también `media`.

## Archivo `configuracion.env`

Es una copia de `.env`.

Contiene:

- nombre de base;
- usuario de base;
- clave PostgreSQL;
- configuración de hosts;
- rutas de datos;
- rutas de respaldo.

Por seguridad se guarda con permisos restringidos:

```bash
chmod 600 configuracion.env
```

## Archivo `SHA256SUMS`

Permite verificar si los archivos del respaldo fueron modificados o dañados.

El script de restauración ejecuta:

```bash
sha256sum -c "$BACKUP_PATH/SHA256SUMS"
```

Si la verificación falla, no se debe confiar en ese respaldo.

## Crear Respaldo Manual

Desde el servidor:

```bash
cd /opt/sistema-funerario
sudo ./deploy/scripts/backup.sh
```

Verificar que se creó:

```bash
ls -lah /mnt/funeraria-backups
```

Ver contenido del último respaldo:

```bash
ls -lah /mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS
```

## Respaldo Automático

Los archivos systemd son:

```text
deploy/funeraria-backup.service
deploy/funeraria-backup.timer
```

Instalación:

```bash
cd /opt/sistema-funerario
sudo chmod +x deploy/scripts/*.sh
sudo cp deploy/funeraria-backup.service /etc/systemd/system/
sudo cp deploy/funeraria-backup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now funeraria-backup.timer
```

Ejecutar uno manual:

```bash
sudo systemctl start funeraria-backup.service
```

Ver estado del timer:

```bash
sudo systemctl status funeraria-backup.timer
```

Ver últimas ejecuciones:

```bash
journalctl -u funeraria-backup.service --no-pager -n 80
```

## Retención de Respaldos

El script elimina respaldos de más de 30 días:

```bash
find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf -- {} +
```

Si necesita más historial, cambie `+30` por otro número.

Ejemplo para 90 días:

```bash
-mtime +90
```

## Restaurar un Respaldo

Advertencia: restaurar reemplaza la base de datos actual.

Antes de restaurar:

1. avise a los usuarios;
2. haga un respaldo del estado actual;
3. confirme la carpeta correcta;
4. revise que el respaldo tenga `base-datos.dump`.

Crear respaldo de emergencia antes de restaurar:

```bash
cd /opt/sistema-funerario
sudo ./deploy/scripts/backup.sh
```

Restaurar:

```bash
sudo ./deploy/scripts/restore.sh /mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS
```

Ejemplo:

```bash
sudo ./deploy/scripts/restore.sh /mnt/funeraria-backups/2026-06-14_18-30-00
```

## Qué Hace `restore.sh`

Flujo:

```text
1. Recibe ruta del respaldo.
2. Convierte ruta a absoluta.
3. Carga .env actual.
4. Verifica que exista base-datos.dump.
5. Verifica SHA256SUMS.
6. Elimina la base PostgreSQL actual.
7. Crea una base vacía.
8. Restaura el dump.
9. Extrae documentos.tar.gz si existe.
10. Reinicia web.
```

## Probar Restauración Sin Dañar Producción

Lo ideal es probar en otro equipo o en otra carpeta.

Pasos recomendados:

```bash
mkdir -p /opt/sistema-funerario-prueba
cp -a /opt/sistema-funerario/. /opt/sistema-funerario-prueba/
```

Editar `.env` de prueba:

```text
POSTGRES_DB=funeraria_prueba
DATA_DIR=/srv/funeraria/prueba
```

Levantar prueba en otro puerto si modifica `docker-compose.yml`.

Esto permite confirmar que los respaldos sirven antes de necesitarlos en una emergencia.

## Respaldo Completo del Sistema Operativo

Además de los respaldos de aplicación, se puede crear una imagen completa del SSD con Clonezilla.

Esa imagen sirve para recuperar:

- Ubuntu;
- Docker;
- configuración de red;
- instalación de Tailscale;
- sistema desplegado.

Pero la imagen completa no reemplaza los respaldos diarios porque:

- queda desactualizada rápidamente;
- puede ser muy grande;
- no siempre contiene los últimos clientes/pagos/documentos;
- restaurarla toma más tiempo.

Estrategia recomendada:

```text
Imagen Clonezilla: después de instalar o hacer cambios grandes.
Respaldos de aplicación: diarios o cada 6 horas.
Copia externa: periódica, fuera del servidor.
```

## Copia Externa Recomendada

El disco mecánico está dentro del mismo servidor. Eso no protege contra:

- robo;
- incendio;
- falla eléctrica grave;
- ransomware;
- error humano con acceso al servidor;
- falla simultánea de hardware.

Recomendación:

- copiar respaldos periódicamente a un disco USB externo;
- o subir copia cifrada a almacenamiento externo;
- o tener otro equipo/NAS en otra ubicación.

Ejemplo simple con disco USB montado en `/mnt/usb-backups`:

```bash
sudo rsync -a --delete /mnt/funeraria-backups/ /mnt/usb-backups/funeraria-backups/
```

## Checklist Semanal

```bash
df -h /mnt/funeraria-backups
ls -lah /mnt/funeraria-backups | tail
journalctl -u funeraria-backup.service --no-pager -n 40
```

Confirmar:

- hay respaldos recientes;
- no hay errores en journal;
- el disco tiene espacio;
- existe `base-datos.dump`;
- existe `documentos.tar.gz` si hay archivos subidos;
- se puede verificar `SHA256SUMS`.

## Checklist Mensual

1. Hacer restauración de prueba.
2. Copiar respaldos fuera del servidor.
3. Revisar espacio de SSD y HDD.
4. Revisar que el timer sigue activo.
5. Revisar que Tailscale sigue conectado.
6. Confirmar que el usuario administrador todavía puede entrar.

## Comandos Rápidos

Ver respaldos:

```bash
ls -lah /mnt/funeraria-backups
```

Crear respaldo:

```bash
cd /opt/sistema-funerario
sudo ./deploy/scripts/backup.sh
```

Ver timer:

```bash
sudo systemctl status funeraria-backup.timer
```

Ver errores:

```bash
journalctl -u funeraria-backup.service --no-pager -n 100
```

Restaurar:

```bash
sudo ./deploy/scripts/restore.sh /mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS
```
