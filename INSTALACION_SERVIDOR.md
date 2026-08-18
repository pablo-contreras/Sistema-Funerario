# Instalación en Dell PowerEdge T150

Guía preparada el 14 de junio de 2026.

## 1. Sistema operativo recomendado

Instale **Ubuntu Server 24.04.4 LTS de 64 bits** en el SSD. Es una versión madura, recibe mantenimiento estándar hasta mayo de 2029 y evita adoptar Ubuntu 26.04 LTS durante sus primeros meses. Dell indica soporte general para Ubuntu Server LTS en el PowerEdge T150; su página específica aún enumera 20.04 y 22.04, por lo que conviene actualizar primero BIOS, iDRAC y firmware del controlador desde Lifecycle Controller.

Si su contrato de soporte Dell exige una versión expresamente certificada para el T150, use Ubuntu Server 22.04.5 LTS y manténgalo con Ubuntu Pro o planifique la actualización. La aplicación funciona en ambas versiones porque se ejecuta en contenedores.

Descarga oficial: <https://ubuntu.com/download/server>

## 2. Distribución de los discos

- **SSD:** Ubuntu, Docker, PostgreSQL y documentos activos.
- **HDD mecánico:** respaldos versionados de PostgreSQL y documentos.
- No forme RAID 1 entre ambos discos. Mezclar SSD y HDD reduce el rendimiento y un espejo no conserva versiones anteriores.
- Un solo HDD de respaldo no cubre incendio, robo, falla del servidor ni ransomware. Agregue una copia cifrada externa o en otra ubicación.

Antes de instalar, anote modelo y tamaño de cada disco. En el instalador seleccione el SSD por modelo/tamaño y deje el HDD sin modificar. Use UEFI, tabla GPT, LVM y sistema de archivos ext4. Active la instalación de OpenSSH Server.

## 3. Preparación inicial

```bash
sudo apt update
sudo apt full-upgrade -y
sudo timedatectl set-timezone America/Santiago
sudo hostnamectl set-hostname servidor-funeraria
sudo reboot
```

Reserve una IP fija para el servidor en el router, por ejemplo `192.168.1.50`. Es preferible una reserva DHCP por dirección MAC a fijar una IP duplicable manualmente.

## 4. Montar el disco mecánico

Identifique cuidadosamente el HDD:

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

Los siguientes comandos borran el disco indicado. Sustituya `/dev/sdb` sólo después de verificar que sea el HDD mecánico y no el SSD:

```bash
sudo parted /dev/sdb --script mklabel gpt mkpart primary ext4 0% 100%
sudo mkfs.ext4 -L FUNERARIA_BACKUP /dev/sdb1
sudo mkdir -p /mnt/funeraria-backups
sudo blkid /dev/sdb1
```

Copie el UUID mostrado y agregue una línea en `/etc/fstab`:

```text
UUID=REEMPLACE-ESTE-UUID /mnt/funeraria-backups ext4 defaults,nofail 0 2
```

Luego monte y compruebe:

```bash
sudo mount -a
df -h /mnt/funeraria-backups
sudo mkdir -p /srv/funeraria/data /mnt/funeraria-backups
```

## 5. Instalar Docker y la aplicación

```bash
sudo apt install -y docker.io docker-compose-v2 git curl ufw
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
sudo mkdir -p /opt/sistema-funerario
sudo chown -R "$USER":"$USER" /opt/sistema-funerario /srv/funeraria /mnt/funeraria-backups
```

Copie esta carpeta completa a `/opt/sistema-funerario`, entre en ella y configure las claves:

```bash
cd /opt/sistema-funerario
cp .env.example .env
openssl rand -base64 48
nano .env
```

En `.env` cambie como mínimo:

- `DJANGO_SECRET_KEY`: salida de `openssl rand`.
- `POSTGRES_PASSWORD`: contraseña larga y distinta.
- `DJANGO_ALLOWED_HOSTS`: IP local y nombre Tailscale final.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: URL HTTPS final de Tailscale.

Levante el sistema y cree el administrador:

```bash
sudo docker compose up -d --build
sudo docker compose exec web python manage.py createsuperuser
sudo docker compose ps
```

Abra `http://192.168.1.50:8080` en Chrome, usando la IP reservada de su servidor.

## 6. Cortafuegos local

Cambie `192.168.1.0/24` si su red usa otro rango:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 8080 proto tcp
sudo ufw enable
sudo ufw status verbose
```

No redirija el puerto 8080 desde el router hacia Internet.

## 7. Acceso remoto privado con Tailscale

Tailscale permite entrar desde fuera sin publicar el sistema para toda Internet. Instálelo en el servidor y en cada computador o teléfono autorizado:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo tailscale serve --bg localhost:8080
sudo tailscale serve status
```

El último comando mostrará una dirección HTTPS similar a `https://servidor-funeraria.nombre.ts.net`. Añádala a `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_TRUSTED_ORIGINS`, luego reinicie:

```bash
sudo docker compose up -d
```

Use **Tailscale Serve**, no Funnel: Serve limita el acceso a sus dispositivos y usuarios autorizados; Funnel lo publicaría en Internet.

## 8. Respaldos automáticos en el HDD

```bash
cd /opt/sistema-funerario
sudo chmod +x deploy/scripts/*.sh
sudo cp deploy/funeraria-backup.service /etc/systemd/system/
sudo cp deploy/funeraria-backup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now funeraria-backup.timer
sudo systemctl start funeraria-backup.service
sudo systemctl status funeraria-backup.timer
ls -la /mnt/funeraria-backups
```

El temporizador crea un `pg_dump` de PostgreSQL y un archivo comprimido de documentos cada seis horas. Conserva 30 días. Revise el espacio con `df -h` y haga una restauración de prueba periódica.

## 9. Recomendaciones de operación

1. Conecte el servidor y el equipo de red a una UPS.
2. Mantenga iDRAC en una VLAN o red de administración, con contraseña distinta.
3. Cree una cuenta individual por empleado; no comparta la cuenta administradora.
4. Ejecute `sudo apt update && sudo apt upgrade` mensualmente.
5. Revise `sudo docker compose logs`, respaldos y espacio en disco.
6. Conserve una segunda copia cifrada fuera del PowerEdge.

## Fuentes oficiales

- Ubuntu 24.04 LTS: <https://documentation.ubuntu.com/release-notes/24.04/>
- Ciclo de soporte Ubuntu: <https://ubuntu.com/about/release-cycle>
- Sistemas compatibles Dell T150: <https://www.dell.com/support/home/en-us/drivers/supportedos/poweredge-t150>
- Instalación mediante Lifecycle Controller: <https://www.dell.com/support/kbdoc/en-us/000130160/how-to-install-the-operating-system-on-a-dell-poweredge-server-os-deployment>
- Respaldos PostgreSQL: <https://www.postgresql.org/docs/current/backup.html>
- Instalación de Tailscale en Linux: <https://tailscale.com/docs/install/linux>
- Tailscale Serve: <https://tailscale.com/docs/reference/tailscale-cli/serve>
- Django 5.2 LTS: <https://docs.djangoproject.com/en/6.0/releases/5.2/>
