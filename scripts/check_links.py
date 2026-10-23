"""Check source Markdown destinations and generated HTML links/anchors offline."""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git','site','dist','.venv','__pycache__'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids = [], set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href','src'):
            if key in attrs:
                self.links.append(attrs[key])


def main():
    errors, checked = [], 0
    for p in ROOT.rglob('*.md'):
        if EXCLUDE.intersection(p.relative_to(ROOT).parts):
            continue
        for href in re.findall(r'\]\(([^\s)]+)\)',p.read_text(encoding='utf-8')):
            u = urlsplit(href)
            if u.scheme or u.netloc or not u.path:
                continue
            checked += 1
            if not (p.parent/unquote(u.path)).exists():
                errors.append(f'{p.relative_to(ROOT)} -> {href}')
    pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in (ROOT/'site').rglob('*.html')}
    if not pages:
        errors.append('Build site before running link checks')
    for p,page in pages.items():
        for href in page.links:
            u = urlsplit(href)
            if u.scheme or u.netloc:
                continue
            checked += 1
            target = (p.parent/unquote(u.path)).resolve() if u.path else p
            if not target.exists():
                errors.append(f'{p.relative_to(ROOT)} -> {href}')
            elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
                errors.append(f'{p.relative_to(ROOT)} -> missing anchor {href}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Passed {checked} local link/asset checks; {len(pages)} HTML pages.')


if __name__ == '__main__':
    main()
