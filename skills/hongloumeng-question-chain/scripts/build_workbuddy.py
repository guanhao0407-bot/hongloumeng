#!/usr/bin/env python3
"""Build a WorkBuddy-specific ZIP from the standard skill without changing it."""
import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = '''---
name: hongloumeng-question-chain
display_name: 红楼梦整本书阅读问题链建构
display_name_en: Dream of the Red Chamber Inquiry Chains
description: 为《红楼梦》整本书阅读教学整理学生疑问、建构或诊断问题链、设计递进追问，并依据阅读反馈调整问题。
description_zh: 围绕学生疑问、文本联系、递进追问和学习反馈辅助建构《红楼梦》阅读问题链。
description_en: Support inquiry chains for reading Dream of the Red Chamber using student questions, textual evidence, follow-up prompts, and feedback.
version: 1.0.0
author: Project contributors
---
'''


def main():
    parser = argparse.ArgumentParser(description='Create a WorkBuddy upload ZIP; no network is used.')
    parser.add_argument('--output', type=Path, required=True, help='Output ZIP path outside the skill directory')
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('output must be outside the skill directory')
    entry = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'\A---\s*\n.*?\n---\s*\n', entry, re.S)
    if not match or 'name: hongloumeng-question-chain' not in match.group():
        raise ValueError('Unexpected standard skill frontmatter')
    replacement = HEADER + entry[match.end():]
    files = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_symlink():
            raise ValueError('Refusing to include symbolic link: ' + str(path))
        if path.is_file() and '__pycache__' not in path.parts and '.git' not in path.parts:
            files.append(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in files:
            arcname = (Path(ROOT.name) / path.relative_to(ROOT)).as_posix()
            if path == ROOT / 'SKILL.md':
                z.writestr(arcname, replacement.encode('utf-8'))
            else:
                z.write(path, arcname)
    print(f'Created {output} with {len(files)} files.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
