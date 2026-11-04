#!/usr/bin/env python3
"""Construye <slug>/index.html a partir de _plantilla.html y <slug>/config.json.
Uso: python3 scripts/build.py <slug>
"""
import json, sys, pathlib
slug = sys.argv[1]
root = pathlib.Path(__file__).resolve().parent.parent
tpl = (root / "_plantilla.html").read_text()
cfg = json.loads((root / slug / "config.json").read_text())
start = tpl.index("const CONFIG = {")
end = tpl.index("\n};\n", start) + 4
page = tpl[:start] + "const CONFIG = " + json.dumps(cfg, ensure_ascii=False, indent=2) + ";\n" + tpl[end:]
title = f"{cfg['client']} · Entrega · Manu Galdámez"
i = page.index("<title>"); j = page.index("</title>")
page = page[:i] + "<title>" + title + page[j:]
(root / slug / "index.html").write_text(page)
print("ok", slug)
