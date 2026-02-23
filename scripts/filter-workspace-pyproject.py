#!/usr/bin/env python3
"""Залишає в pyproject.toml лише вказані workspace-пакети (для Docker-збірки).
Використання: filter-workspace-pyproject.py <пакет> [пакет ...]
Наприклад: filter-workspace-pyproject.py ubot-queue ubot-bot
"""
import re
import sys
from pathlib import Path

WORKSPACE_PACKAGES = {"ubot-bot", "ubot-extract-from-pdf", "ubot-adapt", "ubot-queue"}
KEEP_PACKAGES = {"ubot-queue"} | set(sys.argv[1:])
if not KEEP_PACKAGES or KEEP_PACKAGES == {"ubot-queue"}:
    sys.exit("Вкажіть хоча б один пакет окрім ubot-queue")

path = Path("pyproject.toml")
if not path.exists():
    path = Path("/app/pyproject.toml")
text = path.read_text()

# members = ["packages/ubot-queue", "packages/ubot-bot", ...]
members = [f"packages/{p}" for p in sorted(KEEP_PACKAGES)]
new_members = 'members = ["' + '", "'.join(members) + '"]'
text = re.sub(r'^members = \[.*\]\s*$', new_members, text, flags=re.MULTILINE)

# У [project] dependencies прибрати workspace-пакети, яких немає в KEEP_PACKAGES
in_deps = False
deps_lines = []
for line in text.splitlines():
    if line.strip() == "dependencies = [":
        in_deps = True
        deps_lines.append(line)
        continue
    if in_deps:
        if line.strip() == "]":
            in_deps = False
        else:
            m = re.match(r'\s*"([^"]+)"', line)
            if m and m.group(1) in WORKSPACE_PACKAGES and m.group(1) not in KEEP_PACKAGES:
                continue
    deps_lines.append(line)
text = "\n".join(deps_lines) + "\n"

# У секції [tool.uv.sources] залишити лише рядки для KEEP_PACKAGES
in_sources = False
lines_out = []
for line in text.splitlines():
    if line.strip() == "[tool.uv.sources]":
        in_sources = True
        lines_out.append(line)
        continue
    if in_sources:
        if line.startswith("["):
            in_sources = False
        else:
            # рядок виду "ubot-bot = { workspace = true }"
            m = re.match(r"^([\w-]+)\s*=", line)
            if m and m.group(1) not in KEEP_PACKAGES:
                continue  # пропустити непотрібний пакет
    lines_out.append(line)

path.write_text("\n".join(lines_out) + "\n")
