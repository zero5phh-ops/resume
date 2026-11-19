#!/usr/bin/env python3
"""Build the resume site from i18n/<lang>.json.

Per language: a simple home page (short intro + a six-card menu) and detail pages
(software, SOL Studio, Onset, experience, awards, films, photo, skills) plus `all`,
the whole resume on one page (used for printing / the PDF).

  zh: index.html           zh/<page>.html
  en: en.html              en/<page>.html     (same for ms, ja, ko)

Run: python3 build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
LANGS = [  # code, home file, <html lang>, label in the switcher
    ("zh", "index.html", "zh-Hant", "中文"),
    ("en", "en.html", "en", "EN"),
    ("ms", "ms.html", "ms", "BM"),
    ("ja", "ja.html", "ja", "日本語"),
    ("ko", "ko.html", "ko", "한국어"),
]
BASE_URL = "https://zero5phh-ops.github.io/resume/"
LATIN = "Noto+Sans:wght@400;500;700;900&family=Noto+Serif:wght@600;900&family=Noto+Sans+TC:wght@400;700&family=Noto+Serif+TC:wght@900"
FONTS = {
    "en": LATIN,
    "ms": LATIN,
    "ja": "Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@600;900&family=Noto+Sans+TC:wght@400;700",
    "ko": "Noto+Sans+KR:wght@400;500;700;900&family=Noto+Serif+KR:wght@600;900&family=Noto+Sans+TC:wght@400;700",
}
DEFAULT_FONT = "Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@600;900"
EXT = 'target="_blank" rel="noopener"'
CUR = ' aria-current="page"'
NOW = ' class="now"'
HL = ' class="hl"'
DETAIL = ["software", "sol", "onset", "experience", "awards", "films", "photo", "skills", "all"]
PARENT = {"sol": "software", "onset": "software"}
MENU = ["software", "experience", "awards", "films", "photo", "skills"]
SOL_URL = "https://studio.neuroyoung.co/login"
HANDBOOK_URL = "https://zero5phh-ops.github.io/onset-handbook/"
VPIPE_URL = "https://github.com/zero5phh-ops/vpipe-workbench"


# ---------------------------------------------------------------- paths
def path(code, page):
    if page == "home":
        return next(f for c, f, _, _ in LANGS if c == code)
    return f"{code}/{page}.html"


def rel(depth, code, page):
    return "../" * depth + path(code, page)


def abs_url(code, page):
    return (BASE_URL + path(code, page)).replace("index.html", "")


def strip(s):
    return re.sub("<[^>]+>", "", s)


# ---------------------------------------------------------------- small parts
def level(n):
    return "".join(f'<i class="{"on" if i <= n else ""}"></i>' for i in range(1, 6))


def skill_row(n, l, s=""):
    sub = f" <small>· {s}</small>" if s else ""
    return f'<div class="skill"><span>{n}{sub}</span><span class="lv" aria-label="{l} / 5">{level(l)}</span></div>'


def vid(v):
    pic = (f'<img src="https://i.ytimg.com/vi/{v["yt"]}/mqdefault.jpg" alt="" loading="lazy">'
           if v.get("yt") else f'<div class="ph">{v.get("ph", "")}</div>')
    return (f'<a class="vid" href="{v["url"]}" {EXT}>{pic}<div><div class="t">{v["t"]}</div>'
            f'<div class="d">{v["d"]}</div></div></a>')


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "\n".join(f"<li>{x}</li>" for x in items) + "</ul>"


def tag(kind):
    return {"priv": '<span class="vis priv">PRIVATE</span>',
            "pub": '<span class="vis pub">PUBLIC</span>',
            "mit": '<span class="vis pub">PUBLIC · MIT</span>'}[kind]


# ---------------------------------------------------------------- blocks
def hero(t, simple):
    lead = t["home"]["tagline"] if simple else t["hero"]["lead"]
    h = t["hero"]
    return f'''<header class="wrap hero{" simple" if simple else ""}" id="top">
  <div>
    <div class="eyebrow">Director · Photographer · AI Workflow Builder</div>
    <h1>{h["name"]}<small>{h["sub"]}</small></h1>
    <p class="lead">{lead}</p>
    <div class="facts">
      <span class="chip">📍 {h["loc"]}</span>
      <span class="chip">{h["born"]}</span>
      <span class="chip">{h["langs"]}</span>
    </div>
    <div class="links">
      <a class="btn primary" href="https://github.com/zero5phh-ops" {EXT}>GitHub</a>
      <a class="btn" href="https://www.linkedin.com/in/lonny-pang-a0172687/" {EXT}>LinkedIn</a>
      <a class="btn" href="https://www.instagram.com/zero5phh/" {EXT}>Instagram</a>
      <a class="btn" href="https://www.facebook.com/zero5phh" {EXT}>Facebook</a>
      <a class="btn" href="https://www.flickr.com/photos/zero5phh" {EXT}>{h["flickr"]}</a>
    </div>
  </div>
  <div class="portrait">
    <img src="{{P}}assets/portrait.jpg" alt="{h["name"]} Lonny Pang">
    <div class="badge"><b>2010</b>Photographer of the Year<br>{h["badge"]}</div>
  </div>
</header>'''


def menu(t, code, depth):
    cards = []
    for i, k in enumerate(MENU, 1):
        cards.append(
            f'<a href="{rel(depth, code, k)}"><span class="n">0{i}</span><span class="t">{t["nav"][k]}</span>'
            f'<span class="d">{t["home"]["cards"][k]}</span><span class="arrow">→</span></a>')
    return f'<section class="menu-sec"><div class="wrap"><h2 class="menu-title">{t["ui"]["menu_title"]}</h2><nav class="menu">' + "\n".join(cards) + "</nav></div></section>"


def proj_card(name, kind, summary, href=None, go="", external=False):
    head = f'<div class="phead"><h3>{name}</h3>{tag(kind)}</div>'
    body = f"{head}<p>{summary}</p>"
    if href:
        ext = f" {EXT}" if external else ""
        return f'<a class="proj" href="{href}"{ext}>{body}<span class="go">{go} {"↗" if external else "→"}</span></a>'
    return f'<div class="proj static">{body}</div>'


def games_links(t):
    return "\n".join(
        f'<a class="mini" href="{g["url"]}" {EXT}><span class="t">{g["t"]}</span><span class="d">{g["d"]}</span>'
        f'<span class="u">{g["url"].replace("https://", "").rstrip("/")}</span></a>' for g in t["games"]["items"])


def software_list(t, code, depth):
    ui = t["ui"]
    cards = [
        proj_card("SOL Studio", "priv", t["sol"]["summary"], rel(depth, code, "sol"), ui["details"]),
        proj_card("Onset 3.0", "priv", t["onset"]["summary"], rel(depth, code, "onset"), ui["details"]),
        proj_card("Onset Handbook", "pub", t["handbook"]["summary"], HANDBOOK_URL, t["handbook"]["link"], True),
        proj_card("vpipe工作台 · vpipe Workbench", "mit", t["vpipe"]["summary"], VPIPE_URL, "GitHub", True),
        proj_card("AI Stock Research Desk", "priv", t["stock"]["summary"]),
    ]
    games = (f'<div class="proj static"><div class="phead"><h3>{t["games"]["title"]}</h3>{tag("pub")}</div>'
             f'<p>{t["games"]["summary"]}</p><details class="fold"><summary>{ui["all_games"]}</summary>'
             f'<div class="grid3">{games_links(t)}</div></details></div>')
    return "\n".join(cards) + "\n" + games


def points(items):
    return '<div class="points">' + "".join(
        f'<div class="point"><b>{p["t"]}</b><span>{p["d"]}</span></div>' for p in items) + "</div>"


def feature_block(t, key, page_mode):
    feats = ul(t[key]["features"], "feat")
    if page_mode:
        return f'<details class="fold"><summary>{t["ui"]["all_features"]}</summary>{feats}</details>'
    return feats


def sol_block(t, page_mode):
    s = t["sol"]
    stack = ("<span>Next.js</span><span>Fastify</span><span>Prisma / SQLite</span><span>Expo (React Native)</span>"
             "<span>FFmpeg</span><span>faster-whisper</span><span>Claude API / Claude CLI</span><span>HeyGen</span>"
             "<span>GoHighLevel API</span><span>Docker</span><span>Cloudflare Tunnel</span><span>MCP</span>")
    return f'''<p class="meta">{s["meta"]}</p>
    <p class="pdesc">{s["desc"]}</p>
    <div class="links" style="margin-bottom:18px"><a class="btn primary" href="{SOL_URL}" {EXT}>{s["open"]} ↗</a></div>
    {points(s["points"]) if page_mode else ""}
    {feature_block(t, "sol", page_mode)}
    <div class="stack">{stack}</div>
    <figure class="shot"><a href="{SOL_URL}" {EXT}><img src="{{P}}assets/sol-studio-landing.jpg" alt="SOL Studio landing page" loading="lazy"></a><figcaption>{s["caption"]}</figcaption></figure>'''


def onset_block(t, page_mode):
    o = t["onset"]
    stack = ("<span>React</span><span>TypeScript</span><span>Vite</span><span>Node helper</span><span>FFmpeg</span>"
             "<span>Whisper</span><span>Demucs</span><span>Claude CLI</span><span>Tauri 2 / Rust</span><span>Swift</span>"
             "<span>Cloudflare Workers · D1 · Durable Objects</span><span>MLX Whisper</span><span>WebGL / Three.js</span><span>MCP</span>")
    shots = f'''<div class="shots">
      <figure class="shot wide"><img src="{{P}}assets/onset-editing.jpg" alt="Onset 3.0 Editing" loading="lazy"><figcaption>{o["cap_editing"]}</figcaption></figure>
      <figure class="shot wide"><img src="{{P}}assets/onset-board.jpg" alt="Animation board" loading="lazy"><figcaption>{o["cap_board"]}</figcaption></figure>
      <figure class="shot"><img src="{{P}}assets/onset-script.jpg" alt="Create Script" loading="lazy"><figcaption>{o["cap_script"]}</figcaption></figure>
      <figure class="shot"><img src="{{P}}assets/onset-recording.jpg" alt="Recording" loading="lazy"><figcaption>{o["cap_recording"]}</figcaption></figure>
      <figure class="shot wide"><img src="{{P}}assets/onset-phone.jpg" alt="Onset on iPhone" loading="lazy"><figcaption>{o["cap_phone"]}</figcaption></figure>
      <figure class="shot"><img src="{{P}}assets/onset-ipad.jpg" alt="Onset on iPad" loading="lazy"><figcaption>{o["cap_ipad"]}</figcaption></figure>
      <figure class="shot"><img src="{{P}}assets/onset-start.jpg" alt="Onset Start" loading="lazy"><figcaption>{o["cap_start"]}</figcaption></figure>
    </div>'''
    handbook = (f'<div class="links" style="margin-bottom:18px"><a class="btn primary" href="{HANDBOOK_URL}" {EXT}>'
                f'{t["handbook"]["link"]} ↗</a></div>')
    return f'''<p class="meta">{o["meta"]}</p>
    <p class="pdesc">{o["desc"]}</p>
    {handbook}
    {points(o["points"]) if page_mode else ""}
    {feature_block(t, "onset", page_mode)}
    <div class="stack">{stack}</div>
    {shots}'''


def software_full(t):
    out = [f'<article class="card project"><div class="phead"><h3>SOL Studio</h3>{tag("priv")}</div>{sol_block(t, False)}</article>',
           f'<article class="card project"><div class="phead"><h3>Onset 3.0</h3>{tag("priv")}</div>{onset_block(t, False)}</article>',
           f'<article class="card project"><div class="phead"><h3>Onset Handbook</h3>{tag("pub")}<span class="meta">{t["handbook"]["meta"]}</span></div>'
           f'<p class="pdesc">{t["handbook"]["desc"]}</p><div class="links"><a class="btn primary" href="{HANDBOOK_URL}" {EXT}>{HANDBOOK_URL.replace("https://", "")} ↗</a></div></article>',
           f'<article class="card project"><div class="phead"><h3>vpipe工作台 · vpipe Workbench</h3>{tag("mit")}<span class="meta">2026-11</span></div>'
           f'<p class="pdesc">{t["vpipe"]["desc"]}</p><div class="links"><a class="btn primary" href="{VPIPE_URL}" {EXT}>github.com/zero5phh-ops/vpipe-workbench ↗</a></div></article>',
           f'<article class="card project"><div class="phead"><h3>AI Stock Research Desk</h3>{tag("priv")}<span class="meta">{t["stock"]["meta"]}</span></div>'
           f'<p class="pdesc">{t["stock"]["desc"]}</p></article>',
           f'<h4>{t["games"]["title"]}</h4><div class="grid3">{games_links(t)}</div>']
    return "\n".join(out)


def inner_experience(t):
    e = t["exp"]
    jobs = "\n".join(
        f'<li{NOW if j.get("now") else ""}><div class="yr">{j["yr"]}</div><div class="role">{j["role"]}</div>'
        f'<div class="org">{j["org"]}</div>' + (f'<p>{j["p"]}</p>' if j.get("p") else "") + "</li>"
        for j in e["jobs"])
    return f'<ul class="timeline">{jobs}</ul><h4>{e["edu_title"]}</h4><p>{e["edu"]}</p>'


def inner_awards(t):
    cols = ["\n".join(
        f'<li{HL if a.get("hl") else ""}><span>{a["y"]}</span>{a["t"]}</li>' for a in col)
        for col in t["aw"]["cols"]]
    return f'<div class="two"><ul class="awards">{cols[0]}</ul><ul class="awards">{cols[1]}</ul></div>'


def inner_films(t):
    f = t["films"]
    return (f'<h4>{f["tzuchi"]}</h4><div class="vids">' + "\n".join(vid(v) for v in f["tzuchi_items"]) +
            f'</div><h4>{f["brand"]}</h4><div class="vids">' + "\n".join(vid(v) for v in f["brand_items"]) + "</div>")


def inner_photo(t):
    return '<div class="gallery">' + "\n".join(
        f'<figure><img src="{{P}}assets/{g["img"]}" alt="{strip(g["cap"])}" loading="lazy"><figcaption>{g["cap"]}</figcaption></figure>'
        for g in t["photo"]["items"]) + "</div>"


def inner_skills(t):
    s = t["skills"]
    rows = "\n".join(skill_row(x["n"], x["l"], x.get("s", "")) for x in s["items"])
    langs = "\n".join(skill_row(x["n"], x["l"]) for x in s["langs"])
    return (f'<div class="skills">{rows}</div><div class="two" style="margin-top:32px"><div><h4 style="margin-top:0">{s["lang_title"]}</h4>'
            f'<div class="skills" style="grid-template-columns:1fr">{langs}</div></div><div><h4 style="margin-top:0">{s["hobby_title"]}</h4>'
            f'<p>{s["hobby"]}</p></div></div>')


# ---------------------------------------------------------------- pages
def shell(code, t, page, title, desc, body, depth):
    html_lang = next(h for c, _, h, _ in LANGS if c == code)
    fonts = "https://fonts.googleapis.com/css2?family=" + FONTS.get(code, DEFAULT_FONT) + "&display=swap"
    alts = "\n".join(f'<link rel="alternate" hreflang="{h}" href="{abs_url(c, page)}">' for c, _, h, _ in LANGS)
    langs = "".join(
        f'<a href="{rel(depth, c, page)}" hreflang="{h}"{CUR if c == code else ""}>{lab}</a>' for c, _, h, lab in LANGS)
    if page == "home":
        left = f'<a class="brand" href="#top">{t["nav"]["brand"]}</a>'
    else:
        parent = PARENT.get(page, "home")
        label = t["ui"]["back_sw"] if parent == "software" else t["ui"]["back"]
        left = f'<a class="back" href="{rel(depth, code, parent)}">{label}</a>'
    css = (ROOT / "src/style.css").read_text()
    P = "../" * depth
    footer_extra = ""
    if page == "home":
        footer_extra = (f'<p class="homefoot"><a class="btn" href="{rel(depth, code, "all")}">{t["home"]["full"]}</a> '
                        f'<span class="muted">{t["ui"]["all_note"]}</span></p>')
    out = f'''<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{strip(title)}</title>
<meta name="description" content="{strip(desc).replace('"', "&quot;")}">
{alts}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<nav class="top"><div class="wrap">
  {left}
  <span class="langs">{langs}</span>
  <button class="theme" id="theme" type="button" aria-label="{strip(t["nav"]["theme"])}">◐</button>
</div></nav>
{body}
<footer><div class="wrap">{footer_extra}{t["footer"]} · <a href="https://github.com/zero5phh-ops" {EXT}>github.com/zero5phh-ops</a></div></footer>
<script>
const root=document.documentElement,key="resume-theme";
try{{const t=localStorage.getItem(key);if(t)root.dataset.theme=t}}catch(e){{}}
document.getElementById("theme").onclick=()=>{{const dark=root.dataset.theme?root.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;root.dataset.theme=dark?"light":"dark";try{{localStorage.setItem(key,root.dataset.theme)}}catch(e){{}}}};
</script>
</body>
</html>
'''
    return out.replace("{P}", P)


def detail(title, sub, inner):
    s = f'<p class="sub">{sub}</p>' if sub else ""
    return f'<main class="wrap detail"><h1 class="ptitle">{title}</h1>{s}{inner}</main>'


def section(sid, title, sub, inner):
    s = f'<p class="sub">{sub}</p>' if sub else ""
    return f'<section id="{sid}"><div class="wrap"><h2>{title}</h2>{s}{inner}</div></section>'


def build_page(code, t, page, depth):
    nav = t["nav"]
    brand = nav["brand"]
    if page == "home":
        body = hero(t, True) + "\n" + menu(t, code, depth)
        return shell(code, t, page, t["meta"]["title"], t["meta"]["description"], body, depth)
    if page == "all":
        body = (hero(t, False) +
                section("software", t["sw"]["title"], t["sw"]["sub"], software_full(t)) +
                section("experience", t["exp"]["title"], t["exp"]["sub"], inner_experience(t)) +
                section("awards", t["aw"]["title"], t["aw"]["sub"], inner_awards(t)) +
                section("films", t["films"]["title"], t["films"]["sub"], inner_films(t)) +
                section("photo", t["photo"]["title"], t["photo"]["sub"], inner_photo(t)) +
                section("skills", t["skills"]["title"], t["skills"]["sub"], inner_skills(t)))
        return shell(code, t, page, f'{t["home"]["full"]} · {brand}', t["meta"]["description"], body, depth)
    if page == "software":
        body = detail(nav["software"], t["sw"]["sub"], software_list(t, code, depth))
        title = nav["software"]
    elif page == "sol":
        body = detail("SOL Studio", "", sol_block(t, True))
        title = "SOL Studio"
    elif page == "onset":
        body = detail("Onset 3.0", "", onset_block(t, True))
        title = "Onset 3.0"
    else:
        inner = {"experience": inner_experience, "awards": inner_awards, "films": inner_films,
                 "photo": inner_photo, "skills": inner_skills}[page](t)
        sub = strip(t[{"experience": "exp", "awards": "aw", "films": "films", "photo": "photo", "skills": "skills"}[page]]["sub"])
        sub = "" if page in ("experience", "awards", "skills") else sub
        body = detail(nav[page], t[{"films": "films", "photo": "photo"}.get(page, "x")]["sub"] if page in ("films", "photo") else "", inner)
        title = nav[page]
    return shell(code, t, page, f"{title} · {brand}", t["meta"]["description"], body, depth)


def main():
    for code, _, _, _ in LANGS:
        src = ROOT / "i18n" / f"{code}.json"
        if not src.exists():
            print(f"skip {code}: no {src.name}")
            continue
        t = json.loads(src.read_text())
        (ROOT / path(code, "home")).write_text(build_page(code, t, "home", 0))
        (ROOT / code).mkdir(exist_ok=True)
        for page in DETAIL:
            (ROOT / path(code, page)).write_text(build_page(code, t, page, 1))
        print("wrote", code, 1 + len(DETAIL), "pages")


if __name__ == "__main__":
    main()
