---
name: acceso-stod
description: Da de alta un usuario de STOD (y sus accesos, p. ej. FEIC) pedido por ticket de Odoo o por correo, con los mismos accesos que otro usuario. Usar cuando un ticket diga "generar acceso a STOD", "usuario nuevo en STOD", "mismos accesos que fulano", "FEIC", o cuando el usuario pida crear o revisar un usuario o rol de STOD.
argument-hint: <ticket de Odoo> (opcional)
---

# Alta de acceso a STOD

MCP `stod` (lectura + `crear_usuario`) y `odoo-helpdesk`. Si las herramientas `usuarios`, `usuario`, `roles`, `permisos_rol` o `crear_usuario` no están cargadas: el MCP se modificó a mitad de sesión; pedir reiniciar Claude Code. STOD no se maneja por Chrome (no tiene la sesión).

## Reglas
- Nunca recibir, escribir ni repetir contraseñas en el chat, notas o borradores. La temporal la genera el supervisor, una por alta: `! C:\Users\<user>\mcp-servers\.venv\Scripts\python.exe C:\Users\<user>\mcp-servers\_stod_env.py nuevaclave` (aleatoria con el formato de STOD; queda guardada y copiada al portapapeles, se limpia en 90 s; NO imprime nada, por eso es seguro con `!`). Para entregarla después: `... _stod_env.py copiarclave` y pegarla en el canal de entrega. Si prefiere elegirla él: `setclave`. Se borra con `borrarclave` al terminar. En PowerShell normal va sin `!`.
- Si el ticket o correo trae una contraseña en texto plano (suele pasar): avisar a el supervisor, no usarla (se copia el rol, no se entra como ese usuario), ofrecer ocultarla en la descripción («[contraseña omitida]», con confirmación) y pedir en el correo al solicitante que el dueño la cambie.
- `crear_usuario` solo con `dry_run=False` tras confirmación explícita de el supervisor en el chat.
- Un usuario tiene UN rol existente; no se crean roles ni se tocan permisos.

## Pasos
0. Odoo ya deja en la nota automática del ticket «Posible alta de acceso a STOD…» cuando la aplicación es STOD y el asunto/cuerpo habla de acceso, usuario, módulo o permisos (regla 11, acción 59616). El tipo de soporte sigue siendo «Actualización de Datos»: así lo usa todo el equipo.
1. **Datos** (`get_ticket`; imágenes con `get_attachment_image`): nombre completo y apellidos, NIT (suele venir en un PDF de la SAT adjunto), usuario «modelo» (`copiar_de`), correo o buzón a usar, solicitante.
2. **Revisar duplicados:** `usuarios("apellido")` y `usuarios("nombre apellido")` (la primera búsqueda recorre ~2,545 usuarios, ~50 s; luego hay caché de 10 min).
3. **Modelo:** `usuario(modelo)` (rol, depto, correo) y `permisos_rol(rol)` (menús). Mostrar a el supervisor en pocas líneas qué accesos se darán.
4. **Nombre de usuario:** convención = inicial del nombre + primer apellido, en minúscula (`mlima`, `fpozuelos`, `user1`). Si está tomado, proponer variante (segundo nombre o apellido).
5. **Simular:** `crear_usuario(usuario, nombre, apellido, email, copiar_de=modelo, nit=..., dry_run=True)`. Revisar `posibles_duplicados_por_nombre` y `clave_inicial_guardada`; si falta la clave, pedirle a el supervisor `setclave`.
6. **Confirmar y crear:** con el visto bueno, `dry_run=False`. Verificar en la respuesta `usuario_en_stod` (rol, depto, correo, NIT).
7. **Correos (borradores `outlook-desktop`, sin enviar):**
   - Al solicitante: usuario creado, accesos (rol), que la contraseña temporal se entrega por otro medio y que la cambie en el primer ingreso (STOD > Opciones de Usuario > Cambiar contraseña), y recomendación de seguridad si había contraseñas en el correo. El correo original de la lista `mesadeayuda@` no suele estar en el buzón de el supervisor: `create_draft` nuevo con asunto `RE: <asunto>`.
   - Si piden cambiar el nombre de un buzón: a user@example.com, cc user@ y user@ (el supervisor no tiene Exchange Admin Center), con la prueba de cierre.
8. **Ticket:** `post_note` interna (Hecho · Pendiente · Prueba de cierre, sin contraseñas) y `set_ticket_stage(id, "En proceso")`. Cerrar (`close_ticket`) cuando el usuario confirme ingreso a STOD y al módulo (p. ej. FEIC > Crear / editar) y se haya aplicado lo de Exchange.
9. **Pendientes de el supervisor al terminar:** `copiarclave` y entregar la temporal por otro medio (no correo), enviar los borradores y `borrarclave`.

## Notas técnicas (STOD)
- Grid Telerik: el filtro por postback da 500; funcionan `PageSize` y `Page`. Por eso `usuarios` recorre las páginas.
- Los `RadTextBox` guardan su valor también en un oculto `…_ClientState` (nombre con `_`): `crear_usuario` ya lo llena; si un alta «no se crea» y el formulario sigue abierto, revisar los validadores sin `visibility:hidden`.
- Probado el 16-nov-2026 con el ticket NNNNN: `user1`, rol DIGITADOR_X (copiado de `user2`, depto BRAND-X).
