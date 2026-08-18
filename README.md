# Sistema Funerario

Carpeta final del sistema funerario desarrollado para funcionar en un servidor local Dell PowerEdge T150, usando Ubuntu Server, Docker, PostgreSQL, Django, Nginx y acceso remoto privado mediante Tailscale.

El sistema permite:

- crear fichas de clientes;
- exigir solo `nombre` y `RUT` como datos obligatorios;
- buscar clientes por nombre, RUT, fallecido o folio;
- editar y eliminar fichas;
- registrar pagos y calcular saldo pendiente;
- subir documentos a una carpeta asociada al cliente;
- imprimir el contrato desde Chrome;
- descargar el contrato en PDF;
- operar en red local y por Tailscale;
- respaldar la base de datos y documentos al disco mecánico.

## Lectura Recomendada

Para entender el proyecto por completo, lea estos documentos en orden:

1. [docs/01_ARQUITECTURA.md](docs/01_ARQUITECTURA.md)  
   Explica cómo se divide el sistema, qué hace cada capa y cómo se comunican Django, PostgreSQL, Nginx y Docker.

2. [docs/02_MODULOS_DEL_CODIGO.md](docs/02_MODULOS_DEL_CODIGO.md)  
   Explica archivo por archivo qué hace cada módulo del código.

3. [docs/03_FLUJOS_DEL_SISTEMA.md](docs/03_FLUJOS_DEL_SISTEMA.md)  
   Describe los flujos principales: crear cliente, registrar pagos, subir documentos, imprimir contrato y generar PDF.

4. [docs/04_INSTALACION_OPERACION.md](docs/04_INSTALACION_OPERACION.md)  
   Guía para instalar, levantar, detener, actualizar y revisar el sistema en el servidor.

5. [docs/05_RESPALDOS_RESTAURACION.md](docs/05_RESPALDOS_RESTAURACION.md)  
   Explica cómo se hacen los respaldos, qué contienen y cómo restaurarlos.

6. [docs/06_SEGURIDAD_ACCESO_REMOTO.md](docs/06_SEGURIDAD_ACCESO_REMOTO.md)  
   Recomendaciones de seguridad, usuarios, Tailscale, firewall y exposición fuera de la red.

7. [docs/07_DESARROLLO_PRUEBAS.md](docs/07_DESARROLLO_PRUEBAS.md)  
   Cómo probar el sistema, ejecutar tests y modificar el código en el futuro.

8. [docs/08_RESPALDOS_Y_FALLA_CRITICA.md](docs/08_RESPALDOS_Y_FALLA_CRITICA.md)  
   Diagrama y guía de emergencia para respaldar/restaurar la base de datos y reemplazar archivos fuente dañados.

9. [docs/MANUAL_TECNICO_PROGRAMADOR_ADMINISTRADOR.md](docs/MANUAL_TECNICO_PROGRAMADOR_ADMINISTRADOR.md)  
   Manual técnico completo para perfil programador y administrador. También está disponible en PDF:
   [docs/manual_tecnico_programador_administrador.pdf](docs/manual_tecnico_programador_administrador.pdf).

10. [docs/MANUAL_USUARIO_COMUN.md](docs/MANUAL_USUARIO_COMUN.md)  
    Manual para usuarios comunes: ingresar, buscar, crear, editar, eliminar, registrar pagos, imprimir contrato y subir documentos. También está disponible en PDF:
    [docs/manual_usuario_comun.pdf](docs/manual_usuario_comun.pdf).

## Estructura General

```text
sistema-funerario-final/
├── clientes/              Aplicación principal: clientes, pagos, documentos y contratos.
├── funeraria/             Configuración global Django: settings, urls, WSGI/ASGI.
├── deploy/                Nginx, scripts de respaldo/restauración y timer systemd.
├── static/                Archivos estáticos globales, incluido el logo.
├── tests/                 Pruebas automáticas del sistema.
├── docs/                  Documentación detallada del proyecto.
├── Dockerfile             Imagen Docker de la aplicación Django.
├── docker-compose.yml     Orquesta PostgreSQL, Django/Gunicorn y Nginx.
├── .env.example           Plantilla de variables de entorno.
├── requirements.txt       Dependencias Python.
└── manage.py              Comando principal de administración Django.
```

## Inicio Rápido en el Servidor

Dentro del servidor:

```bash
cd /opt/sistema-funerario
cp .env.example .env
nano .env
sudo docker compose up -d --build
sudo docker compose exec web python manage.py createsuperuser
sudo docker compose ps
```

Luego abra en Chrome:

```text
http://IP-DEL-SERVIDOR:8080
```

En la instalación que dejamos funcionando, la IP local fue:

```text
http://192.168.0.22:8080
```

Y el acceso remoto privado por Tailscale quedó expuesto como:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

## Datos Importantes

- El sistema usa PostgreSQL en producción.
- Los archivos subidos quedan en `DATA_DIR/media`.
- Los respaldos se guardan en `BACKUP_DIR`.
- El disco mecánico se montó en `/mnt/funeraria-backups`.
- El código de producción debe vivir en `/opt/sistema-funerario`.
- No se recomienda publicar el puerto `8080` directamente a Internet.
- Para acceso externo privado se recomienda Tailscale Serve.

## Comandos Útiles

Ver estado:

```bash
sudo docker compose ps
```

Ver logs:

```bash
sudo docker compose logs -f web
sudo docker compose logs -f nginx
sudo docker compose logs -f db
```

Reiniciar:

```bash
sudo docker compose restart
```

Actualizar después de copiar cambios:

```bash
sudo docker compose up -d --build
```

Crear respaldo manual:

```bash
sudo ./deploy/scripts/backup.sh
```

Restaurar un respaldo:

```bash
sudo ./deploy/scripts/restore.sh /mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS
```

## Nota Sobre Esta Carpeta

Esta carpeta es la versión final documentada del código. La carpeta original `outputs/sistema-funerario` se conserva sin cambios como referencia inicial.
