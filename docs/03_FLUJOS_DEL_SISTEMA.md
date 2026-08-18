# 03 - Flujos del Sistema

Este documento explica qué ocurre internamente cuando el usuario realiza las acciones principales.

## 1. Inicio de Sesión

Ruta:

```text
/ingresar/
```

Archivo:

```text
funeraria/urls.py
clientes/templates/registration/login.html
```

Flujo:

```text
1. El usuario abre el sistema.
2. Si no tiene sesión activa, Django lo envía a /ingresar/.
3. El usuario escribe usuario y contraseña.
4. Django valida credenciales con su sistema interno de usuarios.
5. Si son correctas, crea sesión.
6. Redirige a la lista de clientes.
```

El sistema no permite acceder a fichas, pagos, documentos ni contratos sin login.

## 2. Lista y Búsqueda de Clientes

Ruta:

```text
/
```

Vista:

```text
clientes.views.client_list
```

Plantilla:

```text
clientes/templates/clientes/client_list.html
```

Flujo:

```text
1. Usuario entra a la página principal.
2. Django lee el parámetro q de la URL.
3. Si q está vacío, muestra clientes recientes.
4. Si q tiene texto, busca por:
   - nombre;
   - RUT;
   - nombre del fallecido;
   - folio.
5. Si parece RUT, también lo normaliza para mejorar la búsqueda.
6. Muestra máximo 100 resultados.
```

Ejemplo de búsqueda:

```text
/?q=12.345.678-5
/?q=Juan
/?q=FUN-2026-00001
```

## 3. Crear una Ficha de Cliente

Ruta:

```text
/clientes/nuevo/
```

Vista:

```text
clientes.views.client_create
```

Formulario:

```text
clientes.forms.ClientForm
```

Modelo:

```text
clientes.models.Client
```

Flujo:

```text
1. Usuario abre "Nueva ficha".
2. Django muestra el formulario.
3. Usuario escribe los datos.
4. Al guardar, Django valida el formulario.
5. El RUT se normaliza.
6. El RUT se valida con módulo 11.
7. Se guarda el cliente.
8. El modelo genera folio automático.
9. El modelo genera carpeta automática de documentos.
10. Se muestra mensaje de éxito.
11. El usuario queda en la ficha del cliente.
```

Datos obligatorios:

```text
Nombre
RUT
```

El resto de datos se puede completar después.

## 4. Editar una Ficha

Ruta:

```text
/clientes/<id>/editar/
```

Vista:

```text
clientes.views.client_update
```

Flujo:

```text
1. Usuario abre una ficha existente.
2. Hace clic en Editar.
3. Django carga el formulario con datos actuales.
4. Usuario modifica campos.
5. Django valida.
6. Guarda cambios.
7. Redirige al detalle.
```

Campos como folio, carpeta, fecha de creación y usuario creador no se editan desde el formulario.

## 5. Ver Detalle del Cliente

Ruta:

```text
/clientes/<id>/
```

Vista:

```text
clientes.views.client_detail
```

Plantilla:

```text
clientes/templates/clientes/client_detail.html
```

La pantalla muestra:

- folio;
- nombre;
- RUT;
- fecha de actualización;
- total del servicio;
- total pagado;
- saldo pendiente;
- cantidad de archivos;
- resumen de datos;
- botones de contrato;
- registro de pagos;
- documentos;
- botón de eliminación.

## 6. Registrar Pago

Ruta:

```text
/clientes/<id>/pagos/nuevo/
```

Vista:

```text
clientes.views.payment_create
```

Formulario:

```text
clientes.forms.PaymentForm
```

Modelo:

```text
clientes.models.Payment
```

Flujo:

```text
1. Usuario está en la ficha del cliente.
2. Completa fecha, monto, número de recibo y detalle.
3. Presiona "Registrar pago".
4. Django valida el monto.
5. Django asocia el pago al cliente.
6. Guarda en PostgreSQL.
7. Redirige a la misma ficha, sección #pagos.
8. El total pagado y saldo se recalculan automáticamente.
```

El saldo no se guarda como campo fijo. Se calcula con:

```text
saldo = total servicio - suma de pagos
```

Esto evita errores por datos duplicados.

## 7. Eliminar Pago

Ruta:

```text
/pagos/<id>/eliminar/
```

Vista:

```text
clientes.views.payment_delete
```

Flujo:

```text
1. Usuario hace clic en Eliminar junto al pago.
2. Chrome pide confirmación.
3. Django elimina el pago.
4. Redirige a la ficha.
5. El saldo se recalcula.
```

## 8. Subir Documento

Ruta:

```text
/clientes/<id>/documentos/subir/
```

Vista:

```text
clientes.views.document_upload
```

Formulario:

```text
clientes.forms.DocumentForm
```

Modelo:

```text
clientes.models.ClientDocument
```

Flujo:

```text
1. Usuario abre la ficha del cliente.
2. Selecciona categoría del documento.
3. Selecciona archivo.
4. Django valida extensión.
5. Django valida tamaño máximo de 20 MB.
6. Django asigna cliente y usuario.
7. Se guarda el registro en PostgreSQL.
8. Se guarda el archivo físico en DATA_DIR/media.
9. Se muestra mensaje de éxito.
```

Ejemplo de ruta física:

```text
/srv/funeraria/data/media/clientes/juan-perez-12345678_5/contrato.pdf
```

## 9. Descargar Documento

Ruta:

```text
/documentos/<id>/descargar/
```

Vista:

```text
clientes.views.document_download
```

Flujo:

```text
1. Usuario hace clic en Descargar.
2. Django busca el documento.
3. Abre el archivo físico.
4. Devuelve FileResponse.
5. Chrome descarga el archivo con su nombre original.
```

Si el archivo físico no existe, Django devuelve error 404.

## 10. Eliminar Documento

Ruta:

```text
/documentos/<id>/eliminar/
```

Vista:

```text
clientes.views.document_delete
```

Flujo:

```text
1. Usuario confirma eliminación.
2. Django borra el registro ClientDocument.
3. La señal post_delete borra el archivo físico.
4. Django vuelve a la ficha del cliente.
```

Esto evita que queden documentos sueltos en disco.

## 11. Imprimir Contrato

Ruta:

```text
/clientes/<id>/contrato/
```

Vista:

```text
clientes.views.contract_print
```

Plantilla:

```text
clientes/templates/clientes/contract_print.html
```

Flujo:

```text
1. Usuario hace clic en Imprimir.
2. Django arma contexto del contrato.
3. Django calcula pagos con saldo progresivo.
4. Se muestra contrato en formato A4.
5. Usuario presiona "Imprimir en Chrome".
6. Chrome abre su diálogo de impresión.
```

El contrato tiene dos páginas:

1. contrato de servicios funerarios;
2. entrega de documentos y registro de pagos.

## 12. Descargar Contrato PDF

Ruta:

```text
/clientes/<id>/contrato.pdf
```

Vista:

```text
clientes.views.contract_pdf
```

Flujo:

```text
1. Usuario hace clic en Descargar PDF.
2. Django obtiene el cliente.
3. Django arma contexto.
4. Django renderiza el HTML del contrato.
5. En Linux intenta usar WeasyPrint.
6. Si WeasyPrint no está disponible, usa ReportLab.
7. Devuelve PDF como descarga.
```

Nombre de archivo:

```text
contrato-FUN-2026-00001.pdf
```

## 13. Eliminar Cliente

Ruta:

```text
/clientes/<id>/eliminar/
```

Vista:

```text
clientes.views.client_delete
```

Flujo:

```text
1. Usuario presiona Eliminar cliente.
2. Chrome pide confirmación.
3. Django elimina el cliente.
4. Django elimina pagos asociados.
5. Django elimina documentos asociados.
6. La señal borra los archivos físicos.
7. Redirige a la lista de clientes.
```

Esta acción es irreversible desde la aplicación. Para recuperar datos hay que restaurar respaldo.

## 14. Respaldo Automático

Script:

```text
deploy/scripts/backup.sh
```

Flujo:

```text
1. systemd timer ejecuta el servicio.
2. backup.sh entra a /opt/sistema-funerario.
3. Carga variables de .env.
4. Crea carpeta con fecha y hora.
5. Ejecuta pg_dump de PostgreSQL.
6. Comprime documentos.
7. Copia .env.
8. Genera SHA256SUMS.
9. Elimina copias mayores a 30 días.
```

## 15. Restauración

Script:

```text
deploy/scripts/restore.sh
```

Flujo:

```text
1. Administrador indica carpeta de respaldo.
2. Script verifica integridad con SHA256.
3. Elimina base actual.
4. Crea base nueva.
5. Restaura dump.
6. Restaura documentos.
7. Reinicia web.
8. Administrador revisa el sistema.
```

## 16. Acceso Fuera de la Red

Servicio:

```text
Tailscale Serve
```

Flujo:

```text
1. Servidor está conectado a Tailscale.
2. Computador o celular externo también instala Tailscale.
3. Ambos usan la misma cuenta/red privada.
4. Usuario abre URL HTTPS de Tailscale.
5. Tailscale enruta al servidor.
6. Serve proxy pasa tráfico a localhost:8080.
7. Django muestra login.
```

Comando usado:

```bash
sudo tailscale serve --bg http://127.0.0.1:8080
```

Dirección:

```text
https://servidor-funeraria.example.ts.net/
```
