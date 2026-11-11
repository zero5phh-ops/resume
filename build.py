#!/usr/bin/env python3
"""Build the resume pages: src/template.html + i18n/<lang>.json → index.html (中文) and en/ms/ja/ko .html.

Run: python3 build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
LANGS = [  # code, file, <html lang>, label in the switcher
    ("zh", "index.html", "zh-Hant", "中文"),
    ("en", "en.html", "en", "EN"),
    ("ms", "ms.html", "ms", "BM"),
    ("ja", "ja.html", "ja", "日本語"),
    ("ko", "ko.html", "ko", "한국어"),
]
BASE_URL = "https://zero5phh-ops.github.io/resume/"
FONTS = {
    "ja": "Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@600;900&family=Noto+Sans+TC:wght@400;700",
    "ko": "Noto+Sans+KR:wght@400;500;700;900&family=Noto+Serif+KR:wght@600;900&family=Noto+Sans+TC:wght@400;700",
}
DEFAULT_FONT = "Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@600;900"
EXT = 'target="_blank" rel="noopener"'
CUR = ' aria-current="page"'
NOW = ' class="now"'
HL = ' class="hl"'


def get(d, path):
    for k in path.split("."):
        d = d[k]
    return d


def level(n):
    return "".join(f'<i class="{"on" if i <= n else ""}"></i>' for i in range(1, 6))


def skill_row(n, l, s=""):
    sub = f" <small>· {s}</small>" if s else ""
    return f'<div class="skill"><span>{n}{sub}</span><span class="lv" aria-label="{l} / 5">{level(l)}</span></div>'


def vid(v):
    pic = (f'<img src="https://i.ytimg.com/vi/{v["yt"]}/mqdefault.jpg" alt="" loading="lazy">'
           if v.get("yt") else f'<div class="ph">{v.get("ph", "")}</div>')
    return f'<a class="vid" href="{v["url"]}" {EXT}>{pic}<div><div class="t">{v["t"]}</div><div class="d">{v["d"]}</div></div></a>'


def render(code, t):
    html = (ROOT / "src/template.html").read_text()
    blocks = {
        "@htmllang": next(h for c, _, h, _ in LANGS if c == code),
        "@css": (ROOT / "src/style.css").read_text(),
        "@fonts": "https://fonts.googleapis.com/css2?family=" + FONTS.get(code, DEFAULT_FONT) + "&display=swap",
        "@alternates": "\n".join(
            f'<link rel="alternate" hreflang="{h}" href="{BASE_URL}{"" if f == "index.html" else f}">'
            for _, f, h, _ in LANGS),
        "@langs": '<span class="langs">' + "".join(
            f'<a href="{f}" hreflang="{h}"{CUR if c == code else ""}>{lab}</a>'
            for c, f, h, lab in LANGS) + "</span>",
        "@list:sol.features": "\n".join(f"      <li>{x}</li>" for x in t["sol"]["features"]),
        "@list:onset.features": "\n".join(f"      <li>{x}</li>" for x in t["onset"]["features"]),
        "@games": "\n".join(
            f'    <a class="mini" href="{g["url"]}" {EXT}><span class="t">{g["t"]}</span><span class="d">{g["d"]}</span>'
            f'<span class="u">{g["url"].replace("https://", "").rstrip("/")}</span></a>' for g in t["games"]["items"]),
        "@jobs": "\n".join(
            f'    <li{NOW if j.get("now") else ""}><div class="yr">{j["yr"]}</div><div class="role">{j["role"]}</div>'
            f'<div class="org">{j["org"]}</div>{("<p>" + j["p"] + "</p>") if j.get("p") else ""}</li>' for j in t["exp"]["jobs"]),
        "@awards:0": "\n".join(
            f'      <li{HL if a.get("hl") else ""}><span>{a["y"]}</span>{a["t"]}</li>' for a in t["aw"]["cols"][0]),
        "@awards:1": "\n".join(
            f'      <li{HL if a.get("hl") else ""}><span>{a["y"]}</span>{a["t"]}</li>' for a in t["aw"]["cols"][1]),
        "@vids:tzuchi": "\n".join("    " + vid(v) for v in t["films"]["tzuchi_items"]),
        "@vids:brand": "\n".join("    " + vid(v) for v in t["films"]["brand_items"]),
        "@gallery": "\n".join(
            f'    <figure><img src="assets/{g["img"]}" alt="{re.sub("<[^>]+>", "", g["cap"])}" loading="lazy"><figcaption>{g["cap"]}</figcaption></figure>'
            for g in t["photo"]["items"]),
        "@skills": "\n".join("    " + skill_row(s["n"], s["l"], s.get("s", "")) for s in t["skills"]["items"]),
        "@langlevels": "\n".join("        " + skill_row(s["n"], s["l"]) for s in t["skills"]["langs"]),
    }

    def sub(m):
        key = m.group(1)
        if key.startswith("@"):
            return blocks[key]
        val = get(t, key)
        if key.startswith("meta.") or key == "nav.theme":  # attribute / <title> context: no tags
            val = re.sub("<[^>]+>", "", val).replace('"', "&quot;")
        return val

    out = re.sub(r"\{\{([^}]+)\}\}", sub, html)
    assert "{{" not in out, f"unfilled placeholder in {code}"
    return out


def main():
    for code, fname, _, _ in LANGS:
        src = ROOT / "i18n" / f"{code}.json"
        if not src.exists():
            print(f"skip {code}: no {src.name}")
            continue
        (ROOT / fname).write_text(render(code, json.loads(src.read_text())))
        print("wrote", fname)


if __name__ == "__main__":
    main()
