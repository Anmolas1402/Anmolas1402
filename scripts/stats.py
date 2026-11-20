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
    W = 840
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    langs, colors = {}, {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs[n] = langs.get(n, 0) + e["size"]
            colors[n] = e["node"]["color"] or t["mute"]
    total_b = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:5]

    streak = 0  # counted back from today; today may still be empty
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            streak += 1
        elif i > 0:
            break

    b = [txt(32, 48, "Live from GitHub", 17, t["text"], 700)]
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    b.append(txt(W - 32, 48, f"refreshed {stamp}", 13, t["sub"], anchor="end"))

    nums = [
        (f'{cal["totalContributions"]:,}', "contributions"),
        (f'{cc["totalCommitContributions"]:,}', "commits"),
        (f'{u["repositories"]["totalCount"]}', "public repos"),
        (f"{stars}", "stars"),
        (f"{streak}", "day streak"),
    ]
    cw = (W - 64) / len(nums)
    for i, (v, l) in enumerate(nums):
        x = 32 + cw * i + cw / 2
        if i:
            b.append(f'<line x1="{32 + cw*i:.0f}" y1="72" x2="{32 + cw*i:.0f}" y2="124" stroke="{t["line"]}"/>')
        col = t["accent"] if i in (0, len(nums) - 1) else t["text"]
        b.append(txt(x, 104, v, 30, col, 800, anchor="middle", extra='letter-spacing="-1"'))
        b.append(txt(x, 126, l, 13, t["sub"], anchor="middle"))

    weeks = cal["weeks"][-52:]
    cs, gap = 11, 3.6
    gw = len(weeks) * (cs + gap) - gap
    hx, hy = (W - gw) / 2, 152
    mx = max([d["contributionCount"] for w in weeks for d in w["contributionDays"]] + [1])
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dow = (datetime.strptime(d["date"], "%Y-%m-%d").weekday() + 1) % 7
            c = d["contributionCount"]
            fill, op = (t["tile"], 1) if c == 0 else (t["accent"], 0.3 + 0.7 * min(1, c / mx) ** 0.6)
            b.append(f'<rect x="{hx + wi*(cs+gap):.1f}" y="{hy + dow*(cs+gap):.1f}" width="{cs}" height="{cs}" rx="2.5" '
                     f'fill="{fill}" opacity="{op:.2f}" stroke="{t["line"]}" stroke-opacity="{.6 if c == 0 else 0}"/>')

    ly = hy + 7 * (cs + gap) + 22
    x = hx
    for n, sz in top:
        w = gw * sz / total_b
        b.append(f'<rect x="{x:.1f}" y="{ly}" width="{max(w-3,1):.1f}" height="8" rx="4" fill="{colors[n]}"/>')
        x += w
    lx = hx
    for n, sz in top:
        label = f"{n} {100*sz/total_b:.0f}%"
        b.append(f'<circle cx="{lx+5}" cy="{ly+30}" r="5" fill="{colors[n]}"/>')
        b.append(txt(lx + 16, ly + 35, label, 13, t["sub"]))
        lx += 34 + len(label) * 7
    H = int(ly + 58)

    label = (f'{cal["totalContributions"]} contributions in the last year, {cc["totalCommitContributions"]} commits, '
             f'{u["repositories"]["totalCount"]} public repos, {stars} stars, {streak} day streak')
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
