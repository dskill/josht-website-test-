"""Compile plain CMS fields into original markup without normalizing source formatting.

No network, third-party packages, credentials, or browser CMS runtime is needed.
Only the prepared output is changed; committed source and the original archive stay intact.
"""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re


def string(value, label, limit=100000):
    if value is None:
        return ''
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f'{label}: expected text of at most {limit} characters')
    return value


def link(value, label):
    value = string(value, label, 4000)
    parsed = urlsplit(value)
    if value and (any(ord(c) < 32 for c in value) or value.startswith('//') or
                  not (parsed.scheme in ('https', 'http', 'mailto', 'tel') or
                       (not parsed.scheme and value.startswith(('/', '#'))))):
        raise ValueError(f'{label}: use https://, mailto:, tel:, /path or #anchor')
    return value


def image_path(value, root, label, required=False):
    value = string(value, label, 1000)
    if not value and not required:
        return ''
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not value.startswith('/assets/'):
        raise ValueError(f'{label}: choose a local image under /assets/')
    path = (root / 'dist' / unquote(parsed.path).lstrip('/')).resolve()
    asset_root = (root / 'dist/assets').resolve()
    if not path.is_relative_to(asset_root) or not path.is_file():
        raise ValueError(f'{label}: image file does not exist in dist/assets')
    if path.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.webp') or path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError(f'{label}: use a JPG, PNG, GIF or WebP image smaller than 20 MiB')
    return value


def render_text(template, values, label):
    if not isinstance(values, dict):
        raise ValueError(f'{label}: missing text group')
    result = template['html']
    for slot in sorted(template['slots'], key=lambda x: x['start'], reverse=True):
        value = string(values.get(slot['key']), label)
        if slot['kind'] == 'link':
            value = link(value, label)
        # Preserve original entity spelling, spaces and every tag on a no-op save.
        if value != slot['original']:
            replacement = escape(value, quote=slot['kind'] == 'link')
            result = result[:slot['start']] + replacement + result[slot['end']:]
    return result


def render_event(event, root, label):
    if not isinstance(event, dict):
        raise ValueError(f'{label}: expected an event object')
    title = string(event.get('title'), label + '.title', 500)
    when = string(event.get('when'), label + '.when', 500)
    if not title.strip() or not when.strip():
        raise ValueError(f'{label}: event title and date/time text are required')
    lines = ['<strong>' + escape(title) + '</strong>']
    subtitle = string(event.get('subtitle'), label + '.subtitle', 500)
    if subtitle:
        lines.append('<strong>' + escape(subtitle) + '</strong>')
    lines.append(escape(when))
    details = string(event.get('details'), label + '.details', 10000)
    if details:
        lines.append(escape(details).replace('\n', '<br>'))
    url = link(event.get('url'), label + '.url')
    if url:
        caption = string(event.get('link_label'), label + '.link_label', 500)
        if not caption.strip():
            caption = url
        lines.append('<a href="' + escape(url, quote=True) + '">' + escape(caption) + '</a>')
    image = image_path(event.get('image'), root, label + '.image')
    if image:
        alt = string(event.get('image_alt'), label + '.image_alt', 1000)
        lines.append('<img src="' + escape(image, quote=True) + '" alt="' + escape(alt, quote=True) + '" loading="lazy" style="max-width:100%;height:auto">')
    return '<br>'.join(lines)


class BlockRanges(HTMLParser):
    """Locate marked div inner HTML without reserializing the rest of the page."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.offsets = [0]
        for m in re.finditer('\n', source):
            self.offsets.append(m.end())
        self.stack, self.ranges = [], {}
        self.feed(source)

    def position(self):
        row, column = self.getpos()
        return self.offsets[row - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            key = dict(attrs).get('data-content-block')
            self.stack.append((key, self.position() + len(self.get_starttag_text())))

    def handle_endtag(self, tag):
        if tag == 'div' and self.stack:
            key, start = self.stack.pop()
            if key:
                self.ranges[key] = (start, self.position())


def replace_blocks(source, blocks):
    ranges = BlockRanges(source).ranges
    edits = []
    for block in blocks:
        if block['id'] not in ranges:
            raise ValueError('Missing source content slot ' + block['id'])
        start, end = ranges[block['id']]
        edits.append((start, end, block['html']))
    for start, end, value in sorted(edits, reverse=True):
        source = source[:start] + value + source[end:]
    return source


def replace_image(source, old, current, root, label):
    src = image_path(current.get('image'), root, label, required=True)
    alt = string(current.get('alt'), label + '.alt', 1000)
    matches = 0
    def change(match):
        nonlocal matches
        tag = match.group()
        found = re.search(r'\ssrc="([^"]*)"', tag)
        if not found or unescape(found.group(1)) != old['src']:
            return tag
        matches += 1
        for attr in ('src', 'data-src', 'data-image'):
            tag = re.sub(r'(?<=\s)' + attr + r'="[^"]*"', lambda m: attr + '="' + escape(src, quote=True) + '"', tag)
        tag = re.sub(r'(?<=\s)alt="[^"]*"', lambda m: 'alt="' + escape(alt, quote=True) + '"', tag)
        # Never keep an old responsive source after choosing a replacement.
        if src != old['src']:
            tag = re.sub(r'\s(?:srcset|data-srcset)="[^"]*"', '', tag)
        return tag
    result = re.sub(r'<img\b[^>]*>', change, source)
    if matches != 1:
        raise ValueError(f'{label}: expected exactly one original image slot, got {matches}')
    return result


def compile_content(root):
    root = Path(root)
    read = lambda name: json.loads((root / name).read_text())
    data = read('dist/content.json')
    templates = read('cms/templates.json')
    # Pages CMS serializes a wholly empty optional object as an empty file.
    files = {name: json.loads((root / ('cms/' + name + '.json')).read_text().strip() or '{}')
             for name in ('homepage', 'presentations')}
    by_id = {b['id']: b for blocks in data['pages'].values() for b in blocks}
    for key, template in templates['blocks'].items():
        by_id[key]['html'] = render_text(template, files[template['file']].get(key, {}), key)
    events = read('cms/events.json')
    for key in ('upcoming', 'additional_past'):
        events[key] = events.get(key) or []
        if not isinstance(events[key], list) or len(events[key]) > 200:
            raise ValueError(key + ': expected up to 200 events')
    heading = string(events.get('upcoming_heading'), 'upcoming_heading', 500)
    if not heading.strip():
        raise ValueError('upcoming_heading is required')
    h3 = '<h3 style="text-align: center; white-space: pre-wrap" data-rte-preserve-empty="true">' + escape(heading) + '</h3>'
    p = '<p style="text-align: center; white-space: pre-wrap" data-rte-preserve-empty="true">'
    by_id['events-10']['html'] = h3 + p + '<br>__<br>'.join(render_event(e, root, 'upcoming') for e in events['upcoming']) + '</p>'
    if events['additional_past']:
        extra = p + '<br>__<br>'.join(render_event(e, root, 'additional_past') for e in events['additional_past']) + '</p>'
        archive = by_id['events-11']['html']
        end = archive.index('</h3>') + len('</h3>')
        by_id['events-11']['html'] = archive[:end] + extra + archive[end:]
    return data


def apply_cms(root, output):
    root, output = Path(root), Path(output)
    data = compile_content(root)
    templates = json.loads((root / 'cms/templates.json').read_text())
    images = json.loads((root / 'cms/images.json').read_text())
    for page, filename in [('index', 'index.html'), ('events', 'events/index.html')]:
        path = output / filename
        source = replace_blocks(path.read_text(), data['pages'][page])
        for key, template in templates['images'].items():
            if template['page'] == page:
                if not isinstance(images.get(key), dict):
                    raise ValueError('Missing image slot ' + key)
                source = replace_image(source, template, images[key], root, key)
        path.write_text(source)
    (output / 'content.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('Compiled CMS homepage, presentations, events and 7 image slots into static output.')
