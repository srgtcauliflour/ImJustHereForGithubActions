import asyncio, re, os, hashlib, zipfile
from urllib.parse import urlsplit, urlunsplit
from playwright.async_api import async_playwright

URL="https://pokecottage.com/sets/30th-anniversary-card-list"
OUT="cards"
os.makedirs(OUT, exist_ok=True)

def clean(u):
    if not u or not u.startswith("http"): return None
    p=urlsplit(u)
    return urlunsplit((p.scheme,p.netloc,p.path,"",""))

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        page=await browser.new_page(viewport={"width":1440,"height":1000})
        await page.goto(URL, wait_until="domcontentloaded", timeout=120000)
        for _ in range(80):
            await page.mouse.wheel(0,1400)
            await page.wait_for_timeout(250)
        await page.wait_for_timeout(2000)
        imgs=await page.locator("img").evaluate_all("""els => els.flatMap(i => [i.currentSrc,i.src,i.dataset.src,i.getAttribute('data-src')]).filter(Boolean)""")
        srcsets=await page.locator("img").evaluate_all("""els => els.flatMap(i => [i.srcset,i.getAttribute('data-srcset')]).filter(Boolean)""")
        for s in srcsets:
            imgs += [x.strip().split(" ")[0] for x in s.split(",") if x.strip()]
        urls=[]
        for u in imgs:
            u=clean(u)
            if u and ("squarespace-cdn.com" in u or "pokecottage.com" in u):
                urls.append(u)
        urls=list(dict.fromkeys(urls))
        seen=set(); n=0
        for u in urls:
            try:
                r=await page.request.get(u, timeout=60000)
                if not r.ok: continue
                ct=(r.headers.get("content-type") or "").lower()
                if "image" not in ct: continue
                b=await r.body()
                if len(b)<20000: continue
                h=hashlib.sha256(b).hexdigest()
                if h in seen: continue
                seen.add(h); n+=1
                ext=".jpg"
                if "png" in ct: ext=".png"
                elif "webp" in ct: ext=".webp"
                open(f"{OUT}/{n:03d}{ext}","wb").write(b)
            except Exception as e:
                print("skip",u,e)
        await browser.close()
        print(f"Downloaded {n} unique images")
    with zipfile.ZipFile("Pokemon-30th-Anniversary-Cards.zip","w",zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            z.write(os.path.join(OUT,f),f)
asyncio.run(main())
