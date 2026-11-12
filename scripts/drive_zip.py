#!/usr/bin/env python3
"""Empaqueta en un ZIP los originales de una carpeta pública de Drive.

Cada _zips/<slug>.json tiene: {"slug": "...", "folder": "<ID carpeta>", "name": "MUSA"}
Descarga todos los archivos (2 niveles de subcarpetas) en tamaño original y crea
out/<name>.zip (sin comprimir: JPG y vídeo ya lo están). Escribe out/release.env con
SLUG, ZIP, SIZE y COUNT para el paso de subida a la release.
Uso: python3 scripts/drive_zip.py _zips/<slug>.json out
"""
import json, re, sys, html, time, zipfile, pathlib, urllib.request, subprocess

AGENT = "Mozilla/5.0 (entregas-bot)"

def list_folder(fid, path="", depth=0):
    u = f"https://drive.google.com/embeddedfolderview?id={fid}"
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": AGENT}), timeout=60) as r:
        page = r.read().decode("utf-8", "replace")
    items = []
    for m in re.finditer(r'<div class="flip-entry" id="entry-([\w-]+)".*?<div class="flip-entry-title">(.*?)</div>', page, re.S):
        eid, name = m.group(1), html.unescape(m.group(2)).strip()
        block = page[m.start():m.end()]
        if "/drive/folders/" in block or "folders/" in block and "file/d/" not in block:
            if depth < 2:
                items += list_folder(eid, f"{path}{name}/", depth + 1)
            continue
        items.append({"id": eid, "name": name, "path": path})
    return items

def download(fid, dest):
    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
    for attempt in range(4):
        r = subprocess.run(["curl", "-sSL", "--fail", "-A", AGENT, "-o", str(dest), "-w", "%{content_type}", url],
                           capture_output=True, text=True)
        ctype = r.stdout.strip()
        if r.returncode == 0 and dest.exists() and dest.stat().st_size > 10000 and "text/html" not in ctype:
            return True
        print("  retry", dest.name, r.returncode, ctype, r.stderr[:200])
        time.sleep(5 * (attempt + 1))
    return False

job = json.loads(pathlib.Path(sys.argv[1]).read_text())
out = pathlib.Path(sys.argv[2]); work = out / "files"; work.mkdir(parents=True, exist_ok=True)
files = list_folder(job["folder"])
print("listed", len(files), "files")
fails = []
for f in files:
    d = work / f["path"]; d.mkdir(parents=True, exist_ok=True)
    print("get", f["path"] + f["name"], flush=True)
    if not download(f["id"], d / f["name"]):
        fails.append(f["path"] + f["name"])
if fails:
    sys.exit("FALLARON: " + ", ".join(fails))
name = job.get("name", job["slug"]).replace(" ", "-")
zpath = out / f"{name}.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
    for p in sorted(work.rglob("*")):
        if p.is_file():
            z.write(p, f"{name}/{p.relative_to(work)}")
size = zpath.stat().st_size
print("zip", zpath, size)
if size > 2_000_000_000:
    sys.exit("ZIP de más de 2 GB: GitHub no lo admite como archivo de release")
(out / "release.env").write_text(f"SLUG={job['slug']}\nZIP={zpath}\nSIZE={size}\nCOUNT={len(files)}\n")
