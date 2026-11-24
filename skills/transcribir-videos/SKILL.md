---
name: transcribir-videos
description: Transcribe videos o audios largos (capacitaciones, reuniones grabadas) en esta PC sin GPU y los resume. Usar cuando el usuario pida transcribir videos, grabaciones o audios locales, o resumir una capacitación grabada.
argument-hint: <carpeta con los videos> [tema o términos propios]
---

# Transcribir y resumir videos

Pedido: $ARGUMENTS

Script: `C:\Users\<user>\mcp-servers\scripts\transcribir_videos.py` (leer su encabezado: explica por qué trabaja en tramos y cómo reanudar). Python: `C:\Users\<user>\mcp-servers\.venv\Scripts\python.exe`.

## Antes de empezar

- Si junto al video hay un `.vtt` o `.srt` (Teams lo descarga con la grabación), no transcribir: leerlo con `filesystem-trabajo.read_transcript(path)`, que quita las marcas de tiempo, une los turnos por hablante y pagina con `offset` / `siguiente_offset`.
- Si la grabación es de Teams/Stream y ya tiene transcripción en línea, usar esa (conector de Microsoft 365 o Read AI) en vez de transcribir.
- Comprobar requisitos y decir qué falta: `ffmpeg -version`; `python -c "import faster_whisper, numpy"`. Instalar con `pip install --proxy http://10.0.0.10:8080 faster-whisper numpy`; ffmpeg con `winget install Gyan.FFmpeg` (pedir permiso antes de instalar).
- Estimar y avisar el tiempo: con el modelo `small` en CPU, cuente aproximadamente el mismo tiempo que dura el audio; `base` es más rápido y menos exacto.

## Pasos

1. Audio: por cada video, `ffmpeg -i <video> -vn -ac 1 -ar 16000 <salida>.wav` en una carpeta de trabajo fuera de OneDrive.
2. Transcribir en segundo plano con prioridad baja (el comando exacto está en el encabezado del script), con `--contexto "<tema y términos propios>"`. Usar `run_in_background`; no hacer sondeo con sleep.
3. Es reanudable: si se interrumpe, volver a lanzar el mismo comando.
4. Leer los `.txt` por partes y resumir cada sesión: temas con su marca de tiempo, decisiones, pasos y pendientes.
5. Entregar donde el usuario pida. Para Odoo Knowledge, usar el skill `publicar-knowledge`.

## Cuidados

- No cerrar programas del usuario para liberar memoria sin preguntar.
- Si el proceso muere por memoria, bajar `--hilos` o usar un modelo menor antes de reintentar.
