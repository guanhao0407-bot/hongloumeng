#!/usr/bin/env python3
"""Functional tests using synthetic EPUB content; no original text or network."""
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'epub_reader.py'
CONTAINER = '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>'
OPF = '''<package><metadata><title>虚构测试书</title></metadata><manifest>
<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
</manifest></package>'''
NCX = '''<ncx><navMap>
<navPoint><navLabel><text>第一回 虚构标题</text></navLabel><content src="text/one.html"/></navPoint>
<navPoint><navLabel><text>第十七回至十八回 虚构合回</text></navLabel><content src="text/merged.html"/></navPoint>
</navMap></ncx>'''
ONE = '''<html><body><p>虚构正文：海棠线索<sup>[1]</sup>清晰。</p>
<p class="note">虚构校注：海棠另有解释。</p>
<p>一个图像字<img src="x"/>在此。</p></body></html>'''
MERGED = '<html><body><p>合回虚构内容中的海棠。</p></body></html>'


class TestReader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='epub-reader-test-')
        tmp_path = Path(self.tmp.name).resolve()
        if tmp_path.parent != Path(tempfile.gettempdir()).resolve() or not tmp_path.name.startswith('epub-reader-test-'):
            raise RuntimeError('temporary test directory is outside the intended temporary root')
        self.path = Path(self.tmp.name) / 'fixture.epub'
        with zipfile.ZipFile(self.path, 'w') as z:
            for name, value in {'META-INF/container.xml': CONTAINER, 'content.opf': OPF,
                                'toc.ncx': NCX, 'text/one.html': ONE,
                                'text/merged.html': MERGED}.items():
                z.writestr(name, value)

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.path), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def test_inspect_merged_range_and_image(self):
        r = self.invoke('inspect')
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual((data['section_count'], data['chapter_count']), (2, 3))
        self.assertEqual(data['chapters'][1]['chapter_to'], 18)
        self.assertEqual(data['chapters'][0]['image_markers'], 1)

    def test_search_separates_notes_and_removes_sup(self):
        r = self.invoke('search', '--query', '海棠', '--scope', 'text', '--to-chapter', '1')
        data = json.loads(r.stdout)
        self.assertEqual(data['total_matching_paragraphs'], 1)
        self.assertNotIn('[1]', data['hits'][0]['excerpt'])
        r = self.invoke('search', '--query', '海棠', '--scope', 'note', '--to-chapter', '1')
        self.assertEqual(json.loads(r.stdout)['total_matching_paragraphs'], 1)

    def test_partial_merged_range_is_not_searched(self):
        r = self.invoke('search', '--query', '海棠', '--to-chapter', '17')
        data = json.loads(r.stdout)
        self.assertEqual(data['skipped_partial_sections'], [{'from': 17, 'to': 18}])
        self.assertTrue(all(hit['chapter_to'] <= 17 for hit in data['hits']))

    def test_merged_range_only_fails_closed(self):
        r = self.invoke('search', '--query', '海棠', '--from-chapter', '17', '--to-chapter', '17')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('合并章节', r.stderr)

    def test_missing_keyword_is_error(self):
        self.assertNotEqual(self.invoke('search').returncode, 0)


if __name__ == '__main__':
    unittest.main()
