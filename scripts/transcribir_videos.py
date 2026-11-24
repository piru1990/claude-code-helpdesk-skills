"""Transcribe audios WAV largos con faster-whisper en una PC sin GPU, sin agotar la memoria.

Uso:
  python transcribir_videos.py DIR_WAV DIR_SALIDA [--modelo small] [--idioma es] [--hilos 6]
                               [--contexto "Capacitación de SAP ..."] [--solo TEXTO]

  DIR_WAV      carpeta con .wav mono de 16 kHz (ver "Preparar el audio")
  DIR_SALIDA   un .txt por archivo, con una línea por segmento: [HH:MM:SS] texto
  --contexto   frase con el tema y los términos propios; mejora mucho los nombres técnicos
  --solo       procesa solo los archivos cuyo nombre contiene TEXTO

Preparar el audio (ffmpeg): ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 audio.wav

Lo aprendido en la transcripción de la capacitación SAP (16 videos, 25 h):
  * importar PyAV se queda colgado en esta PC (antivirus): se anula y se lee el WAV con `wave`;
  * cargar un audio de 2 h completo agota la RAM: se procesa en tramos de 15 minutos;
  * es reanudable: salta los archivos que ya tienen .txt y escribe a .part mientras trabaja;
  * lanzarlo en segundo plano con prioridad baja para que la PC siga usable:
      Start-Process python -ArgumentList '...' -WindowStyle Hidden -PassThru | % { $_.PriorityClass = 'BelowNormal' }
  * requiere: pip install faster-whisper numpy (con --proxy http://10.0.0.10:8080).
"""
import argparse
import gc
import glob
import os
import re
import sys
import time
import types
import wave

import numpy as np

sys.modules["av"] = types.ModuleType("av")  # PyAV se cuelga al importarse; se alimenta PCM crudo
from faster_whisper import WhisperModel  # noqa: E402

TRAMO_S = 15 * 60
SR = 16000


def clave(p: str) -> str:
    m = re.search(r"(\d{8}_\d{6})", p)
    return m.group(1) if m else os.path.splitext(os.path.basename(p))[0]


def hms(s: float) -> str:
    s = int(s)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir_wav")
    ap.add_argument("dir_salida")
    ap.add_argument("--modelo", default="small")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--contexto", default="")
    ap.add_argument("--solo", default="")
    a = ap.parse_args()

    os.makedirs(a.dir_salida, exist_ok=True)
    archivos = sorted(glob.glob(os.path.join(a.dir_wav, "*.wav")), key=clave)
    if a.solo:
        archivos = [f for f in archivos if a.solo in f]
    if not archivos:
        raise SystemExit(f"No hay .wav en {a.dir_wav}")
    modelo = WhisperModel(a.modelo, device="cpu", compute_type="int8", cpu_threads=a.hilos, num_workers=1)

    for f in archivos:
        salida = os.path.join(a.dir_salida, clave(f) + ".txt")
        if os.path.exists(salida) and os.path.getsize(salida) > 0:
            print("ya hecho", clave(f), flush=True)
            continue
        t0 = time.time()
        print("inicio", clave(f), flush=True)
        tmp = salida + ".part"
        with wave.open(f, "rb") as w, open(tmp, "w", encoding="utf-8") as fh:
            if w.getframerate() != SR or w.getnchannels() != 1 or w.getsampwidth() != 2:
                raise SystemExit(f"{f}: debe ser WAV mono de 16 kHz y 16 bits (ver ayuda)")
            fh.write(f"# {os.path.basename(f)}\n# duracion {hms(w.getnframes() / SR)}\n")
            desfase = 0.0
            while True:
                crudo = w.readframes(TRAMO_S * SR)
                if not crudo:
                    break
                audio = np.frombuffer(crudo, np.int16).astype(np.float32) / 32768.0
                del crudo
                segmentos, _ = modelo.transcribe(audio, language=a.idioma, vad_filter=True, beam_size=1,
                                                 initial_prompt=a.contexto or None,
                                                 condition_on_previous_text=False)
                for s in segmentos:
                    fh.write(f"[{hms(desfase + s.start)}] {s.text.strip()}\n")
                    fh.flush()
                desfase += len(audio) / SR
                del audio, segmentos
                gc.collect()
        os.replace(tmp, salida)
        print("listo", clave(f), f"{(time.time() - t0) / 60:.1f} min", flush=True)
    print("TODO LISTO", flush=True)


if __name__ == "__main__":
    main()
