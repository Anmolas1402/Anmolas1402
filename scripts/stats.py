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
from build_cards import bubble, timing_marks  # noqa: E402

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
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total_b = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:5]

    streak = 0  # counted back from today; today may still be empty
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            streak += 1
        elif i > 0:
            break

    b = [txt(36, 44, "Attendance on GitHub, last 12 months", 15, t["print"], "cond")]
    stamp = datetime.now(timezone.utc).strftime("%-d %b %Y")
    b.append(txt(W - 24, 44, f"Checked on {stamp}", 14, t["print"], "cond", "end"))

    nums = [
        ("Contributions", f'{cal["totalContributions"]:,}'),
        ("Commits", f'{cc["totalCommitContributions"]:,}'),
        ("Public repos", f'{u["repositories"]["totalCount"]}'),
        ("Current streak", f"{streak} days"),
    ]
    cw = (W - 60) / len(nums)
    for i, (lab, v) in enumerate(nums):
        x = 36 + cw * i
        b.append(txt(x, 82, lab, 14, t["print"], "cond"))
        b.append(f'<line x1="{x}" y1="116" x2="{x + cw - 28:.0f}" y2="116" stroke="{t["print"]}" stroke-width=".9"/>')
        b.append(txt(x + 2, 110, v, 26, t["ink"], "pen"))

    weeks = cal["weeks"][-53:]
    pitch, r = 13.6, 4.9
    gw = len(weeks) * pitch
    hx, hy = 36 + (W - 60 - gw) / 2 + pitch / 2, 150
    for k, dname in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b.append(txt(hx - 12, hy + k * pitch + 4, dname, 10, t["print"], "cond", "end"))
    mx = max([d["contributionCount"] for w in weeks for d in w["contributionDays"]] + [1])
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dow = (datetime.strptime(d["date"], "%Y-%m-%d").weekday() + 1) % 7
            c = d["contributionCount"]
            op = 0.35 + 0.65 * min(1, c / mx) ** 0.6
            b.append(bubble(hx + wi * pitch, hy + dow * pitch, r, t, filled=c > 0, opacity=f"{op:.2f}"))

    ly = hy + 7 * pitch + 20
    b.append(txt(36, ly + 5, "Languages", 14, t["print"], "cond"))
    lx = 110
    for n, sz in top:
        label = f"{n} {100*sz/total_b:.0f}%"
        b.append(bubble(lx + 7, ly, 7, t, filled=True))
        b.append(txt(lx + 21, ly + 5, label, 14, t["text"], "body"))
        lx += 40 + len(label) * 7
    H = int(ly + 30)
    b.insert(0, timing_marks(H, t))
    label = (f'GitHub attendance: {cal["totalContributions"]} contributions in the last year, '
             f'{cc["totalCommitContributions"]} commits, {u["repositories"]["totalCount"]} public repos, {streak} day streak')
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
