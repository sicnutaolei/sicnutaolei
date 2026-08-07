#!/usr/bin/env python3
"""用 GitHub API 取真实数据，生成 stats.svg 与 trophies.svg。
环境变量：
  GH_USER  目标用户名（默认 sicnutaolei）
  GH_TOKEN  GitHub 令牌（可选；不填则匿名，速率受限）
  OUT_DIR   输出目录（默认当前目录）
"""
import os
import datetime
import requests

API = "https://api.github.com"
USER = os.environ.get("GH_USER", "sicnutaolei")
TOKEN = os.environ.get("GH_TOKEN", "")
OUT = os.environ.get("OUT_DIR", ".")


def api(path, params=None):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "profile-stats-bot"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    r = requests.get(API + path, headers=h, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tier(v, tiers):
    name = "None"
    for th, nm in tiers:
        if v >= th:
            name = nm
    return name


TIER_COLORS = {
    "None": "#585b70", "Bronze": "#b5793b", "Silver": "#9ba3ab",
    "Gold": "#f9e2af", "Platinum": "#89dceb", "Diamond": "#cba6f7",
}

BG = '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e1e2e"/><stop offset="1" stop-color="#181825"/></linearGradient></defs>'


def main():
    u = api(f"/users/{USER}")
    public_repos = u.get("public_repos", 0)
    followers = u.get("followers", 0)
    following = u.get("following", 0)
    created = (u.get("created_at") or "")[:10]
    years = 0.0
    if created:
        d0 = datetime.date.fromisoformat(created)
        years = round((datetime.date.today() - d0).days / 365.25, 1)

    repos = api(f"/users/{USER}/repos", params={"per_page": 100, "type": "public"})
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs = {}
    forks = 0
    for r in repos:
        l = r.get("language")
        if l:
            langs[l] = langs.get(l, 0) + 1
        if r.get("fork"):
            forks += 1
    top_lang = max(langs, key=langs.get) if langs else "\u2014"

    # ---------- stats card ----------
    rows = [
        ("\U0001F4E6", "Public Repos", public_repos),
        ("\U0001F465", "Followers", followers),
        ("\u27a1\ufe0f", "Following", following),
        ("\u2b50", "Total Stars", total_stars),
        ("\U0001F4BB", "Top Language", top_lang),
        ("\U0001F4C5", "On GitHub", f"{years} yrs"),
    ]
    W = 470
    pad = 22
    header_h = 44
    row_h = 34
    H = pad + header_h + len(rows) * row_h + pad
    y = pad + 30
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">']
    svg.append(BG)
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="url(#bg)"/>')
    svg.append(f'<text x="{pad}" y="{pad + 26}" font-size="20" font-weight="700" fill="#89b4fa">GitHub Stats \u00b7 @{esc(USER)}</text>')
    svg.append(f'<line x1="{pad}" y1="{pad + header_h - 6}" x2="{W - pad}" y2="{pad + header_h - 6}" stroke="#313244" stroke-width="1"/>')
    for icon, label, val in rows:
        svg.append(f'<text x="{pad}" y="{y}" font-size="18" fill="#cdd6f4">{esc(icon)}</text>')
        svg.append(f'<text x="{pad + 30}" y="{y}" font-size="15" fill="#a6adc8">{esc(label)}</text>')
        svg.append(f'<text x="{W - pad}" y="{y}" font-size="16" font-weight="700" fill="#f9e2af" text-anchor="end">{esc(val)}</text>')
        y += row_h
    svg.append("</svg>")
    with open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    # ---------- trophies card ----------
    trophies = [
        ("\U0001F4E6", "Repositories", public_repos, [(1, "Bronze"), (5, "Silver"), (15, "Gold"), (40, "Platinum"), (100, "Diamond")]),
        ("\u2b50", "Stars Earned", total_stars, [(1, "Bronze"), (10, "Silver"), (50, "Gold"), (200, "Platinum"), (500, "Diamond")]),
        ("\U0001F465", "Followers", followers, [(1, "Bronze"), (10, "Silver"), (50, "Gold"), (200, "Platinum"), (1000, "Diamond")]),
        ("\U0001F4C5", "Years on GH", years, [(1, "Bronze"), (2, "Silver"), (4, "Gold"), (7, "Platinum"), (10, "Diamond")]),
        ("\U0001F4BB", "Languages", len(langs), [(1, "Bronze"), (3, "Silver"), (5, "Gold"), (8, "Platinum"), (12, "Diamond")]),
        ("\U0001F94D", "Forks", forks, [(1, "Bronze"), (3, "Silver"), (8, "Gold"), (20, "Platinum"), (50, "Diamond")]),
    ]
    cols = 3
    cell_w = 150
    cell_h = 84
    gx = 12
    gy = 12
    pad2 = 20
    header_h2 = 44
    rows_n = (len(trophies) + cols - 1) // cols
    W2 = pad2 * 2 + cols * cell_w + (cols - 1) * gx
    H2 = pad2 * 2 + header_h2 + rows_n * cell_h + (rows_n - 1) * gy
    t = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" font-family="Segoe UI, Helvetica, Arial, sans-serif">']
    t.append(BG)
    t.append(f'<rect x="0" y="0" width="{W2}" height="{H2}" rx="14" fill="url(#bg)"/>')
    t.append(f'<text x="{pad2}" y="{pad2 + 26}" font-size="20" font-weight="700" fill="#89b4fa">Trophies</text>')
    for i, (icon, label, val, tiers) in enumerate(trophies):
        r_i = i // cols
        c_i = i % cols
        x = pad2 + c_i * (cell_w + gx)
        yy = pad2 + header_h2 + r_i * (cell_h + gy)
        lvl = tier(val, tiers)
        col = TIER_COLORS[lvl]
        t.append(f'<rect x="{x}" y="{yy}" width="{cell_w}" height="{cell_h}" rx="10" fill="#313244" stroke="{col}" stroke-width="2"/>')
        t.append(f'<text x="{x + 14}" y="{yy + 34}" font-size="22" fill="#cdd6f4">{esc(icon)}</text>')
        t.append(f'<text x="{x + 44}" y="{yy + 30}" font-size="13" fill="#a6adc8">{esc(label)}</text>')
        t.append(f'<text x="{x + 44}" y="{yy + 54}" font-size="15" font-weight="700" fill="{col}">{esc(val)} \u00b7 {lvl}</text>')
    t.append("</svg>")
    with open(os.path.join(OUT, "trophies.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(t))

    print(f"OK user={USER} repos={public_repos} stars={total_stars} followers={followers} langs={len(langs)} years={years}")


if __name__ == "__main__":
    main()
