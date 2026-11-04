# Nodo · publicación automática en Instagram

Este repositorio publica solo los carruseles de Instagram de Nodo, en la nube,
sin depender de que ningún ordenador esté encendido.

## Cómo publicar algo

1. Crea una carpeta dentro de `cola/` con este nombre:
   `AAAA-MM-DD_FRANJA_lo-que-sea` → la fecha es el **día** y FRANJA es `am`
   (mañana, 07:30) o `pm` (tarde, 20:00).
   Ejemplo: `cola/2026-11-10_am_carrusel-02` o `cola/2026-11-10_pm_story-serie`.
2. Mete dentro las imágenes en orden (`01.png`, `02.png`, …; también vale `.jpg`)
   y un archivo `caption.txt` con el texto del post.
3. Ya está. Se publican **dos veces al día** (07:30 y 20:00, hora de Madrid): el
   proceso coge la carpeta de la franja que toca, apunta el enlace en
   `registro.csv` y la mueve a `publicados/`. Una carpeta sin `am`/`pm` se publica
   en la primera franja de su día; una carpeta atrasada se recupera a la siguiente.

¿Publicar ahora mismo una carpeta concreta? En la pestaña **Actions** →
**Publicar en Instagram** → **Run workflow**, y (opcional) escribe la ruta de la
carpeta.

## Credenciales (secretas)

En **Settings → Secrets and variables → Actions** hay dos secretos:

- `IG_USER_ID` — id de la cuenta de Instagram.
- `IG_TOKEN` — token de acceso de larga duración (System User de Meta, no caduca).

El token nunca se guarda en archivos ni en mensajes, solo como secreto cifrado.

## Cómo funciona por dentro

`publicar.py` usa la Graph API de Meta. Las imágenes se sirven desde este mismo
repositorio (`raw.githubusercontent.com`), así que no hace falta ningún
alojamiento externo; Instagram guarda su propia copia al publicar.
