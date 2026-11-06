# Entregas · Manu Galdámez — cómo hacer una entrega

Manu pega en el chat un link de carpeta de Google Drive y los datos del proyecto (o la cotización). Tú haces TODO lo demás sin pedirle archivos.
Sitio publicado por Netlify desde la rama `main`: https://entregas.manugaldamez.com/<slug>  (también responde en https://manuentregas.netlify.app/<slug>)

## 0. Repo
- `add_repo` owner `manuelgaldamezfoto`, repo `ENTREGAS`, access `push`. Clonar en /home/claude/entregas.
- Commits con: `git -c user.name="Manu Galdámez" -c user.email="manuelgaldamezfoto@gmail.com" commit ...`

## 1. Comprobar la carpeta (conector Google Drive)
- ID de carpeta = lo que va tras `/folders/` en el link.
- `get_file_metadata` (título) y `get_file_permissions`: debe haber `type: anyone, role: reader`. Si no, para y pide a Manu que la comparta como "Cualquier persona con el enlace" (sin eso, ni el proceso ni el cliente pueden verla).
- No uses `download_file_content` para fotos: falla con archivos de más de ~6 MB.

## 2. Descargar miniaturas (automático, GitHub Actions)
- Crea `_jobs/<slug>.json` → `{"slug": "<slug>", "folder": "<ID carpeta>", "size": 1600}`, commit y push a `main`.
- La Action "Descargar miniaturas de Drive" lista la carpeta (y subcarpetas, 2 niveles) y sube las imágenes a 1600 px a la rama `drive-cache` en `<slug>/`, con `_report.json` (ok/fail) y `_manifest.json` (imágenes, vídeos y otros con sus IDs). Tarda 2–4 min.
- Espera en segundo plano con `git ls-remote origin drive-cache` + `git fetch --depth 1 origin drive-cache` hasta que exista `<slug>/_report.json`. Ábrela con `git worktree add /home/claude/cache FETCH_HEAD`.
- Si hay que repetir (Manu cambió la carpeta), borra `<slug>/` en `drive-cache` y vuelve a hacer push del job.

## 3. Elegir
- Haz hojas de contactos con `montage` (40 por hoja, 8 columnas) y míralas TODAS. Mapea posición → nombre con la lista ordenada.
- Portada: horizontal, la más reconocible del lugar (aérea o plano general). Si hay un vídeo-loop corto en la carpeta, puede ir de portada.
- Selección: 8–12 fotos variadas (espacios, detalle, gente, comida/bebida, surf si hay). Evita casi-duplicados y repetir la misma escena. Mezcla horizontales y verticales.
- Copia a `<slug>/portada.jpg` y `<slug>/01.jpg…` (máx. 1600 px, `convert -strip -quality 78 -interlace Plane`).

## 4. Configurar y construir
- Crea `<slug>/config.json` siguiendo `pomelo/config.json` (mismos campos). Reglas:
  - Sin precios. Sin datos inventados: si no sabes una fecha o un dato, pregúntalo o déjalo fuera.
  - `photoTotal` = número de imágenes del manifest. `downloads.all` = link de la carpeta. `downloads.web` = link de una subcarpeta "web" si existe, si no `null`.
  - Vídeos del manifest → `videos: [{title, format: "16:9"|"9:16", length (opcional), drive: "https://drive.google.com/file/d/<ID>/view"}]`. El formato se deduce del nombre o se pregunta. Se reproducen dentro de la página.
  - `website`: Instagram (la web de Manu está caída).
  - Español de México para clientes mexicanos (tú / ustedes, nunca vosotros). Inglés si el cliente es angloparlante (`lang: "en"`).
  - Nota al cliente: 2–3 frases, concreta, sin clichés ni emojis.
- `python3 scripts/build.py <slug>` genera `<slug>/index.html`.
- Revisa una vez con Playwright (390 px y 1280 px, sin errores ni scroll horizontal).

## 5. Publicar y responder
- Commit + push a `main`. Netlify publica en ~1 min.
- Responde a Manu con: link, mensaje corto para el cliente (WhatsApp/email, en su idioma), checklist (permisos de Drive, datos, pagos pendientes) y lo que no cuadre con la cotización.

## Archivos
- `_plantilla.html` — plantilla base (objeto CONFIG). Cambios de diseño aquí y luego reconstruir las páginas.
- `scripts/build.py` — CONFIG desde config.json → index.html.
- `scripts/drive_fetch.py` + `.github/workflows/drive-fetch.yml` — descarga de miniaturas.
- `robots.txt` y `noindex` — las entregas no aparecen en Google.
- Legal: `privacidad/index.html` (aviso de privacidad ES/EN, LFPDPPP). La plantilla enlaza el aviso bajo el formulario y en el pie, pone © y una nota de derechos de autor/licencia en "Uso del material". Si la cotización trae condiciones de uso concretas, añádelas como un item más de `usage`.
- Feedback: cada página tiene un formulario opcional (Netlify Forms, nombre `feedback`, campos `cliente` y `mensaje`). Las respuestas llegan al panel de Netlify (Forms) y al email de Manu si tiene la notificación activada.
