"""Builds every static card on the profile, in dark and light.

Run: python3 scripts/build_cards.py
Reads data/ncr-pins.json (a snapshot from the NCR Hiring Map) and writes assets/*.svg.
Every number on a card lives in this file, next to where it is drawn.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards_common import ROOT, ASSETS, THEMES, svg, txt, write, escape  # noqa: E402

# ---------------------------------------------------------------- hero
pins = json.load(open(os.path.join(ROOT, "data", "ncr-pins.json")))
PTS = pins["pts"]  # [lat, lng, verified, hiring]


def project(pts, x0, y0, w, h, pad=6):
    lats = [p[0] for p in pts]
    lngs = [p[1] for p in pts]
    # trim outliers so the cluster fills the frame
    lats_s, lngs_s = sorted(lats), sorted(lngs)
    k = int(len(pts) * 0.01)
    la0, la1 = lats_s[k], lats_s[-k - 1]
    lo0, lo1 = lngs_s[k], lngs_s[-k - 1]
    kx = math.cos(math.radians((la0 + la1) / 2))
    sw, sh = (lo1 - lo0) * kx, (la1 - la0)
    scale = min((w - 2 * pad) / sw, (h - 2 * pad) / sh)
    ox = x0 + (w - sw * scale) / 2
    oy = y0 + (h - sh * scale) / 2

    def f(lat, lng):
        return ox + (lng - lo0) * kx * scale, oy + (la1 - lat) * scale

    inside = lambda p: la0 <= p[0] <= la1 and lo0 <= p[1] <= lo1
    return f, inside


def hero(t, theme):
    W, H = 840, 340
    mx, my, mw, mh = 520, 34, 290, 250
    f, inside = project(PTS, mx, my, mw, mh)
    dots = []
    for i, p in enumerate(PTS):
        if not inside(p):
            continue
        x, y = f(p[0], p[1])
        if p[2]:
            delay = (i * 37 % 300) / 100
            dots.append(f'<circle class="tw" style="animation-delay:{delay:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="1.9" fill="{t["accent"]}"/>')
        else:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.2" fill="{t["dot"]}" opacity=".22"/>')
    gx, gy = f(28.4595, 77.0266)  # Gurugram, where I live
    body = []
    body.append(f'<defs><radialGradient id="g" cx="{mx+mw/2}" cy="{my+mh/2}" r="220" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity=".13"/>'
                f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>')
    body.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#g)"/>')
    # left column
    body.append(txt(40, 52, "ANMOLAS1402", 11, t["accent"], 700, mono=True, extra='letter-spacing="2"'))
    body.append(f'<circle class="ping" cx="185" cy="48" r="3.5" fill="{t["green"]}"/><circle cx="185" cy="48" r="3.5" fill="{t["green"]}"/>')
    body.append(txt(195, 52, "open to work, can join now", 11, t["sub"], 500, mono=True))
    body.append(f'<g class="rise">{txt(38, 112, "Anmol Sethi", 46, t["text"], 800, extra="letter-spacing=\"-1.5\"")}</g>')
    body.append(f'<g class="rise" style="animation-delay:.15s">'
                + txt(40, 146, "Product ops person who writes the code too.", 18, t["text"], 600) + '</g>')
    lines = [
        "Two years running ops and data pipelines at MathonGo,",
        "an edtech platform with 500K+ students. Now I build",
        "AI tools that show their sources.",
    ]
    for i, l in enumerate(lines):
        body.append(f'<g class="rise" style="animation-delay:{.3 + i*.08:.2f}s">' + txt(40, 180 + i * 22, l, 14.5, t["sub"]) + '</g>')
    chips = ["Product Ops", "Data pipelines", "AI agents", "SQL"]
    cx = 40
    for c in chips:
        w = 16 + len(c) * 7.1
        body.append(f'<rect x="{cx}" y="262" width="{w:.0f}" height="26" rx="13" fill="{t["chip"]}" stroke="{t["line"]}"/>')
        body.append(txt(cx + w / 2, 279, c, 11.5, t["text"], 500, mono=True, anchor="middle"))
        cx += w + 8
    body.append(txt(40, 314, "Gurugram, India  ·  B.Tech ENC @ Thapar, 2027", 11, t["mute"], 400, mono=True))
    # map
    body.append(f'<rect x="{mx-14}" y="{my-12}" width="{mw+28}" height="{mh+60}" rx="10" fill="{t["bg2"]}" opacity=".55" stroke="{t["line"]}"/>')
    body.append("".join(dots))
    body.append(f'<circle class="ping" cx="{gx:.1f}" cy="{gy:.1f}" r="4" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>')
    body.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="3.2" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="2"/>')
    body.append(txt(gx - 9, gy + 4, "me", 10, t["accent"], 700, mono=True, anchor="end"))
    total, ver = pins["total"], pins["verified"]
    body.append(f'<circle cx="{mx+2}" cy="{my+mh+21}" r="3" fill="{t["accent"]}"/>')
    body.append(txt(mx + 11, my + mh + 25, f"{ver} verified", 10.5, t["sub"], 500, mono=True))
    body.append(f'<circle cx="{mx+106}" cy="{my+mh+21}" r="2.4" fill="{t["dot"]}" opacity=".35"/>')
    body.append(txt(mx + 114, my + mh + 25, f"{total-ver:,} approx", 10.5, t["sub"], 500, mono=True))
    body.append(txt(mx + mw, my + mh + 25, "ncrhiring.in", 10.5, t["accent"], 700, mono=True, anchor="end"))
    body.append(txt(mx + mw, my + 4, f"{total:,} NCR startups", 10.5, t["mute"], 500, mono=True, anchor="end"))
    label = (f"Anmol Sethi. Product ops person who writes the code too. Map of {total:,} Delhi NCR startups "
             f"from ncrhiring.in, {ver} with verified addresses.")
    return svg(W, H, label, "".join(body), t)


# ---------------------------------------------------------------- metrics
METRICS = [
    ("500K+", "students served by the exam", "analysis pipelines I built", None),
    ("1 → 14", "exam categories in the", "MathonGo test series", (1, 14)),
    ("99.4%", "College Predictor accuracy", "at launch, ~10 L visits", .994),
    ("100+", "interns hired and onboarded", "across a 30+ person team", None),
]


def metrics(t, theme):
    W, H = 840, 150
    body = [txt(28, 34, "RECEIPTS FROM MATHONGO, DEC 2023 TO JAN 2026", 10.5, t["mute"], 700, mono=True, extra='letter-spacing="1.5"')]
    cw = (W - 56) / 4
    for i, (v, a, b, viz) in enumerate(METRICS):
        x = 28 + i * cw
        if i:
            body.append(f'<line x1="{x-10}" y1="52" x2="{x-10}" y2="128" stroke="{t["line"]}"/>')
        body.append(txt(x, 82, v, 32, t["text"], 800, extra='letter-spacing="-1"'))
        body.append(txt(x, 104, a, 11.5, t["sub"]))
        body.append(txt(x, 119, b, 11.5, t["sub"]))
        bw = cw - 30
        if isinstance(viz, tuple):
            n = viz[1]
            sw = (bw - (n - 1) * 3) / n
            for k in range(n):
                fill = t["accent"]
                body.append(f'<rect class="rise" style="animation-delay:{.05*k:.2f}s" x="{x + k*(sw+3):.1f}" y="132" width="{sw:.1f}" height="5" rx="1.5" fill="{fill}" opacity="{1 if k < 1 else .55}"/>')
        elif isinstance(viz, float):
            body.append(f'<rect x="{x}" y="132" width="{bw:.0f}" height="5" rx="2.5" fill="{t["line"]}"/>')
            body.append(f'<rect class="grow" x="{x}" y="132" width="{bw*viz:.1f}" height="5" rx="2.5" fill="{t["accent"]}"/>')
        else:
            body.append(f'<rect class="grow" style="animation-delay:{.2*i:.1f}s" x="{x}" y="132" width="{bw:.0f}" height="5" rx="2.5" fill="{t["accent"]}" opacity=".85"/>')
    label = "Numbers from MathonGo: " + "; ".join(f"{v} {a} {b}" for v, a, b, _ in METRICS)
    return svg(W, H, label, "".join(body), t)


# ---------------------------------------------------------------- project cards
def tags_row(tags, x, y, t):
    out, cx = [], x
    for tg in tags:
        w = 12 + len(tg) * 6.3
        out.append(f'<rect x="{cx:.0f}" y="{y}" width="{w:.0f}" height="20" rx="10" fill="{t["chip"]}" stroke="{t["line"]}"/>')
        out.append(txt(cx + w / 2, y + 14, tg, 10, t["sub"], 500, mono=True, anchor="middle"))
        cx += w + 6
    return "".join(out)


def card(t, idx, kicker, title, lines, stat, stat_label, tags, viz):
    W, H = 412, 196
    b = [txt(22, 32, f"{idx}  ·  {kicker}", 10, t["mute"], 700, mono=True, extra='letter-spacing="1.2"')]
    b.append(txt(22, 62, title, 21, t["text"], 800, extra='letter-spacing="-.5"'))
    for i, l in enumerate(lines):
        b.append(txt(22, 88 + i * 18, l, 12.5, t["sub"]))
    b.append(txt(W - 22, 62, stat, 24, t["accent"], 800, anchor="end", extra='letter-spacing="-.8"'))
    b.append(txt(W - 22, 34, stat_label, 9.5, t["mute"], 600, mono=True, anchor="end"))
    b.append(viz)
    b.append(tags_row(tags, 22, 160, t))
    b.append(txt(W - 22, 174, "↗", 15, t["accent"], 700, anchor="end"))
    return svg(W, H, f"{title}: {' '.join(lines)} {stat} {stat_label}", "".join(b), t)


def viz_map(t):
    f, inside = project(PTS, 300, 76, 92, 70, pad=2)
    return "".join(f'<circle cx="{f(p[0],p[1])[0]:.1f}" cy="{f(p[0],p[1])[1]:.1f}" r="{1.1 if p[2] else .7}" '
                   f'fill="{t["accent"] if p[2] else t["dot"]}" opacity="{.9 if p[2] else .2}"/>'
                   for p in PTS if inside(p))


def viz_labels(t):
    rows = [("verified", t["green"], 1), ("inferred", "#eab308", 1), ("unknown", t["mute"], 1)]
    out = []
    for i, (lab, col, _) in enumerate(rows):
        y = 84 + i * 22
        out.append(f'<rect x="306" y="{y}" width="84" height="17" rx="4" fill="{col}" fill-opacity=".13" stroke="{col}" stroke-opacity=".5"/>')
        out.append(f'<circle cx="316" cy="{y+8.5}" r="3" fill="{col}"/>')
        out.append(txt(325, y + 12.5, lab, 10, col, 700, mono=True))
    return "".join(out)


def viz_bars(t):
    # 100 apps: 94 auth solved, 30 approval gates, 12 architectural (of 65 blocked)
    out = []
    data = [("auth ok", 94), ("gated", 30), ("arch", 12)]
    for i, (lab, v) in enumerate(data):
        y = 88 + i * 20
        out.append(txt(304, y + 8, lab, 9, t["mute"], 600, mono=True))
        out.append(f'<rect x="344" y="{y}" width="46" height="9" rx="2" fill="{t["line"]}"/>')
        out.append(f'<rect class="grow" style="animation-delay:{.15*i:.2f}s" x="344" y="{y}" width="{46*v/100:.1f}" height="9" rx="2" fill="{t["accent"]}"/>')
    return "".join(out)


def viz_predictor(t):
    # marks to rank to college, the one flow the tool owns
    out = []
    steps = ["marks", "rank", "college"]
    for i, s in enumerate(steps):
        y = 84 + i * 22
        out.append(f'<rect x="318" y="{y}" width="72" height="17" rx="8.5" fill="{t["chip"]}" stroke="{t["line"]}"/>')
        out.append(txt(354, y + 12.5, s, 10, t["text"] if i < 2 else t["accent"], 700, mono=True, anchor="middle"))
        if i < 2:
            out.append(f'<line x1="354" y1="{y+17}" x2="354" y2="{y+22}" stroke="{t["mute"]}"/>')
    return "".join(out)


CARDS = [
    ("ncrhiring", lambda t: card(t, "001", "BUILT AND RUN BY ME", "NCR Hiring Map",
                                 ["Every startup and VC hiring in Delhi NCR,", "from a scraping pipeline, not a spreadsheet.",
                                  "Guessed pins never pass as verified ones."],
                                 f'{pins["total"]:,}', "COMPANIES", ["Next.js", "Leaflet", "Scraping"], viz_map(t))),
    ("fieldguide", lambda t: card(t, "002", "LIVE TOOL", "OAuth Fieldguide",
                                  ["Type a provider, get its OAuth setup guide.", "Every claim is labelled, and a validator",
                                   "demotes quotes it can't find in the source."],
                                  "3", "CLAIM LABELS", ["TypeScript", "React", "LLM agents"], viz_labels(t))),
    ("buildability", lambda t: card(t, "003", "AGENT-BUILT RESEARCH", "100-App Buildability",
                                    ["Can you actually integrate these 100 apps?", "Auth is solved. Paperwork is the blocker.",
                                     "Every claim has an evidence URL."],
                                    "92.5%", "CLAIM ACCURACY", ["Python", "Agents", "Research"], viz_bars(t))),
    ("predictor", lambda t: card(t, "004", "OWNED END TO END AT MATHONGO", "College Predictor",
                                 ["JoSAA, JAC and BITSAT seat prediction,", "wired into the score calculator. Stress-",
                                  "tested on edge cases before every release."],
                                 "~10 L", "VISITS IN 3 MONTHS", ["Product", "Data", "UAT"], viz_predictor(t))),
]


# ---------------------------------------------------------------- links
LINKS = [
    ("portfolio", "PORTFOLIO", "anmolsethi.online", "the long version, with a live map"),
    ("linkedin", "LINKEDIN", "in/anmol-sethi", "work history and what I'm up to"),
    ("email", "EMAIL", "anmolsethi911@gmail.com", "fastest way to reach me"),
    ("map", "LIVE PROJECT", "ncrhiring.in", "find who's hiring near you in NCR"),
]


def link_card(t, kicker, main, sub):
    W, H = 412, 84
    b = [txt(22, 30, kicker, 10, t["mute"], 700, mono=True, extra='letter-spacing="1.5"'),
         txt(22, 56, main, 18, t["text"], 700),
         txt(22, 73, sub, 11, t["sub"]),
         f'<circle cx="{W-38}" cy="42" r="16" fill="{t["chip"]}" stroke="{t["line"]}"/>',
         txt(W - 38, 47.5, "↗", 14, t["accent"], 700, anchor="middle")]
    return svg(W, H, f"{kicker}: {main}", "".join(b), t)


# ---------------------------------------------------------------- path
PATH = [
    ("2022", "Class 12, CBSE", "Delhi", False),
    ("Dec 2023", "Ops Manager, MathonGo", "500K+ students, 100+ interns", False),
    ("Sept 2025", "President, ARC TIET", "40 people, 5 MoUs, 2 podcasts", False),
    ("2026", "Shipping AI tools", "Fieldguide, NCR map, research", False),
    ("2027", "B.Tech ENC, Thapar", "graduating", True),
]


def path_card(t, theme):
    W, H = 840, 150
    b = [txt(28, 34, "THE PATH SO FAR", 10.5, t["mute"], 700, mono=True, extra='letter-spacing="1.5"')]
    x0, x1, y = 40, W - 40, 66
    b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["line"]}" stroke-width="2"/>')
    b.append(f'<line class="grow" x1="{x0}" y1="{y}" x2="{x0 + (x1-x0)*0.8}" y2="{y}" stroke="{t["accent"]}" stroke-width="2"/>')
    step = (x1 - x0) / (len(PATH) - 1)
    for i, (when, what, detail, future) in enumerate(PATH):
        x = x0 + i * step
        anchor = "start" if i == 0 else "end" if i == len(PATH) - 1 else "middle"
        if future:
            b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{t["bg"]}" stroke="{t["mute"]}" stroke-width="2" stroke-dasharray="2 2"/>')
        elif i == len(PATH) - 2:
            b.append(f'<circle class="ping" cx="{x}" cy="{y}" r="5" fill="{t["accent"]}"/>')
            b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{t["accent"]}"/>')
        else:
            b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        b.append(txt(x, 94, when, 10.5, t["accent"] if not future else t["mute"], 700, mono=True, anchor=anchor))
        # wrap the title into two lines if long
        words, l1, l2 = what.split(", "), what, ""
        if len(what) > 24 and len(words) > 1:
            l1, l2 = words[0] + ",", ", ".join(words[1:])
        b.append(txt(x, 112, l1, 12, t["text"], 700, anchor=anchor))
        if l2:
            b.append(txt(x, 127, l2, 12, t["text"], 700, anchor=anchor))
        b.append(txt(x, 142 if l2 else 127, detail, 10, t["sub"], anchor=anchor))
    return svg(W, H + 8, "Timeline: " + "; ".join(f"{w} {a}" for w, a, _, _ in PATH), "".join(b), t)


# ---------------------------------------------------------------- build
for theme, t in THEMES.items():
    write("hero", theme, hero(t, theme))
    write("metrics", theme, metrics(t, theme))
    write("path", theme, path_card(t, theme))
    for name, fn in CARDS:
        write(f"project-{name}", theme, fn(t))
    for name, kicker, main, sub in LINKS:
        write(f"link-{name}", theme, link_card(t, kicker, main, sub))
print("cards written to", ASSETS)
