"""Validate the public Pages artifact without contacting external services."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


ADS = b'google.com, pub-3081928577042149, DIRECT, f08c47fec0942fa0\n'
PRIVACY = 'https://kizwond.github.io/dotimoti-legal/dotidoit/privacy/'
CONTACT = 'mailto:eonseok.yoon@opensky.co.kr'
STORE = 'https://play.google.com/store/apps/details?id=com.doti.doit'


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.lang = ''
        self.title = ''
        self.in_title = False
        self.headings = 0
        self.meta = {}
        self.links = []
        self.ids = set()
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang', '')
        if tag == 'title':
            self.in_title = True
        if tag == 'h1':
            self.headings += 1
        if tag == 'meta':
            self.meta[attrs.get('name')] = attrs.get('content', '')
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key) is not None:
                self.links.append(attrs[key])

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, text):
        if self.in_title:
            self.title += text


def validate_site(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    if not root.is_dir():
        return [f'Site directory does not exist: {root}']
    for name in ('index.html', 'dotidoit/index.html', '404.html', 'assets/styles.css'):
        if not (root / name).is_file():
            errors.append(f'Missing required file: {name}')
    try:
        if (root / 'app-ads.txt').read_bytes() != ADS:
            errors.append('app-ads.txt must match the approved publisher line with final LF')
    except OSError:
        errors.append('Missing readable app-ads.txt')

    pages = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            errors.append(f'Pages artifact must not contain symlink: {path.relative_to(root)}')
            continue
        if path.suffix != '.html' or not path.is_file():
            continue
        name = str(path.relative_to(root))
        try:
            page = Page(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError) as error:
            errors.append(f'{name}: unreadable UTF-8 HTML ({type(error).__name__})')
            continue
        pages[path] = page
        if page.lang != 'ko':
            errors.append(f'{name}: document language must be ko')
        if not page.title.strip():
            errors.append(f'{name}: missing title')
        if page.headings != 1:
            errors.append(f'{name}: requires exactly one h1')
        if not page.meta.get('description', '').strip():
            errors.append(f'{name}: missing description')
        if 'width=device-width' not in page.meta.get('viewport', ''):
            errors.append(f'{name}: missing responsive viewport')
        required = (CONTACT, PRIVACY) if name == 'index.html' else ()
        if name == 'dotidoit/index.html':
            required = (CONTACT, PRIVACY, STORE)
        if name == '404.html':
            required = ('/',)
        for link in required:
            if link not in page.links:
                errors.append(f'{name}: missing required link {link}')

    for path, page in pages.items():
        for link in page.links:
            try:
                url = urlsplit(link)
            except ValueError:
                errors.append(f'{path.relative_to(root)}: invalid URL {link}')
                continue
            if url.scheme or url.netloc:
                if url.scheme not in ('https', 'mailto'):
                    errors.append(f'{path.relative_to(root)}: unsupported URL {link}')
                continue
            local_path = unquote(url.path)
            if local_path.startswith('/'):
                target = root / local_path.lstrip('/')
            elif local_path:
                target = path.parent / local_path
            else:
                target = path
            target = target.resolve()
            if not target.is_relative_to(root):
                errors.append(f'{path.relative_to(root)}: link outside site: {link}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{path.relative_to(root)}: broken link {link}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'{path.relative_to(root)}: broken fragment {link}')
    return errors


if __name__ == '__main__':
    problems = validate_site(Path(sys.argv[1] if len(sys.argv) > 1 else 'site'))
    if problems:
        print('\n'.join(problems), file=sys.stderr)
        sys.exit(1)
    print('Site validation passed.')
