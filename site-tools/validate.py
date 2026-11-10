"""Exercise the published site over HTTP, including relative URLs and scripts."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
from threading import Thread
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--screenshots', type=Path, help='Optional screenshot output directory')
parser.add_argument('--chromium', default=shutil.which('chromium'), help='System Chromium path; otherwise use Playwright Chromium')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / 'docs'

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

with tempfile.TemporaryDirectory(prefix='commons-previews-') as temporary:
    output = args.screenshots or Path(temporary)
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(root)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            options = {'headless': True, 'args': ['--no-sandbox']}
            if args.chromium:
                options['executable_path'] = args.chromium
            browser = p.chromium.launch(**options)
            errors = []
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            page.on('pageerror', lambda error: errors.append(str(error)))
            def visit(target, path):
                response = target.goto(origin + path, wait_until='networkidle')
                assert response and response.ok, path
            visit(page, '/')
            page.screenshot(path=str(output/'home.png'), full_page=True)
            visit(page, '/terms/')
            items = page.locator('.term-item:visible')
            expect(items).to_have_count(35)
            page.locator('#term-search').fill('trajectory')
            expect(items).to_have_count(5)
            page.locator('#term-search').fill('')
            page.locator('#vocab-filter').select_option('Working')
            expect(items).to_have_count(10)
            page.locator('#vocab-filter').select_option('')
            expect(items).to_have_count(35)
            page.screenshot(path=str(output/'glossary.png'))
            visit(page, '/terms/chaperoning/')
            page.screenshot(path=str(output/'term.png'))
            mobile = browser.new_page(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
            mobile.on('pageerror', lambda error: errors.append(str(error)))
            visit(mobile, '/')
            expect(mobile.locator('.nav-toggle')).to_be_visible()
            mobile.locator('.nav-toggle').click()
            expect(mobile.locator('#primary-nav')).to_be_visible()
            expect(mobile.locator('.nav-toggle')).to_have_attribute('aria-expanded', 'true')
            mobile.screenshot(path=str(output/'mobile.png'), full_page=True)
            assert not errors, errors
            browser.close()
            print('PASS: HTTP rendering, search, filters, mobile navigation; no JavaScript errors.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
