"""Builds the static site into the repo root.

Run from anywhere:  python3 _build/build.py
Edit outfits in outfits.py, the Amazon tag in config.json,
exact affiliate URLs in affiliate_links.json.
"""
import html as H
import json
import os
import shutil
from urllib.parse import quote_plus

from PIL import Image

from outfits import CATEGORIES, CHECKLIST_PIN, OUTFITS, PROFILE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CFG = json.load(open(os.path.join(HERE, "config.json")))
LINKS = json.load(open(os.path.join(HERE, "affiliate_links.json")))
PIN = "https://www.pinterest.com/pin/"
CAT = {c[0]: c for c in CATEGORIES}
SITE = "The Corporate Closet"
BY_PIN = {o["pin"]: o for o in OUTFITS}


def esc(s):
    return H.escape(s, quote=True)


def img_dims(pin):
    return Image.open(os.path.join(ROOT, "img", f"{pin}.jpg")).size


def product_url(slug, n, query):
    exact = LINKS.get(f"{slug}/{n}")
    if exact:
        return exact
    url = f"https://{CFG['amazon_domain']}/s?k={quote_plus(query)}"
    if CFG["amazon_tag"]:
        url += f"&tag={quote_plus(CFG['amazon_tag'])}"
    return url


CSS = """
:root{--cream:#F4EFE8;--sand:#EBE4DC;--line:#D9CEC2;--espresso:#2B1A10;--mocha:#6B5444;--card:#FBF8F4;--serif:"Cormorant Garamond",Georgia,serif}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{background:var(--cream);color:var(--espresso);font-family:"Jost",system-ui,sans-serif;font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--mocha)}
h1,h2,h3{font-family:var(--serif);font-weight:600;line-height:1.05}
h2{font-weight:500;font-style:italic;font-size:34px}
.lead{color:var(--mocha);font-size:17px}

.top{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 0}
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.brand img{width:48px;height:48px;border-radius:50%;border:1px solid var(--line);flex:none}
.brand b{font-family:var(--serif);font-size:21px;font-weight:600;line-height:1.05}
.nav{display:flex;align-items:center;gap:6px}
.nav a.link{padding:10px 12px;font-size:15px;color:var(--mocha);border-radius:999px}
.nav a.link:hover{color:var(--espresso)}
.nav .btn{display:none}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:48px;padding:12px 24px;border-radius:999px;border:1px solid var(--espresso);font-weight:500;letter-spacing:.02em;transition:background .2s,color .2s;cursor:pointer;font-family:inherit;font-size:16px}
.btn.solid{background:var(--espresso);color:var(--cream)}
.btn.solid:hover{background:#46301F}
.btn.ghost{background:transparent;color:var(--espresso)}
.btn.ghost:hover{background:var(--espresso);color:var(--cream)}
.btn.small{min-height:42px;padding:9px 18px;font-size:14px}

.hero{display:grid;gap:28px;padding:12px 0 8px}
.hero h1{font-size:44px;margin-top:10px}
.hero h1 em{font-weight:500}
.hero .lead{margin-top:16px;max-width:460px}
.cta{display:grid;gap:12px;margin-top:24px}
.stats{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:22px;font-size:14px;color:var(--mocha)}
.stats span::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:#8A6A4F;margin-right:8px;vertical-align:middle}
.mosaic{display:grid;grid-template-columns:1.15fr 1fr;grid-template-rows:1fr 1fr;gap:12px;height:340px}
.mosaic a{position:relative;overflow:hidden;border-radius:18px;background:var(--sand);display:block}
.mosaic a:first-child{grid-row:1/3}
.mosaic img{width:100%;height:100%;object-fit:cover;display:block}
.mosaic .cap{position:absolute;left:0;right:0;bottom:0;padding:40px 14px 12px;color:#FBF8F4;font-family:var(--serif);font-size:20px;line-height:1.1;font-weight:600;background:linear-gradient(to top,rgba(30,18,10,.75),rgba(30,18,10,0))}

.sec{margin-top:52px}
.sec-head{display:grid;gap:6px;margin-bottom:16px}
.sec-head p{color:var(--mocha)}
.cats{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.cat{position:relative;display:block;border-radius:18px;overflow:hidden;background:var(--sand);aspect-ratio:4/5}
.cat img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
.cat .over{position:absolute;inset:auto 0 0 0;padding:48px 14px 14px;color:#FBF8F4;background:linear-gradient(to top,rgba(30,18,10,.82),rgba(30,18,10,0))}
.cat strong{display:block;font-family:var(--serif);font-size:23px;line-height:1.05;font-weight:600}
.cat small{font-size:13px;opacity:.9}

.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.ph{position:relative}
.card img{width:100%;height:auto;aspect-ratio:2/3;object-fit:cover;display:block;background:var(--sand)}
.tag{position:absolute;bottom:8px;right:8px;padding:5px 12px;border-radius:999px;background:rgba(251,248,244,.95);font-size:12px;font-weight:500}
.card .t{display:block;padding:10px 12px 13px;font-size:14px;line-height:1.3}

.band{display:flex;align-items:center;gap:18px;padding:16px;background:var(--card);border:1px solid var(--line);border-radius:22px}
.band img{width:64px;height:84px;object-fit:cover;border-radius:12px;flex:none}
.band strong{display:block;margin-top:2px;font-family:var(--serif);font-size:21px;line-height:1.08;font-weight:600}
.band p.d{display:none;margin-top:4px;color:var(--mocha);font-size:15px}
.band .go{margin-left:auto;font-size:24px;color:var(--mocha)}

.why{display:grid;gap:12px}
.why div{padding:24px;background:var(--sand);border-radius:20px}
.why b{display:block;font-family:var(--serif);font-size:26px;line-height:1.1;font-weight:600}
.why p{margin-top:8px;color:var(--mocha);font-size:15px}

.closing{padding:44px 24px;text-align:center;background:var(--espresso);color:var(--cream);border-radius:26px}
.closing h2{color:var(--cream)}
.closing p{margin:10px auto 22px;max-width:420px;color:#D9CEC2}
.closing .btn{background:var(--cream);color:var(--espresso);border-color:var(--cream)}

/* page heads */
.crumbs{margin:6px 0 14px;font-size:14px;color:var(--mocha)}
.crumbs a:hover{color:var(--espresso);text-decoration:underline}
.pagehead h1{font-size:40px;margin-top:6px}
.pagehead .lead{margin-top:10px;max-width:560px}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.pill{padding:8px 16px;border:1px solid var(--line);border-radius:999px;font-size:14px}
.pill[aria-current="page"]{background:var(--espresso);border-color:var(--espresso);color:var(--cream)}

/* outfit page */
.outfit{display:grid;gap:24px}
.outfit .photo{border-radius:20px;overflow:hidden;background:var(--sand)}
.outfit .photo img{width:100%;height:auto;display:block}
.outfit h1{font-size:38px;margin-top:6px}
.outfit .lead{margin-top:12px}
.block{margin-top:26px}
.block h2{font-size:28px;margin-bottom:10px}
.tips{list-style:none;display:grid;gap:8px}
.tips li{padding-left:20px;position:relative;color:var(--mocha)}
.tips li::before{content:"";position:absolute;left:0;top:.7em;width:7px;height:7px;border-radius:50%;background:#8A6A4F}
.prods{display:grid;gap:10px}
.prod{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px 12px 18px;background:var(--card);border:1px solid var(--line);border-radius:16px}
.prod b{font-weight:500;line-height:1.3}
.prod .btn{flex:none}
.disc{margin-top:12px;font-size:13px;color:var(--mocha)}
.save{margin-top:18px}

footer{padding:36px 0 40px;margin-top:56px;border-top:1px solid var(--line);text-align:center;font-size:13px;color:var(--mocha)}
footer p+p{margin-top:6px}
footer a{text-decoration:underline}

.card:focus-visible,.cat:focus-visible,.mosaic a:focus-visible,.band:focus-visible,.btn:focus-visible,.pill:focus-visible,.nav a:focus-visible{outline:2px solid var(--mocha);outline-offset:3px}
@media(hover:hover){.card:hover img,.cat:hover img,.mosaic a:hover img{opacity:.92}}

@media(min-width:600px){
  .grid{grid-template-columns:repeat(3,1fr);gap:16px}
  .cats{grid-template-columns:repeat(4,1fr);gap:16px}
  .why{grid-template-columns:repeat(3,1fr)}
  .cta{grid-template-columns:auto auto;justify-content:start}
  .nav .btn{display:inline-flex}
  .mosaic{height:440px}
}
@media(min-width:900px){
  .wrap{padding:0 32px}
  .top{padding:22px 0}
  .brand img{width:56px;height:56px}
  .brand b{font-size:25px}
  .hero{grid-template-columns:1fr 1.05fr;align-items:center;gap:56px;padding:24px 0 8px}
  .hero h1{font-size:72px}
  .hero .lead{font-size:19px}
  .mosaic{height:600px;gap:16px}
  .mosaic .cap{font-size:24px;padding:56px 18px 16px}
  .sec{margin-top:80px}
  h2{font-size:46px}
  .grid{grid-template-columns:repeat(4,1fr);gap:20px}
  .card .t{font-size:15px;padding:12px 14px 15px}
  .cat strong{font-size:28px}
  .band{padding:22px 28px;gap:28px}
  .band img{width:110px;height:146px}
  .band strong{font-size:34px}
  .band p.d{display:block;font-size:17px}
  .why{gap:20px}
  .why div{padding:32px}
  .closing{padding:72px 32px}
  .pagehead h1{font-size:60px}
  .outfit{grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:56px;align-items:start}
  .outfit .photo{position:sticky;top:20px}
  .outfit h1{font-size:54px}
  .block h2{font-size:32px}
  footer{margin-top:80px}
}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&display=swap" rel="stylesheet">')

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases. Links on this site are affiliate links."


def page(depth, title, desc, body, path, og_pin=None):
    r = "../" * depth
    canonical = ""
    og_img = ""
    if CFG["site_url"]:
        base = CFG["site_url"].rstrip("/")
        canonical = f'<link rel="canonical" href="{base}/{path}">'
        pin = og_pin or "logo"
        og_img = f'<meta property="og:image" content="{base}/img/{pin}.jpg">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
{og_img}
{canonical}
<meta name="theme-color" content="#F4EFE8">
<link rel="icon" href="{r}img/logo.jpg">
{FONTS}
<link rel="stylesheet" href="{r}assets/style.css">
</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="{r}index.html"><img src="{r}img/logo.jpg" alt="" width="56" height="56"><b>{SITE}</b></a>
    <nav class="nav" aria-label="Main">
      <a class="link" href="{r}shop/index.html">Shop outfits</a>
      <a class="link" href="{PIN}{CHECKLIST_PIN}/" target="_blank" rel="noopener">Checklist</a>
      <a class="btn solid small" href="{PROFILE}" target="_blank" rel="noopener">Follow on Pinterest</a>
    </nav>
  </header>
{body}
  <footer>
    <p>{DISCLOSURE}</p>
    <p>&copy; {SITE}</p>
  </footer>
</div>
</body>
</html>
"""


def card(o, r):
    w, h = img_dims(o["pin"])
    return (f'<a class="card" href="{r}outfits/{o["slug"]}/index.html">'
            f'<div class="ph"><img src="{r}img/{o["pin"]}.jpg" alt="{esc(o["title"])}" loading="lazy" width="{w}" height="{h}">'
            f'<b class="tag">Shop</b></div><span class="t">{esc(o["title"])}</span></a>')


def cat_tile(c, r):
    key, name, _, cover = c
    n = sum(1 for o in OUTFITS if o["cat"] == key)
    return (f'<a class="cat" href="{r}shop/{key}/index.html"><img src="{r}img/{cover}.jpg" alt="" loading="lazy">'
            f'<div class="over"><strong>{esc(name)}</strong><small>{n} outfits</small></div></a>')


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)


def build():
    # clean generated dirs
    for d in ("shop", "outfits", "assets"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    write("assets/style.css", CSS.strip() + "\n")

    # ---------- home ----------
    r = ""
    m = [BY_PIN["632966922682369892"], BY_PIN["632966922682372722"], BY_PIN["632966922682404047"]]
    mosaic = "".join(
        f'<a href="{r}outfits/{o["slug"]}/index.html"><img src="{r}img/{o["pin"]}.jpg" alt="{esc(o["title"])}" width="736" height="1104">'
        + (f'<span class="cap">{esc(o["title"])}</span>' if i == 0 else "") + "</a>"
        for i, o in enumerate(m))
    home = f"""
  <section class="hero">
    <div>
      <p class="eyebrow">Workwear &amp; Office Outfits</p>
      <h1>Office style for the <em>corporate girlie</em></h1>
      <p class="lead">Affordable business casual looks, capsule wardrobe staples and fresh outfit ideas for the office. Every look comes with the exact pieces to shop.</p>
      <div class="cta">
        <a class="btn solid" href="{r}shop/index.html">Shop outfits</a>
        <a class="btn ghost" href="{PIN}{CHECKLIST_PIN}/" target="_blank" rel="noopener">Capsule checklist</a>
      </div>
      <div class="stats"><span>New outfit ideas every week</span><span>Affordable finds</span><span>Shop each look in one tap</span></div>
    </div>
    <div class="mosaic">{mosaic}</div>
  </section>

  <section class="sec">
    <div class="sec-head"><h2>Shop by category</h2></div>
    <div class="cats">{"".join(cat_tile(c, r) for c in CATEGORIES)}</div>
  </section>

  <section class="sec">
    <div class="sec-head"><h2>Newest outfits</h2><p>Tap a look to see the styling tips and shop every piece.</p></div>
    <div class="grid">{"".join(card(o, r) for o in OUTFITS[:8])}</div>
    <p style="text-align:center;margin-top:22px"><a class="btn ghost" href="{r}shop/index.html">See all outfits</a></p>
  </section>

  <section class="sec">
    <a class="band" href="{PIN}{CHECKLIST_PIN}/" target="_blank" rel="noopener">
      <img src="{r}img/{CHECKLIST_PIN}.jpg" alt="" width="110" height="146">
      <div><p class="eyebrow">Start here</p><strong>Corporate Capsule Wardrobe Checklist</strong>
      <p class="d">The 8 work wardrobe essentials every woman needs.</p></div>
      <span class="go" aria-hidden="true">&rarr;</span>
    </a>
  </section>

  <section class="sec why">
    <div><b>Affordable business casual</b><p>Looks that work in the office without the designer price tag.</p></div>
    <div><b>Capsule wardrobe staples</b><p>The key pieces that mix into endless professional outfits.</p></div>
    <div><b>Daily style inspiration</b><p>Fresh outfit formulas to save for your next office day.</p></div>
  </section>

  <section class="sec closing">
    <h2>Save your next office outfit</h2>
    <p>Follow along on Pinterest for new workwear ideas and capsule wardrobe inspiration.</p>
    <a class="btn" href="{PROFILE}" target="_blank" rel="noopener">Follow on Pinterest</a>
  </section>"""
    write("index.html", page(0, f"{SITE} | Workwear & Office Outfits",
                              "Office outfit ideas and workwear essentials for the corporate girlie. Shop every look.",
                              home, "index.html", "632966922682369892"))

    # ---------- shop ----------
    r = "../"
    pills = "".join(f'<a class="pill" href="{r}shop/{c[0]}/index.html">{esc(c[1])}</a>' for c in CATEGORIES)
    shop = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Shop outfits</nav>
  <section class="pagehead">
    <h1>Shop outfits</h1>
    <p class="lead">Browse every look. Each one comes with styling tips and the pieces to shop.</p>
  </section>
  <section class="sec" style="margin-top:28px"><div class="cats">{"".join(cat_tile(c, r) for c in CATEGORIES)}</div></section>
  <section class="sec">
    <div class="sec-head"><h2>All outfits</h2></div>
    <div class="grid">{"".join(card(o, r) for o in OUTFITS)}</div>
  </section>"""
    write("shop/index.html", page(1, f"Shop outfits | {SITE}", "Browse all office outfit ideas, business casual looks and workwear essentials.", shop, "shop/"))

    # ---------- categories ----------
    r = "../../"
    for key, name, desc, cover in CATEGORIES:
        items = [o for o in OUTFITS if o["cat"] == key]
        pills = "".join(
            f'<a class="pill" href="{r}shop/{c[0]}/index.html"' + (' aria-current="page"' if c[0] == key else "") + f'>{esc(c[1])}</a>'
            for c in CATEGORIES)
        body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / <a href="{r}shop/index.html">Shop outfits</a> / {esc(name)}</nav>
  <section class="pagehead">
    <h1>{esc(name)}</h1>
    <p class="lead">{esc(desc)}</p>
    <div class="pills">{pills}</div>
  </section>
  <section class="sec" style="margin-top:28px"><div class="grid">{"".join(card(o, r) for o in items)}</div></section>"""
        write(f"shop/{key}/index.html", page(2, f"{name} | {SITE}", desc, body, f"shop/{key}/"))

    # ---------- outfit pages ----------
    r = "../../"
    for o in OUTFITS:
        w, h = img_dims(o["pin"])
        cname = CAT[o["cat"]][1]
        prods = "".join(
            f'<div class="prod"><b>{esc(name)}</b>'
            f'<a class="btn solid small" href="{esc(product_url(o["slug"], i, q))}" target="_blank" rel="sponsored nofollow noopener">Shop on Amazon</a></div>'
            for i, (name, q) in enumerate(o["products"], start=1))
        tips = "".join(f"<li>{esc(t)}</li>" for t in o["tips"])
        related = [x for x in OUTFITS if x["cat"] == o["cat"] and x["slug"] != o["slug"]]
        related += [x for x in OUTFITS if x["cat"] != o["cat"] and x["slug"] != o["slug"]]
        related = related[:4]
        body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / <a href="{r}shop/index.html">Shop outfits</a> / <a href="{r}shop/{o["cat"]}/index.html">{esc(cname)}</a></nav>
  <article class="outfit">
    <div class="photo"><img src="{r}img/{o["pin"]}.jpg" alt="{esc(o["title"])}" width="{w}" height="{h}"></div>
    <div>
      <p class="eyebrow">{esc(cname)}</p>
      <h1>{esc(o["title"])}</h1>
      <p class="lead">{esc(o["intro"])}</p>
      <div class="block"><h2>Styling tips</h2><ul class="tips">{tips}</ul></div>
      <div class="block"><h2>Shop this look</h2><div class="prods">{prods}</div>
        <p class="disc">{DISCLOSURE}</p></div>
      <p class="save"><a class="btn ghost" href="{PIN}{o["pin"]}/" target="_blank" rel="noopener">Save on Pinterest</a></p>
    </div>
  </article>
  <section class="sec">
    <div class="sec-head"><h2>More looks</h2></div>
    <div class="grid">{"".join(card(x, r) for x in related)}</div>
  </section>"""
        write(f"outfits/{o['slug']}/index.html",
              page(2, f"{o['title']} | {SITE}", o["intro"], body, f"outfits/{o['slug']}/", o["pin"]))

    # ---------- 404 + robots ----------
    write("404.html", page(0, f"Page not found | {SITE}", "Page not found.",
          '<section class="pagehead" style="padding:40px 0"><h1>Page not found</h1><p class="lead">That page does not exist. Try the shop instead.</p>'
          '<p style="margin-top:20px"><a class="btn solid" href="/shop/">Shop outfits</a></p></section>', "404.html"))
    write("robots.txt", "User-agent: *\nAllow: /\n")

    # ---------- pin links list (outside the site) ----------
    base = CFG["site_url"].rstrip("/") if CFG["site_url"] else "https://YOUR-SITE"
    lines = ["# Pin destination links", "",
             f"Put the link in the 'Destination link' field of each Pinterest pin. Base URL: {base}", "",
             "| Pin | Destination link |", "|---|---|"]
    for o in OUTFITS:
        lines.append(f"| {o['title']} | {base}/outfits/{o['slug']}/ |")
    lines.append("")
    open(os.path.join(os.path.dirname(ROOT), "corporate-closet-pin-links.md"), "w").write("\n".join(lines))
    print(f"built {len(OUTFITS)} outfits, {len(CATEGORIES)} categories")


if __name__ == "__main__":
    build()
