# Manual de Usuario

Sistema Funerario  
Perfil: usuarios comunes del sistema  
Versión: 2026-06-17

---

## 1. ¿Para Qué Sirve Este Sistema?

El Sistema Funerario permite registrar y administrar fichas de clientes, contratos, pagos y documentos.

Con este sistema usted puede:

- crear una ficha de cliente;
- buscar clientes por nombre o RUT;
- editar una ficha existente;
- eliminar una ficha;
- registrar pagos;
- imprimir el contrato;
- descargar el contrato en PDF;
- subir documentos del cliente;
- descargar documentos guardados;
- eliminar documentos o pagos cuando corresponda.

---

## 2. Cómo Entrar al Sistema

Abra Google Chrome y escriba la dirección del sistema.

En la red local:

```text
http://192.168.0.22:8080
```

Si está fuera de la red y usa Tailscale:

```text
https://servidor-funeraria.taild7534a.ts.net/
```

Aparecerá la pantalla de ingreso.

Ingrese:

- usuario;
- contraseña.

Luego presione:

```text
Ingresar
```

Si el usuario o contraseña son incorrectos, el sistema mostrará un mensaje de error.

---

## 3. Pantalla Principal de Clientes

Al entrar, verá la lista de clientes registrados.

En esta pantalla puede:

- buscar clientes;
- abrir una ficha;
- editar una ficha;
- crear una nueva ficha.

La tabla muestra normalmente:

- folio;
- contratante;
- RUT;
- fallecido;
- total;
- saldo;
- opciones para ver o editar.

---

## 4. Buscar un Cliente

En la pantalla principal hay una barra de búsqueda.

Puede buscar por:

- nombre del contratante;
- RUT;
- nombre del fallecido;
- folio.

Ejemplos:

```text
Juan Pérez
12.345.678-5
12345678-5
FUN-2026-00001
```

Después de escribir, presione:

```text
Buscar
```

Para volver a ver todos los clientes, presione:

```text
Limpiar
```

---

## 5. Crear una Nueva Ficha

Desde la pantalla principal, presione:

```text
+ Nueva ficha
```

Se abrirá el formulario de cliente.

### 5.1 Datos Obligatorios

Solo hay dos datos obligatorios:

- nombre del contratante;
- RUT.

El resto se puede completar en el momento o editar después.

### 5.2 Secciones del Formulario

El formulario está dividido en:

1. Datos del contratante.
2. Datos del fallecido.
3. Servicio y ceremonia.
4. Entrega de documentos.

### 5.3 Guardar la Ficha

Después de escribir los datos, baje al final y presione:

```text
Guardar ficha
```

Si todo está correcto, el sistema guardará la ficha y lo llevará al detalle del cliente.

El sistema crea automáticamente:

- folio del contrato;
- carpeta interna para documentos del cliente.

---

## 6. Editar una Ficha

Para editar una ficha:

1. busque el cliente;
2. presione `Ver` o `Editar`;
3. si entró a `Ver`, presione el botón `Editar`;
4. modifique los datos necesarios;
5. presione `Guardar ficha`.

Después de guardar, el sistema volverá a la ficha del cliente.

### Recomendación

Revise bien el RUT antes de guardar. El sistema valida el RUT chileno y puede rechazarlo si el dígito verificador no corresponde.

---

## 7. Ver una Ficha de Cliente

Al abrir una ficha verá:

- nombre del cliente;
- folio;
- RUT;
- total del servicio;
- total pagado;
- saldo pendiente;
- cantidad de archivos;
- resumen de datos;
- botones para editar, imprimir y descargar PDF;
- registro de pagos;
- documentos del cliente;
- opción para eliminar ficha.

---

## 8. Registrar un Pago

Dentro de la ficha del cliente, busque la sección:

```text
Registro de pagos
```

Complete:

- fecha del abono;
- valor;
- número de recibo;
- detalle, si corresponde.

Luego presione:

```text
Registrar pago
```

El pago aparecerá en la tabla y el saldo se actualizará automáticamente.

### Ejemplo

Si el total del servicio es:

```text
$119.000
```

Y registra un pago de:

```text
$30.000
```

El saldo quedará:

```text
$89.000
```

---

## 9. Eliminar un Pago

En la tabla de pagos, presione:

```text
Eliminar
```

El navegador pedirá confirmación.

Si confirma, el pago se borrará y el saldo se recalculará.

### Importante

Elimine pagos solo si fueron ingresados por error.

---

## 10. Imprimir Contrato

Dentro de la ficha del cliente, presione:

```text
Imprimir
```

Se abrirá una vista del contrato en formato A4.

Luego presione:

```text
Imprimir en Chrome
```

Chrome abrirá su ventana de impresión.

### Recomendaciones de impresión

En la ventana de impresión:

- seleccione la impresora correcta;
- use tamaño de papel A4;
- revise la vista previa;
- si se ve cortado, pruebe activar o desactivar márgenes predeterminados;
- confirme la impresión.

---

## 11. Descargar Contrato en PDF

Dentro de la ficha del cliente, presione:

```text
Descargar PDF
```

El sistema descargará un archivo parecido a:

```text
contrato-FUN-2026-00001.pdf
```

Ese PDF puede:

- guardarse;
- enviarse;
- imprimirse;
- respaldarse junto a documentos del cliente.

---

## 12. Subir Documentos del Cliente

Dentro de la ficha, busque la sección:

```text
Archivos del cliente
```

Para subir un archivo:

1. seleccione el tipo de documento;
2. presione seleccionar archivo;
3. elija el archivo desde el computador;
4. presione `Subir archivo`.

Tipos de documento:

- contrato físico;
- certificado;
- comprobante;
- otro.

Formatos permitidos:

```text
PDF, JPG, JPEG, PNG, WEBP, DOC, DOCX, XLS, XLSX
```

Tamaño máximo:

```text
20 MB
```

### Ejemplos de documentos que puede subir

- contrato físico escaneado;
- certificado de defunción;
- comprobante de pago;
- copia de cédula;
- documento Word;
- planilla Excel;
- imagen o foto.

---

## 13. Descargar Documentos Guardados

En la sección `Archivos del cliente`, cada documento tiene una opción:

```text
Descargar
```

Presione esa opción para bajar el archivo al computador.

---

## 14. Eliminar Documentos

En la sección de documentos, presione:

```text
Eliminar
```

El navegador pedirá confirmación.

Si confirma, el documento se eliminará del sistema.

### Importante

Elimine documentos solo si:

- se subieron por error;
- están repetidos;
- no corresponden al cliente.

---

## 15. Eliminar una Ficha de Cliente

Al final de la ficha existe una sección de eliminación.

Presione:

```text
Eliminar cliente
```

El navegador pedirá confirmación.

Si confirma, se eliminarán:

- ficha del cliente;
- pagos asociados;
- documentos asociados.

### Advertencia

Esta acción es delicada. Solo debe usarse si la ficha fue creada por error.

Si elimina una ficha por accidente, avise al administrador inmediatamente para revisar respaldos.

---

## 16. Cerrar Sesión

En el menú lateral, presione:

```text
Cerrar sesión
```

Haga esto cuando termine de usar el sistema, especialmente si está en un computador compartido.

---

## 17. Buenas Prácticas para Usuarios

### Antes de guardar una ficha

Revise:

- nombre del contratante;
- RUT;
- teléfono;
- nombre del fallecido;
- valor del servicio;
- fecha del contrato.

### Al registrar pagos

Revise:

- fecha;
- monto;
- número de recibo;
- cliente correcto.

### Al subir documentos

Revise:

- que el documento corresponda al cliente;
- que el archivo no esté repetido;
- que el nombre del archivo sea entendible;
- que el archivo no supere 20 MB.

---

## 18. Problemas Frecuentes

### No puedo entrar

Revise:

- usuario correcto;
- contraseña correcta;
- mayúsculas/minúsculas;
- conexión a red o Tailscale.

Si sigue sin entrar, avise al administrador.

### No encuentro un cliente

Pruebe buscar por:

- primer nombre;
- apellido;
- RUT sin puntos;
- RUT con puntos;
- folio;
- nombre del fallecido.

### No me deja guardar el RUT

El RUT puede estar mal escrito o el dígito verificador puede no corresponder.

Revise el formato:

```text
12.345.678-5
```

### No puedo subir un archivo

Revise:

- que el formato esté permitido;
- que pese menos de 20 MB;
- que el archivo no esté abierto o bloqueado;
- que la conexión al servidor esté funcionando.

### El contrato no imprime bien

Revise en Chrome:

- tamaño A4;
- impresora correcta;
- vista previa;
- escala de impresión;
- márgenes.

También puede descargar PDF e imprimir el PDF.

---

## 19. Flujo Recomendado de Trabajo

Para una atención completa:

```text
1. Crear ficha del cliente.
2. Completar datos del contratante.
3. Completar datos del fallecido.
4. Completar servicio y ceremonia.
5. Guardar ficha.
6. Registrar pagos si corresponde.
7. Subir documentos físicos o certificados.
8. Revisar el contrato.
9. Imprimir o descargar PDF.
10. Cerrar sesión al terminar.
```

---

## 20. Resumen Rápido

Crear:

```text
+ Nueva ficha -> completar nombre y RUT -> Guardar ficha
```

Editar:

```text
Buscar cliente -> Editar -> Guardar ficha
```

Eliminar:

```text
Abrir ficha -> Eliminar cliente -> Confirmar
```

Imprimir:

```text
Abrir ficha -> Imprimir -> Imprimir en Chrome
```

Descargar PDF:

```text
Abrir ficha -> Descargar PDF
```

Subir documento:

```text
Abrir ficha -> Archivos del cliente -> seleccionar archivo -> Subir archivo
```

Registrar pago:

```text
Abrir ficha -> Registro de pagos -> completar datos -> Registrar pago
```
