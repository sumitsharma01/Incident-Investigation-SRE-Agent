import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
root=Path(__file__).resolve().parents[1]
base=root/'docs/case-studies/worker-capacity';out=base/'screenshots';out.mkdir(exist_ok=True)
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
  page=await b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto('http://127.0.0.1:8010/workspace');await page.wait_for_function("document.querySelectorAll('#incidents button').length > 0")
  await page.locator('#filter').fill('checkout-lab');await page.locator('#refresh').click()
  await page.wait_for_function("document.querySelectorAll('#incidents button').length > 0")
  incident=json.loads((base/'investigation.json').read_text())['incident_id']
  await page.evaluate('(id)=>open(id)',incident)
  await page.screenshot(path=str(out/'workspace-desktop.png'),full_page=True)
  await page.locator('#verification').screenshot(path=str(out/'recovery-verification.png'))
  followup=json.loads((base/'followup-investigation.json').read_text())['incident_id']
  await page.evaluate('(id)=>open(id)',followup)
  await page.locator('#detail').screenshot(path=str(out/'opensre-followup.png'))
  await page.set_viewport_size({'width':390,'height':844})
  await page.evaluate('(id)=>open(id)',incident)
  await page.locator('#observations').evaluate('(e)=>e.scrollIntoView({block:"start"})')
  await page.screenshot(path=str(out/'workspace-mobile.png'))
  assert not errors,errors
  print('Desktop, mobile, recovery and OpenSRE screenshots captured; no browser errors.')
  await b.close()
asyncio.run(main())
