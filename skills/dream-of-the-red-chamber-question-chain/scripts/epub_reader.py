#!/usr/bin/env python3
"""Read a user-supplied, chapter-per-file EPUB locally; never modify the source."""
import argparse
import hashlib
import json
import posixpath
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

LIMIT = 32 * 1024 * 1024


def local(tag):
    return tag.rsplit('}', 1)[-1]


def read(z, name):
    info = z.getinfo(name)
    if info.file_size > LIMIT:
        raise ValueError('EPUB member exceeds size limit: ' + name)
    return z.read(info)


def chinese_number(value):
    digits = {'零': 0, '〇': 0, '○': 0, '一': 1, '二': 2, '三': 3, '四': 4,
              '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    if value.isdigit():
        return int(value)
    if all(c in digits for c in value):
        return int(''.join(str(digits[c]) for c in value))
    total = current = 0
    for c in value:
        if c in digits:
            current = digits[c]
        elif c == '十':
            total += (current or 1) * 10
            current = 0
        elif c == '百':
            total += (current or 1) * 100
            current = 0
        else:
            raise ValueError('unrecognized chapter number: ' + value)
    return total + current


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.parts = [], None
        self.kind, self.skip = None, 0
        self.image_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'p' and self.parts is None:
            self.parts = []
            self.kind = 'note' if 'note' in attrs.get('class', '').split() else 'text'
        elif self.parts is not None and tag == 'sup':
            self.skip += 1
        elif self.parts is not None and tag == 'img':
            self.parts.append('〔图像内容或字形待核〕')
            self.image_count += 1

    def handle_endtag(self, tag):
        if tag == 'sup' and self.skip:
            self.skip -= 1
        elif tag == 'p' and self.parts is not None:
            value = re.sub(r'\s+', ' ', ''.join(self.parts)).strip()
            if value:
                self.rows.append((self.kind, value))
            self.parts, self.kind, self.skip = None, None, 0

    def handle_data(self, data):
        if self.parts is not None and not self.skip:
            self.parts.append(data)


def parse(z, filename):
    parser = Paragraphs()
    parser.feed(read(z, filename).decode('utf-8-sig'))
    return parser


def catalog(z):
    container = ET.fromstring(read(z, 'META-INF/container.xml'))
    opf = next(e.attrib['full-path'] for e in container.iter()
               if local(e.tag) == 'rootfile' and 'full-path' in e.attrib)
    package = ET.fromstring(read(z, opf))
    manifest = {e.attrib.get('id'): e.attrib for e in package.iter() if local(e.tag) == 'item'}
    ncx = next((v for v in manifest.values()
                if v.get('media-type') == 'application/x-dtbncx+xml'), None)
    if ncx is None:
        raise ValueError('需要带 NCX 目录且每回独立文件的 EPUB；此 EPUB 格式暂不支持。')
    ncx_path = posixpath.normpath(posixpath.join(posixpath.dirname(opf), unquote(ncx['href'])))
    ncx_root = ET.fromstring(read(z, ncx_path))
    chapters = {}
    for point in ncx_root.iter():
        if local(point.tag) != 'navPoint':
            continue
        label = next((x for x in point if local(x.tag) == 'navLabel'), None)
        target = next((x for x in point if local(x.tag) == 'content'), None)
        title = ''.join(label.itertext()).strip() if label is not None else ''
        match = re.match(r'^第([零〇○一二三四五六七八九十百0-9]+)回(?:至第?([零〇○一二三四五六七八九十百0-9]+)回)?', title)
        if not match or target is None:
            continue
        number = chinese_number(match.group(1))
        end = chinese_number(match.group(2)) if match.group(2) else number
        if end < number or end - number > 10:
            raise ValueError('invalid chapter range: ' + title)
        src = unquote(target.attrib.get('src', '')).split('#', 1)[0]
        name = posixpath.normpath(posixpath.join(posixpath.dirname(ncx_path), src))
        if any(not (end < item['number'] or number > item['end']) for item in chapters.values()):
            raise ValueError('overlapping chapter range: ' + str(number))
        chapters[number] = {'number': number, 'end': end, 'title': title, 'file': name}
    if not chapters or len({c['file'] for c in chapters.values()}) != len(chapters):
        raise ValueError('未找到独立的逐回目录；此 EPUB 格式暂不支持。')
    if any(c['file'] not in z.namelist() for c in chapters.values()):
        raise ValueError('目录中的章节文件缺失。')
    metadata = {}
    for node in package.iter():
        key = local(node.tag)
        if key in ('title', 'creator', 'publisher', 'date', 'language') and node.text:
            metadata.setdefault(key, []).append(node.text.strip())
    return metadata, chapters


def run():
    p = argparse.ArgumentParser(description='本地查阅用户提供的 EPUB，支持本项目验证过的逐回 NCX 格式。')
    p.add_argument('epub', type=Path)
    p.add_argument('command', choices=['inspect', 'search'])
    p.add_argument('--query', help='search 的精确关键词，不做语义检索')
    p.add_argument('--from-chapter', type=int, default=1)
    p.add_argument('--to-chapter', type=int, default=None, help='限制阅读进度，避免展示超出范围的结果')
    p.add_argument('--scope', choices=['text', 'note'], default='text')
    p.add_argument('--limit', type=int, default=12)
    args = p.parse_args()
    if args.command == 'search' and not args.query:
        p.error('search 需要 --query')
    if args.query and len(args.query) > 80:
        p.error('关键词不能超过80个字符')
    if not 1 <= args.limit <= 100 or args.from_chapter < 1:
        p.error('limit 应为 1—100，from-chapter 应大于零')
    if args.to_chapter is not None and args.to_chapter < args.from_chapter:
        p.error('to-chapter 不能小于 from-chapter')
    digest = hashlib.sha256(args.epub.read_bytes()).hexdigest()
    with zipfile.ZipFile(args.epub) as z:
        meta, chapters = catalog(z)
        upper = args.to_chapter if args.to_chapter is not None else max(c['end'] for c in chapters.values())
        overlaps = [c for _, c in sorted(chapters.items())
                    if c['end'] >= args.from_chapter and c['number'] <= upper]
        selected = [c for c in overlaps if c['number'] >= args.from_chapter and c['end'] <= upper]
        skipped = [{'from': c['number'], 'to': c['end']} for c in overlaps if c not in selected]
        if not selected:
            raise ValueError('指定范围无法安全包含完整目录项；合并章节请扩大范围后重试。')
        if args.command == 'inspect':
            coverage = []
            for ch in selected:
                parsed = parse(z, ch['file'])
                counts = {'text': 0, 'note': 0}
                for kind, value in parsed.rows:
                    counts[kind] += len(value)
                coverage.append({'chapter_from': ch['number'], 'chapter_to': ch['end'], 'body_characters': counts['text'],
                                 'note_characters': counts['note'], 'image_markers': parsed.image_count})
            print(json.dumps({'metadata': meta, 'sha256': digest, 'section_count': len(chapters),
                              'chapter_count': sum(c['end'] - c['number'] + 1 for c in chapters.values()),
                              'skipped_partial_sections': skipped, 'chapters': coverage}, ensure_ascii=False, indent=2))
        else:
            hits, total = [], 0
            for ch in selected:
                parsed = parse(z, ch['file'])
                ordinal = {'text': 0, 'note': 0}
                for kind, value in parsed.rows:
                    ordinal[kind] += 1
                    idx = value.find(args.query) if kind == args.scope else -1
                    if idx < 0:
                        continue
                    total += 1
                    if len(hits) < args.limit:
                        excerpt = value[max(0, idx-45):min(len(value), idx+len(args.query)+45)]
                        hits.append({'chapter_from': ch['number'], 'chapter_to': ch['end'], 'scope': kind, 'paragraph': ordinal[kind],
                                     'excerpt': excerpt, 'file': ch['file']})
            print(json.dumps({'sha256': digest, 'query': args.query, 'scope': args.scope,
                              'total_matching_paragraphs': total, 'hits': hits, 'skipped_partial_sections': skipped,
                              'notice': '段落号为脚本定位号而非书中页码；请回 EPUB 核对正文与校注。'},
                             ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        run()
    except (OSError, KeyError, ValueError, UnicodeError, StopIteration, ET.ParseError, zipfile.BadZipFile) as exc:
        print('无法读取：' + str(exc), file=sys.stderr)
        sys.exit(2)
