# claude-code-helpdesk-skills

[Claude Code](https://claude.com/claude-code) **skills** (`SKILL.md` runbooks) for operating a help desk on Odoo with the MCP servers in the sibling repos.

| Skill | Use |
|---|---|
| `ticket-odoo` | Resolve a ticket end to end: read, act, document, log hours, reply, close. |
| `conciliar-mesa-ayuda` | Reconcile the shared mailbox against tickets and create what is missing. |
| `tablero-mesa-ayuda` | Update/create Odoo dashboards, the Cloudflare Worker and the claude.ai artifact. |
| `personalizar-odoo` | Add fields, filters, views and areas without touching vendor modules. |
| `publicar-knowledge` | Publish or edit a Knowledge article from a folder, Word, HTML or doc. |
| `reporte-tickets-gerencia` | Management report (Word + PDF) and e-mail draft. |
| `acceso-stod`, `soporte-stod` | Provision users and diagnose a legacy portal. |
| `pendientes` | Keep a to-do list across sessions. |
| `transcribir-videos` | Local transcription (no GPU) and summary of recorded trainings (`scripts/transcribir_videos.py`). |

Each skill states **when to trigger**, the exact tools to call, the traps already hit (with dates), and what must be confirmed with a human before acting.

## Español
Runbooks como skills de Claude Code: cuándo usarlos, qué herramientas llamar, errores conocidos y qué confirmar con una persona antes de ejecutar.

> **Note / Nota:** sanitized portfolio version of production work built for a corporate IT help desk. Company names, people, hosts, IDs and data were replaced with placeholders; secrets never lived in the code (they sit in the Windows Credential Manager). / Versión anonimizada de un trabajo real de mesa de ayuda corporativa: nombres, hosts, IDs y datos fueron reemplazados; los secretos nunca estuvieron en el código.
