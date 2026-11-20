"""Delhi Metro edition of the profile cards.

Run: python3 scripts/metro.py [outdir]
The career drawn as a metro line: a bilingual station board with a
platform LED display, a route map, station info panels and exit gates.
"""
import base64
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards_common import ROOT, svg, txt, image  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)

LINE = dict(yellow="#ffc80a", blue="#1f66b5", magenta="#c4227f", violet="#7a4cc2", green="#00843d", red="#d7262e")
BOARD = "#22305c"
LED = "#ffb21e"
HOUSING = "#1d1a14"

THEMES = {
    "light": dict(bg="#ffffff", text="#1b2033", sub="#55607a", rule="#d8dce6", panel="#f3f5f9", station="#ffffff"),
    "dark": dict(bg="#141a2e", text="#f1f3f8", sub="#a9b1c6", rule="#2f3854", panel="#1b2240", station="#141a2e"),
}


def write(name, theme, content):
    with open(os.path.join(OUT, f"{name}-{theme}.svg"), "w") as f:
        f.write(content)


# ------------------------------------------------------------------ LED display
def led_strip(text, pitch=5, rows=17):
    """Render text as lit LED dots, returned as (png data uri, width, height)."""
    from fontTools.ttLib import TTFont
    tt = TTFont(os.path.join(ROOT, "data", "fonts", "hind-latin-600-normal.woff2"))
    tt.flavor = None
    raw = io.BytesIO()
    tt.save(raw)
    raw.seek(0)
    font = ImageFont.truetype(raw, 17)
    w = int(font.getlength(text)) + 4
    im = Image.new("L", (w, rows + 4), 0)
    ImageDraw.Draw(im).text((0, -3), text, font=font, fill=255)
    cols, rr = im.size
    big = Image.new("RGBA", (cols * pitch, rr * pitch), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    amber = tuple(int(LED[i:i + 2], 16) for i in (1, 3, 5))
    px = im.load()
    for y in range(rr):
        for x in range(cols):
            if px[x, y] > 110:
                cx, cy = x * pitch + pitch / 2, y * pitch + pitch / 2
                d.ellipse([cx - 1.9, cy - 1.9, cx + 1.9, cy + 1.9], fill=amber + (255,))
    buf = io.BytesIO()
    big.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), big.width, big.height


def hero(theme):
    W, H = 840, 410
    t = THEMES[theme]
    b = [f'<rect width="{W}" height="{H}" rx="10" fill="{BOARD}"/>']
    # platform pictogram
    b.append(f'<rect x="{W-96}" y="30" width="58" height="58" rx="6" fill="#ffffff"/>')
    b.append(txt(W - 67, 78, "1", 46, BOARD, "hindb", "middle"))
    b.append(txt(W - 108, 54, "प्लेटफ़ॉर्म", 15, "#c9d1ea", "deva", "end"))
    b.append(txt(W - 108, 78, "Platform", 16, "#ffffff", "hinds", "end"))
    # station name, Hindi above English, as on every DMRC board
    b.append(txt(44, 92, "अनमोल सेठी", 44, "#ffffff", "deva"))
    b.append(txt(40, 172, "Anmol Sethi", 80, "#ffffff", "hindb", extra='letter-spacing="-1.5"'))
    b.append(txt(44, 206, "Product ops, Gurugram. Towards your product team.", 18, "#c9d1ea", "hind"))
    # line stripe
    b.append(f'<rect x="0" y="226" width="{W}" height="14" fill="{LINE["yellow"]}"/>')
    # LED platform display
    msg = ("NEXT STATION: YOUR PRODUCT TEAM      ANMOL SETHI, PRODUCT OPS      CAN JOIN IMMEDIATELY      "
           "500K+ STUDENTS REACHED AT MATHONGO      1,298 NCR STARTUPS MAPPED      ")
    uri, lw, lh = led_strip(msg)
    lx, ly, lwid, lht = 34, 270, W - 68, 106
    b.append(f'<rect x="{lx-10}" y="{ly-12}" width="{lwid+20}" height="{lht+24}" rx="6" fill="{HOUSING}"/>')
    b.append(f'<defs><pattern id="off" width="5" height="5" patternUnits="userSpaceOnUse">'
             f'<circle cx="2.5" cy="2.5" r="1.6" fill="#3a3122"/></pattern>'
             f'<clipPath id="ledclip"><rect x="{lx}" y="{ly}" width="{lwid}" height="{lht}"/></clipPath></defs>')
    b.append(f'<rect x="{lx}" y="{ly}" width="{lwid}" height="{lht}" fill="url(#off)"/>')
    top = ly + (lht - lh) / 2
    b.append(f'<g clip-path="url(#ledclip)"><g class="marquee">'
             f'<image x="{lx}" y="{top:.0f}" width="{lw}" height="{lh}" href="{uri}" xlink:href="{uri}"/>'
             f'<image x="{lx+lw}" y="{top:.0f}" width="{lw}" height="{lh}" href="{uri}" xlink:href="{uri}"/>'
             f'</g></g>')
    css = (f"@keyframes run{{to{{transform:translateX(-{lw}px)}}}}"
           f".marquee{{animation:run {lw/90:.0f}s linear infinite}}")
    label = "Anmol Sethi, अनमोल सेठी. Product ops, Gurugram. Next station: your product team. Can join immediately."
    return svg(W, H, label, "".join(b), t, frame=False, extra_css=css)


# ------------------------------------------------------------------ route map
STATIONS = [  # x, name, when, kind
    (64, "Thapar Institute", "2022", "terminus"),
    (196, "MathonGo", "Dec 2023", "interchange"),
    (330, "ARC, Thapar", "Sept 2025", "station"),
    (446, "NCR Hiring Map", "2026", "station"),
    (556, "100-App Study", "2026", "station"),
    (666, "OAuth Fieldguide", "2026", "station"),
    (764, "Your team", "Next", "future"),
]
BRANCH = ["Test series, 1 to 14 exams", "College Predictor, 99.4%", "500K+ students reached", "100+ interns onboarded"]


def route(theme):
    t = THEMES[theme]
    W, H = 840, 430
    y = 176
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["bg"]}" stroke="{t["rule"]}"/>']
    b.append(txt(36, 46, "The Anmol Line", 20, t["text"], "hindb"))
    b.append(txt(36, 70, "Every stop so far, and the one I'm headed to.", 15, t["sub"], "hind"))
    # main line
    b.append(f'<line x1="64" y1="{y}" x2="666" y2="{y}" stroke="{LINE["yellow"]}" stroke-width="10" stroke-linecap="round"/>')
    b.append(f'<line x1="666" y1="{y}" x2="764" y2="{y}" stroke="{LINE["yellow"]}" stroke-width="10" stroke-dasharray="10 8"/>')
    # MathonGo branch
    bx = 196
    by0, step = y + 74, 40
    b.append(f'<path d="M{bx} {y} V{by0 + step*(len(BRANCH)-1)}" stroke="{LINE["blue"]}" stroke-width="8" fill="none" stroke-linecap="round"/>')
    for i, name in enumerate(BRANCH):
        yy = by0 + i * step
        b.append(f'<circle cx="{bx}" cy="{yy}" r="7" fill="{t["station"]}" stroke="{LINE["blue"]}" stroke-width="3.5"/>')
        b.append(txt(bx + 20, yy + 5, name, 15, t["text"], "hind"))
    for x, name, when, kind in STATIONS:
        if kind == "interchange":
            b.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{t["station"]}" stroke="{t["text"]}" stroke-width="4"/>')
        elif kind == "future":
            b.append(f'<circle cx="{x}" cy="{y}" r="11" fill="{t["station"]}" stroke="{LINE["yellow"]}" stroke-width="4" stroke-dasharray="4 3"/>')
        else:
            b.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{t["station"]}" stroke="{t["text"]}" stroke-width="3"/>')
        b.append(f'<g transform="rotate(-38 {x} {y-22})">'
                 + txt(x, y - 22, name, 15, t["text"], "hinds") + "</g>")
        if x != bx:
            b.append(txt(x, y + 36, when, 13, t["sub"], "hind", "middle"))
        else:
            b.append(txt(x - 20, y + 36, when, 13, t["sub"], "hind", "end"))
    label = ("Route map of Anmol's career: Thapar Institute 2022, MathonGo Dec 2023 with a branch for the test series, "
             "College Predictor, 500K+ students and 100+ interns, ARC Thapar Sept 2025, NCR Hiring Map, "
             "100-App Study and OAuth Fieldguide in 2026, next stop your team.")
    return svg(W, H, label, "".join(b), t, frame=False)


# ------------------------------------------------------------------ station panels
def station_card(theme, code, color, title, lines, change, big, big_label):
    t = THEMES[theme]
    W, H = 412, 212
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["bg"]}" stroke="{t["rule"]}"/>',
         f'<path d="M10 .5 H{W-10} a9.5 9.5 0 0 1 9.5 9.5 V12 H.5 V10 a9.5 9.5 0 0 1 9.5 -9.5z" fill="{color}"/>']
    b.append(f'<circle cx="44" cy="54" r="20" fill="{color}"/>')
    b.append(txt(44, 60, code, 15, "#ffffff" if color != LINE["yellow"] else "#1b2033", "hindb", "middle"))
    b.append(txt(76, 62, title, 23, t["text"], "hindb"))
    for i, l in enumerate(lines):
        b.append(txt(24, 104 + i * 22, l, 15, t["sub"], "hind"))
    b.append(f'<line x1="24" y1="160" x2="{W-24}" y2="160" stroke="{t["rule"]}"/>')
    # interchange glyph
    b.append(f'<circle cx="32" cy="184" r="7" fill="none" stroke="{t["text"]}" stroke-width="2.5"/>')
    b.append(txt(48, 189, f"Change here for {change}", 14, t["text"], "hinds"))
    b.append(txt(W - 24, 112, big, 30, color if color != LINE["yellow"] else ("#b88a00" if theme == "light" else LINE["yellow"]), "hindb", "end"))
    b.append(txt(W - 24, 134, big_label, 13, t["sub"], "hind", "end"))
    return svg(W, H, f"{title}: {' '.join(lines)} {big} {big_label}", "".join(b), t, frame=False)


CARDS = [
    ("ncrhiring", "NH", LINE["yellow"], "NCR Hiring Map", ["Every startup hiring in Delhi NCR,", "from a scraping pipeline.", ""],
     "Next.js, Leaflet", "1,298", "startups mapped"),
    ("fieldguide", "OF", LINE["magenta"], "OAuth Fieldguide", ["Type a provider, get its OAuth", "guide. Every claim shows its", "evidence."],
     "TypeScript, agents", "3", "claim labels"),
    ("buildability", "AB", LINE["blue"], "100-App Study", ["Which apps can you integrate,", "and what stops you? Every", "claim has a source."],
     "Python, agents", "92.5%", "claim accuracy"),
    ("predictor", "CP", LINE["violet"], "College Predictor", ["Exam marks to a likely college", "in one flow, at MathonGo.", ""],
     "product, data, UAT", "~10 L", "visits in 3 months"),
]


# ------------------------------------------------------------------ exits
EXITS = [("portfolio", "1", "Portfolio", "anmolsethi.online"),
         ("linkedin", "2", "LinkedIn", "in/anmol-sethi-79ba03228"),
         ("email", "3", "Email", "anmolsethi911@gmail.com"),
         ("resume", "4", "Resume", "Anmol_Resume.pdf")]


def exit_card(theme, gate, title, value):
    t = THEMES[theme]
    W, H = 412, 96
    g = LINE["green"]
    b = [f'<rect width="{W}" height="{H}" rx="10" fill="{g}"/>',
         f'<rect x="16" y="16" width="64" height="64" rx="6" fill="#ffffff"/>',
         txt(48, 46, "निकास", 16, g, "deva", "middle"),
         txt(48, 68, "Exit", 17, g, "hindb", "middle"),
         txt(98, 42, f"Gate {gate}", 15, "#d7f2e2", "hinds"),
         txt(98, 70, title, 24, "#ffffff", "hindb"),
         txt(W - 22, 70, value, 15, "#ffffff", "hind", "end")]
    return svg(W, H, f"Gate {gate}, {title}: {value}", "".join(b), t, frame=False)


# ------------------------------------------------------------------ notice
QUOTE = ["Anmol is a cool-headed guy who can manage a big team at such a young age.",
         "Started working at a young age. I worked with Anmol on multiple products from",
         "scratch at MathonGo for a good 1.5 years. Highly recommend Anmol for",
         "management, consulting and product roles."]


def notice(theme):
    t = THEMES[theme]
    W = 840
    H = 108 + len(QUOTE) * 28 + 70
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["bg"]}" stroke="{t["rule"]}"/>',
         f'<path d="M10 .5 H{W-10} a9.5 9.5 0 0 1 9.5 9.5 V58 H.5 V10 a9.5 9.5 0 0 1 9.5 -9.5z" fill="{BOARD}"/>',
         txt(36, 38, "सूचना", 19, "#c9d1ea", "deva"),
         txt(100, 38, "A word from my manager", 19, "#ffffff", "hinds")]
    y = 100
    for l in QUOTE:
        b.append(txt(36, y, l, 17, t["text"], "hind"))
        y += 28
    b.append(f'<rect x="36" y="{y+4}" width="6" height="44" fill="{LINE["yellow"]}"/>')
    b.append(txt(54, y + 22, "Kunal Taneja", 17, t["text"], "hindb"))
    b.append(txt(54, y + 44, "Founder, Canvas Classes. Ex-Head of Content, MathonGo. Managed me directly.", 14, t["sub"], "hind"))
    return svg(W, H, "Kunal Taneja on Anmol: " + " ".join(QUOTE), "".join(b), t, frame=False)


# ------------------------------------------------------------------ numbers
NUMS = [("500K+", "students reached"), ("1 → 14", "exams scaled"), ("99.4%", "predictor accuracy"),
        ("100+", "interns onboarded"), ("1,298", "startups mapped")]


def numbers(theme):
    t = THEMES[theme]
    W, H = 840, 120
    b = [f'<rect width="{W}" height="{H}" rx="10" fill="{BOARD}"/>']
    cw = (W - 40) / len(NUMS)
    for i, (v, l) in enumerate(NUMS):
        cx = 20 + cw * i + cw / 2
        if i:
            b.append(f'<line x1="{20+cw*i:.0f}" y1="26" x2="{20+cw*i:.0f}" y2="94" stroke="#3b4a7e"/>')
        b.append(txt(cx, 66, v, 34, "#ffffff", "hindb", "middle"))
        b.append(txt(cx, 92, l, 14, "#c9d1ea", "hind", "middle"))
    return svg(W, H, "Numbers: " + ", ".join(f"{v} {l}" for v, l in NUMS), "".join(b), t, frame=False)


for theme in THEMES:
    write("hero", theme, hero(theme))
    write("route", theme, route(theme))
    write("notice", theme, notice(theme))
    write("numbers", theme, numbers(theme))
    for key, *args in CARDS:
        write(f"station-{key}", theme, station_card(theme, *args))
    for key, gate, title, value in EXITS:
        write(f"exit-{key}", theme, exit_card(theme, gate, title, value))
print("metro cards written to", OUT)
