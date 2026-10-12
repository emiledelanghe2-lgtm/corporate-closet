"""Builds the static site into the repo root.

Run:  python3 _build/build.py
Edit outfits in outfits.py, extras in extras.py, the Amazon tag in config.json,
exact affiliate URLs in affiliate_links.json, product photos/prices in product_data.json.
"""
import html as H
import json
import os
import shutil
from urllib.parse import quote_plus

from PIL import Image

from extras import (ATTRS, BUILDER, BUILDER_GROUPS, CAPSULES, CHECKLIST, COLORS, QUIZ,
                    SEASONS, SIZES, STYLES)
from outfits import CATEGORIES, CHECKLIST_PIN, OUTFITS, PROFILE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(name, default):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else default


CFG = load("config.json", {})
LINKS = load("affiliate_links.json", {})
PDATA = load("product_data.json", {})
CFG.setdefault("amazon_tag", "")
CFG.setdefault("amazon_domain", "www.amazon.com")
CFG.setdefault("site_url", "")
CFG.setdefault("about_intro", "")
CFG.setdefault("about_photo", "")

PIN = "https://www.pinterest.com/pin/"
CAT = {c[0]: c for c in CATEGORIES}
SITE = "The Corporate Closet"
BY_SLUG = {o["slug"]: o for o in OUTFITS}
for o in OUTFITS:
    o.update(ATTRS[o["slug"]])
STYLE_ORDER = list(STYLES)

HEART = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7.5-4.6-9.6-9.2C.8 8.3 3 4.5 6.6 4.5c2 0 3.5 1.1 5.4 3.1 '
         '1.9-2 3.4-3.1 5.4-3.1 3.6 0 5.8 3.8 4.2 7.3C19.5 16.4 12 21 12 21z"/></svg>')
HANGER = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7a2 2 0 1 1 2 2c-1 .3-2 .9-2 2v1m0 0L3.5 17.2c-.8.6-.4 1.8.6 1.8h15.8c1 0 1.4-1.2.6-1.8L12 12z"/></svg>')
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases. Links on this site are affiliate links."


def esc(s):
    return H.escape(s, quote=True)


def img_dims(pin):
    return Image.open(os.path.join(ROOT, "img", f"{pin}.jpg")).size


def cap_for(name):
    n = name.lower()
    for words, cap in [(("coat", "trench"), 90), (("blazer", "jacket"), 60), (("boot", "loafer", "flat", "shoe", "sandal"), 60),
                       (("dress",), 50), (("jeans", "trouser", "pants"), 50), (("skirt", "short"), 40),
                       (("bag", "tote"), 50), (("belt", "scarf"), 25), (("bangle", "bracelet", "tights"), 20)]:
        if any(w in n for w in words):
            return cap
    return 35


def amazon(query, extra=""):
    url = f"https://{CFG['amazon_domain']}/s?k={quote_plus(query)}{extra}"
    if CFG["amazon_tag"]:
        url += f"&tag={quote_plus(CFG['amazon_tag'])}"
    return url


def budget_x(cap):
    return f"&rh=p_36%3A-{int(cap) * 100}"


def premium_x(cap):
    return f"&rh=p_36%3A{int(cap) * 200}-"


def heart_btn(slug):
    return (f'<button class="heart" type="button" data-slug="{slug}" aria-pressed="false" '
            f'aria-label="Save this outfit">{HEART}</button>')


def card(o, r):
    w, h = img_dims(o["pin"])
    return (f'<div class="card" data-colors="{" ".join(o["colors"])}" data-style="{o["style"]}">'
            f'<a class="cl" href="{r}outfits/{o["slug"]}/index.html">'
            f'<div class="ph"><img src="{r}img/{o["pin"]}.jpg" alt="{esc(o["title"])}" loading="lazy" width="{w}" height="{h}">'
            f'<b class="tag">Shop</b></div><span class="t">{esc(o["title"])}</span></a>{heart_btn(o["slug"])}</div>')


def tile(href, img, name, small):
    return (f'<a class="cat" href="{href}"><img src="{img}" alt="" loading="lazy">'
            f'<div class="over"><strong>{esc(name)}</strong><small>{esc(small)}</small></div></a>')


def cat_tile(c, r):
    key, name, _, cover = c
    n = sum(1 for o in OUTFITS if o["cat"] == key)
    return tile(f"{r}shop/{key}/index.html", f"{r}img/{cover}.jpg", name, f"{n} outfits")


NEWS_N = [0]


def newsletter(r):
    NEWS_N[0] += 1
    i = NEWS_N[0]
    return f"""<section class="news">
    <h2>Get the weekly outfit</h2>
    <p>One new look every week, plus the printable capsule checklist.</p>
    <form name="newsletter" method="POST" action="{r}thanks/index.html" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="newsletter">
      <p hidden><label>Leave this empty <input name="bot-field"></label></p>
      <label class="sr" for="em{i}">Email address</label>
      <input id="em{i}" type="email" name="email" required autocomplete="email" placeholder="Your email address">
      <button class="btn solid" type="submit">Subscribe</button>
    </form>
    <small>No spam. Unsubscribe at any time.</small>
  </section>"""


def prod_row(label, query, cap, url_exact, data, fixed_key):
    price = ""
    if data.get("price"):
        chk = f' <span class="chk">checked {esc(data["checked"])}</span>' if data.get("checked") else ""
        price = f'<span class="price">{esc(data["price"])}{chk}</span>'
    thumb = (f'<img src="{esc(data["image"])}" alt="" loading="lazy">' if data.get("image") else HANGER)
    main = url_exact or amazon(query)
    fixed = ' data-fixed="1"' if url_exact else ""
    alts = ""
    if not url_exact:
        alts = (f'<span class="alts"><a data-q="{esc(query)}" data-x="{esc(budget_x(cap))}" href="{esc(amazon(query, budget_x(cap)))}" '
                f'target="_blank" rel="sponsored nofollow noopener">Budget finds</a>'
                f'<a data-q="{esc(query)}" data-x="{esc(premium_x(cap))}" href="{esc(amazon(query, premium_x(cap)))}" '
                f'target="_blank" rel="sponsored nofollow noopener">Premium picks</a></span>')
    return (f'<div class="prod"><div class="thumb">{thumb}</div><div class="pi"><b>{esc(label)}</b>{price}{alts}</div>'
            f'<a class="btn solid small buy" data-q="{esc(query)}" data-x=""{fixed} href="{esc(main)}" target="_blank" '
            f'rel="sponsored nofollow noopener">Shop on Amazon</a></div>')


CSS = r"""
:root{--cream:#F4EFE8;--sand:#EBE4DC;--line:#D9CEC2;--espresso:#2B1A10;--mocha:#6B5444;--card:#FBF8F4;--serif:"Cormorant Garamond",Georgia,serif}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{background:var(--cream);color:var(--espresso);font-family:"Jost",system-ui,sans-serif;font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--mocha)}
h1,h2,h3{font-family:var(--serif);font-weight:600;line-height:1.05}
h2{font-weight:500;font-style:italic;font-size:34px}
.lead{color:var(--mocha);font-size:17px}

/* header */
.top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 12px;padding:14px 0 6px}
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.brand img{width:48px;height:48px;border-radius:50%;border:1px solid var(--line);flex:none}
.brand b{font-family:var(--serif);font-size:21px;font-weight:600;line-height:1.05}
.actions{display:flex;align-items:center;gap:8px}
.saved{display:inline-flex;align-items:center;gap:6px;min-height:42px;padding:8px 14px;border:1px solid var(--line);border-radius:999px;font-size:14px}
.saved svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2}
.menu{order:3;width:100%;display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;margin:0 -16px;padding:2px 16px 8px}
.menu::-webkit-scrollbar{display:none}
.menu a{flex:none;padding:9px 14px;font-size:15px;color:var(--mocha);border-radius:999px}
.menu a:hover,.menu a[aria-current="page"]{color:var(--espresso);background:var(--sand)}
.long{display:none}
.actions .follow{display:none}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:48px;padding:12px 24px;border-radius:999px;border:1px solid var(--espresso);font-weight:500;letter-spacing:.02em;transition:background .2s,color .2s;cursor:pointer;font-family:inherit;font-size:16px;text-align:center}
.btn.solid{background:var(--espresso);color:var(--cream)}
.btn.solid:hover{background:#46301F}
.btn.ghost{background:transparent;color:var(--espresso)}
.btn.ghost:hover{background:var(--espresso);color:var(--cream)}
.btn.small{min-height:42px;padding:9px 18px;font-size:14px}

/* hero */
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

/* cards */
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.card{position:relative;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.card[hidden]{display:none}
.card .cl{display:block}
.ph{position:relative}
.card img{width:100%;height:auto;aspect-ratio:2/3;object-fit:cover;display:block;background:var(--sand)}
.tag{position:absolute;bottom:8px;right:8px;padding:5px 12px;border-radius:999px;background:rgba(251,248,244,.95);font-size:12px;font-weight:500}
.card .t{display:block;padding:10px 12px 13px;font-size:14px;line-height:1.3}
.heart{position:absolute;top:8px;right:8px;z-index:2;width:44px;height:44px;border-radius:50%;border:0;background:rgba(251,248,244,.94);color:var(--espresso);display:grid;place-items:center;cursor:pointer}
.heart svg{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linejoin:round}
.heart[aria-pressed="true"] svg{fill:#8A3B2E;stroke:#8A3B2E}

/* chips */
.chips{display:flex;gap:8px;overflow-x:auto;margin:0 -16px;padding:2px 16px 10px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:none;display:inline-flex;align-items:center;gap:8px;min-height:42px;padding:8px 18px;border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--espresso);font:inherit;font-size:14px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--espresso);border-color:var(--espresso);color:var(--cream)}
.sw{width:12px;height:12px;border-radius:50%;border:1px solid rgba(0,0,0,.2)}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.pill{padding:8px 16px;border:1px solid var(--line);border-radius:999px;font-size:14px}
.pill[aria-current="page"]{background:var(--espresso);border-color:var(--espresso);color:var(--cream)}

/* sections */
.otw{display:grid;gap:18px;padding:16px;background:var(--card);border:1px solid var(--line);border-radius:24px}
.otw img{width:100%;height:auto;border-radius:16px;display:block;aspect-ratio:4/5;object-fit:cover;object-position:top}
.otw h3{font-size:32px;margin-top:6px}
.otw p.lead{margin-top:10px}
.otw .btn{margin-top:18px}
.tools{display:grid;gap:12px}
.tool{display:block;padding:26px;border-radius:22px;background:var(--sand)}
.tool b{display:block;font-family:var(--serif);font-size:28px;line-height:1.05;font-weight:600}
.tool p{margin-top:8px;color:var(--mocha)}
.tool span{display:inline-block;margin-top:14px;font-weight:500;border-bottom:1px solid var(--espresso)}
.band{display:flex;align-items:center;gap:18px;padding:16px;background:var(--card);border:1px solid var(--line);border-radius:22px}
.band img{width:64px;height:84px;object-fit:cover;border-radius:12px;flex:none}
.band strong{display:block;margin-top:2px;font-family:var(--serif);font-size:21px;line-height:1.08;font-weight:600}
.band p.d{display:none;margin-top:4px;color:var(--mocha);font-size:15px}
.band .go{margin-left:auto;font-size:24px;color:var(--mocha)}
.why{display:grid;gap:12px}
.why div{padding:24px;background:var(--sand);border-radius:20px}
.why b{display:block;font-family:var(--serif);font-size:26px;line-height:1.1;font-weight:600}
.why p{margin-top:8px;color:var(--mocha);font-size:15px}
.news{padding:36px 22px;text-align:center;background:var(--sand);border-radius:26px}
.news p{margin:8px auto 18px;max-width:440px;color:var(--mocha)}
.news form{display:grid;gap:10px;max-width:460px;margin:0 auto}
.news input[type=email]{min-height:50px;padding:12px 20px;border:1px solid var(--line);border-radius:999px;background:#FBF8F4;font:inherit;color:var(--espresso)}
.news small{display:block;margin-top:12px;font-size:12px;color:var(--mocha)}
.closing{padding:44px 24px;text-align:center;background:var(--espresso);color:var(--cream);border-radius:26px}
.closing h2{color:var(--cream)}
.closing p{margin:10px auto 22px;max-width:420px;color:#D9CEC2}
.closing .btn{background:var(--cream);color:var(--espresso);border-color:var(--cream)}

/* page heads */
.crumbs{margin:6px 0 14px;font-size:14px;color:var(--mocha)}
.crumbs a:hover{color:var(--espresso);text-decoration:underline}
.pagehead h1{font-size:40px;margin-top:6px}
.pagehead .lead{margin-top:10px;max-width:600px}
.prose{max-width:680px}
.prose h2{font-size:30px;margin:30px 0 8px}
.prose p{margin-top:10px;color:var(--mocha)}
.prose img{border-radius:20px;margin-top:16px}

/* outfit page */
.outfit{display:grid;gap:24px}
.outfit .photo{border-radius:20px;overflow:hidden;background:var(--sand);position:relative}
.outfit .photo img{width:100%;height:auto;display:block}
.outfit .photo .heart{top:12px;right:12px}
.outfit h1{font-size:38px;margin-top:6px}
.outfit .lead{margin-top:12px}
.jump{margin-top:18px}
.block{margin-top:26px}
.block h2{font-size:28px;margin-bottom:10px}
.tips{list-style:none;display:grid;gap:8px}
.tips li{padding-left:20px;position:relative;color:var(--mocha)}
.tips li::before{content:"";position:absolute;left:0;top:.7em;width:7px;height:7px;border-radius:50%;background:#8A6A4F}
.size{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:12px}
.size > span{font-size:14px;color:var(--mocha);margin-right:4px}
.size label{display:inline-flex;min-height:40px;align-items:center;padding:6px 14px;border:1px solid var(--line);border-radius:999px;font-size:14px;cursor:pointer}
.size input{position:absolute;opacity:0;pointer-events:none}
.size input:checked + span{font-weight:500}
.size label:has(input:checked){background:var(--espresso);border-color:var(--espresso);color:var(--cream)}
.size label:has(input:focus-visible){outline:2px solid var(--mocha);outline-offset:3px}
.prods{display:grid;gap:10px}
.prod{display:grid;grid-template-columns:56px 1fr;gap:8px 14px;align-items:center;padding:12px 14px;background:var(--card);border:1px solid var(--line);border-radius:16px}
.prod .thumb{width:56px;height:56px;border-radius:12px;background:var(--sand);display:grid;place-items:center;overflow:hidden}
.prod .thumb img{width:100%;height:100%;object-fit:cover}
.prod .thumb svg{width:26px;height:26px;fill:none;stroke:var(--mocha);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.prod .pi{display:grid;gap:3px;min-width:0}
.prod .pi b{font-weight:500;line-height:1.3}
.price{font-size:14px;color:var(--mocha)}
.chk{font-size:12px;opacity:.85}
.alts{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px;color:var(--mocha)}
.alts a{text-decoration:underline;text-underline-offset:3px}
.alts a:hover{color:var(--espresso)}
.prod .buy{grid-column:1/-1}
.disc{margin-top:12px;font-size:13px;color:var(--mocha)}
.save{margin-top:18px}
.shopbar{position:fixed;left:0;right:0;bottom:0;z-index:5;padding:12px 16px calc(12px + env(safe-area-inset-bottom));background:linear-gradient(to top,var(--cream) 62%,rgba(244,239,232,0))}
.shopbar a{width:100%;max-width:488px;margin:0 auto;display:flex}

/* quiz */
.quiz{max-width:620px;margin:28px auto 0}
.qbar{height:6px;border-radius:99px;background:var(--sand);overflow:hidden}
.qbar i{display:block;height:100%;background:var(--espresso);transition:width .3s}
.qcount{margin:14px 0 6px;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--mocha)}
.quiz h2{font-size:34px;margin-bottom:16px}
.opts{display:grid;gap:10px}
.opt{width:100%;min-height:56px;padding:14px 20px;text-align:left;border:1px solid var(--line);border-radius:16px;background:var(--card);font:inherit;font-size:17px;color:var(--espresso);cursor:pointer}
.opt:hover{border-color:var(--espresso)}
.result{text-align:center}
.result h2{font-size:44px}
.result .lead{margin:10px auto 0;max-width:460px}
.result .grid{margin-top:26px;text-align:left}
.result .acts{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:20px}

/* builder */
.builder{display:grid;gap:22px}
.group h3{font-size:26px;margin-bottom:10px}
.picks{display:flex;flex-wrap:wrap;gap:8px}
.pick{display:inline-flex;align-items:center;min-height:44px;padding:8px 16px;border:1px solid var(--line);border-radius:999px;background:var(--card);cursor:pointer;font-size:15px}
.pick input{position:absolute;opacity:0;pointer-events:none}
.pick:has(input:checked){background:var(--espresso);border-color:var(--espresso);color:var(--cream)}
.pick:has(input:focus-visible){outline:2px solid var(--mocha);outline-offset:3px}
.sum{padding:22px;border-radius:22px;background:var(--espresso);color:var(--cream)}
.sum .n{font-family:var(--serif);font-size:56px;line-height:1;font-weight:600}
.sum p{margin-top:6px;color:#D9CEC2}
.sum ul{list-style:none;display:grid;gap:8px;margin-top:16px}
.sum li{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px 10px 16px;border-radius:14px;background:rgba(255,255,255,.08)}
.sum li a{flex:none;padding:7px 14px;border-radius:999px;background:var(--cream);color:var(--espresso);font-size:13px;font-weight:500}

/* checklist */
.check{list-style:none;display:grid;gap:10px;margin-top:22px;max-width:560px}
.check li{display:flex;align-items:center;gap:14px;padding:14px 18px;background:var(--card);border:1px solid var(--line);border-radius:14px;font-size:17px}
.check li::before{content:"";width:22px;height:22px;border:1.5px solid var(--espresso);border-radius:6px;flex:none}

footer{padding:36px 0 40px;margin-top:56px;border-top:1px solid var(--line);text-align:center;font-size:13px;color:var(--mocha)}
footer nav{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 18px;margin-bottom:14px;font-size:14px}
footer nav a:hover{color:var(--espresso);text-decoration:underline}
footer p + p{margin-top:6px}
.has-shopbar footer{padding-bottom:110px}

.card .cl:focus-visible,.cat:focus-visible,.mosaic a:focus-visible,.band:focus-visible,.btn:focus-visible,.pill:focus-visible,.menu a:focus-visible,.chip:focus-visible,.heart:focus-visible,.opt:focus-visible,.tool:focus-visible,.saved:focus-visible,.alts a:focus-visible{outline:2px solid var(--mocha);outline-offset:3px}
@media(hover:hover){.card:hover img,.cat:hover img,.mosaic a:hover img{opacity:.92}}

@media(min-width:600px){
  .actions .follow{display:inline-flex}
  .grid{grid-template-columns:repeat(3,1fr);gap:16px}
  .cats{grid-template-columns:repeat(4,1fr);gap:16px}
  .why,.tools{grid-template-columns:repeat(3,1fr)}
  .tools{grid-template-columns:repeat(2,1fr)}
  .cta{grid-template-columns:auto auto;justify-content:start}
  .mosaic{height:440px}
  .long{display:inline}
  .news form{grid-template-columns:1fr auto}
  .otw{grid-template-columns:minmax(0,5fr) minmax(0,6fr);align-items:center;gap:32px;padding:22px}
}
@media(min-width:900px){
  .wrap{padding:0 32px}
  .top{flex-wrap:nowrap;padding:22px 0}
  .brand img{width:56px;height:56px}
  .brand b{font-size:25px}
  .menu{order:0;width:auto;margin:0;padding:0;overflow:visible}
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
  .tools{grid-template-columns:repeat(2,1fr);gap:20px}
  .tool{padding:36px}
  .otw{padding:28px 36px;gap:48px}
  .otw h3{font-size:46px}
  .band{padding:22px 28px;gap:28px}
  .band img{width:110px;height:146px}
  .band strong{font-size:34px}
  .band p.d{display:block;font-size:17px}
  .why{gap:20px}
  .why div{padding:32px}
  .news{padding:56px 32px}
  .closing{padding:72px 32px}
  .pagehead h1{font-size:60px}
  .outfit{grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:56px;align-items:start}
  .outfit .photo{position:sticky;top:20px}
  .outfit h1{font-size:54px}
  .block h2{font-size:32px}
  .prod{grid-template-columns:64px 1fr auto}
  .prod .thumb{width:64px;height:64px}
  .prod .buy{grid-column:auto}
  .builder{grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:40px;align-items:start}
  .sum{position:sticky;top:20px}
  .quiz h2{font-size:42px}
  footer{margin-top:80px}
  .shopbar{display:none}
  .has-shopbar footer{padding-bottom:40px}
}
@media print{
  .top,.menu,footer,.news,.shopbar,.noprint{display:none!important}
  body{background:#fff}
  .check li{break-inside:avoid}
}
"""

JS = r"""
(function () {
  var CC = window.CC || {};
  var root = document.body.getAttribute('data-root') || '';
  var HEART = '__HEART__';
  function ls(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function ss(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function all(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function amazon(q, x) {
    var u = 'https://' + CC.config.domain + '/s?k=' + encodeURIComponent(q) + (x || '');
    if (CC.config.tag) u += '&tag=' + encodeURIComponent(CC.config.tag);
    return u;
  }
  function byslug(s) { return CC.outfits.filter(function (o) { return o.slug === s; })[0]; }
  function card(o) {
    return '<div class="card" data-colors="' + o.colors.join(' ') + '" data-style="' + o.style + '">' +
      '<a class="cl" href="' + root + 'outfits/' + o.slug + '/index.html"><div class="ph"><img src="' + root + 'img/' + o.pin +
      '.jpg" alt="' + esc(o.title) + '" loading="lazy" width="' + o.w + '" height="' + o.h + '"><b class="tag">Shop</b></div>' +
      '<span class="t">' + esc(o.title) + '</span></a>' +
      '<button class="heart" type="button" data-slug="' + o.slug + '" aria-pressed="false" aria-label="Save this outfit">' + HEART + '</button></div>';
  }

  /* saved outfits (hearts) */
  function refreshHearts() {
    var s = ls('cc_saved', []);
    all('.heart').forEach(function (b) { b.setAttribute('aria-pressed', s.indexOf(b.getAttribute('data-slug')) > -1 ? 'true' : 'false'); });
    all('[data-saved-count]').forEach(function (n) { n.textContent = s.length; });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.heart') : null;
    if (!b) return;
    e.preventDefault();
    var slug = b.getAttribute('data-slug'), s = ls('cc_saved', []), i = s.indexOf(slug);
    if (i > -1) s.splice(i, 1); else s.push(slug);
    ss('cc_saved', s);
    refreshHearts();
    var grid = document.getElementById('savedGrid');
    if (grid) renderSaved();
  });

  function renderSaved() {
    var grid = document.getElementById('savedGrid'), empty = document.getElementById('savedEmpty');
    if (!grid) return;
    var s = ls('cc_saved', []).map(byslug).filter(Boolean);
    grid.innerHTML = s.map(card).join('');
    if (empty) empty.hidden = s.length > 0;
    refreshHearts();
  }

  /* outfit of the week */
  var otw = document.getElementById('otw');
  if (otw && CC.outfits) {
    var week = Math.floor(Date.now() / 604800000);
    var o = CC.outfits[week % CC.outfits.length];
    otw.innerHTML = '<a href="' + root + 'outfits/' + o.slug + '/index.html"><img src="' + root + 'img/' + o.pin + '.jpg" alt="' + esc(o.title) + '"></a>' +
      '<div><p class="eyebrow">Outfit of the week</p><h3>' + esc(o.title) + '</h3><p class="lead">' + esc(o.intro) + '</p>' +
      '<a class="btn solid" href="' + root + 'outfits/' + o.slug + '/index.html">Shop this look</a></div>';
  }

  /* size preference rewrites Amazon search links */
  var sizeBox = document.getElementById('sizes');
  function applySize(key) {
    var prefix = '';
    CC.sizes.forEach(function (z) { if (z.key === key) prefix = z.prefix; });
    all('a[data-q]').forEach(function (a) {
      if (a.hasAttribute('data-fixed')) return;
      var q = (prefix ? prefix + ' ' : '') + a.getAttribute('data-q');
      a.href = amazon(q, a.getAttribute('data-x') || '');
    });
  }
  if (sizeBox) {
    var cur = ls('cc_size', 'regular');
    all('input[name=size]', sizeBox).forEach(function (r) {
      r.checked = r.value === cur;
      r.addEventListener('change', function () { ss('cc_size', r.value); applySize(r.value); });
    });
    applySize(cur);
  }

  /* shop page color filter */
  var cf = document.getElementById('colorfilter');
  if (cf) {
    var cards = all('#grid .card');
    all('.chip', cf).forEach(function (chip) {
      chip.addEventListener('click', function () {
        var f = chip.getAttribute('data-filter');
        all('.chip', cf).forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
        cards.forEach(function (c) { c.hidden = f !== 'all' && c.getAttribute('data-colors').split(' ').indexOf(f) < 0; });
      });
    });
  }

  /* style quiz */
  var quiz = document.getElementById('quiz');
  if (quiz) {
    var step = 0, score = {};
    function show(style) {
      var st = CC.styles[style], list = CC.outfits.filter(function (o) { return o.style === style; }).slice(0, 4);
      quiz.innerHTML = '<div class="result"><p class="eyebrow">Your office style</p><h2>' + esc(st.name) + '</h2><p class="lead">' + esc(st.desc) +
        '</p><div class="grid">' + list.map(card).join('') + '</div><div class="acts"><button class="btn ghost" id="retake" type="button">Retake the quiz</button>' +
        '<a class="btn solid" href="' + root + 'shop/index.html">Shop all outfits</a></div></div>';
      document.getElementById('retake').addEventListener('click', function () { step = 0; score = {}; history.replaceState(null, '', location.pathname); render(); });
      refreshHearts();
    }
    function render() {
      if (step >= CC.quiz.length) {
        var best = 'classic', max = -1;
        CC.styleOrder.forEach(function (k) { if ((score[k] || 0) > max) { max = score[k] || 0; best = k; } });
        history.replaceState(null, '', '#' + best);
        show(best);
        return;
      }
      var q = CC.quiz[step];
      quiz.innerHTML = '<div class="qbar"><i style="width:' + (step / CC.quiz.length * 100) + '%"></i></div><p class="qcount">Question ' + (step + 1) + ' of ' + CC.quiz.length +
        '</p><h2>' + esc(q.q) + '</h2><div class="opts">' + q.a.map(function (a, i) { return '<button class="opt" type="button" data-s="' + a.s + '">' + esc(a.t) + '</button>'; }).join('') + '</div>';
      all('.opt', quiz).forEach(function (b) {
        b.addEventListener('click', function () { var s = b.getAttribute('data-s'); score[s] = (score[s] || 0) + 1; step++; render(); });
      });
    }
    var h = location.hash.replace('#', '');
    if (CC.styles[h]) show(h); else render();
  }

  /* capsule builder */
  var bd = document.getElementById('builder');
  if (bd) {
    var boxes = all('input[type=checkbox]', bd), out = document.getElementById('sum');
    function calc() {
      var sel = boxes.filter(function (b) { return b.checked; }), g = {tops: 0, bottoms: 0, layers: 0, dresses: 0, shoes: 0};
      sel.forEach(function (b) { g[b.getAttribute('data-g')]++; });
      var combos = (g.tops * g.bottoms + g.dresses) * (1 + g.layers);
      var msg = sel.length === 0 ? 'Pick the pieces you own or want. Aim for 8 to 12.' :
        sel.length < 8 ? 'Add a few more pieces to unlock more outfits.' : 'A solid capsule. Every piece mixes with the rest.';
      out.innerHTML = '<div class="n">' + combos + '</div><p>possible outfit combinations from ' + sel.length + ' pieces. ' + msg + '</p>' +
        (sel.length ? '<ul>' + sel.map(function (b) {
          return '<li><span>' + esc(b.getAttribute('data-n')) + '</span><a target="_blank" rel="sponsored nofollow noopener" href="' +
            amazon(b.getAttribute('data-q'), '') + '">Shop</a></li>';
        }).join('') + '</ul>' : '');
    }
    boxes.forEach(function (b) { b.addEventListener('change', calc); });
    calc();
  }

  /* print button */
  all('[data-print]').forEach(function (b) { b.addEventListener('click', function () { window.print(); }); });

  renderSaved();
  refreshHearts();
})();
"""


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)


def page(depth, title, desc, body, path, og_pin=None, nav=None, shopbar=""):
    r = "../" * depth
    canonical = og_img = ""
    if CFG["site_url"]:
        base = CFG["site_url"].rstrip("/")
        canonical = f'<link rel="canonical" href="{base}/{path}">'
        og_img = f'<meta property="og:image" content="{base}/img/{og_pin or "logo"}.jpg">'
    links = [("shop", "Shop outfits", "shop/index.html"), ("seasons", "Seasons", "seasons/index.html"),
             ("quiz", "Style quiz", "quiz/index.html"), ("capsule", "Build a capsule", "capsule-builder/index.html"),
             ("about", "About", "about/index.html")]
    menu = "".join(f'<a href="{r}{h}"' + (' aria-current="page"' if nav == k else "") + f">{t}</a>" for k, t, h in links)
    flinks = "".join(f'<a href="{r}{h}">{t}</a>' for _, t, h in links) + f'<a href="{r}checklist/index.html">Checklist</a><a href="{r}saved/index.html">Saved outfits</a><a href="{PROFILE}" target="_blank" rel="noopener">Pinterest</a>'
    cls = ' class="has-shopbar"' if shopbar else ""
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/style.css">
<script src="{r}assets/data.js" defer></script>
<script src="{r}assets/site.js" defer></script>
</head>
<body data-root="{r}"{cls}>
<div class="wrap">
  <header class="top">
    <a class="brand" href="{r}index.html"><img src="{r}img/logo.jpg" alt="" width="56" height="56"><b>{SITE}</b></a>
    <nav class="menu" aria-label="Main">{menu}</nav>
    <div class="actions">
      <a class="saved" href="{r}saved/index.html" aria-label="Saved outfits">{HEART}<span data-saved-count>0</span></a>
      <a class="btn solid small follow" href="{PROFILE}" target="_blank" rel="noopener"><span>Follow<span class="long"> on Pinterest</span></span></a>
    </div>
  </header>
{body}
  <footer>
    <nav aria-label="Footer">{flinks}</nav>
    <p>{DISCLOSURE}</p>
    <p>&copy; {SITE}</p>
  </footer>
</div>
{shopbar}
</body>
</html>
"""


def build():
    for d in ("shop", "outfits", "assets", "seasons", "quiz", "capsule-builder", "checklist", "saved", "about", "thanks"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    NEWS_N[0] = 0

    # ---------- assets ----------
    write("assets/style.css", CSS.strip() + "\n")
    write("assets/site.js", JS.replace("__HEART__", HEART.replace("'", "\\'")).strip() + "\n")
    data = {
        "config": {"domain": CFG["amazon_domain"], "tag": CFG["amazon_tag"]},
        "sizes": [{"key": k, "label": l, "prefix": p} for k, l, p in SIZES],
        "styles": {k: {"name": v[0], "desc": v[1]} for k, v in STYLES.items()},
        "styleOrder": STYLE_ORDER,
        "quiz": [{"q": q, "a": [{"s": s, "t": t} for s, t in a]} for q, a in QUIZ],
        "outfits": [{"slug": o["slug"], "title": o["title"], "intro": o["intro"], "pin": o["pin"], "style": o["style"],
                     "colors": o["colors"], "w": img_dims(o["pin"])[0], "h": img_dims(o["pin"])[1]} for o in OUTFITS],
    }
    write("assets/data.js", "window.CC=" + json.dumps(data, separators=(",", ":")) + ";\n")

    # ---------- home ----------
    r = ""
    m = [BY_SLUG["fall-capsule-brown-tones"], BY_SLUG["leather-blazer"], BY_SLUG["white-button-down"]]
    mosaic = "".join(
        f'<a href="{r}outfits/{o["slug"]}/index.html"><img src="{r}img/{o["pin"]}.jpg" alt="{esc(o["title"])}" width="736" height="1104">'
        + (f'<span class="cap">{esc(o["title"])}</span>' if i == 0 else "") + "</a>" for i, o in enumerate(m))
    first = OUTFITS[0]
    season_tiles = "".join(tile(f"{r}seasons/{k}/index.html", f"{r}img/{pin}.jpg", t, b) for k, t, b, pin in SEASONS)
    home = f"""
  <section class="hero">
    <div>
      <p class="eyebrow">Workwear &amp; Office Outfits</p>
      <h1>Office style for the <em>corporate girlie</em></h1>
      <p class="lead">Affordable business casual looks, capsule wardrobe staples and fresh outfit ideas for the office. Every look comes with the exact pieces to shop.</p>
      <div class="cta">
        <a class="btn solid" href="{r}shop/index.html">Shop outfits</a>
        <a class="btn ghost" href="{r}quiz/index.html">Find your style</a>
      </div>
      <div class="stats"><span>New outfit ideas every week</span><span>Affordable finds</span><span>Shop each look in one tap</span></div>
    </div>
    <div class="mosaic">{mosaic}</div>
  </section>

  <section class="sec">
    <div class="otw" id="otw">
      <a href="{r}outfits/{first["slug"]}/index.html"><img src="{r}img/{first["pin"]}.jpg" alt="{esc(first["title"])}"></a>
      <div><p class="eyebrow">Outfit of the week</p><h3>{esc(first["title"])}</h3><p class="lead">{esc(first["intro"])}</p>
      <a class="btn solid" href="{r}outfits/{first["slug"]}/index.html">Shop this look</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="sec-head"><h2>Shop by category</h2></div>
    <div class="cats">{"".join(cat_tile(c, r) for c in CATEGORIES)}</div>
  </section>

  <section class="sec">
    <div class="sec-head"><h2>Newest outfits</h2><p>Tap a look to see the styling tips and shop every piece. Tap the heart to save it.</p></div>
    <div class="grid">{"".join(card(o, r) for o in OUTFITS[:8])}</div>
    <p style="text-align:center;margin-top:22px"><a class="btn ghost" href="{r}shop/index.html">See all outfits</a></p>
  </section>

  <section class="sec">
    <div class="sec-head"><h2>Shop by season</h2><p>A capsule of 8 pieces for every season.</p></div>
    <div class="cats">{season_tiles}</div>
  </section>

  <section class="sec tools">
    <a class="tool" href="{r}quiz/index.html"><b>What is your office style?</b><p>Five quick questions, then outfits picked for you.</p><span>Take the quiz</span></a>
    <a class="tool" href="{r}capsule-builder/index.html"><b>Build your capsule</b><p>Pick your pieces and see how many outfits they make.</p><span>Start building</span></a>
  </section>

  <section class="sec">
    <a class="band" href="{r}checklist/index.html">
      <img src="{r}img/{CHECKLIST_PIN}.jpg" alt="" width="110" height="146">
      <div><p class="eyebrow">Free download</p><strong>Printable capsule wardrobe checklist</strong>
      <p class="d">The work wardrobe essentials, ready to tick off.</p></div>
      <span class="go" aria-hidden="true">&rarr;</span>
    </a>
  </section>

  <section class="sec why">
    <div><b>Affordable business casual</b><p>Looks that work in the office without the designer price tag.</p></div>
    <div><b>Capsule wardrobe staples</b><p>The key pieces that mix into endless professional outfits.</p></div>
    <div><b>Daily style inspiration</b><p>Fresh outfit formulas to save for your next office day.</p></div>
  </section>

  <section class="sec">{newsletter(r)}</section>

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
    chips = ('<button class="chip" type="button" data-filter="all" aria-pressed="true">All colors</button>' + "".join(
        f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false"><i class="sw" style="background:{sw}"></i>{esc(n)}</button>'
        for (k, n), sw in zip(COLORS, ["#6B4A35", "#F1E8DA", "#9A9A9A", "#5B7BA3"])))
    shop = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Shop outfits</nav>
  <section class="pagehead">
    <h1>Shop outfits</h1>
    <p class="lead">Browse every look. Each one comes with styling tips and the pieces to shop.</p>
  </section>
  <section class="sec" style="margin-top:28px"><div class="cats">{"".join(cat_tile(c, r) for c in CATEGORIES)}</div></section>
  <section class="sec">
    <div class="sec-head"><h2>All outfits</h2></div>
    <div class="chips" id="colorfilter" role="group" aria-label="Filter by color">{chips}</div>
    <div class="grid" id="grid">{"".join(card(o, r) for o in OUTFITS)}</div>
  </section>"""
    write("shop/index.html", page(1, f"Shop outfits | {SITE}", "Browse all office outfit ideas, business casual looks and workwear essentials.", shop, "shop/", nav="shop"))

    for key, name, desc, cover in CATEGORIES:
        items = [o for o in OUTFITS if o["cat"] == key]
        pills = "".join(
            f'<a class="pill" href="{"../"*2}shop/{c[0]}/index.html"' + (' aria-current="page"' if c[0] == key else "") + f'>{esc(c[1])}</a>'
            for c in CATEGORIES)
        rr = "../../"
        body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{rr}index.html">Home</a> / <a href="{rr}shop/index.html">Shop outfits</a> / {esc(name)}</nav>
  <section class="pagehead">
    <h1>{esc(name)}</h1>
    <p class="lead">{esc(desc)}</p>
    <div class="pills">{pills}</div>
  </section>
  <section class="sec" style="margin-top:28px"><div class="grid">{"".join(card(o, rr) for o in items)}</div></section>"""
        write(f"shop/{key}/index.html", page(2, f"{name} | {SITE}", desc, body, f"shop/{key}/", nav="shop"))

    # ---------- outfit pages ----------
    r = "../../"
    size_chips = "".join(
        f'<label><input type="radio" name="size" value="{k}"{" checked" if k == "regular" else ""}><span>{esc(l)}</span></label>'
        for k, l, _ in SIZES)
    for o in OUTFITS:
        w, h = img_dims(o["pin"])
        cname = CAT[o["cat"]][1]
        rows = []
        for i, (name, q) in enumerate(o["products"], start=1):
            key = f"{o['slug']}/{i}"
            d = PDATA.get(key, {})
            exact = d.get("url") or LINKS.get(key)
            rows.append(prod_row(name, q, d.get("cap", cap_for(name)), exact, d, key))
        tips = "".join(f"<li>{esc(t)}</li>" for t in o["tips"])
        related = [x for x in OUTFITS if x["cat"] == o["cat"] and x["slug"] != o["slug"]]
        related += [x for x in OUTFITS if x["cat"] != o["cat"] and x["slug"] != o["slug"]]
        shopbar = '<div class="shopbar"><a class="btn solid" href="#shop">Shop the whole look</a></div>'
        body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / <a href="{r}shop/index.html">Shop outfits</a> / <a href="{r}shop/{o["cat"]}/index.html">{esc(cname)}</a></nav>
  <article class="outfit">
    <div class="photo"><img src="{r}img/{o["pin"]}.jpg" alt="{esc(o["title"])}" width="{w}" height="{h}">{heart_btn(o["slug"])}</div>
    <div>
      <p class="eyebrow">{esc(cname)}</p>
      <h1>{esc(o["title"])}</h1>
      <p class="lead">{esc(o["intro"])}</p>
      <p class="jump"><a class="btn solid" href="#shop">Shop the whole look</a></p>
      <div class="block"><h2>Styling tips</h2><ul class="tips">{tips}</ul></div>
      <div class="block" id="shop"><h2>Shop this look</h2>
        <div class="size" id="sizes" role="radiogroup" aria-label="Your fit"><span>Your fit:</span>{size_chips}</div>
        <div class="prods">{"".join(rows)}</div>
        <p class="disc">Prices change often, so check the current price on Amazon. Budget finds and Premium picks open the same search filtered by price. {DISCLOSURE}</p></div>
      <p class="save"><a class="btn ghost" href="{PIN}{o["pin"]}/" target="_blank" rel="noopener">Save on Pinterest</a></p>
    </div>
  </article>
  <section class="sec">
    <div class="sec-head"><h2>More looks</h2></div>
    <div class="grid">{"".join(card(x, r) for x in related[:4])}</div>
  </section>"""
        write(f"outfits/{o['slug']}/index.html",
              page(2, f"{o['title']} | {SITE}", o["intro"], body, f"outfits/{o['slug']}/", o["pin"], nav="shop", shopbar=shopbar))

    # ---------- seasons ----------
    r = "../"
    stiles = "".join(tile(f"{r}seasons/{k}/index.html", f"{r}img/{pin}.jpg", t, b) for k, t, b, pin in SEASONS)
    body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Seasons</nav>
  <section class="pagehead"><h1>Seasonal capsules</h1>
    <p class="lead">Eight pieces per season that mix into dozens of office outfits.</p></section>
  <section class="sec" style="margin-top:28px"><div class="cats">{stiles}</div></section>
  <section class="sec">{newsletter(r)}</section>"""
    write("seasons/index.html", page(1, f"Seasonal capsules | {SITE}", "A capsule wardrobe for every season, with outfits and shopping links.", body, "seasons/", nav="seasons"))
    r = "../../"
    for k, t, blurb, pin in SEASONS:
        rows = "".join(prod_row(n, q, cap, None, {}, f"{k}/{i}") for i, (n, q, cap) in enumerate(CAPSULES[k], start=1))
        items = [o for o in OUTFITS if k in o["seasons"]]
        size_html = f'<div class="size" id="sizes" role="radiogroup" aria-label="Your fit"><span>Your fit:</span>{size_chips}</div>'
        body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / <a href="{r}seasons/index.html">Seasons</a> / {t}</nav>
  <section class="pagehead"><h1>{t} capsule</h1><p class="lead">{esc(blurb)} Eight pieces to build your {t.lower()} work wardrobe.</p></section>
  <section class="sec" style="margin-top:28px"><h2>The 8 pieces</h2><div style="margin-top:14px">{size_html}<div class="prods">{rows}</div>
    <p class="disc">Prices change often, so check the current price on Amazon. {DISCLOSURE}</p></div></section>
  <section class="sec"><div class="sec-head"><h2>{t} outfits</h2></div><div class="grid">{"".join(card(o, r) for o in items)}</div></section>
  <section class="sec">{newsletter(r)}</section>"""
        write(f"seasons/{k}/index.html", page(2, f"{t} capsule wardrobe | {SITE}", f"{blurb} A capsule of 8 pieces with outfits and shopping links.", body, f"seasons/{k}/", pin, nav="seasons"))

    # ---------- quiz ----------
    r = "../"
    body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Style quiz</nav>
  <section class="pagehead"><h1>What is your office style?</h1><p class="lead">Five quick questions. Then outfits picked for you.</p></section>
  <div class="quiz" id="quiz"><p class="lead">The quiz needs JavaScript. You can still <a href="{r}shop/index.html" style="text-decoration:underline">browse all outfits</a>.</p></div>"""
    write("quiz/index.html", page(1, f"Style quiz | {SITE}", "Take the quiz to find your office style and the outfits that match it.", body, "quiz/", nav="quiz"))

    # ---------- capsule builder ----------
    groups = ""
    for gk, gn in BUILDER_GROUPS:
        picks = "".join(
            f'<label class="pick"><input type="checkbox" data-g="{gk}" data-n="{esc(n)}" data-q="{esc(q)}">{esc(n)}</label>'
            for _, g, n, q, _ in BUILDER if g == gk)
        groups += f'<div class="group"><h3>{gn}</h3><div class="picks">{picks}</div></div>'
    body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Build a capsule</nav>
  <section class="pagehead"><h1>Build your capsule</h1><p class="lead">Tick the pieces you own or want. See how many outfits they make, then shop what is missing.</p></section>
  <div class="builder sec" style="margin-top:28px" id="builder">
    <div style="display:grid;gap:26px">{groups}</div>
    <aside class="sum" id="sum" aria-live="polite"></aside>
  </div>
  <p class="disc" style="margin-top:18px">The count is an estimate: tops x bottoms, plus dresses, times your layers. {DISCLOSURE}</p>"""
    write("capsule-builder/index.html", page(1, f"Build your capsule wardrobe | {SITE}", "Pick your pieces and see how many work outfits they make.", body, "capsule-builder/", nav="capsule"))

    # ---------- checklist ----------
    items = "".join(f"<li>{esc(c)}</li>" for c in CHECKLIST)
    body = f"""
  <nav class="crumbs noprint" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Checklist</nav>
  <section class="pagehead"><h1>Capsule wardrobe checklist</h1>
    <p class="lead">The work wardrobe essentials, ready to tick off.</p></section>
  <ul class="check">{items}</ul>
  <p class="noprint" style="margin-top:22px;display:flex;flex-wrap:wrap;gap:10px">
    <button class="btn solid" type="button" data-print>Print or save as PDF</button>
    <a class="btn ghost" href="{PIN}{CHECKLIST_PIN}/" target="_blank" rel="noopener">See it on Pinterest</a></p>
  <section class="sec noprint">{newsletter(r)}</section>"""
    write("checklist/index.html", page(1, f"Capsule wardrobe checklist | {SITE}", "A printable checklist of work wardrobe essentials.", body, "checklist/"))

    # ---------- saved ----------
    body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / Saved outfits</nav>
  <section class="pagehead"><h1>Saved outfits</h1><p class="lead">Your favorites, stored on this device.</p></section>
  <section class="sec" style="margin-top:28px">
    <p id="savedEmpty" class="lead">Nothing saved yet. Tap the heart on any outfit to keep it here. <a href="{r}shop/index.html" style="text-decoration:underline">Browse outfits</a></p>
    <div class="grid" id="savedGrid"></div>
  </section>"""
    write("saved/index.html", page(1, f"Saved outfits | {SITE}", "Your saved outfits.", body, "saved/"))

    # ---------- about ----------
    intro = f"<p>{esc(CFG['about_intro'])}</p>" if CFG["about_intro"] else ""
    photo = f'<img src="{r}{esc(CFG["about_photo"])}" alt="">' if CFG["about_photo"] else ""
    body = f"""
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{r}index.html">Home</a> / About</nav>
  <section class="pagehead"><h1>About {SITE}</h1></section>
  <section class="prose">
    {photo}{intro}
    <h2>What this is</h2>
    <p>Office outfit ideas and workwear essentials for the corporate girlie. Affordable business casual looks, capsule wardrobe staples and style inspiration, with every outfit broken down into the pieces you can shop.</p>
    <h2>How the pieces are chosen</h2>
    <p>Affordable where possible, versatile, and office-appropriate. The palette is neutral, so pieces mix with each other and one purchase works in many outfits.</p>
    <h2>How the links work</h2>
    <p>Every Pinterest pin links to its matching outfit page here. The shop buttons take you to Amazon. {DISCLOSURE} It costs you nothing extra.</p>
    <p style="margin-top:22px"><a class="btn solid" href="{PROFILE}" target="_blank" rel="noopener">Follow on Pinterest</a></p>
  </section>
  <section class="sec">{newsletter(r)}</section>"""
    write("about/index.html", page(1, f"About | {SITE}", "About The Corporate Closet and how the shop links work.", body, "about/", nav="about"))

    # ---------- thanks, 404, robots ----------
    body = f"""<section class="pagehead" style="padding:28px 0"><h1>Thank you</h1><p class="lead">You are on the list. Your first outfit is on its way.</p>
    <p style="margin-top:20px"><a class="btn solid" href="{r}shop/index.html">Shop outfits</a></p></section>"""
    write("thanks/index.html", page(1, f"Thank you | {SITE}", "Thanks for subscribing.", body, "thanks/"))
    write("404.html", page(0, f"Page not found | {SITE}", "Page not found.",
          '<section class="pagehead" style="padding:28px 0"><h1>Page not found</h1><p class="lead">That page does not exist. Try the shop instead.</p>'
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
    print(f"built {len(OUTFITS)} outfits, {len(CATEGORIES)} categories, {len(SEASONS)} seasons")


if __name__ == "__main__":
    build()
