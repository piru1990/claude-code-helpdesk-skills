---
name: personalizar-odoo
description: Personaliza Odoo (Acme) sin tocar el código de los módulos CNxxx - agregar un campo x_ a un modelo, un filtro, agrupado o columna a una vista, cambiar un favorito, o cambiar los usuarios o el supervisor de un área de CN003. Usar cuando el usuario pida agregar un campo, filtro o agrupado en Tickets / CN003, clasificar tickets por un dato nuevo, quitar o poner usuarios en "Áreas y usuarios", o dé una URL example.odoo.com/odoo/action-NNN pidiendo un cambio de configuración.
argument-hint: <qué se quiere cambiar, o URL de la acción>
---

# Personalizar Odoo sin tocar los módulos

Pedido: $ARGUMENTS

Todas las herramientas son del MCP `odoo-helpdesk`. Los módulos `(CNxxx)` son de el proveedor: no se edita su código ni sus vistas. Se trabaja con campos `x_` (`ir.model.fields`, `state = manual`), vistas heredadas nuevas sin identificador externo y favoritos (`ir.filters`).

## 1. Entender (solo lectura)

1. Si hay imágenes de referencia, verlas.
2. `action_info(<id o URL>)`: modelo, contexto y las vistas que **realmente** usa la acción. La de búsqueda casi nunca es la del módulo: Tickets de CN003 (acción 900) usa la estándar de Helpdesk (1097), compartida con los demás equipos.
3. `module_info("CNxxx")` para los modelos y campos del módulo; `team_areas()` para áreas, usuarios y supervisor.
4. `custom_field_check(modelo, relation=…)` antes de proponer un campo. Leer sus advertencias.
5. `view_arch(modelo, tipo, view_id)` para saber dónde insertar (nombres de campos y filtros vecinos).

## 2. Trampas conocidas

- **Modelo sin nombre para mostrar.** `cn003_helpdesk_ticket_area` (y otros `cn003_*` con guion bajo) no tienen `name`: un many2one hacia ellos se ve como `modelo,id`. Crear `x_name` no lo arregla. Usar un campo de **selección**.
- **Campo calculado o relacionado almacenado.** Al crearlo, Odoo recalcula toda la tabla y cambia "Última actualización" (y su autor a OdooBot) en cada registro que recibe valor. En `helpdesk.ticket` son decenas de miles y no se puede revertir. Decírselo a el supervisor y esperar su confirmación antes de crear el campo.
- **El cálculo solo corre al crear el campo y cuando cambian sus dependencias.** Si depende de quién está en un área, crear el campo antes de sacar a alguien del área; después, sus registros históricos solo se corrigen con `write_where`.
- **Vistas compartidas.** Lo que se agregue a una vista estándar se condiciona con `invisible="not context.get('cn003_context_key')"` (la acción 900 lleva esa clave) para que no aparezca en otros equipos.
- **Campo calculado editable.** `readonly: false` con `compute` y `depends`: se llena solo y se puede cambiar a mano; el cambio manual dura hasta que cambie una dependencia.
- **Áreas y usuarios.** Agregar o quitar líneas con `write` sobre el área y `context={"cn003_mode": "cn003"}` (`user_ids: [[0,0,{…}]]` para agregar, `[[2, id_linea, 0]]` para quitar). El supervisor del área recibe las notificaciones de partes de horas. Quitar a alguien del área no le quita grupos de seguridad.

## 3. Proponer

Plan corto: qué se crea, en qué orden, efectos (sobre todo el de "Última actualización" y a quién le cambia la pantalla) y cómo revertir. Preguntar solo lo que sea decisión de el supervisor.

## 4. Aplicar, en este orden

1. Datos de configuración (áreas, usuarios).
2. Campo: `create("ir.model.fields", {...})`. Si el permiso se bloquea, parar y pedirlo; no buscar otro camino.
3. Comprobar el llenado con `read_group` contra los conteos esperados.
4. Vistas heredadas: `create("ir.ui.view", {inherit_id, mode: "extension", priority: 99, arch})`, con nombre terminado en "(personalización)".
5. `view_arch(…, contains="<nombre del campo>")` para confirmar que la vista compila y trae lo nuevo.
6. Favoritos (`ir.filters`): solo los de el supervisor.
7. Correcciones masivas: `write_where` primero con `dry_run=True`.

## 5. Limpiar

Lo que quede sin uso se borra con `delete_customization` (primero `dry_run=True`; se niega si el campo sigue en una vista, favorito u otro campo). Borrar primero los campos que dependen de otros.

## 6. Cerrar

- Decir qué se verificó por API y qué falta ver en pantalla.
- Si cambiaron ids o campos que se usarán otra vez, actualizar `~/.claude/CLAUDE.md` y `mcp-servers\odoo-helpdesk\mesa_ayuda_config.py`.
- Resumen: hecho, efectos, pendiente y cómo revertir.
