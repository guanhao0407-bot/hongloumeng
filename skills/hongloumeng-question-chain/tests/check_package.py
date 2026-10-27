#!/usr/bin/env python3
"""Check portable packaging and local Markdown references. No model is invoked."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parent.parent
required = [
    "SKILL.md", "README.md", "LICENSE",
    "references/student-questions.md", "references/question-links.md",
    "references/inquiry-dialogue.md", "references/feedback-revision.md",
    "references/question-record.md", "references/text-evidence.md",
    "references/research-and-data.md", "assets/student-feedback-template.csv",
    "scripts/epub_reader.py", "scripts/build_workbuddy.py", "examples/虚构输入与使用方式.md",
    "tests/行为评估.md", "tests/课堂材料评估摘要.md", "tests/test_epub_reader.py", "tests/test_workbuddy_package.py", "DESIGN.md",
]
errors = []
for path in required:
    if not (root / path).is_file():
        errors.append(f"missing: {path}")
manifest = root / "SKILL.md"
if manifest.is_file():
    content = manifest.read_text(encoding="utf-8")
    header = re.match(r"\A---\s*\n(.*?)\n---\s*\n", content, re.S)
    if not header:
        errors.append("invalid or missing front matter")
    else:
        lines = header.group(1).splitlines()
        pairs = {}
        for line in lines:
            if ": " not in line:
                errors.append(f"invalid front matter line: {line}")
                continue
            key, value = line.split(": ", 1)
            if key in pairs:
                errors.append(f"duplicate front matter key: {key}")
            pairs[key] = value.strip()
        allowed = {"name", "description", "display_name", "display_name_en",
                   "description_zh", "description_en", "version", "author"}
        if not {"name", "description"} <= set(pairs) or set(pairs) - allowed:
            errors.append("front matter must have name and description and known metadata only")
        name = pairs.get("name", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or name != root.name or len(name) > 64:
            errors.append("invalid skill name or folder mismatch")
        if not pairs.get("description") or len(pairs.get("description", "")) > 1024:
            errors.append("invalid description")
    if "[TODO:" in content:
        errors.append("unfinished skill instructions")
    for filename in ("student-questions.md", "question-links.md", "inquiry-dialogue.md", "feedback-revision.md", "question-record.md", "text-evidence.md", "research-and-data.md"):
        if f"references/{filename}" not in content:
            errors.append(f"reference not routed from SKILL.md: {filename}")

for p in root.rglob("*.md"):
    content = p.read_text(encoding="utf-8")
    for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", content):
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        path = (p.parent / target).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"link escapes project: {p.relative_to(root)} -> {target}")
            continue
        if not path.exists():
            errors.append(f"broken link: {p.relative_to(root)} -> {target}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print(f"Package check passed: {len(required)} required files and local Markdown links.")
print("This does not run the model or evaluate teaching outcomes.")
