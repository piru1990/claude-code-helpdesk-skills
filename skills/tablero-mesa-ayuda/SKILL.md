---
name: tablero-mesa-ayuda
description: Actualiza, crea o consulta los tableros de Mesa de Ayuda (Técnico A, Técnico B, Técnico C; equipo 35) - los de Odoo (53/54/55 de supervisión y 56 de indicadores de desempeño), el Worker de Cloudflare y el artifact de claude.ai - o responde cifras de supervisión diaria, semanal o mensual y la nota de desempeño de cada técnico. Usar cuando el usuario pida actualizar el tablero, republicar los tableros, desplegar el tablero, crear un tablero nuevo en Odoo, dar o revisar acceso a un tablero, cómo va el equipo hoy / esta semana / este mes, o qué nota o indicadores lleva un técnico.
argument-hint: [consultar | odoo | nuevo | acceso | worker | artifact] [detalle]
---

# Tableros de supervisión de Mesa de Ayuda

Pedido: $ARGUMENTS

Python: `C:\Users\<user>\mcp-servers\.venv\Scripts\python.exe`. Scripts en `C:\Users\<user>\mcp-servers\odoo-helpdesk\`. Técnicos y equipo: `mesa_ayuda_config.py` (único lugar donde se cambian). Meta: 8 h registradas por técnico al día.

## Solo quieren cifras

No regenerar nada. Usar el MCP `odoo-helpdesk`:
- `team_stats(desde, hasta, ["user_id"])` — tickets y horas por técnico (creados en el periodo); `por="close_date"` para cerrados.
- `hours_by_tech(desde, hasta)` — horas registradas por empleado.
- `team_queue()` — abiertos por etapa y por técnico; `team_queue(sin_asignar=True)`.
- `kpi_indicadores(desde, hasta)` — nota de desempeño y los 4 rubros por técnico y equipo, tickets y horas por división, tickets fuera del margen y `fechas_invalidas` (cierre anterior a la apertura: avisar para que se corrija la fecha manual). Es lo mismo que muestra el tablero 56.
Fechas en hora de Guatemala.

## Tableros de Odoo (53 diario, 54 semanal, 55 mensual, 56 indicadores, 57 redes, 58 operaciones)

Publicar: `dashboard_publish(["diario","semanal","mensual"])` del MCP, o `python tablero_odoo.py <dir_salida> --publicar diario semanal mensual`. Ids en `TABLEROS` de `mesa_ayuda_config.py`.
- Para cambiar un tablero se edita `tablero_odoo.py` y se vuelve a publicar; lo editado a mano en Odoo se sobrescribe. El MCP no ve cambios de código hasta reiniciar Claude Code: tras editar el script, publicar por línea de comandos.
- Tablero 56 "KPI Mesa de Ayuda" (antes "Indicadores de desempeño", renombrado el 16-nov-2026; clave `indicadores`; el nombre está en `NOMBRES` de `tablero_odoo.py`, que publicar usa para encontrarlo): tabla de medición de resultados por técnico con la lógica del Excel "Odoo CTL Horas PROT" (4 rubros con peso y meta → nota) más tickets y horas por división y mes. Incluye a ex-técnico. Pesos, metas y margen (20 min) están en `RUBROS` / `MARGEN_MIN` de `mesa_ayuda_config.py`; el cálculo equivalente fuera de Odoo es `indicadores.py`. Carga hasta 1,200 tickets por periodo (`MAX_TICKETS`).
- Tablero 56 (cambios 16-nov-2026): las tarjetas ya no muestran "N de 4 en meta" (la columna "En meta" de la tabla sigue); bloque "KPI del técnico seleccionado" (hoja `_Template` del Excel) que sigue el filtro Técnico; exportar (cambio del 16-nov-2026, 56/57/58): línea `EXPORTAR` en el tablero (A6 en el 56, A5 en el 57, A7 en el 58) que indica la exportación nativa de Odoo: Excel = botón Compartir → Descargar (crea un `spreadsheet.dashboard.share`; trae solo lo que se ve), PDF = Ctrl+P → Guardar como PDF. Se quitaron los enlaces al Worker porque daban 401 (la API key del Worker ya no existe en Odoo; el Worker y su Excel con una hoja por técnico siguen en `…workers.dev/indicadores.html?accion=pdf|excel` y volvieron a funcionar el 16-nov-2026 al cargar el supervisor una key nueva con `(Get-Clipboard).Trim() | npx.cmd wrangler secret put ODOO_API_KEY`; en PowerShell usar `npx.cmd`, porque `npx.ps1` está bloqueado por la política de ejecución). Respaldo previo: `respaldos\tablero_56_indicadores_antes_20261116.json`.
- «Cómo leer la tabla» (17-nov-2026): bloque de celdas Columna | Qué significa en los tableros 56, 57 y 58, creado con el helper `leyenda(t, fila, filas, hasta, nota)` de `tablero_odoo.py` (pesos, metas y plazos salen de `RUBROS`, `MARGEN_MIN` y `DIAS_*`, no están fijos). Al agregar una columna o tarjeta, agregar su fila. Textos de ≤ ~110 caracteres en el 57 y ~150 en el 56/58, o se cortan a la derecha.
- Tablero 57 "KPI Redes y Ciberseguridad" (clave `redes`, creado 16-nov-2026, abierto a Helpdesk / User): NO sale de tickets sino del Excel `OneDrive - Acme, S.A\KPI Redes y Ciberseguridad\KPI Redes y Ciberseguridad.xlsx` (`RUTA_KPI_REDES`; hojas Ciberseguridad y Comunicaciones; cifras de las consolas y reportes de el líder de Redes, ene–sep 2026 tomadas de `Nuevos-KPI-Agosto2026 Redes y Ciberseguridad.pptx`). Cada mes: llenar la columna del mes en el Excel y `python tablero_odoo.py <dir> --publicar redes` (solo muestra hasta el último mes con dato; concepto nuevo = fila nueva). Sin filtros globales (`Tablero.sin_filtros`); gráficos estándar con `grafico_rango`. Faltan oct–nov 2026 por cargar.
- Tablero 58 "KPI Operaciones Informática" (clave `operaciones`, creado 16-nov-2026, solo Dashboard/Admin hasta que el supervisor lo abra a Helpdesk): equipo de el líder de Operaciones (Técnico D 2766 y Técnico E 3537 con equipos de cómputo; Técnico F 3464 con facturas y órdenes de compra), también del equipo 35. Replica el Excel `OneDrive - Acme, S.A\KPI 2026 - Operaciones Informatica\KPI hasta Octubre 2026.xlsx` (explicación en `KPI - Operaciones.vtt`): fallas por rubro y semana del mes (S1 = días 1-7…), nota del rubro = peso si fallas ≤ tolerancia, si no peso ÷ fallas, nota del mes = promedio de semanas. Tiempos en el mismo ticket, días hábiles apertura→cierre menos 1: checklist ≤ 2, entrega ≤ 5, factura ≤ 3, orden ≤ 5 (`DIAS_*` y `RUBROS_EQUIPOS`/`RUBROS_COMPRAS` en `mesa_ayuda_config.py`). Equipos = Tipo de Soporte «Equipo Nuevo» + «Cambio de Equipo»; órdenes = «Orden de compra»; facturas = «factura» en el asunto. Problemas reportados y errores de orden salen del campo `x_cn003_kpi_error` «Error KPI» (selección `problema_equipo` / `error_orden`, ir.model.fields 59603, en formulario 5148 y filtro «Con error KPI» en 5147): alguien debe marcarlo en el ticket, si no esos rubros dan siempre el 100 %. Incluye además entregas por departamento y por división y mes, y listas de tickets fuera de plazo. Cálculo equivalente fuera de Odoo: `kpi_operaciones.py AAAA-MM` (oct-2026 cuadra con el tablero y con el Excel: 30 equipos, 52 órdenes). Carga hasta 120 tickets de equipos y 200 de compras por periodo (`NE`, `NC`).
- Formato Odoo 19: las celdas deben ser texto (un número crudo rompe la carga); `PIVOT.VALUE` sin datos devuelve vacío (usar `+0`); "últimos 12 meses" excluye el mes en curso; un tablero sin publicar no se puede abrir (para probar, publicar solo al grupo 253).
- Verificar cifras: `kpi_indicadores` (56) o `team_stats` (53–55) contra lo que muestra el tablero.
- Verificar diseño, solo si cambió: abrir `https://example.odoo.com/odoo/dashboards?dashboard_id=<id>` con Claude in Chrome (tiene la sesión de Odoo de el supervisor). El perfil de `edge` solo sirve si el supervisor inició sesión ahí; no pedir ni escribir la contraseña. Con `edge`, las capturas solo se guardan en su carpeta `.playwright-mcp` (no pasar otra ruta en `filename`).

### Accesos

- `dashboard_access(<id o clave>, [correos])` dice qué grupos ven el tablero y si cada persona entra. Los cuatro están abiertos a Helpdesk / User (grupo 43): técnicos, el gerente y la dirección (`user@example.com`).
- Un tablero nuevo nace visible solo para Dashboard/Admin (253). Abrirlo a los técnicos es decisión de el supervisor: `dashboard_publish([...], abrir_a_helpdesk=True)` o `--visible <clave>` (`--visible` a secas abre solo los tres de supervisión).
- Quien no tiene usuario interno en Odoo (p. ej. un correo `@el proveedor.com`) no puede ver tableros; `find_user` lo confirma. Crear usuarios o cambiar sus grupos se pide a el administrador.

### Crear un tablero nuevo

1. Si la lógica viene de un Excel, leerla con `excel-office.workbook_logic` (fórmulas, tablas y nombres definidos; sirve con `.xlsb` y macros). Si hay grabación de Teams con `.vtt`, `filesystem-trabajo.read_transcript`.
2. Confirmar con `fields_get` / `ir.model.fields` que los campos están almacenados (`store`): solo esos se agrupan en pivotes.
3. Escribir un generador en `tablero_odoo.py` con la clase `Tablero` (`pivot`, `lista`, `put`, `titulo`, `tarjeta`, `grafico`, `alto`) y registrarlo en `GENERADORES` y `NOMBRES`; añadir su id a `TABLEROS`.
4. Publicar (nace solo para el grupo 253), comparar cifras con un cálculo independiente y revisar el diseño en el navegador.

Lo que ya se sabe que funciona:
- Un pivote no calcula por registro (p. ej. cierre − apertura). Para eso, `ODOO.LIST` en la hoja Data con columnas calculadas y `COUNTIF`/`SUMIF` encima; poner tope de filas y un aviso comparando contra el conteo de un pivote.
- `ODOO.LIST` de un many2one devuelve el nombre, no el id: para casar por técnico usar `PIVOT.HEADER(pivote,"user_id",uid)` con un nombre de respaldo en `IFERROR`.
- Columnas de pivote por posición: `"#create_date:month",k` en `PIVOT.HEADER` y `PIVOT.VALUE`; así no se fija el año.
- Variantes de un mismo valor de texto (divisiones): sumar un `PIVOT.VALUE` por variante y sacar la división por defecto (Tecnología, que también recibe los tickets sin división) por diferencia contra el total. No debe existir una fila "Otros / sin división".
- Lista filtrada (p. ej. tickets con problema): contador acumulado en Data y `MATCH` + `INDEX` en el tablero.
- Encabezados cortos: con columnas de ~96 px se corta todo lo que pase de unos 12 caracteres; tarjetas de 235 px con base de menos de 30 caracteres.
- No usar formato condicional `CellIsRule` (su formato cambia entre versiones y puede romper la carga); solo `DataBarRule`, o una columna de texto con el estado.

## Worker de Cloudflare (en vivo)

`https://tablero-mesa-ayuda.user-el supervisor.workers.dev`, proyecto en `C:\Users\<user>\tablero-mesa-ayuda\` (fuente en `page\`).
1. `pwsh build\armar.ps1` arma `public\`.
2. `$env:HTTPS_PROXY='http://10.0.0.10:8080'; npx wrangler deploy`.
3. Comprobar que sin sesión responde 403 (Cloudflare Access).
- `wrangler login` y los secretos los pone el supervisor en su terminal: `(Get-Clipboard).Trim() | npx wrangler secret put NOMBRE` (pegar con Ctrl+V mete un carácter de control y Odoo responde 400 vacío). El Worker usa una API key propia, distinta de la del MCP; no copiar la del MCP.
- Dar acceso a alguien: agregar su correo a una política de la app `tablero-mesa-ayuda` en Cloudflare Access (lo hace el supervisor).

## Artifact de claude.ai (copia, no en vivo)

`https://claude.ai/artifact/NSPJSA2TYQn6RBGXjXmAZ9`
1. `python tablero_mesa_ayuda.py <dir_salida>` genera `tickets.json` y `horas_dia.json`.
2. Subir cada archivo como asset del artifact (Artifact publish con `asset: true`, `url`, `file_path`).
3. Con ArtifactData, `update` de `datasets/tickets` y `datasets/horas_dia`: `source.url` nuevo (`/_blob/<id>`), `updated.at` y `edit`. Borrar los assets viejos.

## Al terminar

Decir qué tablero se actualizó, con qué fecha de corte, y cualquier cifra que llame la atención (técnico sin horas, cola sin asignar).
