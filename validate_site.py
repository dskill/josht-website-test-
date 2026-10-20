"""Validate every local URL and the absence of unsupported service widgets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--directory',default='dist');p.add_argument('--base-path',default='');a=p.parse_args()
root=Path(__file__).resolve().parent/a.directory;base='/'+a.base_path.strip('/')+'/' if a.base_path.strip('/') else '/';errors=[];count=0
class Parse(HTMLParser):
 def __init__(self,path):super().__init__();self.path=path
 def handle_starttag(self,tag,attrs):
  global count
  d=dict(attrs)
  if tag in ['form','input'] and self.path.name!='editor.html':errors.append((str(self.path),'Unexpected live form/input'))
  if tag=='script' and d.get('src','').startswith(('http','//')):errors.append((str(self.path),'Remote runtime script'))
  for attr in ['href','src','poster']:
   u=d.get(attr,'')
   if not u or u.startswith(('#','data:','mailto:','tel:')):continue
   parsed=urlsplit(u)
   if parsed.scheme or parsed.netloc:continue
   path=unquote(parsed.path)
   if path.startswith('/'):
    if not path.startswith(base):errors.append((str(self.path),'Wrong base path '+path));continue
    target=root/path[len(base):]
   else:target=self.path.parent/path
   if target.is_dir():target=target/'index.html'
   if not target.exists() and not target.with_suffix('.html').exists():errors.append((str(self.path),'Missing '+str(target)))
   count+=1
for f in root.rglob('*.html'):
 if f.name=='responsive-check.html':continue
 Parse(f).feed(f.read_text())
for f in root.rglob('*.css'):
 for u in re.findall(r'url\([\'\"]?([^\)\'\"]+)',f.read_text()):
  if not u.startswith('/'):continue
  if not u.startswith(base):errors.append((str(f),'Wrong CSS base '+u));continue
  target=root/urlsplit(u[len(base):]).path
  if not target.exists():errors.append((str(f),'Missing CSS asset '+str(target)))
c=json.loads((root/'content.json').read_text());assert c['schema']==2 and c['pages']['index'] and c['pages']['events']
for file,err in errors:print(file,err)
print('Validated',count,'local references;',len(errors),'errors; schema 2 content intact.')
raise SystemExit(bool(errors))
