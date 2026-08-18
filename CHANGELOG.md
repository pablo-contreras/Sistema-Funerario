# Changelog

Este archivo registra las principales versiones del Sistema de Gestión Funeraria.

## [1.0.0] - 2026-08-18

### Funcionalidades

- Gestión de clientes.
- Creación, edición y eliminación de fichas.
- Validación y normalización de RUT.
- Generación automática de folios.
- Registro de información del fallecido.
- Gestión de servicios funerarios.
- Registro de contratos.
- Registro de pagos y abonos.
- Historial de pagos.
- Cálculo automático de IVA.
- Cálculo automático del valor total.
- Cálculo de saldo pendiente.
- Gestión documental por cliente.
- Generación de contratos en PDF.
- Autenticación de usuarios.
- Administración mediante Django Admin.

### Infraestructura

- Django 5.2.
- Python 3.12.
- PostgreSQL 16.
- SQLite para desarrollo local.
- Docker.
- Docker Compose.
- Gunicorn.
- Nginx.
- Persistencia de datos.
- Scripts de respaldo y restauración.
- Automatización de respaldos mediante systemd.

### Seguridad

- Autenticación mediante Django.
- Protección CSRF.
- Protección contra clickjacking.
- Protección Content-Type nosniff.
- Variables sensibles mediante archivo .env.
- Exclusión de credenciales mediante .gitignore.
- Configuración para cookies seguras.
- Acceso remoto privado compatible con VPN.

### Calidad

- Pruebas automatizadas.
- Verificación de configuración Django.
- Integración continua mediante GitHub Actions.

### Documentación

- README principal.
- Arquitectura.
- Descripción de módulos.
- Flujos del sistema.
- Instalación y operación.
- Respaldos y restauración.
- Seguridad y acceso remoto.
- Desarrollo y pruebas.
- Recuperación ante fallas críticas.
- Manual técnico.
- Manual de usuario.