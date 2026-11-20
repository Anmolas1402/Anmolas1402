"""Shared palette, fonts and SVG helpers.

The look is an Indian exam OMR sheet: white paper, pink drop-out ink for
everything printed, blue ballpoint for everything filled in. Fonts are
subset per card and embedded, so GitHub shows real type, not system fallbacks.
"""
import base64
import io
import os
from html import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

THEMES = {
    # paper sheet
    "light": dict(paper="#ffffff", print="#d9416f", rule="#f4c3d3", tint="#fdf0f4",
                  ink="#1d3a9a", text="#24222b", sub="#5d5866", mark="#24222b"),
    # the same sheet as a carbon copy, for dark mode
    "dark": dict(paper="#111633", print="#ff7aa2", rule="#4b2f55", tint="#1a1c3d",
                 ink="#c7d3ff", text="#eceaf3", sub="#a7a3b8", mark="#eceaf3"),
}

FONTS = {
    ("Barlow", 400): "barlow-latin-400-normal.woff2",
    ("Barlow", 500): "barlow-latin-500-normal.woff2",
    ("Barlow Condensed", 600): "barlow-condensed-latin-600-normal.woff2",
    ("Barlow Condensed", 700): "barlow-condensed-latin-700-normal.woff2",
    ("Kalam", 400): "kalam-latin-400-normal.woff2",
    ("Hind", 400): "hind-latin-400-normal.woff2",
    ("Hind", 600): "hind-latin-600-normal.woff2",
    ("Hind", 700): "hind-latin-700-normal.woff2",
    ("Hind Deva", 600): "hind-devanagari-600-normal.woff2",
}
ROLE = {
    "body": ("Barlow", 400), "bodym": ("Barlow", 500),
    "cond": ("Barlow Condensed", 600), "condb": ("Barlow Condensed", 700),
    "pen": ("Kalam", 400),
    "hind": ("Hind", 400), "hinds": ("Hind", 600), "hindb": ("Hind", 700),
    "deva": ("Hind Deva", 600),
}

_used = {}  # (family, weight) -> set of chars, for the card being built


def _font_css():
    css = []
    for key, chars in _used.items():
        path = os.path.join(ROOT, "data", "fonts", FONTS[key])
        f = TTFont(path)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        s = subset.Subsetter(opts)
        s.populate(text="".join(sorted(chars | {" "})))
        s.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff2"
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        css.append(f"@font-face{{font-family:'{key[0]}';font-weight:{key[1]};"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(css)


MOTION = """
@keyframes fill{from{transform:scale(0)}to{transform:scale(1)}}
.fill{transform-box:fill-box;transform-origin:center;animation:fill .35s cubic-bezier(.3,1.6,.5,1) both}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg(w, h, label, body, t, frame=True, extra_css=""):
    css = _font_css()
    _used.clear()
    if not frame:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
                f'<title>{escape(label)}</title><style>{css}{MOTION}{extra_css}</style>{body}</svg>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><style>{css}{MOTION}</style>'
            f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="3" fill="{t["paper"]}" stroke="{t["print"]}" stroke-width="1.5"/>'
            f'{body}</svg>')


def txt(x, y, s, size, fill, role="body", anchor="start", extra=""):
    fam, wt = ROLE[role]
    _used.setdefault((fam, wt), set()).update(s)
    return (f'<text x="{x}" y="{y}" font-family="\'{fam}\'" font-weight="{wt}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def img_uri(name):
    path = os.path.join(ROOT, "data", "img", name)
    mime = "image/jpeg" if name.endswith(".jpg") else "image/png"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def image(x, y, w, h, name, clip=None, extra=""):
    c = f' clip-path="url(#{clip})"' if clip else ""
    u = img_uri(name)
    return (f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{u}" xlink:href="{u}"{c} '
            f'preserveAspectRatio="xMidYMid slice" {extra}/>')


def write(name, theme, content):
    with open(os.path.join(ASSETS, f"{name}-{theme}.svg"), "w") as f:
        f.write(content)
