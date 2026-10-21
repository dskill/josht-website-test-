"""CMS build contracts. Fixtures are temporary; no sample edit is ever published."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch
import copy, json, shutil, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cms_content import compile_content, render_text, render_event, replace_blocks, replace_image, image_path
ROOT = Path(__file__).resolve().parents[1]

class CmsTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT/'cms', self.root/'cms')
        (self.root/'dist/assets/uploads').mkdir(parents=True)
        shutil.copy(ROOT/'dist/content.json', self.root/'dist/content.json')
        self.baseline = json.loads((ROOT/'dist/content.json').read_text())
        templates = json.loads((ROOT/'cms/templates.json').read_text())
        # Tests use immutable seed fixtures, not the author's current edits.
        for name in ['homepage', 'presentations']:
            fields = {key: {slot['key']: slot['original'] for slot in t['slots']}
                      for key, t in templates['blocks'].items() if t['file'] == name}
            (self.root/'cms'/(name+'.json')).write_text(json.dumps(fields))
        (self.root/'cms/events.json').write_text(json.dumps(templates['event_defaults']))

    def tearDown(self): self.tmp.cleanup()

    def edit(self, name, mutate):
        path = self.root/'cms'/name
        data = json.loads(path.read_text()); mutate(data)
        path.write_text(json.dumps(data))

    def test_noop_is_exact(self):
        self.assertEqual(compile_content(self.root), self.baseline)
        for page,path in [('index','index.html'),('events','events/index.html')]:
            original = (ROOT/'dist'/path).read_text()
            self.assertEqual(replace_blocks(original, compile_content(self.root)['pages'][page]), original)

    def test_homepage_plain_text_is_escaped_and_formatting_retained(self):
        self.edit('homepage.json', lambda d: d['index-0'].update(text_01='Test <script>alert(1)</script> & title'))
        content = compile_content(self.root)
        b = content['pages']['index'][0]['html']
        self.assertIn('Test &lt;script&gt;alert(1)&lt;/script&gt; &amp; title', b)
        self.assertIn('sqsrte-text-color--white', b)
        self.assertNotIn('<script>', b)
        self.assertEqual(content['pages']['index'][1:], self.baseline['pages']['index'][1:])

    def test_create_reorder_remove_and_archive_events(self):
        fixture = {'title':'Isolated test event','when':'January 1, 2030, 2 PM UTC','subtitle':'Panel','details':'Line 1\nLine 2','url':'https://example.com/event','link_label':'Details'}
        self.edit('events.json', lambda d: (d['upcoming'].insert(0,fixture),d['additional_past'].append(d['upcoming'].pop())))
        content = compile_content(self.root)
        upcoming = content['pages']['events'][10]['html']; past = content['pages']['events'][11]['html']
        self.assertLess(upcoming.index('Isolated test event'), upcoming.index('Texas Library'))
        self.assertNotIn('Mill Creek', upcoming); self.assertIn('Mill Creek', past)
        self.assertIn('Line 1<br>Line 2', upcoming)
        self.assertIn('href="https://example.com/event"', upcoming)
        self.assertIn(self.baseline['pages']['events'][11]['html'].split('</h3>',1)[1],past)

    def test_cms_omitted_empty_fields_and_lists(self):
        self.edit('events.json', lambda d: (d.pop('upcoming'), d.pop('additional_past')))
        result = compile_content(self.root)
        self.assertNotIn('Texas Library',result['pages']['events'][10]['html'])
        self.assertEqual(result['pages']['events'][11],self.baseline['pages']['events'][11])
        self.edit('homepage.json', lambda d: d['index-0'].pop('text_01'))
        self.assertNotIn('Serious Damage',compile_content(self.root)['pages']['index'][0]['html'])

    def test_image_upload_replacement_and_alt(self):
        # Existing trusted image bytes stand in for an upload, in the isolated fixture only.
        asset = next((ROOT/'dist/assets/original').glob('*.png'))
        shutil.copy(asset,self.root/'dist/assets/uploads/test-image.png')
        new = '/assets/uploads/test-image.png'
        old = {'src':'/assets/original/example.jpg'}
        tag = '<img src="/assets/original/example.jpg" data-src="/assets/original/example.jpg" srcset="old.jpg 1x" alt="" width="100" height="200">'
        rendered = replace_image(tag,old,{'image':new,'alt':'Test & image'},self.root,'test')
        self.assertIn('src="'+new+'"',rendered); self.assertIn('alt="Test &amp; image"',rendered)
        self.assertNotIn('srcset=',rendered); self.assertIn('width="100"',rendered)
        event = render_event({'title':'Test','when':'2030','image':new,'image_alt':'Poster'},self.root,'test')
        self.assertIn('src="'+new+'"',event)

    def test_unsafe_or_missing_media_and_links_fail(self):
        for value in ['https://example.com/a.png','/assets/../../README.md','/assets/uploads/missing.png','javascript:alert(1)']:
            with self.assertRaises(ValueError): image_path(value,self.root,'test')
        self.edit('homepage.json',lambda d:d['index-2'].update(link_01='javascript:alert(1)'))
        with self.assertRaises(ValueError): compile_content(self.root)

    def test_invalid_event_fails_before_deploy(self):
        self.edit('events.json',lambda d:d['upcoming'].append({'title':'No date'}))
        with self.assertRaises(ValueError): compile_content(self.root)

    def test_fully_cleared_text_files_and_optional_link_caption(self):
        (self.root/'cms/homepage.json').write_text('')
        result = compile_content(self.root)
        self.assertNotIn('Serious Damage', result['pages']['index'][0]['html'])
        event = render_event({'title':'Test','when':'2030','url':'https://example.com'},self.root,'test')
        self.assertIn('>https://example.com</a>',event)

    def test_missing_original_slot_fails(self):
        with self.assertRaises(ValueError): replace_blocks('<div>wrong template</div>',self.baseline['pages']['index'])

if __name__ == '__main__': main()
