#!/usr/bin/env python3
"""
Publica carruseles de Instagram de Nodo con la API de Meta (Graph API).

Cómo funciona, en resumen:
  - En la carpeta `cola/` dejas una carpeta por publicación, llamada
    `AAAA-MM-DD_nombre` (la fecha es el día en que debe publicarse).
    Dentro van las imágenes `01.png`, `02.png`... (o .jpg) en orden
    y un `caption.txt` con el texto del post.
  - Este script coge las carpetas cuya fecha ya ha llegado (<= hoy),
    sube el carrusel a Instagram y, si sale bien, apunta el enlace en
    `registro.csv` y mueve la carpeta a `publicados/`.

Las imágenes se sirven desde el propio repositorio (raw.githubusercontent),
así que no dependemos de ningún alojamiento externo. Instagram guarda su
propia copia al publicar, por lo que la URL solo hace falta un momento.

Credenciales (como secretos del repositorio en GitHub Actions):
  IG_USER_ID  -> id de la cuenta de Instagram (p. ej. 17841462825912071)
  IG_TOKEN    -> token de acceso de larga duración (System User, no caduca)

Nunca se escriben el token ni el id en ningún archivo.
"""

import csv
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

API = "https://graph.facebook.com/v22.0"

RAIZ = Path(__file__).resolve().parent
COLA = RAIZ / "cola"
PUBLICADOS = RAIZ / "publicados"
REGISTRO = RAIZ / "registro.csv"

IG_USER_ID = os.environ.get("IG_USER_ID", "17841462825912071").strip()
IG_TOKEN = os.environ.get("IG_TOKEN", "").strip()
REPO = os.environ.get("GITHUB_REPOSITORY", "").strip()      # "igazmar/nodo-social"
BRANCH = os.environ.get("GITHUB_REF_NAME", "main").strip() or "main"

EXTS = (".png", ".jpg", ".jpeg")


def _abrir(req):
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode(errors="replace")
        print(f"  [Graph API {e.code}] {cuerpo}")
        raise


def _post(path, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{API}/{path}", data=data, method="POST")
    return _abrir(req)


def _get(path, params):
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{API}/{path}?{q}", method="GET")
    return _abrir(req)


def comprobar_token():
    info = _get(IG_USER_ID, {"fields": "username", "access_token": IG_TOKEN})
    print(f"Token OK -> cuenta @{info.get('username')}")


def imagenes_de(carpeta: Path):
    fotos = sorted(p for p in carpeta.iterdir() if p.suffix.lower() in EXTS)
    if not fotos:
        raise SystemExit(f"Sin imágenes en {carpeta}")
    return fotos


def url_raw(carpeta: Path, foto: Path):
    rel = f"cola/{carpeta.name}/{foto.name}"
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{urllib.parse.quote(rel)}"


def publicar_reel(carpeta: Path, video: Path, caption: str):
    print(f"\n== {carpeta.name}: reel {video.name} ==")
    creation_id = _post(
        f"{IG_USER_ID}/media",
        {"media_type": "REELS", "video_url": url_raw(carpeta, video),
         "caption": caption, "share_to_feed": "true", "access_token": IG_TOKEN},
    )["id"]
    print(f"  contenedor -> {creation_id}")
    # Instagram procesa el vídeo de forma asíncrona: esperar a que acabe.
    for _ in range(40):
        time.sleep(6)
        est = _get(creation_id, {"fields": "status_code", "access_token": IG_TOKEN})
        code = est.get("status_code")
        print(f"  procesando… {code}")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise SystemExit(f"Instagram no pudo procesar el vídeo: {est}")
    else:
        raise SystemExit("El vídeo tardó demasiado en procesarse (timeout)")
    media_id = _post(
        f"{IG_USER_ID}/media_publish",
        {"creation_id": creation_id, "access_token": IG_TOKEN},
    )["id"]
    permalink = _get(media_id, {"fields": "permalink", "access_token": IG_TOKEN}).get("permalink", "")
    print(f"  PUBLICADO (reel) -> {media_id}  {permalink}")
    return media_id, permalink


def publicar_carpeta(carpeta: Path):
    caption = (carpeta / "caption.txt").read_text(encoding="utf-8").strip()
    videos = sorted(p for p in carpeta.iterdir() if p.suffix.lower() == ".mp4")
    if videos:
        return publicar_reel(carpeta, videos[0], caption)
    fotos = imagenes_de(carpeta)
    print(f"\n== {carpeta.name}: {len(fotos)} imágenes ==")

    if len(fotos) == 1:
        creation_id = _post(
            f"{IG_USER_ID}/media",
            {"image_url": url_raw(carpeta, fotos[0]), "caption": caption,
             "access_token": IG_TOKEN},
        )["id"]
    else:
        hijos = []
        for foto in fotos:
            cid = _post(
                f"{IG_USER_ID}/media",
                {"image_url": url_raw(carpeta, foto), "is_carousel_item": "true",
                 "access_token": IG_TOKEN},
            )["id"]
            print(f"  {foto.name} -> {cid}")
            hijos.append(cid)
        creation_id = _post(
            f"{IG_USER_ID}/media",
            {"media_type": "CAROUSEL", "children": ",".join(hijos),
             "caption": caption, "access_token": IG_TOKEN},
        )["id"]

    print(f"  contenedor -> {creation_id}")
    time.sleep(8)  # dar tiempo a Instagram a procesar las imágenes
    media_id = _post(
        f"{IG_USER_ID}/media_publish",
        {"creation_id": creation_id, "access_token": IG_TOKEN},
    )["id"]
    permalink = _get(media_id, {"fields": "permalink", "access_token": IG_TOKEN}).get("permalink", "")
    print(f"  PUBLICADO -> {media_id}  {permalink}")
    return media_id, permalink


def anotar(carpeta, media_id, permalink):
    nuevo = not REGISTRO.exists()
    with REGISTRO.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha_publicado", "carpeta", "media_id", "permalink"])
        w.writerow([date.today().isoformat(), carpeta.name, media_id, permalink])


def slot_actual():
    # Franja por hora UTC. Crons: 06:30 UTC → mañana (am); 19:00 UTC → tarde (pm).
    h = int(os.environ.get("SLOT_HORA", datetime.now(timezone.utc).hour))
    return "am" if h < 12 else "pm"


def partes_carpeta(carpeta: Path):
    # Nombre: AAAA-MM-DD[_am|_pm]_descripcion
    try:
        f = date.fromisoformat(carpeta.name[:10])
    except ValueError:
        return None, None
    resto = carpeta.name[11:].split("_", 1)
    slot = None
    if resto and resto[0].lower() in ("am", "pm", "manana", "mañana", "tarde", "noche"):
        slot = "am" if resto[0].lower() in ("am", "manana", "mañana") else "pm"
    return f, slot


def carpetas_pendientes(slot):
    hoy = date.today()
    pend = []
    for c in sorted(COLA.iterdir() if COLA.exists() else []):
        if not c.is_dir():
            continue
        f, s = partes_carpeta(c)
        if f is None:
            print(f"  (ignoro {c.name}: el nombre no empieza por AAAA-MM-DD)")
            continue
        if f < hoy:
            pend.append(c)                       # atrasada: se recupera siempre
        elif f == hoy and (s is None or s == slot):
            pend.append(c)                       # de hoy y de esta franja (sin franja = cualquiera)
    return pend


def main():
    if not IG_USER_ID or not IG_TOKEN:
        raise SystemExit("Faltan IG_USER_ID o IG_TOKEN (configúralos como secretos).")
    comprobar_token()

    # Modo manual: `python publicar.py cola/2026-11-10_am_carrusel-01`
    objetivo = sys.argv[1] if len(sys.argv) > 1 else None
    if objetivo:
        carpetas = [Path(objetivo).resolve()]
    else:
        slot = slot_actual()
        print(f"Franja: {slot}")
        carpetas = carpetas_pendientes(slot)

    if not carpetas:
        print("Nada que publicar en esta franja.")
        return

    PUBLICADOS.mkdir(exist_ok=True)
    for c in carpetas:
        media_id, permalink = publicar_carpeta(c)
        anotar(c, media_id, permalink)
        shutil.move(str(c), str(PUBLICADOS / c.name))
        print(f"  movido a publicados/{c.name}")


if __name__ == "__main__":
    main()
