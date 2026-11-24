---
name: pendientes
description: Lleva la lista de pendientes entre sesiones en ~/.claude/pendientes.md. Usar cuando el usuario diga "retoma", "continúa con lo de ayer", "qué quedó pendiente", "en qué íbamos", o al cerrar un trabajo que deja algo abierto ("guarda los pendientes", "seguimos mañana").
argument-hint: [ver | guardar | cerrar <tema>]
---

# Pendientes entre sesiones

Archivo: `C:\Users\<user>\.claude\pendientes.md`. Sirve para no tener que pegar un resumen largo al empezar otra sesión.

## Retomar ("retoma", "qué quedó pendiente")

1. Leer `pendientes.md`.
2. Para cada pendiente abierto, comprobar su estado real antes de afirmarlo (el archivo dice lo que era cierto cuando se escribió): ticket con `get_ticket`, respuesta de correo con `outlook-desktop.search_messages`, flujo con `power-automate.get_flow` / `list_runs`.
3. Presentar: qué sigue abierto, qué cambió desde entonces, y cuál conviene atacar primero. Si el usuario nombró un tema, ir directo a ese.

## Guardar (al terminar un trabajo con algo abierto)

Una entrada por tema, corta y autosuficiente:

```markdown
## <Tema> — actualizado AAAA-MM-DD
- Estado: <una línea>
- Hecho: <lo ya realizado, con identificadores: ticket 59673, flujo ff733ad5…, artículo 721>
- Falta: <siguiente paso concreto> — responsable: <quién>
- Espera: <de quién se espera respuesta y desde cuándo>
- Dónde: <rutas, URLs, entry de correo>
```

- Actualizar la entrada existente del tema en vez de agregar otra.
- No guardar secretos ni contenido de correos; solo lo necesario para continuar.

## Cerrar

Cuando un tema termina, borrar su entrada (el historial está en el ticket o en el correo). Si el archivo queda vacío, dejar solo el título.
