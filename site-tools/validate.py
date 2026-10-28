from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]/'docs'
css=(root/'assets/style.css').read_text()
js=(root/'assets/app.js').read_text()
def inline(path):
 s=(root/path).read_text()
 s=s.replace('<link rel="stylesheet" href="./assets/style.css">','<style>'+css+'</style>')
 s=s.replace('<link rel="stylesheet" href="../assets/style.css">','<style>'+css+'</style>')
 s=s.replace('<link rel="stylesheet" href="../../assets/style.css">','<style>'+css+'</style>')
 for pre in ['./','../','../../']:
  s=s.replace(f'<script defer src="{pre}assets/app.js"></script>','<script>'+js+'</script>')
 return s
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(inline(Path('index.html')),wait_until='load')
 page.screenshot(path='/mnt/data/commons_site_home_preview.png',full_page=True)
 page.set_content(inline(Path('terms/index.html')),wait_until='load')
 assert page.locator('.term-item:visible').count()==35
 page.locator('#term-search').fill('trajectory')
 assert 1<=page.locator('.term-item:visible').count()<35
 page.locator('#term-search').fill('')
 page.locator('#vocab-filter').select_option('Working')
 assert 1<=page.locator('.term-item:visible').count()<35
 page.locator('#vocab-filter').select_option('')
 page.screenshot(path='/mnt/data/commons_site_glossary_preview.png')
 page.set_content(inline(Path('terms/chaperoning/index.html')),wait_until='load')
 page.screenshot(path='/mnt/data/commons_site_term_preview.png')
 mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
 mobile.set_content(inline(Path('index.html')),wait_until='load')
 assert mobile.locator('.nav-toggle').is_visible()
 mobile.locator('.nav-toggle').click();assert mobile.locator('#primary-nav').is_visible()
 mobile.screenshot(path='/mnt/data/commons_site_mobile_preview.png',full_page=True)
 print('Rendered desktop and mobile previews; search/filter/nav tests passed. JS errors:',errors)
 assert not errors
 browser.close()
