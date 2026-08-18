# 00 - Índice de Documentación

Esta carpeta contiene la documentación final del sistema funerario.

## Orden de Lectura

1. `README.md` en la raíz del proyecto  
   Entrada rápida al sistema, estructura general y comandos principales.

2. `docs/01_ARQUITECTURA.md`  
   Explica cómo se conectan navegador, Nginx, Django, PostgreSQL, archivos y respaldos.

3. `docs/02_MODULOS_DEL_CODIGO.md`  
   Explica archivo por archivo qué hace cada módulo del código.

4. `docs/03_FLUJOS_DEL_SISTEMA.md`  
   Explica qué ocurre al crear clientes, registrar pagos, subir documentos, imprimir y descargar PDF.

5. `docs/04_INSTALACION_OPERACION.md`  
   Comandos para instalar, levantar, revisar, reiniciar y actualizar el sistema.

6. `docs/05_RESPALDOS_RESTAURACION.md`  
   Explica cómo se crean respaldos, qué contienen y cómo restaurarlos.

7. `docs/06_SEGURIDAD_ACCESO_REMOTO.md`  
   Explica Tailscale, firewall, usuarios, cookies seguras y recomendaciones de seguridad.

8. `docs/07_DESARROLLO_PRUEBAS.md`  
   Explica cómo modificar el sistema, correr pruebas y mantenerlo.

9. `docs/08_RESPALDOS_Y_FALLA_CRITICA.md`  
   Contiene diagramas y pasos de emergencia para respaldar/restaurar la base de datos y reemplazar archivos fuente dañados sin tocar los datos.

10. `docs/MANUAL_TECNICO_PROGRAMADOR_ADMINISTRADOR.md` y `docs/manual_tecnico_programador_administrador.pdf`  
    Manual técnico consolidado para perfil administrador y programador.

11. `docs/MANUAL_USUARIO_COMUN.md` y `docs/manual_usuario_comun.pdf`  
    Manual de operación para usuarios comunes del sistema.

## Mapa Rápido del Código

| Carpeta o archivo | Qué contiene |
|---|---|
| `clientes/models.py` | Tablas y reglas principales: clientes, pagos, documentos, saldos y folios. |
| `clientes/forms.py` | Formularios para ficha, pagos y documentos. |
| `clientes/views.py` | Vistas web: lista, crear, editar, detalle, pagos, documentos, contrato y PDF. |
| `clientes/validators.py` | Normalización y validación de RUT chileno. |
| `clientes/urls.py` | Rutas de la aplicación de clientes. |
| `clientes/admin.py` | Configuración del panel administrativo. |
| `clientes/pdf_fallback.py` | Generación alternativa de PDF con ReportLab. |
| `clientes/templates/` | Pantallas HTML. |
| `clientes/static/clientes/app.css` | Estilos visuales del sistema. |
| `funeraria/settings.py` | Configuración general de Django. |
| `funeraria/urls.py` | Rutas globales: admin, login, logout y clientes. |
| `deploy/nginx/default.conf` | Configuración del proxy Nginx. |
| `deploy/scripts/backup.sh` | Respaldo de base de datos, documentos y configuración. |
| `deploy/scripts/restore.sh` | Restauración desde respaldo. |
| `deploy/scripts/entrypoint.sh` | Migraciones y archivos estáticos al iniciar el contenedor. |
| `docker-compose.yml` | Servicios Docker: PostgreSQL, Django/Gunicorn y Nginx. |
| `Dockerfile` | Imagen de la aplicación. |
| `tests/test_system.py` | Pruebas automáticas del sistema. |

## Documentos de Emergencia

| Documento | Cuándo usarlo |
|---|---|
| `05_RESPALDOS_RESTAURACION.md` | Para entender la estrategia general de respaldos. |
| `08_RESPALDOS_Y_FALLA_CRITICA.md` | Para actuar rápido ante pérdida de base, restauración o código fuente dañado. |
| `manual_tecnico_programador_administrador.pdf` | Manual técnico entregable para imprimir o compartir. |
| `manual_usuario_comun.pdf` | Manual simple para operadores que crean, editan, eliminan, imprimen y suben documentos. |

## Comandos Más Usados

```bash
cd /opt/sistema-funerario
sudo docker compose ps
sudo docker compose logs -f web
sudo docker compose up -d --build
sudo ./deploy/scripts/backup.sh
```

## Recuperación Rápida

Si el sistema falla:

```bash
cd /opt/sistema-funerario
sudo docker compose ps
sudo docker compose logs --tail=100 web
sudo docker compose logs --tail=100 nginx
```

Si hay que restaurar:

```bash
sudo ./deploy/scripts/restore.sh /mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS
```
