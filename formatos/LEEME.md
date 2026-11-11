# Formatos de Nodo en Instagram (sistema visual vivo)

**Por qué existe:** entre el 4 y el 8 de noviembre se publicaron 13 piezas casi idénticas (fondo azul,
titular blanco, una palabra en coral). Nos dijeron que era repetitivo. La marca se mantiene
(colores, Sora + DM Sans, logo, coral solo para personas), pero **el formato y el fondo rotan**.

## Paleta ampliada (todo sale del azul y el coral de la marca)

| Nombre | Color | Uso |
| --- | --- | --- |
| Azul nodo | `#12264A` | fondo fuerte, CTA, cierres |
| Noche | `#0B1830` | escenas «de noche» (reloj, insomnio) |
| Niebla | `#F4F6FA` | fondo neutro, capturas, chats |
| Arena | `#F2EBE1` | fondo cálido: notas, editorial, frases |
| Cielo | `#D6E4F5` | fondo claro alterno: giros, puntos pares |
| Coral | `#E2603F` (`#F07A5C` sobre oscuro) | SOLO personas o la palabra clave. Nunca fondo. |

## Los formatos (plantillas en esta carpeta)

| Código | Qué es | Plantilla |
| --- | --- | --- |
| `reel-gancho` | Reel de tipografía animada: gancho en el 1.er segundo, una idea por escena, el fondo cambia en cada escena, audio propio | `reel-gancho/reel.html` (guion en `window.GUION`) + `grabar_reel.js` + `reel-gancho/sonido.sh` |
| `reel-chat` | Reel de chat de WhatsApp/web animado (fondo arena o azul) | `reel-chat/dudas-domingo.html` (copiar y cambiar mensajes; define `DURACION`) |
| `nota` | Post «nota del móvil» con lista de pendientes (fondo arena) | `estaticos.html` formato `nota` |
| `antes-despues` | Post partido: sin sistema / con sistema | `estaticos.html` formato `antes-despues` |
| `editorial` | Carrusel claro con numerales grandes (arena/cielo, cierre azul) | `estaticos.html` formatos `ed-portada`, `ed-punto`, `ed-cierre` |
| `clasico` | La plantilla azul/niebla original | `/mnt/project-files/contenido-redes/plantilla/` → **máximo 1 de cada 6 piezas** |

Una pieza estática = un JSON en `piezas/` y
`NODE_PATH=/opt/node22/lib/node_modules node formatos/render_estatico.js formatos/piezas/X.json cola/AAAA-MM-DD_FRANJA_tema`.
Un reel = editar `GUION` en una copia de `reel-gancho/reel.html`, crear el audio con `sonido.sh` y
`node formatos/grabar_reel.js <reel.html> cola/…/01.mp4 <audio.m4a>`.

## Reglas de rotación (obligatorias al rellenar la cola)

1. **Nunca dos piezas seguidas con el mismo formato ni con el mismo color de fondo dominante.**
   Antes de crear, mira las 4 últimas de `registro.csv` / `publicados/`.
2. **Mezcla semanal (14 piezas):** mínimo 3 reels, 3 carruseles, 4 posts de formatos distintos; la
   plantilla clásica como mucho 2.
3. **Gancho primero** (método ig-reel): elige 3 ganchos de fórmulas distintas («Nadie te cuenta…»,
   «Deja de…», contraste, pregunta espejo, error común), quédate con el más concreto. El texto del
   primer fotograma, 6 palabras o menos. Sin saludos ni logo al inicio.
4. **Reels:** 15–30 s, una idea, el fondo o el plano cambia cada 2–3 s, texto dentro de la zona segura
   (y 230–1440, 230 px libres a la derecha), cierre con una sola petición (comenta PALABRA) y una
   última frase que haga eco del gancho.
5. **Captions** humanizados (método ig-human): sin rayas largas, sin frases de relleno de IA, frases
   cortas. Siempre: CTA «Comenta AUDITORÍA/HORAS 👇» + enlace de auditoría + «(también en la bio)».
6. Guardrails de siempre: nada de cifras sin validar, nada de plazos garantizados, gestión y no
   tratamientos, liberar/devolver/acompañar (nunca sustituir).
7. Nuevos formatos bienvenidos (meme de texto, «pregunta de paciente», mini-encuesta, story-serie):
   si se crea uno, se añade a esta tabla.
