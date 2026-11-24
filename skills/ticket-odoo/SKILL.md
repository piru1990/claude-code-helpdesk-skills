---
name: ticket-odoo
description: Resuelve un ticket de Helpdesk de Odoo (Acme) de principio a fin con el MCP odoo-helpdesk. Usar cuando el usuario pase un número o URL de ticket de example.odoo.com, o pida revisar, resolver, documentar o cerrar un ticket de mesa de ayuda.
argument-hint: <número o URL del ticket>
---

# Resolver un ticket de Odoo

Ticket: $ARGUMENTS (si viene vacío, llamar `my_tickets` y preguntar cuál).

Todas las herramientas son del MCP `odoo-helpdesk`. Si no están cargadas, decirlo y pedir reiniciar Claude Code; no pedir credenciales.

## 1. Entender (solo lectura)

1. `get_ticket(<número o URL>)`: ticket, conversación, adjuntos y etapas del equipo.
2. Ver cada imagen adjunta con `get_attachment_image(id)`. Otros archivos: `download_attachment` al scratchpad.
3. Si el título trae un código `(CNxxx)`, `module_info("CNxxx")`.
4. Investigar el estado actual con `search_read`, `read`, `fields_get`; para temas de correo, `mail_config()`.
5. Tickets relacionados o repetidos: `search_tickets(texto=…, remitente=…)`. Contacto del solicitante: `find_partner`.
6. Si el ticket remite a un correo, una reunión o una grabación, leerlos antes de proponer: correo con `outlook-desktop` (`search_messages`, `get_message`, `save_attachments`); reuniones con el conector de Microsoft 365 o Read AI; una grabación de Stream/SharePoint solo tiene transcripción en el navegador (`edge`).

## 2. Proponer

Explicar en pocas líneas la causa y el cambio propuesto. Preguntar solo lo que sea decisión del usuario (método cuando hay más de uno razonable, qué hacer con el ticket al terminar). Si el usuario ya lo indicó, no volver a preguntar.

## 3. Aplicar

- Cambios con `write` / `create` / `call_method`, y releer después para confirmar el resultado antes de seguir.
- No borrar registros; si hace falta, archivar (`active = false`).
- No tocar configuración ajena al ticket.

## 4. Documentar en el ticket

- `post_note("helpdesk.ticket", id, html)` con nota **interna** (por defecto). Nunca enviar mensaje al cliente (`internal=False`) sin que el usuario lo pida.
- Estructura de la nota: **Hecho** (qué se cambió y dónde) · **Pendiente** (pasos y responsable) · **Prueba de cierre**.
- Etapa: `set_ticket_stage(id, "En proceso")` si queda algo pendiente o sin verificar; `close_ticket(id, nota)` solo cuando la prueba de cierre pasó.
- Asignar o reasignar: `assign_ticket(id, "Técnico A")`. Evidencia: `upload_attachment("helpdesk.ticket", id, ruta)`.
- Horas: si el usuario dice cuánto tiempo llevó, `log_hours(id, horas, descripción)`; no inventar horas.

## 5. Si depende de terceros

Dejar un borrador de correo con el MCP `outlook-desktop`, sin enviar: `create_reply_draft(entry_id, html)` si ya existe un hilo con esa persona (buscarlo con `search_messages`), o `create_draft(to, subject, html, cc)` si es un correo nuevo. Contenido: por qué se necesita, lo ya realizado, lo que falta paso a paso, opciones para completarlo y la prueba de cierre. No usar el navegador para esto. Destinatarios habituales en `~/.claude/CLAUDE.md`.

## 5a. Caso: ticket de SAP que Mesa de Ayuda no resuelve

Se escala a ERP-PARTNER (partner de SAP B1) con el MCP `integra-soporte`: primero `escalar_desde_odoo(ticket, dry_run=True)` y mostrar a el supervisor el asunto, el mensaje y los adjuntos; solo con su confirmación en el chat, repetir con `dry_run=False`. Crea el ticket en ERP-Partner (asunto `[Odoo #id] …`), pasa los adjuntos de hasta 2 MB y deja nota interna en el ticket de Odoo con el número de ERP-Partner. El seguimiento posterior: `listar_tickets` / `ver_ticket` y `responder_ticket` (también con `adjuntos`). Dejar el ticket en «30-En proceso» hasta que ERP-Partner responda.

## 5b. Caso: acceso a la API de Sub-D (distribuidores)

Tickets de "dar acceso / no me sale el inventario" de un distribuidor (código `Cxxxxx`). MCP `inventory-api`:
Guía completa: artículo de Knowledge 727 «API de inventario de Sub-D: acceso y soporte a distribuidores» (capacitación de un capacitador, 16-nov-2026).
1. `distribuidor_info(codigo)`: ¿ya tiene palabra clave? Si no la tiene, el alta es así: la página DistribuidoresWEB genera una clave aleatoria (no permite elegir distribuidor; el desplegable vacío es porque nunca se terminó) y se hace un INSERT manual en `PalabrasDistribuidor` (servidor 10.0.0.180, base Tecno_distribuidores) con código de cliente + clave. Mesa de Ayuda aún no tiene usuario SQL (consultado a Marvin el 19-nov-2026): avisar a el supervisor y dejar el pendiente. Responder siempre con copia a Iris y al coordinador, y enviar los dos PDF de documentación.
2. `probar_acceso(codigo)`; para fallas puntuales `inventario(codigo, articulo)` / `inventario_bodega(codigo, articulo)`. Código de respuesta 99999 = "Consulta sin datos". Si falla el token, se renueva (dura 30 min). Si el distribuidor reporta fallas: Postman, probar también fuera de la red de Acme, revisar `Tecno_bitacora` (servidor 180) y, si no aparece la petición, preguntar a redes por tráfico de la IP del cliente.
3. Entregar las credenciales (código + clave) por borrador de correo con `outlook-desktop`, sin enviar. La clave nunca se escribe en la nota del ticket ni en el chat: `copiar_clave(codigo)` la deja en el portapapeles y el supervisor la pega en un hueco visible (`>>> PEGAR CLAVE AQUÍ <<<`) del borrador; revisar que no quede el marcador antes de enviar (pasó el 16-nov con SEISA).
4. `post_note` sin la clave, `log_hours` si el usuario da el tiempo y `close_ticket` solo si el cliente confirmó que consulta bien.

## 5c. Caso: acceso a STOD (usuario nuevo, «mismos accesos que X»)

Usar el skill `acceso-stod` (MCP `stod`: `usuarios`, `usuario`, `roles`, `permisos_rol`, `crear_usuario`). Probado con el ticket NNNNN (16-nov-2026).

## 5d. Regla general: datos sensibles en el ticket

Si el ticket o el correo trae una contraseña, token o clave en texto plano: avisar a el supervisor, no repetirla en el chat, en notas ni en borradores, y ofrecer reemplazarla en la descripción por «[contraseña omitida]» (con `write`, solo con su confirmación) y pedir al dueño que la cambie.

## 6. Resumen final

Qué quedó hecho, qué no se probó, qué falta y quién lo hace.
