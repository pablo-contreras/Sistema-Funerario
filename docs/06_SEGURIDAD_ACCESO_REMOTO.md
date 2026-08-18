# 06 - Seguridad y Acceso Remoto

Este documento explica cómo dejar el sistema razonablemente protegido en red local y cómo acceder desde fuera usando Tailscale.

## Principio Básico

El sistema contiene datos sensibles de clientes, pagos y documentos. Por eso no conviene exponerlo directamente a Internet.

Recomendación:

```text
Usar red local + Tailscale Serve.
No abrir el puerto 8080 en el router hacia Internet.
```

## Acceso Local

En red local:

```text
http://192.168.0.22:8080
```

Este acceso debe estar disponible solo para equipos conectados a la red de la funeraria.

## Acceso Fuera de la Red

Se configuró Tailscale Serve.

URL:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

Tailscale permite que solo dispositivos autorizados entren al servidor.

## Tailscale Serve vs Funnel

### Tailscale Serve

Serve expone el servicio solo dentro de la red privada Tailscale.

Es lo recomendado para este sistema.

Uso:

```bash
sudo tailscale serve --bg http://127.0.0.1:8080
```

### Tailscale Funnel

Funnel expone el servicio a Internet público.

No se recomienda para este sistema funerario porque cualquier persona con la URL podría llegar a la pantalla de login.

Aunque exista login, sigue siendo más riesgoso.

## Instalar Tailscale en el Servidor

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Ver estado:

```bash
tailscale status
```

Activar Serve:

```bash
sudo tailscale serve --bg http://127.0.0.1:8080
```

Ver estado de Serve:

```bash
sudo tailscale serve status
```

## Instalar Tailscale en un Computador Externo

1. Instalar Tailscale para Windows, macOS o Linux.
2. Iniciar sesión con la misma cuenta autorizada.
3. Verificar que aparezca como dispositivo conectado.
4. Abrir:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

## Instalar Tailscale en Celular

### Android

1. Abrir Play Store.
2. Buscar `Tailscale`.
3. Instalar.
4. Iniciar sesión con la misma cuenta.
5. Activar la VPN de Tailscale.
6. Abrir Chrome.
7. Entrar a:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

### iPhone

1. Abrir App Store.
2. Buscar `Tailscale`.
3. Instalar.
4. Iniciar sesión.
5. Permitir la configuración VPN.
6. Activar Tailscale.
7. Entrar desde Safari o Chrome.

## Configuración Django Para Tailscale

En `.env` debe aparecer el dominio de Tailscale:

```text
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.22,servidor-funeraria.taild7534a.ts.net
DJANGO_CSRF_TRUSTED_ORIGINS=https://servidor-funeraria.taild7534a.ts.net
```

Después de cambiar `.env`:

```bash
cd /opt/sistema-funerario
sudo docker compose up -d
```

## Cookies Seguras

Si el sistema se usará principalmente por HTTPS de Tailscale, se puede activar:

```text
DJANGO_SECURE_COOKIES=True
```

Esto hace que las cookies de sesión y CSRF se envíen solo por HTTPS.

Si también necesita entrar por `http://192.168.0.22:8080`, deje:

```text
DJANGO_SECURE_COOKIES=False
```

Porque HTTP local no enviará cookies marcadas como seguras.

## Firewall UFW

Reglas recomendadas si la red local es `192.168.0.0/24`:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.0.0/24 to any port 22 proto tcp
sudo ufw allow from 192.168.0.0/24 to any port 8080 proto tcp
sudo ufw enable
sudo ufw status verbose
```

Tailscale no necesita abrir el puerto `8080` hacia Internet.

## Usuarios del Sistema

Recomendaciones:

- crear una cuenta por persona;
- no compartir usuario administrador;
- usar contraseñas largas;
- cambiar contraseña si alguien deja de trabajar;
- dar permisos de `staff` solo a quien necesita `/admin/`;
- evitar usar `admin/admin` o claves débiles.

Crear usuario administrador:

```bash
sudo docker compose exec web python manage.py createsuperuser
```

Cambiar contraseña:

```bash
sudo docker compose exec web python manage.py changepassword usuario
```

## Panel Administrativo

URL local:

```text
http://192.168.0.22:8080/admin/
```

URL Tailscale:

```text
https://servidor-funeraria.taild7534a.ts.net/admin/
```

Desde ahí se puede gestionar:

- usuarios;
- grupos;
- clientes;
- pagos;
- documentos.

## Archivos Permitidos

El sistema permite subir:

```text
pdf, jpg, jpeg, png, webp, doc, docx, xls, xlsx
```

Tamaño máximo desde el formulario:

```text
20 MB
```

Límite de Nginx:

```text
25 MB
```

No se permiten archivos ejecutables como:

```text
.exe, .bat, .sh, .js
```

## Qué No Hacer

No hacer esto:

```text
Abrir puerto 8080 del router hacia Internet.
Publicar con Tailscale Funnel sin una razón fuerte.
Compartir la clave del usuario administrador.
Guardar respaldos solo dentro del mismo servidor.
Usar contraseñas cortas.
Desactivar respaldos automáticos.
```

## Revisión Mensual de Seguridad

1. Revisar usuarios activos en `/admin/`.
2. Cambiar contraseñas si alguien ya no debe entrar.
3. Revisar Tailscale Machines.
4. Quitar dispositivos antiguos de Tailscale.
5. Confirmar que Funnel está desactivado.
6. Confirmar respaldos recientes.
7. Revisar actualizaciones de Ubuntu.

Comando para actualizar:

```bash
sudo apt update
sudo apt upgrade
```

## Verificar Tailscale

```bash
tailscale status
sudo tailscale serve status
```

Si Serve falla:

```bash
curl -I http://127.0.0.1:8080
sudo docker compose ps
sudo tailscale serve --bg http://127.0.0.1:8080
```

## Respuesta Ante Incidente

Si sospecha acceso indebido:

1. desconecte temporalmente Tailscale Serve:

```bash
sudo tailscale serve --https=443 off
```

2. cambie contraseñas de usuarios;
3. revise logs:

```bash
sudo docker compose logs web
sudo docker compose logs nginx
```

4. revise dispositivos Tailscale;
5. haga respaldo del estado actual;
6. restaure respaldo limpio si corresponde.
