"""Builds every static card on the profile, in light (paper) and dark (carbon copy).

Run: python3 scripts/build_cards.py
Inputs: data/ncr-pins.json (snapshot of the NCR Hiring Map), data/img/ (photo,
logos), data/fonts/. Output: assets/*.svg. Every word and number lives here.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards_common import THEMES, ROOT, svg, txt, image, write  # noqa: E402

pins = json.load(open(os.path.join(ROOT, "data", "ncr-pins.json")))
PTS = pins["pts"]  # [lat, lng, verified, hiring]
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ------------------------------------------------------------------ primitives
def bubble(x, y, r, t, filled=False, letter=None, delay=None, opacity=1):
    out = [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{t["print"]}" stroke-width=".9"/>']
    if letter and not filled:
        out.append(txt(x, y + r * 0.55, letter, r * 1.25, t["print"], "cond", "middle"))
    if filled:
        anim = f' class="fill" style="animation-delay:{delay:.2f}s"' if delay is not None else ""
        out.append(f'<circle{anim} cx="{x:.1f}" cy="{y:.1f}" r="{r-.6:.1f}" fill="{t["ink"]}" opacity="{opacity}"/>')
    return "".join(out)


def field(x, y, w, label, value, t, size=22):
    return (txt(x, y, label, 14, t["print"], "cond")
            + f'<line x1="{x}" y1="{y+32}" x2="{x+w}" y2="{y+32}" stroke="{t["print"]}" stroke-width=".9"/>'
            + txt(x + 2, y + 28, value, size, t["ink"], "pen"))


def timing_marks(h, t, x=10):
    return "".join(f'<rect x="{x}" y="{y}" width="11" height="4" fill="{t["mark"]}"/>'
                   for y in range(28, h - 24, 18))


def wrap(text, n):
    out, line = [], ""
    for w in text.split():
        if line and len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return out + [line]


def project(pts, x0, y0, w, h, pad=2):
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
NAME = "ANMOL SETHI"


def hero(t, theme):
    W, H = 840, 456
    b = [timing_marks(H, t)]
    # name grid, the way every JEE aspirant has filled it
    gx, pitch, by, step, r = 42, 20, 104, 12.6, 5.2
    b.append(txt(gx, 46, "Candidate's name", 14, t["print"], "cond"))
    for c, ch in enumerate(NAME):
        x = gx + c * pitch + 9
        b.append(f'<rect x="{x-9}" y="60" width="18" height="26" fill="none" stroke="{t["print"]}" stroke-width=".9"/>')
        if ch != " ":
            b.append(txt(x, 81, ch, 19, t["ink"], "pen", "middle"))
        for i, a in enumerate(ALPHA):
            b.append(bubble(x, by + i * step, r, t, filled=(a == ch), letter=a, delay=.25 + c * .11))
    # fields
    fx, fw = 292, 330
    b.append(field(fx, 46, fw, "Applying for", "Product Ops, APM or PM roles", t))
    b.append(field(fx, 106, fw, "Based in", "Gurugram, Haryana", t))
    b.append(field(fx, 166, fw, "Education", "B.Tech ENC, Thapar Institute, 2027", t))
    b.append(txt(fx, 238, "Can join", 14, t["print"], "cond"))
    ox = fx
    for i, opt in enumerate(["Immediately", "In 30 days", "In 60 days"]):
        b.append(bubble(ox + 8, 260, 7, t, filled=(i == 0), delay=1.6 if i == 0 else None))
        b.append(txt(ox + 22, 265, opt, 15, t["text"], "body"))
        ox += 112
    # photo and signature
    px, py, pw, ph = 664, 46, 140, 176
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="{t["print"]}" stroke-width=".9" stroke-dasharray="4 3"/>')
    b.append(f'<clipPath id="ph"><rect x="{px+6}" y="{py+6}" width="{pw-12}" height="{ph-12}"/></clipPath>')
    b.append(image(px + 6, py + 6, pw - 12, ph - 12, "anmol-passport.jpg", clip="ph"))
    b.append(txt(px + pw / 2, py + ph + 18, "Photograph", 13, t["print"], "cond", "middle"))
    b.append(f'<rect x="{px}" y="252" width="{pw}" height="40" fill="none" stroke="{t["print"]}" stroke-width=".9"/>')
    b.append(txt(px + pw / 2, 281, "Anmol Sethi", 24, t["ink"], "pen", "middle", extra='transform="rotate(-3 734 276)"'))
    b.append(txt(px + pw / 2, 310, "Signature", 13, t["print"], "cond", "middle"))
    # about
    ay = 330
    b.append(f'<rect x="{fx}" y="{ay}" width="{804-fx}" height="96" fill="{t["tint"]}" stroke="{t["rule"]}"/>')
    lines = [
        "I ran operations and data at MathonGo, an edtech platform, where the exam",
        "analysis pipelines I built reached 500K+ JEE students. Now I build tools for",
        "data that has to be right, like a live map of every startup hiring in Delhi NCR.",
    ]
    for i, l in enumerate(lines):
        b.append(txt(fx + 16, ay + 30 + i * 23, l, 15, t["text"], "body"))
    label = ("Anmol Sethi, filled in like an OMR sheet. Applying for Product Ops, APM or PM roles. "
             "Based in Gurugram. B.Tech ENC, Thapar Institute, 2027. Can join immediately. " + " ".join(lines))
    return svg(W, H, label, "".join(b), t)


# ------------------------------------------------------------------ marks
MARKS = [
    ("Students reached", "500K+"),
    ("Exams in test series", "1 → 14"),
    ("Predictor accuracy", "99.4%"),
    ("Interns onboarded", "100+"),
    ("Startups mapped", f'{pins["total"]:,}'),
]


def marks(t, theme):
    W, H = 840, 132
    b = [timing_marks(H, t)]
    x0, cw = 34, (W - 34 - 16) / len(MARKS)
    b.append(f'<rect x="{x0}" y="18" width="{W-x0-16}" height="32" fill="{t["tint"]}"/>')
    b.append(f'<line x1="{x0}" y1="50" x2="{W-16}" y2="50" stroke="{t["print"]}" stroke-width=".9"/>')
    for i, (lab, v) in enumerate(MARKS):
        cx = x0 + cw * i + cw / 2
        if i:
            b.append(f'<line x1="{x0+cw*i:.1f}" y1="18" x2="{x0+cw*i:.1f}" y2="{H-16}" stroke="{t["rule"]}"/>')
        b.append(txt(cx, 40, lab, 14, t["print"], "cond", "middle"))
        b.append(txt(cx, 98, v, 36, t["ink"], "pen", "middle"))
    return svg(W, H, "From my MathonGo years and the NCR map: " + ", ".join(f"{l} {v}" for l, v in MARKS), "".join(b), t)


# ------------------------------------------------------------------ project cards
def card(t, title, where, lines, built, viz, label):
    W, H = 412, 224
    b = [txt(24, 50, title, 28, t["text"], "condb")]
    b.append(txt(24, 72, where, 14, t["print"], "cond"))
    for i, l in enumerate(lines):
        b.append(txt(24, 104 + i * 21, l, 14.5, t["sub"], "body"))
    b.append(f'<line x1="24" y1="178" x2="250" y2="178" stroke="{t["rule"]}"/>')
    b.append(txt(24, 200, built, 13.5, t["text"], "bodym"))
    b.append(viz)
    return svg(W, H, label, "".join(b), t)


def viz_map(t):
    f, inside = project(PTS, 268, 24, 128, 180)
    out = []
    for p in PTS:
        if not inside(p):
            continue
        x, y = f(p[0], p[1])
        if p[2]:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="{t["ink"]}"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.2" fill="none" stroke="{t["print"]}" stroke-width=".4" opacity=".5"/>')
    out.append(txt(332, 210, "filled = verified address", 11.5, t["print"], "cond", "middle"))
    return "".join(out)


def viz_answer_key(t):
    # each claim gets exactly one label, like one bubble per question
    cols, rows = ["V", "I", "U"], [0, 0, 1, 0, 2, 0, 1]
    x0, y0 = 300, 44
    out = []
    for j, c in enumerate(cols):
        out.append(txt(x0 + 30 + j * 24, y0, c, 13, t["print"], "condb", "middle"))
    for i, pick in enumerate(rows):
        y = y0 + 20 + i * 20
        out.append(txt(x0 + 6, y + 4, f"{i+1}", 12, t["print"], "cond", "end"))
        for j in range(3):
            out.append(bubble(x0 + 30 + j * 24, y, 7, t, filled=(j == pick)))
    out.append(txt(396, 210, "verified, inferred, unknown", 11.5, t["print"], "cond", "end"))
    return "".join(out)


def viz_hundred(t):
    out = []
    x0, y0, s = 286, 34, 11.6
    for i in range(100):
        r_, c_ = divmod(i, 10)
        out.append(bubble(x0 + c_ * s, y0 + r_ * s, 4.3, t, filled=i < 94))
    out.append(txt(x0 + 4.5 * s, 210, "94 of 100 have solved auth", 11.5, t["print"], "cond", "middle"))
    return "".join(out)


def viz_predictor(t):
    out = []
    steps = [("Marks", 60, "your score"), ("Rank", 112, "category rank"), ("College", 164, "likely college")]
    for i, (lab, y, pen) in enumerate(steps):
        out.append(f'<rect x="296" y="{y-22}" width="96" height="34" fill="none" stroke="{t["print"]}" stroke-width=".9"/>')
        out.append(txt(302, y - 10, lab, 11, t["print"], "cond"))
        out.append(txt(302, y + 7, pen, 14, t["ink"], "pen"))
        if i < 2:
            out.append(f'<path d="M372 {y+12} q6 12 0 18" fill="none" stroke="{t["ink"]}" stroke-width="1.6" stroke-linecap="round"/>'
                       f'<path d="M368 {y+26} l4 4 l5 -3" fill="none" stroke="{t["ink"]}" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(txt(344, 210, "JoSAA, JAC, BITSAT", 11.5, t["print"], "cond", "middle"))
    return "".join(out)


CARDS = [
    ("ncrhiring", lambda t: card(t, "NCR Hiring Map", "ncrhiring.in",
                                 [f'{pins["total"]:,} Delhi NCR startups on one', "map, built from a scraping pipeline.",
                                  "Guessed pins never pass as verified."],
                                 "Next.js, Leaflet, scraping", viz_map(t),
                                 f'NCR Hiring Map at ncrhiring.in: {pins["total"]:,} Delhi NCR startups, verified addresses kept apart from guesses.')),
    ("fieldguide", lambda t: card(t, "OAuth Fieldguide", "Live on Render",
                                  ["Type a provider, get its OAuth setup", "guide. Every claim is labelled by",
                                   "the evidence behind it."],
                                  "TypeScript, React, LLM agents", viz_answer_key(t),
                                  "OAuth Fieldguide: type a provider, get its OAuth setup guide with every claim labelled verified, inferred or unknown.")),
    ("buildability", lambda t: card(t, "100-App Buildability", "Research report",
                                    ["Which of 100 apps can you actually", "integrate? Every claim has a source.",
                                     "92.5% accurate on a checked sample."],
                                    "Python, agents, evidence tracking", viz_hundred(t),
                                    "100-App Buildability: research on 100 apps, 94 have solved auth, 92.5% claim accuracy on a checked sample.")),
    ("predictor", lambda t: card(t, "College Predictor", "Owned end to end at MathonGo",
                                 ["From exam marks to a likely college", "in one flow. 99.4% accurate at launch,",
                                  "~10 lakh visits in its first 3 months."],
                                 "Product, data validation, UAT", viz_predictor(t),
                                 "College Predictor at MathonGo: marks to likely college for JoSAA, JAC and BITSAT, 99.4% accurate, about 10 lakh visits in 3 months.")),
]


# ------------------------------------------------------------------ remarks
QUOTE = ("Anmol is a cool-headed guy who can manage a big team at such a young age. Started working at a "
         "young age. I worked with Anmol on multiple products from scratch at MathonGo for a good 1.5 years. "
         "Highly recommend Anmol for management, consulting and product roles.")


def remarks(t, theme):
    W = 840
    b = [txt(36, 42, "Remarks from reporting manager", 15, t["print"], "cond")]
    y = 80
    lines = wrap(QUOTE, 86)
    b.append(f'<rect x="36" y="56" width="{W-72}" height="{len(lines)*28+22}" fill="{t["tint"]}" stroke="{t["rule"]}"/>')
    for l in lines:
        b.append(txt(52, y + 4, l, 17, t["text"], "body"))
        y += 28
    y += 36
    b.append(txt(52, y + 10, "Kunal Taneja", 30, t["ink"], "pen", extra=f'transform="rotate(-2 52 {y})"'))
    b.append(f'<line x1="48" y1="{y+18}" x2="260" y2="{y+18}" stroke="{t["print"]}" stroke-width=".9"/>')
    b.append(txt(52, y + 40, "Founder of Canvas Classes, ex-Head of Content at MathonGo. Managed me directly.", 14, t["sub"], "body"))
    b.append(txt(W - 36, y + 40, "LinkedIn recommendation, May 2026", 14, t["print"], "cond", "end"))
    H = y + 64
    b.insert(0, timing_marks(H, t))
    return svg(W, H, f"Remarks from Kunal Taneja, who managed Anmol at MathonGo: {QUOTE}", "".join(b), t)


# ------------------------------------------------------------------ record
RECORD = [
    ("Dec 2023 to Jan 2026", "MathonGo", "mathongo-mark.png", "Operations Manager",
     "Exam analysis for 500K+ students, test series from 1 to 14 exams, 100+ interns hired"),
    ("Sept 2025 to Jan 2026", "ARC, Thapar", "arc.png", "President",
     "Led a 40-person team, 5 MoUs, two podcasts at 1,500+ listeners an episode"),
    ("2026", "Independent", None, "Builder",
     "NCR Hiring Map, OAuth Fieldguide, the 100-app buildability study"),
    ("Expected 2027", "Thapar Institute", "thapar.png", "B.Tech, ENC",
     "Electronics and Computer Engineering, Patiala"),
]


def record(t, theme):
    W = 840
    cols = [(36, "When"), (190, "Where"), (352, "Role"), (512, "What came out of it")]
    b = [f'<rect x="28" y="22" width="{W-44}" height="34" fill="{t["tint"]}"/>']
    for x, lab in cols:
        b.append(txt(x, 45, lab, 14, t["print"], "cond"))
    y = 56
    for when, org, logo, role, out in RECORD:
        lines = wrap(out, 47)
        rh = max(58, 24 + len(lines) * 20)
        b.append(f'<line x1="28" y1="{y}" x2="{W-16}" y2="{y}" stroke="{t["print"] if y == 56 else t["rule"]}" stroke-width="{.9 if y == 56 else 1}"/>')
        b.append(txt(36, y + 30, when, 14, t["sub"], "body"))
        tx = 190
        if logo:
            b.append(f'<clipPath id="c{y}"><rect x="190" y="{y+13}" width="24" height="24" rx="4"/></clipPath>')
            b.append(image(190, y + 13, 24, 24, logo, clip=f"c{y}"))
            tx = 222
        b.append(txt(tx, y + 30, org, 16, t["text"], "condb"))
        b.append(txt(352, y + 30, role, 15, t["text"], "bodym"))
        for i, l in enumerate(lines):
            b.append(txt(512, y + 30 + i * 20, l, 14, t["sub"], "body"))
        y += rh
    H = y + 18
    b.insert(0, timing_marks(H, t))
    return svg(W, H, "Record of work: " + "; ".join(f"{w}, {o}, {r}: {x}" for w, o, _, r, x in RECORD), "".join(b), t)


# ------------------------------------------------------------------ tools
TOOLS = [
    ("Data", ["Python", "SQL", "BigQuery", "Looker Studio", "Power BI", "Excel", "Google Sheets"]),
    ("Build", ["TypeScript", "React", "Next.js", "Tailwind", "FastAPI", "PostgreSQL", "Docker"]),
    ("AI", ["Claude", "Gemini", "OpenAI API", "PyTorch", "agent pipelines"]),
    ("Product", ["PRDs", "UAT", "funnel analysis", "dashboards", "SOPs", "Figma"]),
]


def tools(t, theme):
    W = 840
    b = []
    y = 46
    for name, items in TOOLS:
        b.append(txt(36, y + 5, name, 16, t["print"], "condb"))
        x = 130
        for it in items:
            w = 26 + len(it) * 6.9
            if x + w > W - 24:
                x = 130
                y += 30
            b.append(bubble(x + 7, y, 7, t, filled=True))
            b.append(txt(x + 21, y + 5, it, 14.5, t["text"], "body"))
            x += w + 14
        y += 40
        if name != TOOLS[-1][0]:
            b.append(f'<line x1="36" y1="{y-20}" x2="{W-24}" y2="{y-20}" stroke="{t["rule"]}"/>')
    H = y - 8
    b.insert(0, timing_marks(H, t))
    return svg(W, H, "Tools I use: " + "; ".join(f"{n}: {', '.join(i)}" for n, i in TOOLS), "".join(b), t)


# ------------------------------------------------------------------ links
LINKS = [
    ("portfolio", "Portfolio", "anmolsethi.online"),
    ("linkedin", "LinkedIn", "in/anmol-sethi-79ba03228"),
    ("email", "Email", "anmolsethi911@gmail.com"),
    ("resume", "Resume", "Anmol_Resume.pdf"),
]


def link_card(t, label, value):
    W, H = 412, 88
    b = [txt(24, 34, label, 14, t["print"], "cond"),
         f'<line x1="24" y1="70" x2="{W-24}" y2="70" stroke="{t["print"]}" stroke-width=".9" stroke-dasharray="2 3"/>',
         txt(26, 64, value, 23, t["ink"], "pen")]
    return svg(W, H, f"{label}: {value}", "".join(b), t)


# ------------------------------------------------------------------ build
if __name__ == "__main__":
    for theme, t in THEMES.items():
        write("hero", theme, hero(t, theme))
        write("marks", theme, marks(t, theme))
        write("remarks", theme, remarks(t, theme))
        write("record", theme, record(t, theme))
        write("tools", theme, tools(t, theme))
        for name, fn in CARDS:
            write(f"project-{name}", theme, fn(t))
        for key, label, value in LINKS:
            write(f"link-{key}", theme, link_card(t, label, value))
    print("cards written")
