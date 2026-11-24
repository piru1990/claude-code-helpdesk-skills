---
name: conciliar-mesa-ayuda
description: Concilia los correos enviados a la lista helpdesk@example.com contra los tickets del equipo 35 de Odoo y crea los tickets que falten. Usar cuando el usuario pida conciliar la mesa de ayuda, revisar qué correos no llegaron a Odoo, registrar correos como tickets, o revisar rebotes (NDR 5.7.520) de la lista.
argument-hint: [desde AAAA-MM-DD] (por defecto, hoy)
---

# Conciliar correos de Mesa de Ayuda contra Odoo

Periodo: $ARGUMENTS (vacío = hoy). Todo con los MCP `outlook-desktop`, `odoo-helpdesk` y `power-automate`; no usar el navegador.

## Cómo funciona (desde el 2026-11-13)

- Todo correo a `helpdesk@example.com` debe tener ticket en el equipo 35, área Mesa de Ayuda. Son tickets **internos**: no se avisa al remitente ni se le da el número (las etapas no tienen plantilla de correo; todo se registra como nota interna).
- Una regla de Outlook mueve esos correos a la carpeta `Mesa de Ayuda` del buzón de el supervisor. El flujo de Power Automate "Mesa de Ayuda → Odoo" (`<FLOW_ID>`, **encendido**) crea el ticket al llegar el correo, o agrega una nota interna si ya hay un ticket abierto con el mismo asunto, y sube los adjuntos.
- Cliente del ticket (misma regla en el flujo y en `create_ticket_from_email`): el contacto con el **correo real** del remitente, para que los técnicos puedan usar "Enviar mensaje" (el contacto de empleado `<código>@employee.example` ya NO se usa). Si no existe se crea: hijo de `[1000] ACME` (partner 1) para `@example.com`, `@sub-a.example.com`, `@sub-c.example.com`, `@sub-d.example.com`; hijo de Sub-B (17) para `@sub-b.example.com`; suelto si es externo. Lista en `DOMINIOS_GRUPO` de `mesa_ayuda_config.py` (y en la acción `Empresa_grupo` del flujo). Si aparece un ticket de correo con cliente `@employee.example`: `python odoo-helpdesk\cliente_correo_real.py [--dry-run]`.
- **Cliente = quien pidió (regla de el gerente, 24-nov-2026):** en un correo reenviado o respondido por un técnico (Técnico A, Técnico B, Técnico C, el supervisor), el cliente es el solicitante del hilo (la persona que pidió o a quien se atendió), NO el técnico que escribe ni el gerente. Se mira el correo más antiguo del hilo que sea de un usuario (no de STOD, Laserfiche ni otro sistema) y se usa su contacto con correo real. el gerente solo va de cliente en el trabajo interno del área (tableros, reglas, reportes). Revisión del 24-nov: 11 tickets corregidos (p. ej. #NNNNN, #NNNNN, #NNNNN).
- "Enviar mensaje" sale desde `helpdesk@example.odoo.com` (alias 8665 del equipo 35) con el número de ticket en el asunto; la respuesta del usuario vuelve al ticket por ese alias. "Registrar una nota" sigue siendo interno.
- Esta conciliación cubre lo que se le escape al flujo (flujo apagado o con ejecuciones fallidas). Crear estos tickets ya está autorizado por el supervisor: no pedir visto bueno por lote.

## 1. Revisar el flujo

`get_flow` (debe estar `Started`) y `list_runs(top=50)`: anotar ejecuciones `Failed` y desde cuándo. Si está apagado, decirlo y encenderlo solo si el supervisor lo pide.

Si hay ejecuciones `Failed`: `python odoo-helpdesk\recuperar_runs_fallidos.py --desde <AAAA-MM-DDTHH:MM UTC> [--dry-run]` registra en Odoo el correo de cada una (lo toma de la salida del disparador, con adjuntos) y omite las que fallaron después de crear el ticket o la nota. Es la vía preferida: Outlook de escritorio tarda en mostrar los correos más recientes de la carpeta. Después de CUALQUIER cambio al flujo, revisar la siguiente ejecución real (el 13-nov-2026 una fórmula mal escrita dejó 6 correos sin ticket durante una hora).

## 2. Simular

```
C:\Users\<user>\mcp-servers\.venv\Scripts\python.exe C:\Users\<user>\mcp-servers\odoo-helpdesk\conciliar_mesa_ayuda.py --desde <AAAA-MM-DD> --dry-run
```

Lista cada correo de la carpeta `Mesa de Ayuda` con `CREAR` (no hay ticket con ese asunto en 14 días) o `NOTA en <ticket>`. Con el flujo encendido casi todo saldrá como `NOTA`: eso significa que el ticket ya existe y **no hay que ejecutar la carga** (duplicaría las notas que ya puso el flujo). Solo interesan los `CREAR`.

## 3. Crear lo que falte

- Pocos casos: `create_ticket_from_email(subject, body_text, sender_name, sender_email, sent, attachments=[...], texto_completo=True)` por cada hilo (adjuntos con `save_attachments`).
- Un periodo completo sin flujo: el mismo script sin `--dry-run`, con `--hasta "AAAA-MM-DD HH:MM"` = momento en que el flujo volvió a funcionar. Lleva registro en `odoo-helpdesk\respaldos\conciliados_mesa_ayuda.json` y no repite correos.
- Rebotes: los NDR aparecen con `class` `REPORT.IPM.Note.NDR`; `get_message(id)` trae el original en `embedded_messages`.
- Asignación y cierre: solo si el supervisor lo indica (`assign_ticket`, `close_ticket`).

## 4. Clasificar, quitar duplicados y asignar

El flujo y `create_ticket_from_email` dejan el ticket con Fecha Ofrecida (fecha del correo + 2 días hábiles, SLA de Mesa de Ayuda; asuetos en `FERIADOS` de `mesa_ayuda_config.py`). Desde el 14-nov-2026 la regla de automatización de Odoo **"(CN003) Repartir y clasificar ticket de correo"** (base.automation 11, acción 59616) lo asigna al crearse y lo pasa a 20-Asignado: si un técnico escribió el correo es suyo; si no, al que menos tickets de correo recibió en 7 días (empate → menos abiertos). También llena Aplicación y Tipo de Soporte con palabras clave aprendidas de los tickets resueltos (≈80 % de acierto) y deja una nota interna con el motivo. Los técnicos del reparto están en el parámetro de sistema `cn003.reparto_correo.tecnicos` (sacar a quien esté de vacaciones). Para regenerar la tabla: `heuristica_clasificacion.py --codigo automatizaciones\reparto_correo_publicado.py` y `publicar_reparto.py`; para apagarla, `publicar_reparto.py --desactivar`. Este paso queda para duplicados, clasificaciones "por defecto" y lo que la regla no haya cubierto:

1. `python odoo-helpdesk\tickets_correo_pendientes.py` (solo lectura): por cada ticket de correo sin clasificar (o clasificado "por defecto") muestra texto, quién respondió en el hilo y candidatos a duplicado.
2. Decidir ticket por ticket y escribir un JSON en `odoo-helpdesk\respaldos\clasificacion_<fecha>.json` (formato en la cabecera de `aplicar_clasificacion.py`; ejemplo: `clasificacion_2026-11-13.json`):
   - **Clasificación** con los catálogos `cn003.helpdesk.ticket.tipo.soporte`, `cn003_helpdesk_ticket_aplicacion` y `cn003.helpdesk.ticket.modulo`: error/falla → *Lentitud o Errores con Sistema* (13); usuarios, accesos, correcciones → *Actualización de Datos* (11); cambio de comportamiento → *Ajuste al Sistema* (10); algo nuevo → *Nuevos requerimientos* (12); no es soporte → *Administrativo* (23). Aplicaciones frecuentes: SAP 5, STOD 8, (N/A) 6.
   - **Duplicado** (`duplicado_de`): otro ticket del equipo 35 que atiende la misma solicitud (el que creó el técnico, o el del mismo hilo). Se archiva el ticket creado desde el correo y se deja nota de enlace en el que sobrevive. Un antecedente ya finalizado de un caso que sigue sin resolver NO es duplicado: se conserva el nuevo y se enlaza con `nota`.
   - **Técnico** (Técnico A 446, Técnico B 3554, Técnico C 3253): el que ya respondió en el hilo; si nadie, el de más experiencia en esa aplicación/módulo y con ese solicitante en el histórico (incluidos archivados; `read_group` por `user_id`); empate → menos tickets abiertos. Lo que no es soporte de la mesa (Infraestructura, administrativo, proveedores) se queda con el supervisor con una nota.
3. `python odoo-helpdesk\aplicar_clasificacion.py <json> --dry-run` y luego sin `--dry-run`. Avisa al técnico asignado (notificación interna de Odoo), nunca al solicitante.

## 5. Resumen

Cuántos correos e hilos, cuántos ya tenían ticket, cuántos se crearon (con número), contactos creados, duplicados archivados, reparto por técnico y errores. Si se repite un patrón (mismo remitente o asunto que el flujo no registra), señalarlo.
