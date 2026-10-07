import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.validate_site import validate_site
except ModuleNotFoundError:
    validate_site = None


class SiteValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'site'
        self.root.mkdir()
        self.write('app-ads.txt', 'google.com, pub-3081928577042149, DIRECT, f08c47fec0942fa0\n')
        self.write('assets/styles.css', 'body { color: #123; }')
        self.html = '''<!doctype html><html lang="ko"><head><title>도티 안내</title>
        <meta name="description" content="오픈스카이 앱 안내">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/assets/styles.css"></head><body>
        <main id="main"><h1>도티두잇</h1>
        <a href="/">홈</a><a href="/dotidoit/">도티두잇</a>
        <a href="https://play.google.com/store/apps/details?id=com.doti.doit">다운로드</a>
        <a href="https://kizwond.github.io/dotimoti-legal/dotidoit/privacy/">개인정보처리방침</a>
        <a href="mailto:eonseok.yoon@opensky.co.kr">문의</a></main></body></html>'''
        for name in ('index.html', 'dotidoit/index.html', '404.html'):
            self.write(name, self.html)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def validate(self):
        self.assertIsNotNone(validate_site, 'site validator is not implemented')
        return validate_site(self.root)

    def test_valid_fixture(self):
        self.assertEqual([], self.validate())

    def test_wrong_publisher(self):
        self.write('app-ads.txt', 'google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n')
        self.assertTrue(any('app-ads.txt' in error for error in self.validate()))

    def test_missing_final_newline(self):
        self.write('app-ads.txt', 'google.com, pub-3081928577042149, DIRECT, f08c47fec0942fa0')
        self.assertTrue(self.validate())

    def test_html_in_ads_file(self):
        self.write('app-ads.txt', '<html>google.com, pub-3081928577042149, DIRECT, f08c47fec0942fa0</html>')
        self.assertTrue(self.validate())

    def test_missing_required_page(self):
        (self.root / 'dotidoit/index.html').unlink()
        self.assertTrue(any('dotidoit/index.html' in error for error in self.validate()))

    def test_broken_nested_link(self):
        self.write('dotidoit/index.html', self.html.replace('/assets/styles.css', 'assets/styles.css'))
        self.assertTrue(any('assets/styles.css' in error for error in self.validate()))

    def test_valid_relative_link(self):
        self.write('dotidoit/index.html', self.html.replace('/assets/styles.css', '../assets/styles.css'))
        self.assertEqual([], self.validate())

    def test_link_outside_site(self):
        (self.root.parent / 'secret.txt').write_text('private', encoding='utf-8')
        self.write('index.html', self.html.replace('href="/"', 'href="/%2e%2e/secret.txt"'))
        self.assertTrue(any('outside' in error for error in self.validate()))

    def test_symlink_not_packaged(self):
        (self.root.parent / 'secret.txt').write_text('private', encoding='utf-8')
        (self.root / 'leak.txt').symlink_to(self.root.parent / 'secret.txt')
        self.assertTrue(any('symlink' in error for error in self.validate()))

    def test_missing_title_or_metadata(self):
        for old in ('<title>도티 안내</title>', '<meta name="description" content="오픈스카이 앱 안내">',
                    '<meta name="viewport" content="width=device-width, initial-scale=1">', 'lang="ko"', '<h1>도티두잇</h1>'):
            with self.subTest(old=old):
                self.write('index.html', self.html.replace(old, ''))
                self.assertTrue(self.validate())

    def test_missing_support_or_store_link(self):
        for old in ('mailto:eonseok.yoon@opensky.co.kr',
                    'https://play.google.com/store/apps/details?id=com.doti.doit',
                    'https://kizwond.github.io/dotimoti-legal/dotidoit/privacy/'):
            with self.subTest(old=old):
                self.write('dotidoit/index.html', self.html.replace(old, 'https://example.com/'))
                self.assertTrue(self.validate())

    def test_invalid_utf8(self):
        (self.root / 'index.html').write_bytes(b'\xff')
        self.assertTrue(self.validate())

    def test_broken_fragment(self):
        self.write('dotidoit/index.html', self.html.replace('href="/"', 'href="/#missing"'))
        self.assertTrue(any('fragment' in error for error in self.validate()))

    def test_valid_fragment_and_query(self):
        self.write('dotidoit/index.html', self.html.replace('href="/"', 'href="/?from=app#main"'))
        self.assertEqual([], self.validate())

    def test_cli_exit_status(self):
        self.validate()
        command = [sys.executable, 'scripts/validate_site.py', str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.write('app-ads.txt', 'wrong')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn('app-ads.txt', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
