---
name: publicar-knowledge
description: Publica o edita un artículo de Odoo Knowledge (Acme) desde una carpeta, un Word, un HTML o un doc de Claude, o cambia una sola sección de un artículo existente. Usar cuando el usuario pida subir, pasar, publicar, actualizar o corregir contenido en Knowledge / la base de conocimiento de Odoo, o dé una URL de knowledge.article.
argument-hint: <id o URL del artículo> <qué publicar o cambiar>
---

# Publicar o editar en Odoo Knowledge

Pedido: $ARGUMENTS

Herramientas del MCP `odoo-helpdesk`: `knowledge_get`, `knowledge_edit_section`, `knowledge_publish`. No leer ni escribir `knowledge.article.body` con `read`/`write` directos (el HTML pesa ~100 KB y se pierde el control de historial), ni editar por el navegador.

## 1. Mirar el artículo

`knowledge_get(<id o URL>)`: título, `write_date`, índice de encabezados, número de imágenes y de secciones plegables. Guardar el `write_date` para pasarlo como `expected_write_date` al escribir.

## 2. Elegir el camino

**Cambio puntual** (quitar un texto, corregir o agregar a una sección): `knowledge_edit_section(id, heading, op, html_content, expected_write_date)` con `op` = `replace`, `append`, `delete` o `remove_text`. Probar primero con `dry_run=True` y revisar los tamaños antes/después.

**Reemplazo del artículo completo**:
1. Armar un archivo HTML local con el contenido (solo lo que va dentro del cuerpo). Tablas con `class="table table-bordered o_table"`; listas de tareas con `<ul class="o_checklist">`.
2. Imágenes: `<img src="nombre.png">` con los archivos en la misma carpeta (o en `images_dir`). Se suben como adjuntos sin reducir resolución.
3. Si el artículo ya tiene secciones plegables u otras ediciones hechas en Odoo, partir de su HTML actual (`knowledge_get(id, save_html_to=...)`) y modificarlo, en vez de regenerarlo: la herramienta se niega a escribir si se perderían plegables.
4. `knowledge_publish(id, html_path, images_dir, expected_write_date, dry_run=True)`, revisar, y luego sin `dry_run`.

**Origen en un doc de Claude** (artículo 721): exportar el doc a HTML y usar `C:\Users\<user>\mcp-servers\odoo-helpdesk\sync_doc_to_knowledge.py` (ver su encabezado). Ese script regenera el cuerpo: si el artículo tiene plegables hechos en Odoo, avisar al usuario antes, porque se perderían.

**Origen en Word o PDF**: leer con `word-office` (`describe_docx`, `read_docx_table`, `pdf_info`) y armar el HTML; los archivos originales se pueden adjuntar con `upload_attachment("knowledge.article", id, ruta)` y enlazar como `/web/content/<id>?download=true`.

## 3. Verificar

- `knowledge_get(id)` otra vez: encabezados, imágenes y plegables esperados; `write_date` nuevo.
- Cada escritura deja un respaldo del cuerpo anterior en `mcp-servers\odoo-helpdesk\respaldos\`; decir la ruta en el resumen.
- Avisar al usuario que, si tenía el artículo abierto en una pestaña, la recargue antes de editar.

## Reglas

- No borrar artículos ni adjuntos.
- Si `expected_write_date` no coincide, alguien editó el artículo: releer y volver a preparar el cambio; no forzar.
