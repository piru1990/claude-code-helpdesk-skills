---
name: soporte-stod
description: Diagnostica y resuelve fallas de STOD pedidas por ticket de Odoo - pantallas de error (FEIC, Encomiendas, Panel de Tickets), "no existen registros", reportes que no salen o que se piden nuevos, y restablecer la contraseña de un usuario de STOD. Usar cuando un ticket diga error en STOD, FEIC, Encomiendas, reporte de STOD, o "no puedo entrar a STOD". Las altas de usuario van con el skill acceso-stod.
argument-hint: <ticket de Odoo> (opcional)
---

# Soporte de fallas de STOD

MCP `stod` (`menu`, `page`, `usuario`, `permisos_rol`, `diagnosticar`, `ejecutar_reporte`, `restablecer_clave`) y `odoo-helpdesk`. Altas de usuario: skill `acceso-stod`. Si las herramientas nuevas no cargan, el MCP se modificó a mitad de sesión: pedir reiniciar Claude Code. STOD no se maneja por Chrome.

## Reglas
- Nunca contraseñas en el chat, notas o borradores. La temporal la genera el supervisor (`! …\.venv\Scripts\python.exe …\mcp-servers\_stod_env.py nuevaclave`; se entrega con `copiarclave` por otro medio y se borra con `borrarclave`).
- `restablecer_clave` y `crear_usuario` solo con `dry_run=False` tras confirmación de el supervisor en el chat. Primero siempre `dry_run=True`.
- `diagnosticar` no guarda nada, pero `permitir_pasos_de_ui=True` (ENCO_Control, FEICPJ_CrearFormulario) abre pantallas de captura: confirmar con el supervisor.
- La impresión de FEIC escribe un PDF compartido (`Reportes\0\Pruebas_STOD_SAPBONE.pdf`): no repetir pruebas de impresión sin necesidad (pueden pisar el PDF de otro usuario).
- Las fallas de código o de datos no se corrigen desde aquí: se escalan a desarrollo (borrador a user@, cc user@ y user@, sin enviar) con evidencia.

## Pasos
1. `get_ticket` y las imágenes (`get_attachment_image`): pantalla, número de formulario, usuario afectado, excepción.
2. `menu(texto)` para ubicar la página o el reporte; `usuario(login)` y `permisos_rol(rol)` del afectado (¿tiene el menú?).
3. Reproducir: `diagnosticar(path, campos, boton)` (la respuesta trae `pantalla`, `mensajes_de_error` y, si hay 500, la excepción y los métodos de la pila). Comparar un caso que falla con uno que no y con un número inexistente. Si con el usuario de el supervisor funciona y con el del cliente no, sospechar filtro por usuario/empresa/sucursal o por estado del dato.
4. Reportes: `ejecutar_reporte(id)` lista los parámetros; `exportar=True` genera el Excel. Si el servidor responde 500, la excepción va en la evidencia.
5. Clasificar: permisos (se corrige con el rol, solo `acceso-stod`), datos o código (se escala), capacitación (se cierra con instrucciones), contraseña (`restablecer_clave`).
6. Nota interna con `post_note`: Hecho · Pendiente · Prueba de cierre (sin contraseñas); `set_ticket_stage(id, "Esperando cliente")` si se espera respuesta de desarrollo o del usuario.
7. Borradores (`outlook-desktop`, sin enviar): escalamiento con capturas (`download_attachment`) y aviso al solicitante («RE: <asunto>»).
8. Cerrar (`close_ticket`) cuando el usuario confirme que quedó resuelto.

## Casos conocidos
| Falla | Evidencia | Tickets |
|---|---|---|
| FEIC Individual: «ERROR - NO EXISTEN REGISTROS DEL FORMULARIO SOLICITADO» al imprimir un formulario ya creado | Con el usuario de el supervisor el 24269 sí genera PDF; con un número inexistente sale el error. No se reprodujo con el usuario de la solicitante | 59775, 60539 |
| FEIC Jurídico: el combo «Municipio» queda bloqueado al capturar la dirección | Sin reproducir (requiere pasos de UI) | 60539 |
| Encomiendas > Control: `NullReferenceException` en `ENCO_ValidarCliente(String NIT)` (dsENCO.cs:19) con cualquier código | Captura del solicitante (pila: ENCO_Control.aspx.cs:253/264) | 60276 |
| Encomiendas > Consulta: sin datos | Con el usuario de el supervisor devuelve vacío en 01/10–17/11/2026 | 60385 |
| Panel de Tickets: 500 por `REDMINE.dbo.issue_statuses` | 16-nov-2026 | 60268 |
| Reporte «Vaciado de Información» (viáticos, 1556): 500 al exportar | `GetDataByStoredProc`, «Must set an ExceptionManager…» | 60464 |
