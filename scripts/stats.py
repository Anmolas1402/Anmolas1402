"""Draws the live activity card from the GitHub GraphQL API.

Run by .github/workflows/refresh.yml with GH_TOKEN set. Leaves the old card in
place if the API call fails, so a bad run never blanks the profile.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards_common import THEMES, svg, txt, write  # noqa: E402

LOGIN = "Anmolas1402"
Q = """query($login:String!){user(login:$login){
  createdAt
  contributionsCollection{totalCommitContributions totalPullRequestContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
  repositories(first:100,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount
    nodes{name stargazerCount pushedAt languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": Q, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def build(u, t):
    W, H = 840, 230
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    langs = {}
    colors = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs[n] = langs.get(n, 0) + e["size"]
            colors[n] = e["node"]["color"] or t["mute"]
    total_b = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:5]

    # current streak, counted back from today (today may still be empty)
    streak = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            streak += 1
        elif i > 0:
            break

    b = [txt(28, 34, "LIVE FROM GITHUB", 10.5, t["mute"], 700, mono=True, extra='letter-spacing="1.5"')]
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    b.append(txt(W - 28, 34, f"refreshed {stamp}", 10, t["mute"], 500, mono=True, anchor="end"))

    nums = [
        (f'{cc["contributionCalendar"]["totalContributions"]:,}', "contributions, last 12 months"),
        (f'{cc["totalCommitContributions"]:,}', "commits"),
        (f'{u["repositories"]["totalCount"]}', "public repos"),
        (f"{streak}", "day streak" if streak != 1 else "day streak"),
    ]
    for i, (v, l) in enumerate(nums):
        y = 72 + i * 42
        b.append(txt(28, y, v, 22, t["accent"] if i == 0 else t["text"], 800, extra='letter-spacing="-.6"'))
        b.append(txt(28, y + 16, l, 10.5, t["sub"], 500, mono=True))

    # heatmap, last 30 weeks
    weeks = cc["contributionCalendar"]["weeks"][-30:]
    hx, hy, cs, gap = 250, 52, 13, 3
    mx = max([d["contributionCount"] for w in weeks for d in w["contributionDays"]] + [1])
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dow = datetime.strptime(d["date"], "%Y-%m-%d").weekday()
            dow = (dow + 1) % 7  # Sunday first, like GitHub
            c = d["contributionCount"]
            if c == 0:
                fill, op = t["line"], 1
            else:
                fill, op = t["accent"], 0.3 + 0.7 * min(1, c / mx) ** 0.6
            b.append(f'<rect x="{hx + wi*(cs+gap)}" y="{hy + dow*(cs+gap)}" width="{cs}" height="{cs}" rx="3" fill="{fill}" opacity="{op:.2f}"/>')

    # languages bar
    ly = 190
    b.append(txt(hx, ly - 8, "LANGUAGES ACROSS PUBLIC REPOS", 9.5, t["mute"], 700, mono=True, extra='letter-spacing="1.2"'))
    bw = 30 * (cs + gap) - gap
    x = hx
    for n, s in top:
        w = bw * s / total_b
        b.append(f'<rect x="{x:.1f}" y="{ly}" width="{max(w-2,1):.1f}" height="8" rx="2" fill="{colors[n]}"/>')
        x += w
    lx = hx
    for n, s in top:
        label = f"{n} {100*s/total_b:.0f}%"
        b.append(f'<circle cx="{lx+4}" cy="{ly+24}" r="4" fill="{colors[n]}"/>')
        b.append(txt(lx + 12, ly + 28, label, 10.5, t["sub"], 500, mono=True))
        lx += 22 + len(label) * 6.4

    label = (f'{cc["contributionCalendar"]["totalContributions"]} contributions in the last year, '
             f'{cc["totalCommitContributions"]} commits, {u["repositories"]["totalCount"]} public repos, {stars} stars')
    return svg(W, H, label, "".join(b), t)


if __name__ == "__main__":
    try:
        user = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else fetch()
    except Exception as e:  # keep the old card
        print("stats fetch failed, keeping previous card:", e)
        sys.exit(0)
    for theme, t in THEMES.items():
        write("stats", theme, build(user, t))
    print("stats card written")
