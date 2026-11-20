"""Shared palette and SVG helpers for every card."""
import base64
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

# Matched to GitHub's own canvas so the cards sit flush on the profile page.
THEMES = {
    "dark": dict(bg="#0d1117", bg2="#161b22", line="#30363d", text="#f0f6fc", sub="#9198a1",
                 mute="#6e7681", accent="#ff6a2b", green="#3fb950", chip="#161b22", tile="#1c2128",
                 dot="#f0f6fc", glow=".20"),
    "light": dict(bg="#ffffff", bg2="#f6f8fa", line="#d1d9e0", text="#1f2328", sub="#59636e",
                  mute="#818b98", accent="#e8530f", green="#1a7f37", chip="#f6f8fa", tile="#f6f8fa",
                  dot="#1f2328", glow=".10"),
}

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

STYLE = f"""<style>
text{{font-family:{SANS}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes ping{{0%{{transform:scale(1);opacity:.65}}80%,100%{{transform:scale(2.8);opacity:0}}}}
@keyframes tw{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes flow{{to{{stroke-dashoffset:-16}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
.orbit{{transform-box:view-box;animation:spin 14s linear infinite}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}}
.tw{{animation:tw 3.2s ease-in-out infinite}}
.grow{{transform-box:fill-box;transform-origin:left;animation:grow 1.4s cubic-bezier(.2,.8,.2,1) both}}
.flow{{stroke-dasharray:4 4;animation:flow 1.2s linear infinite}}
.float{{animation:float 4.5s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def svg(w, h, label, body, t, glow=None):
    g = ""
    if glow:
        gx, gy, r = glow
        g = (f'<defs><radialGradient id="glow" cx="{gx}" cy="{gy}" r="{r}" gradientUnits="userSpaceOnUse">'
             f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>'
             f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>'
             f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#glow)"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title>{STYLE}'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="{t["bg"]}" stroke="{t["line"]}"/>'
            f'{g}{body}</svg>')


def txt(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def img_uri(name):
    path = os.path.join(ROOT, "data", "img", name)
    mime = "image/jpeg" if name.endswith(".jpg") else "image/png"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def image(x, y, w, h, name, clip=None):
    c = f' clip-path="url(#{clip})"' if clip else ""
    u = img_uri(name)
    return (f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{u}" xlink:href="{u}"{c} '
            f'preserveAspectRatio="xMidYMid slice"/>')


def write(name, theme, content):
    with open(os.path.join(ASSETS, f"{name}-{theme}.svg"), "w") as f:
        f.write(content)
