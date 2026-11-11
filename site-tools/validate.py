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
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' and ('Content Security Policy' in message.text or 'Refused to' in message.text) else None)
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
            # The arrow and card padding open the term; nested evidence links stay independent.
            card = page.locator('.term-card').first
            term_url = card.locator('h2 a').get_attribute('href')
            arrow_box = card.locator('.card-row > span').bounding_box()
            card_box = card.bounding_box()
            card.click(position={'x': arrow_box['x'] - card_box['x'] + arrow_box['width']/2,
                                 'y': arrow_box['y'] - card_box['y'] + arrow_box['height']/2})
            expect(page).to_have_url(origin + '/terms/' + term_url)
            visit(page, '/terms/')
            card = page.locator('.term-card').first
            card.click(position={'x': 8, 'y': 8})
            expect(page).to_have_url(origin + '/terms/' + term_url)
            visit(page, '/terms/')
            evidence_link = page.locator('.term-card').first.locator('.card-reading-aid a')
            evidence_url = evidence_link.get_attribute('href')
            evidence_link.click()
            expect(page).to_have_url(origin + '/terms/' + evidence_url)
            visit(page, '/terms/')
            page.screenshot(path=str(output/'glossary.png'))
            visit(page, '/terms/chaperoning/')
            page.screenshot(path=str(output/'term.png'))
            mobile = browser.new_page(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
            mobile.on('pageerror', lambda error: errors.append(str(error)))
            mobile.on('console', lambda message: errors.append(message.text) if message.type == 'error' and ('Content Security Policy' in message.text or 'Refused to' in message.text) else None)
            visit(mobile, '/')
            expect(mobile.locator('.nav-toggle')).to_be_visible()
            mobile.locator('.nav-toggle').click()
            expect(mobile.locator('#primary-nav')).to_be_visible()
            expect(mobile.locator('.nav-toggle')).to_have_attribute('aria-expanded', 'true')
            mobile.screenshot(path=str(output/'mobile.png'), full_page=True)
            # Long pages keep section navigation reachable without returning to the top.
            for target in [page, mobile]:
                for path in ['/terms/', '/evidence/']:
                    visit(target, path)
                    target.evaluate("window.scrollTo({top:document.body.scrollHeight,behavior:'instant'})")
                    expect(target.locator('.site-header')).to_be_in_viewport()
                    assert abs(target.locator('.site-header').bounding_box()['y']) < 1
            mobile.locator('.nav-toggle').click()
            expect(mobile.locator('#primary-nav')).to_be_visible()
            mobile.keyboard.press('Escape')
            expect(mobile.locator('.nav-toggle')).to_have_attribute('aria-expanded', 'false')
            expect(mobile.locator('.nav-toggle')).to_be_focused()
            mobile.locator('.nav-toggle').click()
            mobile.locator('#primary-nav a').filter(has_text='Glossary').click()
            expect(mobile).to_have_url(origin + '/terms/')
            expect(mobile.locator('.nav-toggle')).to_have_attribute('aria-expanded', 'false')
            mobile.set_viewport_size({'width':320,'height':568})
            mobile.locator('.nav-toggle').click()
            assert mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            mobile.screenshot(path=str(output/'mobile-navigation.png'))
            # The expanded guide/discussions stay reachable under the delivered policy.
            for route, title in [('/considerations/', 'Considerations'), ('/method/', 'How to use the Commons')]:
                visit(page, route)
                expect(page.locator('h1')).to_have_text(title)
            expect(page.locator('#classification-guide')).to_be_visible()
            # Every delivered page declares the same policy; capture CSP console violations.
            from publication_security import CSP
            for html in root.rglob('*.html'):
                route='/' + html.relative_to(root).as_posix()
                visit(page, route)
                expect(page.locator('meta[http-equiv="Content-Security-Policy"]')).to_have_attribute('content', CSP)
                expect(page.locator('.site-header')).to_have_css('position', 'sticky')
                expect(page.locator('.site-header')).to_have_class(__import__('re').compile(r'\bnav-ready\b'))
            visit(page, '/evidence/')
            import json
            evidence=json.loads((root/'evidence/evidence.json').read_text())
            expect(page.locator('.evidence-card')).to_have_count(len(evidence['evidence']))
            page.locator('#search').fill('EVID-155')
            page.get_by_role('button', name='Search', exact=True).click()
            expect(page.locator('.evidence-card')).to_have_count(1)
            expect(page.locator('#EVID-155')).to_be_visible()
            page.locator('#select-visible').click()
            with page.expect_download() as pending:
                page.locator('#export-csv').click()
            assert pending.value.suggested_filename == 'Commons-evidence-selection.csv'
            # Failure behavior is tested separately from ordinary interactive navigation.
            for javascript in [False, True]:
                context=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=javascript)
                if javascript:
                    context.route('**/assets/app.js', lambda route: route.abort())
                fallback=context.new_page()
                visit(fallback, '/terms/')
                expect(fallback.locator('#primary-nav')).to_be_visible()
                expect(fallback.locator('.nav-toggle')).not_to_be_visible()
                fallback.locator('#primary-nav').get_by_role('link', name='Considerations', exact=True).click()
                expect(fallback.locator('h1')).to_have_text('Considerations')
                context.close()
            # A schema-valid source string must remain visible text, never executable markup.
            from publication_security import embed_dataset
            import copy
            fixture=copy.deepcopy(evidence)
            payload='</script><script>window.__publicationProbe=1</script>'
            fixture['evidence'][0]['title']=payload
            fixture_html=embed_dataset((root/'evidence/index.html').read_text(), fixture)
            context=browser.new_context()
            context.route('**/evidence/', lambda route: route.fulfill(status=200, content_type='text/html', body=fixture_html))
            probe=context.new_page();visit(probe,'/evidence/')
            expect(probe.locator('.evidence-card').first.locator('h2')).to_have_text(payload)
            expect(probe.locator('script:not([src]):not([type="application/json"]):not([type="application/ld+json"])')).to_have_count(0)
            assert probe.evaluate('window.__publicationProbe') is None
            context.close()
            # A missing stylesheet must fail a functional assertion even if hashes were refreshed.
            context=browser.new_context(viewport={'width':390,'height':844})
            context.route('**/assets/style.css', lambda route: route.abort())
            unstyled=context.new_page();visit(unstyled,'/terms/')
            assert unstyled.locator('.site-header').evaluate('(node) => getComputedStyle(node).position') != 'sticky'
            context.close()
            assert not errors, errors
            browser.close()
            print('PASS: HTTP rendering, search, filters, mobile navigation; no JavaScript errors.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
