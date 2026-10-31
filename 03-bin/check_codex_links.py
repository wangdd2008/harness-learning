# -*- coding: utf-8 -*-
"""校验 02-docs/codex-cli-docs 下导航类 md 的相对链接是否有效。
排除 source/（原文存档按原样保留站内链接，属刻意设计）。"""
import os
import re
import sys

ROOT = r"C:\Users\Administrator\Documents\Src\harness-learning\02-docs\codex-cli-docs"
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

missing = []
checked = 0
skipped_src = 0
for dirpath, _dirs, files in os.walk(ROOT):
    if os.path.basename(dirpath) == "source":
        skipped_src += len([f for f in files if f.endswith(".md")])
        continue
    for fn in files:
        if not fn.endswith(".md"):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # 去掉锚点
            rel = target.split("#", 1)[0].strip()
            if not rel:
                continue
            checked += 1
            resolved = os.path.normpath(os.path.join(dirpath, rel))
            if not os.path.exists(resolved):
                missing.append((path, target, resolved))

print("checked=%d  skipped_source_archives=%d  missing=%d" % (checked, skipped_src, len(missing)))
for p, t, r in missing:
    print("- %s\n    link: %s\n    resolve: %s" % (p, t, r))
sys.exit(1 if missing else 0)

