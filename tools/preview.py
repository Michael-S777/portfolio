"""Local preview of the GitHub Pages site (no Ruby/Jekyll needed).

Renders index.html with the data in _data/portfolio.yml (the template uses only simple Liquid that Jinja2 also
understands), copies the assets, and serves the result at http://127.0.0.1:4000/portfolio/ - the same address
layout as GitHub Pages.  Requires: pip install jinja2 pyyaml

    python tools/preview.py            # build + serve (Ctrl+C to stop)
    python tools/preview.py --build    # build only, into _preview/
"""
import functools
import http.server
import os
import shutil
import sys

import jinja2
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASEURL = '/portfolio'
OUT = os.path.join(ROOT, '_preview')


def build():
    with open(os.path.join(ROOT, '_data', 'portfolio.yml'), encoding='utf-8') as f:
        data = yaml.safe_load(f)
    with open(os.path.join(ROOT, 'index.html'), encoding='utf-8') as f:
        source = f.read()
    if source.startswith('---'):                       # strip Jekyll front matter
        source = source.split('---', 2)[2].lstrip('\n')
    env = jinja2.Environment(autoescape=False, undefined=jinja2.StrictUndefined)
    # like Jekyll: site paths get the base URL, full addresses (https://...) are left alone
    env.filters['relative_url'] = lambda path: path if '://' in path else BASEURL + path
    html = env.from_string(source).render(site={'data': {'portfolio': data}})
    target = os.path.join(OUT, BASEURL.strip('/'))
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(target, 'assets'))
    with open(os.path.join(target, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    return target


if __name__ == '__main__':
    path = build()
    print('Built', path)
    if '--build' not in sys.argv:
        class Handler(http.server.SimpleHTTPRequestHandler):
            # keep-alive connections: Python's simple server can cut larger files short on Windows otherwise
            protocol_version = 'HTTP/1.1'
        handler = functools.partial(Handler, directory=OUT)
        print(f'Preview: http://127.0.0.1:4000{BASEURL}/   (Ctrl+C to stop)')
        http.server.ThreadingHTTPServer(('127.0.0.1', 4000), handler).serve_forever()
