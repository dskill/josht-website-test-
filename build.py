"""Reproduce the original public pages without Squarespace's service runtime.
Run with Python + lxml. Source wording and per-page grid markup are retained.
"""
from pathlib import Path
from lxml import html, etree
from urllib.parse import urlparse, urljoin, urlsplit, urlunsplit, parse_qs
import json,re,sys,copy
P=Path(__file__).parent; D=P/'dist'; S=P/'source-original'
style_map=json.loads((P/'reference/style-map.json').read_text())
image_map=json.loads((P/'reference/image-map.json').read_text())
if isinstance(image_map,list):raise RuntimeError('Image map must be a URL-to-local-path object')
def key(u):
 p=urlsplit(urljoin('https://www.joshtuininga.com/',u));return urlunsplit((p.scheme,p.netloc,p.path,'',''))
images={key(k):v for k,v in image_map.items()}
local_routes={'/','/projects','/about','/we-are-not-strangers','/whyblue','/dream-on','/events','/events-1','/sketchbook','/gallery','/totheriver','/press','/pressog','/classes-events','/contact'}
content={'schema':2,'pages':{}}
checks=[]
def inner(el):return (el.text or '')+''.join(etree.tostring(c,encoding='unicode',method='html') for c in el)
def mapurl(u):
 if u.startswith('//'):u='https:'+u
 if u in style_map:return style_map[u]
 if key(u) in images:return images[key(u)]
 return u
for file in sorted(S.glob('*.html')):
 slug='' if file.stem=='index' else file.stem
 
 root=html.fromstring(file.read_text())
 # Scripts on Squarespace implement remote services, analytics and hydration. None are retained.
 for el in root.xpath('//script|//noscript|//base|//link[@rel="preconnect"]|//link[@rel="dns-prefetch"]|//link[@rel="preload"]'):
  el.drop_tree()
 head=root.find('head'); body=root.find('body')
 root.set('class','js flexbox canvas canvastext no-touch history rgba hsla backgroundsize borderimage borderradius boxshadow opacity cssanimations csscolumns cssgradients csstransforms csstransitions svg inlinesvg svgclippaths')
 body.set('data-page-slug',slug or 'index')
 for el in root.iter():
  if not isinstance(el.tag,str):continue
  for attr in list(el.attrib):
   if attr.lower().startswith('on'):del el.attrib[attr]
  if el.tag=='img':
   src=el.get('src') or el.get('data-src') or el.get('data-image')
   if src:el.set('src',mapurl(src))
   el.attrib.pop('srcset',None)
   el.attrib.pop('data-loader',None)
   el.set('decoding','async')
  for a in ['src','href','data-src','data-image','poster']:
   if a in el.attrib:el.set(a,mapurl(el.get(a)))
  if el.tag=='style' and el.text:
   for u,v in style_map.items():el.text=el.text.replace(u,v)
  if el.tag=='a' and el.get('href'):
   href=el.get('href'); p=urlparse(urljoin('https://www.joshtuininga.com/',href))
   if p.netloc in ['www.joshtuininga.com','joshtuininga.com'] and not href.startswith('#'):
    path=p.path.rstrip('/') or '/'
    if path in local_routes and not p.query:el.set('href',path+('#'+p.fragment if p.fragment else ''))
    else:el.set('href','https://www.joshtuininga.com'+p.path+('?' + p.query if p.query else '')+('#'+p.fragment if p.fragment else ''))
   if el.get('target')=='_blank':el.set('rel','noopener noreferrer')
 # Original media embeds are static provider iframes, not the Squarespace controllers.
 for el in root.xpath('//*[@data-html]'):
  raw=el.get('data-html')
  if raw and '<iframe' in raw:
   try:
    frag=html.fragment_fromstring(raw,create_parent='div')
    frames=frag.xpath('.//iframe')
    if frames:
     for child in list(el):el.remove(child)
     el.text=None
     for frame in frames:
      frame.set('loading','lazy')
      src=frame.get('src','')
      if 'cdn.embedly.com/' in src:
       src=parse_qs(urlsplit(src).query).get('src',[src])[0]
       frame.set('src',src)
      el.append(frame)
     el.set('class',el.get('class','')+' static-embed')
   except Exception:pass
 # Preserve Contact's original prose, but replace the service placeholder with an explicit note.
 if slug=='contact':
  for block in root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," form-block ")]'):
   for child in list(block):block.remove(child)
   block.text=None
   note=etree.SubElement(block,'div',attrib={'class':'unsupported-feature-note','role':'note'})
   etree.SubElement(note,'strong').text='Contact form is not supported on this static site.'
   etree.SubElement(note,'p').text='The Squarespace form has been removed. A form service and confirmed delivery destination must be connected before messages can be submitted.'
 # Native signup is deliberately absent in the static version.
 for block in root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," newsletter-block ")]'):
  original_heading=block.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," newsletter-form-header ")]')
  original_heading=copy.deepcopy(original_heading[0]) if original_heading else None
  for child in list(block):block.remove(child)
  block.text=None
  if original_heading is not None:block.append(original_heading)
  note=etree.SubElement(block,'div',attrib={'class':'unsupported-feature-note','role':'note'})
  etree.SubElement(note,'strong').text='Newsletter signup is not supported on this static site.'
  etree.SubElement(note,'p').text='The Squarespace subscription widget has been removed. A mailing-list provider must be connected before visitors can subscribe.'
 # Legacy ICS downloads were a Squarespace service, not a static feature.
 ical_links=root.xpath('//a[contains(@href,"format=ical")]')
 for a in ical_links:
  a.tag='span';a.attrib.pop('href',None);a.attrib.pop('target',None);a.set('aria-disabled','true')
 if ical_links:
  main=root.xpath('//main')[0]
  note=etree.Element('div',attrib={'class':'unsupported-feature-note legacy-calendar-note','role':'note'})
  etree.SubElement(note,'strong').text='Calendar downloads are not supported on this static site.'
  etree.SubElement(note,'p').text='Squarespace iCalendar downloads are disabled. Event listings remain available; calendar files need a separate static replacement.'
  main.append(note)
 for el in root.xpath('//meta[@name="robots"]'):el.drop_tree()
 etree.SubElement(head,'meta',name='robots',content='noindex,nofollow')
 etree.SubElement(head,'link',rel='stylesheet',href='/static-runtime.css')
 script=etree.SubElement(body,'script',src='/app.js');script.set('defer','defer')
 # Editable source blocks use the exact original HTML; default pages contain complete fallback content.
 if slug in ['', 'events']:
  blocks=[]
  for i,el in enumerate(root.xpath('//main//*[contains(concat(" ",normalize-space(@class)," ")," sqs-html-content ")]')):
   bid=f'{slug or "index"}-{i}';el.set('data-content-block',bid)
   blocks.append({'id':bid,'label':' '.join(el.text_content().split())[:95], 'html':inner(el)})
  content['pages'][slug or 'index']=blocks
 target=D/('index.html' if not slug else slug+'/index.html');target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text('<!doctype html>\n'+etree.tostring(root,encoding='unicode',method='html'))
 checks.append({'route':'/'+slug,'source':file.name,'images':len(root.xpath('//img')),'textBlocks':len(root.xpath('//main//p|//main//h1|//main//h2|//main//h3'))})
# Source values intentionally retain original wording and date inconsistencies.
content_path=D/'content.json'
if content_path.exists() and '--refresh-original-content' not in sys.argv:
 try:
  saved=json.loads(content_path.read_text())
  if saved.get('schema')==2:
   for page,blocks in content['pages'].items():
    edits={b['id']:b for b in saved.get('pages',{}).get(page,[])}
    content['pages'][page]=[edits.get(b['id'],b) for b in blocks]
 except (ValueError,KeyError,TypeError):pass
content_path.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
(P/'reference/build-inventory.json').write_text(json.dumps(checks,indent=2))
print('Built',len(checks),'source-faithful pages;',sum(x['images'] for x in checks),'image placements. Contact and newsletter use clearly labeled unsupported-feature notes.')
