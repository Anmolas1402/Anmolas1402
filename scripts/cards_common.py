"""Shared palette and SVG helpers for every card."""
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

THEMES = {
    "dark": dict(bg="#0e0e12", bg2="#16161c", line="#26262e", text="#f4f5f7", sub="#a3aab6",
                 mute="#6b7280", accent="#ff5a1f", accent_soft="#ff5a1f", green="#4ade80",
                 dot="#f4f5f7", chip="#1c1c23"),
    "light": dict(bg="#fbfaf7", bg2="#f2f0ea", line="#e4e1d8", text="#1a1a1a", sub="#4b5160",
                  mute="#8b93a1", accent="#e8480c", accent_soft="#e8480c", green="#16a34a",
                  dot="#1a1a1a", chip="#efece4"),
}

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

STYLE = f"""<style>
text{{font-family:{SANS}}}
.m{{font-family:{MONO}}}
@keyframes ping{{0%{{transform:scale(1);opacity:.7}}80%,100%{{transform:scale(3.2);opacity:0}}}}
@keyframes tw{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes scan{{0%{{transform:translateX(-60px);opacity:0}}15%,85%{{opacity:.9}}100%{{transform:translateX(420px);opacity:0}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2.6s ease-out infinite}}
.tw{{animation:tw 3.2s ease-in-out infinite}}
.grow{{transform-box:fill-box;transform-origin:left;animation:grow 1.4s cubic-bezier(.2,.8,.2,1) both}}
.rise{{animation:rise .7s ease-out both}}
.blink{{animation:blink 1.1s steps(1) infinite}}
.scan{{animation:scan 7s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def svg(w, h, label, body, t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{STYLE}'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{t["bg"]}" stroke="{t["line"]}"/>'
            f'{body}</svg>')


def txt(x, y, s, size, fill, weight=400, mono=False, anchor="start", extra=""):
    cls = ' class="m"' if mono else ""
    return (f'<text{cls} x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def write(name, theme, content):
    with open(os.path.join(ASSETS, f"{name}-{theme}.svg"), "w") as f:
        f.write(content)


