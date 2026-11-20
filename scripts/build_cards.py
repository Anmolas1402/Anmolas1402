"""Builds every static card on the profile, in dark and light.

Run: python3 scripts/build_cards.py
Inputs: data/ncr-pins.json (snapshot of the NCR Hiring Map), data/icons.json
(Simple Icons paths), data/img/ (photo and logos). Output: assets/*.svg.
Every word and number on a card lives in this file.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards_common import ROOT, THEMES, svg, txt, image, write  # noqa: E402

pins = json.load(open(os.path.join(ROOT, "data", "ncr-pins.json")))
PTS = pins["pts"]  # [lat, lng, verified, hiring]
ICONS = json.load(open(os.path.join(ROOT, "data", "icons.json")))


# ------------------------------------------------------------------ helpers
def pill(x, y, label, t, dot=True):
    w = 26 + len(label) * 7.4 + (10 if dot else 0)
    out = [f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{t["chip"]}" stroke="{t["line"]}"/>']
    tx = x + 13
    if dot:
        out.append(f'<circle class="ping" cx="{x+14}" cy="{y+12}" r="3.5" fill="{t["green"]}"/>')
        out.append(f'<circle cx="{x+14}" cy="{y+12}" r="3.5" fill="{t["green"]}"/>')
        tx = x + 25
    out.append(txt(tx, y + 16.5, label, 11, t["text"], 700, extra='letter-spacing="1.2"'))
    return "".join(out)


def arrow(x, y, t, size=18):
    return (f'<path d="M{x} {y+size} L{x+size} {y} M{x+5} {y} H{x+size} V{y+size-5}" fill="none" '
            f'stroke="{t["sub"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def icon(key, x, y, size, t, theme):
    ic = ICONS[key]
    col = "#" + ic["hex"]
    if theme == "dark" and lum(ic["hex"]) < 0.25:
        col = t["text"]
    if theme == "light" and lum(ic["hex"]) > 0.85:
        col = t["text"]
    s = size / 24
    return f'<path transform="translate({x} {y}) scale({s:.4f})" d="{ic["path"]}" fill="{col}"/>'


def project(pts, x0, y0, w, h, pad=4):
    lats_s, lngs_s = sorted(p[0] for p in pts), sorted(p[1] for p in pts)
    k = int(len(pts) * 0.01)
    la0, la1, lo0, lo1 = lats_s[k], lats_s[-k - 1], lngs_s[k], lngs_s[-k - 1]
    kx = math.cos(math.radians((la0 + la1) / 2))
    sw, sh = (lo1 - lo0) * kx, la1 - la0
    sc = min((w - 2 * pad) / sw, (h - 2 * pad) / sh)
    ox, oy = x0 + (w - sw * sc) / 2, y0 + (h - sh * sc) / 2
    f = lambda la, lo: (ox + (lo - lo0) * kx * sc, oy + (la1 - la) * sc)
    inside = lambda p: la0 <= p[0] <= la1 and lo0 <= p[1] <= lo1
    return f, inside


# ------------------------------------------------------------------ hero
def hero(t, theme):
    W, H = 840, 352
    cx, cy, r = 680, 196, 96
    b = []
    b.append(txt(40, 50, "@ANMOLAS1402", 12, t["accent"], 700, extra='letter-spacing="2.4"'))
    b.append(f'<circle class="ping" cx="{W-196}" cy="46" r="4" fill="{t["green"]}"/><circle cx="{W-196}" cy="46" r="4" fill="{t["green"]}"/>')
    b.append(txt(W - 40, 50, "Open to work, Gurugram", 13, t["sub"], 500, anchor="end"))
    b.append(f'<line x1="40" y1="68" x2="{W-40}" y2="68" stroke="{t["line"]}"/>')
    b.append(f'<line class="grow" x1="40" y1="68" x2="150" y2="68" stroke="{t["accent"]}" stroke-width="2"/>')
    b.append(txt(36, 146, "Anmol", 76, t["text"], 800, extra='letter-spacing="-3"'))
    b.append(txt(36, 222, "Sethi.", 76, t["accent"], 800, extra='letter-spacing="-3"'))
    b.append(txt(40, 258, "Product ops from Gurugram, India. I build the systems", 15, t["sub"]))
    b.append(txt(40, 279, "behind products that scale, and the tools that run them.", 15, t["sub"]))
    x = 40
    for c in ["Product ops", "Data", "AI tools", "0 → 1"]:
        w = 30 + len(c) * 7.6
        b.append(f'<rect x="{x}" y="300" width="{w:.0f}" height="28" rx="14" fill="none" stroke="{t["line"]}"/>')
        b.append(txt(x + w / 2, 319, c, 13, t["text"], 500, anchor="middle"))
        x += w + 10
    # photo with orbit
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r+26}" fill="none" stroke="{t["accent"]}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="2 6"/>')
    b.append(f'<g class="orbit" style="transform-origin:{cx}px {cy}px"><circle cx="{cx}" cy="{cy-r-26}" r="5" fill="{t["accent"]}"/></g>')
    b.append(f'<clipPath id="ph"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    b.append(image(cx - r, cy - r, 2 * r, 2 * r, "anmol.jpg", clip="ph"))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["line"]}" stroke-width="2"/>')
    b.append(f'<path d="M{W-56} 98 v14 M{W-63} 105 h14" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round"/>')
    label = ("Anmol Sethi. Product ops from Gurugram, India. I build the systems behind products that scale, "
             "and the tools that run them. Open to work.")
    return svg(W, H, label, "".join(b), t, glow=(cx, cy, 300))


# ------------------------------------------------------------------ numbers
NUMBERS = [
    ("500K+", "students served"),
    ("1 → 14", "exams scaled"),
    ("99.4%", "predictor accuracy"),
    ("100+", "interns onboarded"),
    (f'{pins["total"]:,}', "startups mapped"),
]


def numbers(t, theme):
    W, H = 840, 132
    cw = (W - 40) / len(NUMBERS)
    b = []
    for i, (v, l) in enumerate(NUMBERS):
        x = 20 + cw * i + cw / 2
        if i:
            b.append(f'<line x1="{20 + cw*i:.0f}" y1="34" x2="{20 + cw*i:.0f}" y2="98" stroke="{t["line"]}"/>')
        col = t["accent"] if i in (0, len(NUMBERS) - 1) else t["text"]
        b.append(txt(x, 74, v, 34, col, 800, anchor="middle", extra='letter-spacing="-1"'))
        b.append(txt(x, 100, l, 14, t["sub"], anchor="middle"))
    return svg(W, H, "Numbers: " + ", ".join(f"{v} {l}" for v, l in NUMBERS), "".join(b), t)


# ------------------------------------------------------------------ project cards
def card(t, status, title, lines, tech, viz, label):
    W, H = 412, 200
    b = [pill(26, 26, status, t), arrow(W - 44, 28, t)]
    b.append(txt(26, 92, title, 24, t["text"], 700, extra='letter-spacing="-.4"'))
    for i, l in enumerate(lines):
        b.append(txt(26, 120 + i * 21, l, 14, t["sub"]))
    b.append(txt(26, 174, "  ·  ".join(tech), 13, t["accent"], 700))
    b.append(viz)
    return svg(W, H, label, "".join(b), t)


def viz_map(t):
    f, inside = project(PTS, 268, 64, 124, 118)
    out = []
    for i, p in enumerate(PTS):
        if not inside(p):
            continue
        x, y = f(p[0], p[1])
        if p[2]:
            out.append(f'<circle class="tw" style="animation-delay:{(i*37%300)/100:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{t["accent"]}"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r=".9" fill="{t["dot"]}" opacity=".25"/>')
    return "".join(out)


def viz_labels(t):
    rows = [("verified", t["green"]), ("inferred", "#d29922"), ("unknown", t["mute"])]
    out = []
    for i, (lab, col) in enumerate(rows):
        y = 84 + i * 30
        out.append(f'<g class="float" style="animation-delay:{i*.4:.1f}s">')
        out.append(f'<rect x="290" y="{y}" width="96" height="24" rx="12" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".55"/>')
        out.append(f'<circle cx="305" cy="{y+12}" r="3.5" fill="{col}"/>')
        out.append(txt(315, y + 16.5, lab, 12, col, 700))
        out.append("</g>")
    return "".join(out)


def viz_bars(t):
    out = []
    for i, (lab, v) in enumerate([("auth ok", 94), ("gated", 30), ("arch", 12)]):
        y = 90 + i * 28
        out.append(txt(290, y + 9, lab, 11, t["sub"], 600))
        out.append(txt(390, y + 9, str(v), 11, t["text"], 700, anchor="end"))
        out.append(f'<rect x="290" y="{y+15}" width="100" height="5" rx="2.5" fill="{t["line"]}"/>')
        out.append(f'<rect class="grow" style="animation-delay:{.15*i:.2f}s" x="290" y="{y+15}" width="{v:.0f}" height="5" rx="2.5" fill="{t["accent"]}"/>')
    return "".join(out)


def viz_flow(t):
    # marks -> rank -> college, the one flow the predictor owns
    nodes = [(352, 84, "marks"), (352, 120, "rank"), (352, 156, "college")]
    out = []
    for (x1, y1, _), (x2, y2, _) in zip(nodes, nodes[1:]):
        out.append(f'<line class="flow" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["accent"]}" stroke-width="1.5"/>')
    for i, (x, y, lab) in enumerate(nodes):
        w = 18 + len(lab) * 7
        last = i == len(nodes) - 1
        out.append(f'<rect x="{x - w/2:.0f}" y="{y-12}" width="{w:.0f}" height="24" rx="7" fill="{t["tile"]}" stroke="{t["accent"] if last else t["line"]}"/>')
        out.append(txt(x, y + 4.5, lab, 12, t["accent"] if last else t["text"], 700, anchor="middle"))
    return "".join(out)


CARDS = [
    ("ncrhiring", lambda t: card(t, "LIVE", "NCR Hiring Map",
                                 [f'{pins["total"]:,} Delhi NCR startups on one map.', "Verified pins never mix with guesses."],
                                 ["Next.js", "Leaflet", "Scraping"], viz_map(t),
                                 f'NCR Hiring Map: {pins["total"]:,} Delhi NCR startups on one map, built from a scraping pipeline.')),
    ("fieldguide", lambda t: card(t, "LIVE", "OAuth Fieldguide",
                                  ["Type a provider, get its OAuth guide.", "Every claim is labelled by evidence."],
                                  ["TypeScript", "React", "Agents"], viz_labels(t),
                                  "OAuth Fieldguide: type a provider, get its OAuth setup guide, every claim labelled verified, inferred or unknown.")),
    ("buildability", lambda t: card(t, "RESEARCH", "100-App Buildability",
                                    ["Can you integrate these 100 apps?", "92.5% verified claim accuracy."],
                                    ["Python", "Agents", "Evidence"], viz_bars(t),
                                    "100-App Buildability: agent-built research on 100 apps, 92.5% verified claim accuracy.")),
    ("predictor", lambda t: card(t, "SHIPPED", "College Predictor",
                                 ["Marks in, likely college out.", "~10 lakh visits in 3 months."],
                                 ["MathonGo", "Product", "Data"], viz_flow(t),
                                 "College Predictor at MathonGo: JoSAA, JAC and BITSAT seat prediction, about 10 lakh visits in 3 months.")),
]


# ------------------------------------------------------------------ quote
QUOTE = ("Anmol is a cool-headed guy who can manage a big team at such a young age. Started working at a "
         "young age. I worked with Anmol on multiple products from scratch at MathonGo for a good 1.5 years.")
QUOTE_END = "Highly recommend Anmol for management, consulting and product roles."


def wrap(text, n):
    out, line = [], ""
    for w in text.split():
        if line and len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return out + [line]


def quote_card(t, theme):
    W = 840
    b = [f'<path d="M40 44 h10 v10 c0 8 -4 14 -10 16 v-5 c3 -2 5 -5 5 -9 h-5z M58 44 h10 v10 c0 8 -4 14 -10 16 v-5 c3 -2 5 -5 5 -9 h-5z" fill="{t["accent"]}"/>']
    y = 104
    for l in wrap(QUOTE, 99):
        b.append(txt(40, y, l, 16, t["sub"]))
        y += 26
    for l in wrap(QUOTE_END, 99):
        b.append(txt(40, y, l, 16, t["text"], 700))
        y += 26
    y += 18
    b.append(f'<line x1="40" y1="{y-16}" x2="{W-40}" y2="{y-16}" stroke="{t["line"]}"/>')
    b.append(txt(40, y + 12, "Kunal Taneja", 15, t["text"], 700))
    b.append(txt(40, y + 32, "Founder, Canvas Classes. Ex-Head of Content, MathonGo. Managed me directly.", 13, t["sub"]))
    b.append(txt(W - 40, y + 12, "LinkedIn recommendation", 13, t["sub"], 500, anchor="end"))
    b.append(txt(W - 40, y + 32, "May 2026", 13, t["mute"], anchor="end"))
    H = y + 56
    return svg(W, H, f"Kunal Taneja, who managed Anmol at MathonGo: {QUOTE} {QUOTE_END}", "".join(b), t)


# ------------------------------------------------------------------ path
PATH = [
    ("Dec 2023", "MathonGo", "Operations Manager", "mathongo-mark.png", False),
    ("Sept 2025", "ARC, TIET", "President, 40-person team", "arc.png", False),
    ("2026", "Building", "Fieldguide, NCR map, research", None, False),
    ("2027", "Thapar Institute", "B.Tech, ENC", "thapar.png", True),
]


def path_card(t, theme):
    W, H = 840, 200
    b = [txt(40, 46, "The path so far", 17, t["text"], 700)]
    x0, x1, y = 110, W - 110, 116
    b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["line"]}" stroke-width="2"/>')
    step = (x1 - x0) / (len(PATH) - 1)
    b.append(f'<line class="grow" x1="{x0}" y1="{y}" x2="{x0 + step*2}" y2="{y}" stroke="{t["accent"]}" stroke-width="2"/>')
    for i, (when, org, role, logo, future) in enumerate(PATH):
        x = x0 + i * step
        stroke = t["mute"] if future else t["accent"]
        dash = ' stroke-dasharray="3 3"' if future else ""
        if logo:
            b.append(f'<clipPath id="lg{i}"><rect x="{x-15}" y="{y-15}" width="30" height="30" rx="8"/></clipPath>')
            b.append(f'<rect x="{x-18}" y="{y-18}" width="36" height="36" rx="10" fill="{t["bg"]}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
            b.append(image(x - 15, y - 15, 30, 30, logo, clip=f"lg{i}"))
        else:
            b.append(f'<circle class="ping" cx="{x}" cy="{y}" r="6" fill="{t["accent"]}"/><circle cx="{x}" cy="{y}" r="7" fill="{t["accent"]}"/>')
        b.append(txt(x, 160, org, 15, t["text"], 700, anchor="middle"))
        b.append(txt(x, 180, role, 12.5, t["sub"], anchor="middle"))
        b.append(txt(x, 84, when, 12, t["mute"] if future else t["accent"], 700, anchor="middle"))
    label = "Path: " + "; ".join(f"{w} {o}, {r}" for w, o, r, _, _ in PATH)
    return svg(W, H, label, "".join(b), t)


# ------------------------------------------------------------------ stack
STACK = [
    ("DATA", [("siPython", "Python"), ("siPostgresql", "SQL"), ("siGooglebigquery", "BigQuery"),
              ("siLooker", "Looker"), ("siGooglesheets", "Sheets")]),
    ("BUILD", [("siTypescript", "TypeScript"), ("siReact", "React"), ("siNextdotjs", "Next.js"),
               ("siTailwindcss", "Tailwind"), ("siFastapi", "FastAPI")]),
    ("AI & ML", [("siClaude", "Claude"), ("siGooglegemini", "Gemini"), ("siPytorch", "PyTorch")]),
    ("SHIP", [("siDocker", "Docker"), ("siFigma", "Figma"), ("siLeaflet", "Leaflet"), ("siGit", "Git")]),
]


def stack_card(t, theme):
    W = 840
    b = [txt(32, 48, "Toolbox", 17, t["text"], 700),
         txt(W - 32, 48, "what my repos are actually built with", 13, t["sub"], anchor="end")]
    colw, tile, gap = (W - 64) / 2, 52, 76
    rows_h = []
    for gi, (name, items) in enumerate(STACK):
        col, row = gi % 2, gi // 2
        x0 = 32 + col * colw
        y0 = 86 + row * 118
        b.append(txt(x0, y0, name, 12, t["sub"], 700, extra='letter-spacing="1.4"'))
        for i, (key, lab) in enumerate(items):
            x = x0 + i * gap
            y = y0 + 14
            b.append(f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="12" fill="{t["tile"]}" stroke="{t["line"]}"/>')
            b.append(icon(key, x + 13, y + 13, 26, t, theme))
            b.append(txt(x + tile / 2, y + tile + 18, lab, 12, t["sub"], 500, anchor="middle"))
        rows_h.append(y0 + 14 + tile + 30)
    H = int(max(rows_h)) + 6
    names = ", ".join(l for _, items in STACK for _, l in items)
    return svg(W, H, f"Toolbox: {names}", "".join(b), t)


# ------------------------------------------------------------------ links
def glyph_globe(x, y, t):
    c = t["accent"]
    return (f'<g fill="none" stroke="{c}" stroke-width="1.8"><circle cx="{x+13}" cy="{y+13}" r="11"/>'
            f'<ellipse cx="{x+13}" cy="{y+13}" rx="5" ry="11"/><path d="M{x+2} {y+13} h22"/></g>')


def glyph_doc(x, y, t):
    c = t["accent"]
    return (f'<g fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"><path d="M{x+5} {y+1} h11 l6 6 v18 h-17z"/>'
            f'<path d="M{x+16} {y+1} v6 h6"/><path d="M{x+9} {y+14} h9 M{x+9} {y+19} h9"/></g>')


def glyph_in(x, y, t):
    return (f'<rect x="{x}" y="{y}" width="26" height="26" rx="5" fill="#0a66c2"/>'
            + txt(x + 13, y + 20, "in", 17, "#ffffff", 800, anchor="middle"))


LINKS = [
    ("portfolio", "Portfolio", "anmolsethi.online", glyph_globe),
    ("linkedin", "LinkedIn", "in/anmol-sethi-79ba03228", glyph_in),
    ("email", "Email", "anmolsethi911@gmail.com", None),
    ("resume", "Resume", "PDF, the short version", glyph_doc),
]


def link_card(t, theme, title, sub, glyph, key):
    W, H = 412, 104
    b = [f'<rect x="24" y="24" width="56" height="56" rx="14" fill="{t["tile"]}" stroke="{t["line"]}"/>']
    if key == "email":
        b.append(icon("siGmail", 39, 39, 26, t, theme))
    else:
        b.append(glyph(39, 39, t))
    b.append(txt(100, 50, title, 19, t["text"], 700))
    b.append(txt(100, 74, sub, 14, t["sub"]))
    b.append(arrow(W - 48, 43, t))
    return svg(W, H, f"{title}: {sub}", "".join(b), t)


# ------------------------------------------------------------------ build
for theme, t in THEMES.items():
    write("hero", theme, hero(t, theme))
    write("numbers", theme, numbers(t, theme))
    write("quote", theme, quote_card(t, theme))
    write("path", theme, path_card(t, theme))
    write("stack", theme, stack_card(t, theme))
    for name, fn in CARDS:
        write(f"project-{name}", theme, fn(t))
    for key, title, sub, glyph in LINKS:
        write(f"link-{key}", theme, link_card(t, theme, title, sub, glyph, key))
print("cards written")
