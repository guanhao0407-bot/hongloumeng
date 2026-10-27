#!/usr/bin/env python3
"""Verify that the WorkBuddy variant retains the same skill instructions."""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts/build_workbuddy.py'


class TestWorkBuddyPackage(unittest.TestCase):
    def test_package_manifest_content_and_checker(self):
        with tempfile.TemporaryDirectory(prefix='workbuddy-package-test-') as directory:
            temp = Path(directory).resolve()
            self.assertEqual(temp.parent, Path(tempfile.gettempdir()).resolve())
            self.assertTrue(temp.name.startswith('workbuddy-package-test-'))
            output = temp / 'workbuddy.zip'
            result = subprocess.run([sys.executable, str(SCRIPT), '--output', str(output)],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as z:
                self.assertIsNone(z.testzip())
                names = z.namelist()
                self.assertIn(ROOT.name + '/SKILL.md', names)
                self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in names))
                bundled = z.read(ROOT.name + '/SKILL.md').decode('utf-8')
                for field in ('name:', 'display_name:', 'display_name_en:', 'description:',
                              'description_zh:', 'description_en:', 'version:', 'author:'):
                    self.assertIn(field, bundled)
                original_body = (ROOT / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[2]
                bundled_body = bundled.split('---', 2)[2]
                self.assertEqual(original_body.lstrip(), bundled_body.lstrip())
                self.assertEqual(z.read(ROOT.name + '/references/question-links.md'),
                                 (ROOT / 'references/question-links.md').read_bytes())
                z.extractall(temp / 'extracted')
            check = subprocess.run([sys.executable, str(temp / 'extracted' / ROOT.name /
                                    'tests/check_package.py')], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_output_inside_skill_directory_is_rejected(self):
        output = ROOT / 'test-should-not-exist.zip'
        self.assertFalse(output.exists())
        result = subprocess.run([sys.executable, str(SCRIPT), '--output', str(output)],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
