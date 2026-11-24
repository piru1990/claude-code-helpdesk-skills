---
name: reporte-tickets-gerencia
description: Genera el reporte para gerencia "Cantidad de tickets atendidos por Mesa de Ayuda" (Word + PDF) desde Odoo y deja el borrador de correo. Usar cuando el usuario pida el reporte de tickets para gerencia, el reporte mensual o trimestral de mesa de ayuda, el reporte que entregaba ex-técnico, o el reporte para la dirección.
argument-hint: [mes final AAAA-MM; por defecto el último mes cerrado]
---

# Reporte de tickets de Mesa de Ayuda para gerencia

Periodo: enero hasta $ARGUMENTS (si viene vacío, hasta el último mes cerrado).

el supervisor entrega este reporte mensual y trimestralmente desde noviembre 2026; antes lo hacía ex-técnico como una sección del "Resumen de resultados Informática". Tiene cuatro tablas: total por división, tickets por división y mes, horas por división y mes, y Top 10 de departamentos por división.

## 1. Generar

```powershell
$env:PYTHONIOENCODING='utf-8'
& C:\Users\<user>\mcp-servers\.venv\Scripts\python.exe C:\Users\<user>\mcp-servers\odoo-helpdesk\reporte_gerencia_tickets.py <DIR_SALIDA> --hasta AAAA-MM
```

- `<DIR_SALIDA>`: si el usuario no indica carpeta, usar `C:\Users\<user>\Downloads\Reporte tickets gerencia\AAAA-MM`.
- `--desde AAAA-MM` para un periodo que no empiece en enero (mismo año). `--solo-datos` solo saca `datos.json` y los totales.
- El script solo lee de Odoo, valida el total contra `search_count` y escribe el `.docx`, el `.pdf` y `datos.json`. Tarda cerca de un minuto y abre Word en segundo plano.
- Si avisa que el último mes no ha cerrado, decírselo al usuario antes de seguir.

## 2. Criterio (no cambiarlo sin que el supervisor lo pida)

- Desde el 16-nov-2026 (decisión de el supervisor): partes de horas (`account.analytic.line`) de tickets del equipo 35 registrados por el empleado (`user_id`) de `TECNICOS_REPORTE_GERENCIA`, no por el NT Técnico del ticket (hay tickets trabajados en equipo). Mes = fecha del parte; tickets = distintos con parte en el mes; horas = `unit_amount`. Reproduce a el ex-técnico (ene–jun 2026: 4,207 tickets y 3,432 h contra 4,210 y 3,432 h). Todo sale de `mesa_ayuda_config.py`, en la misma carpeta del script.
- Siempre se recalcula todo el periodo desde Odoo; por eso los meses anteriores pueden diferir de ediciones pasadas (la nota del documento ya lo dice).
- No existe la fila "Otros / sin división" (decisión de el supervisor, 2026-11-12): los tickets sin división válida se cuentan en DIVISIÓN TECNOLOGÍA (`DIVISION_POR_DEFECTO`).
- Un técnico nuevo o que sale de la mesa se cambia en `mesa_ayuda_config.py`: `TECNICOS_ACTIVOS` alimenta los tableros de supervisión y `TECNICOS_REPORTE_GERENCIA` este reporte. Quien atendió tickets durante el año se queda en la segunda lista hasta el cierre del año.

## 3. Verificar

1. Leer el PDF con Read y revisar: título con el periodo correcto, las cuatro tablas completas, que los totales de las tablas coincidan entre sí y que quepa en 2 páginas.
2. Comparar con la edición anterior si está a la mano (`datos.json` de la carpeta del mes previo) y contar al usuario los meses que cambiaron más de unos pocos tickets.

## 4. Entregar

Crear el borrador con `mcp__outlook-desktop__create_draft`, con `attachments` = rutas del `.docx` y del `.pdf`. Nunca enviar.

- Para: user@example.com; user@example.com (salvo que el usuario indique otro destinatario)
- CC: user@example.com
- Asunto: `Reporte de tickets Mesa de Ayuda — <periodo>`
- Cuerpo breve: periodo, total de tickets y horas, y lo que haya cambiado respecto de la edición anterior.

Cerrar diciendo dónde quedaron los archivos, los totales y que el borrador está sin enviar.

## Si algo cambia

- Formato del documento: editar `C:\Users\<user>\mcp-servers\odoo-helpdesk\plantillas\reporte_gerencia_tickets.docx`. Debe conservar las 4 tablas en ese orden, el título con el periodo entre paréntesis y el párrafo que empieza con "Fuente: Odoo".
- Para leer otro Word de referencia, usar el MCP `word-office` (`describe_docx`, `read_docx_table`).
- Para explorar cifras en Odoo, `mcp__odoo-helpdesk__read_group` (agrupa en UTC, así que los cortes de mes difieren un poco del reporte, que usa hora local).
