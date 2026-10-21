"""Prepare committed static files for any GitHub Pages base path. No content regeneration."""
from pathlib import Path
import argparse,re,shutil,json
from cms_content import apply_cms
p=argparse.ArgumentParser();p.add_argument('--base-path',default='');p.add_argument('--output',default='_site');a=p.parse_args()
root=Path(__file__).resolve().parent; source=root/'dist'; output=root/a.output
base='/'+a.base_path.strip('/')+'/' if a.base_path.strip('/') else '/'
if output.exists():shutil.rmtree(output)
shutil.copytree(source,output,ignore=shutil.ignore_patterns('responsive-check.html','source.zip'))
apply_cms(root, output)
def prefix_url(m):
 lead,path=m.group(1),m.group(2)
 return lead+(base+path.lstrip('/') if base!='/' else path)
for f in output.rglob('*'):
 if not f.is_file():continue
 if f.suffix in ['.html','.css']:
  s=f.read_text()
  # Remove the original hidden Squarespace cart endpoint and keep mobile folders local.
  s=s.replace('href="https://www.joshtuininga.com/cart"','aria-disabled="true" title="Shopping cart is not supported on this static site."')
  s=s.replace('href="https://www.joshtuininga.com/projects-1"','href="#books"')
  s=s.replace('https:/assets/original/','/assets/original/')
  s=re.sub(r'((?:href|src|poster)=["\'])(/(?!/)[^"\']*)',prefix_url,s)
  s=re.sub(r'(url\(["\']?)(/(?!/)[^\)"\']*)',prefix_url,s)
  f.write_text(s)
(output/'.nojekyll').touch()
print('Prepared GitHub Pages assets at',output,'with base path',base)
