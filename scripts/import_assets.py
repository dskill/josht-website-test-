"""One-time transfer of pinned public preview assets into this repository."""
from pathlib import Path
from urllib.request import urlopen, Request
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
HOSTS={'images.squarespace-cdn.com','file.squarespace-cdn.com','assets.squarespace.com','static1.squarespace.com','fonts.gstatic.com','use.typekit.net'}
from urllib.parse import urlsplit
items=json.loads((ROOT/'reference/import-assets.json').read_text())
def fetch(item):
 path=item['path'];url=item['url']
 if not path.startswith('dist/assets/original/') or '..' in Path(path).parts or urlsplit(url).scheme!='https' or urlsplit(url).hostname not in HOSTS:
  raise ValueError('Unexpected asset destination or source')
 target=ROOT/path
 for attempt in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=120) as r:data=r.read()
   if len(data)!=item['size'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Asset integrity mismatch: '+path)
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   return path
  except Exception:
   if attempt==2:raise
   time.sleep(2**attempt)
with ThreadPoolExecutor(max_workers=6) as pool:
 for path in pool.map(fetch,items):print('Verified',path,flush=True)
print('Imported',len(items),'verified assets.')
