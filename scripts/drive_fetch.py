#!/usr/bin/env python3
"""Descarga miniaturas de archivos públicos de Google Drive para cada trabajo en _jobs/.

Cada _jobs/<slug>.json tiene: {"slug": "...", "files": [{"id": "...", "name": "..."}], "size": 1600}
Guarda las imágenes en out/<slug>/<name>.jpg. Si ya existe out/<slug>/, se salta.
"""
import json, os, re, sys, time, html, urllib.request, pathlib

out = pathlib.Path(sys.argv[1])
jobs = sorted(pathlib.Path("_jobs").glob("*.json"))
UA = {"User-Agent": "Mozilla/5.0 (entregas-bot)"}

def fetch(fid, size):
    urls = [f"https://drive.google.com/thumbnail?id={fid}&sz=w{size}",
            f"https://lh3.googleusercontent.com/d/{fid}=w{size}"]
    for u in urls:
        for attempt in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                    data = r.read()
                    if r.headers.get("Content-Type", "").startswith("image/") and len(data) > 2000:
                        return data
            except Exception as e:
                print("  retry", u, e)
            time.sleep(1.5 * (attempt + 1))
    return None

IMG = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".webp", ".dng", ".arw", ".cr3", ".nef")
VID = (".mp4", ".mov", ".m4v", ".avi", ".mxf")

def list_folder(fid, path="", depth=0):
    """Lista una carpeta pública de Drive sin API key (vista embebida)."""
    u = f"https://drive.google.com/embeddedfolderview?id={fid}"
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
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

changed = False
for jf in jobs:
    job = json.loads(jf.read_text())
    dest = out / job["slug"]
    if dest.exists():
        print("skip", job["slug"]); continue
    dest.mkdir(parents=True)
    size = job.get("size", 1600)
    if job.get("folder"):
        allf = list_folder(job["folder"])
        job["files"] = [f for f in allf if f["name"].lower().endswith(IMG)]
        videos = [f for f in allf if f["name"].lower().endswith(VID)]
        others = [f for f in allf if f not in job["files"] and f not in videos]
        (dest / "_manifest.json").write_text(json.dumps({"images": job["files"], "videos": videos, "others": others}, ensure_ascii=False, indent=1))
        print("listed", len(job["files"]), "images,", len(videos), "videos,", len(others), "others")
    ok = fail = 0
    for f in job["files"]:
        data = fetch(f["id"], size)
        name = (f.get("path", "").replace("/", "__")) + os.path.splitext(f["name"])[0] + ".jpg"
        if data:
            (dest / name).write_bytes(data); ok += 1
        else:
            fail += 1; print("FAIL", f["name"])
    (dest / "_report.json").write_text(json.dumps({"ok": ok, "fail": fail}))
    print(job["slug"], "ok", ok, "fail", fail)
    changed = True
print("changed" if changed else "nothing")
