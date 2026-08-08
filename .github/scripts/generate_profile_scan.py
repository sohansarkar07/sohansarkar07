#!/usr/bin/env python3
"""
GitHub Profile Scan SVG Generator
Generates a terminal-style 'profile scan' SVG for GitHub README
"""

import os
import requests
from datetime import datetime

USERNAME = "sohansarkar07"


def fetch_stats():
    token = os.environ.get("METRICS_TOKEN", "")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"} if token else {}

    try:
        user = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers, timeout=10).json()
        repos_raw = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated",
            headers=headers, timeout=10
        ).json()
        repos = [r for r in repos_raw if isinstance(r, dict)]

        stars = sum(r.get("stargazers_count", 0) for r in repos)
        langs = []
        for r in repos:
            lang = r.get("language")
            if lang and lang not in langs:
                langs.append(lang)

        # Try to get contribution count via search
        search = requests.get(
            f"https://api.github.com/search/commits?q=author:{USERNAME}&per_page=1",
            headers={**headers, "Accept": "application/vnd.github.cloak-preview+json"},
            timeout=10
        ).json()
        contributions = search.get("total_count", "N/A")

        created_year = (user.get("created_at") or "2025")[:4]
        current_year = datetime.utcnow().year
        active_days = (current_year - int(created_year)) * 365

        bio = (user.get("bio") or "Full-Stack AI Developer")
        if len(bio) > 35:
            bio = bio[:32] + "..."

        return {
            "handle": f"@{USERNAME}",
            "name": user.get("name") or USERNAME,
            "bio": bio,
            "languages": ", ".join(langs[:5]),
            "repositories": user.get("public_repos", len(repos)),
            "contributions": contributions,
            "stars": stars,
            "followers": user.get("followers", 0),
            "active_days": active_days,
            "contact": f"github.com/{USERNAME}",
        }

    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {
            "handle": f"@{USERNAME}",
            "name": "Sohan Sarkar",
            "bio": "Full-Stack AI Developer",
            "languages": "Python, JavaScript, Rust, C++",
            "repositories": 28,
            "contributions": "478",
            "stars": 9,
            "followers": 33,
            "active_days": 365,
            "contact": f"github.com/{USERNAME}",
        }


def esc(s):
    """Escape XML special characters."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_svg(stats):
    # ASCII art of a radar/face scan (fixed decorative)
    ascii_art = [
        "       .::::::.        ",
        "    .::::::::::::.     ",
        "   :::: .:::::. ::::   ",
        "  :::  .::::::::  :::  ",
        "  :: .:::::::::::: ::  ",
        " ::: :::: :::: :::: :: ",
        " ::: :::  .  .  ::: :: ",
        " ::: ::: [#] [#] :: :: ",
        " ::: ::::  ~~~  :::::::",
        " ::: ::::::::::::::::: ",
        "  ::::  .:-----:.  ::  ",
        "  :::::.  -----  .::: .",
        "   ::::::.......::::: .",
        "   .. :::::::::::.. ..  ",
        "  .:   ..:::::.  .::.  ",
        "  ::. .       . .:::   ",
        "   ::::::::::::::::    ",
        "    .:::::::::::.      ",
    ]

    W, H = 920, 510

    ascii_lines = ""
    for i, line in enumerate(ascii_art):
        y = 130 + i * 18
        ascii_lines += f'<text x="28" y="{y}" class="ascii">{esc(line)}</text>\n    '

    stat_rows = [
        ("Handle", stats["handle"]),
        ("Subject", stats["name"]),
        ("Role", stats["bio"]),
        ("Languages", stats["languages"]),
        ("Repositories", str(stats["repositories"])),
        ("Contributions", str(stats["contributions"])),
        ("Stars", str(stats["stars"])),
        ("Followers", str(stats["followers"])),
        ("Active Days", str(stats["active_days"])),
        ("Contact", stats["contact"]),
    ]

    stat_elements = ""
    for i, (label, value) in enumerate(stat_rows):
        y = 155 + i * 30
        val_display = esc(str(value)[:30])
        stat_elements += f"""
    <line x1="445" y1="{y - 14}" x2="{W - 20}" y2="{y - 14}" class="divider"/>
    <text x="450" y="{y}" class="label">{esc(label)}</text>
    <text x="630" y="{y}" class="value">{val_display}</text>"""

    cursor_y = 155 + len(stat_rows) * 30
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&amp;display=swap');
      .bg    {{ fill: #060c06; }}
      .frame {{ fill: none; stroke: #00ff41; stroke-width: 1.5; opacity: 0.6; }}
      .title {{ font-family: 'Share Tech Mono', 'Courier New', monospace; font-size: 13px; fill: #00ff41; letter-spacing: 4px; font-weight: bold; }}
      .ascii {{ font-family: 'Share Tech Mono', 'Courier New', monospace; font-size: 13px; fill: #00cc33; }}
      .label {{ font-family: 'Share Tech Mono', 'Courier New', monospace; font-size: 12px; fill: #00aa22; letter-spacing: 1px; }}
      .value {{ font-family: 'Share Tech Mono', 'Courier New', monospace; font-size: 12px; fill: #00ff88; }}
      .header{{ font-family: 'Share Tech Mono', 'Courier New', monospace; font-size: 11px; fill: #00ff4160; letter-spacing: 2px; }}
      .divider {{ stroke: #00ff4118; stroke-width: 0.8; }}
      .sep    {{ stroke: #00ff4150; stroke-width: 1; }}
      .cursor {{ fill: #00ff41; animation: blink 1s step-end infinite; }}
      .scan   {{ fill: none; stroke: #00ff4112; stroke-width: 60; animation: scandown 5s linear infinite; }}
      @keyframes blink    {{ 0%,100%{{opacity:1;}} 50%{{opacity:0;}} }}
      @keyframes scandown {{ 0%{{stroke-dashoffset:0;transform:translateY(-120px);}} 100%{{transform:translateY({H + 120}px);}} }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" class="bg" rx="10"/>

  <!-- Subtle grid lines -->
  {"".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#00ff4106" stroke-width="1"/>' for y in range(0, H, 20))}

  <!-- Scanline animation -->
  <line x1="0" y1="0" x2="{W}" y2="0" class="scan"/>

  <!-- Outer frame -->
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" class="frame" rx="6"/>

  <!-- Title bar -->
  <rect x="8" y="8" width="{W - 16}" height="40" fill="#00ff4108" rx="6"/>
  <circle cx="28" cy="28" r="5" fill="#ff5f56" opacity="0.9"/>
  <circle cx="48" cy="28" r="5" fill="#ffbd2e" opacity="0.9"/>
  <circle cx="68" cy="28" r="5" fill="#27c93f" opacity="0.9"/>
  <text x="{W // 2}" y="33" class="title" text-anchor="middle">PROFILE_SCAN.EXE</text>

  <!-- Shell header -->
  <text x="20" y="66" class="header">$ ./profile-scan --target {esc(USERNAME)} --live</text>
  <text x="20" y="84" class="header">SCANNING... STATUS: ONLINE | {esc(timestamp)}</text>
  <line x1="8" y1="94" x2="{W - 8}" y2="94" class="sep"/>

  <!-- Vertical separator -->
  <line x1="435" y1="94" x2="435" y2="{H - 8}" class="sep"/>

  <!-- Left panel header -->
  <text x="28" y="114" class="label">VISUAL.MAP</text>

  <!-- ASCII Art -->
  {ascii_lines}

  <!-- Right panel header -->
  <text x="450" y="114" class="label">SYSTEM.INFO</text>
  <text x="630" y="114" class="label">SUBJECT</text>

  <!-- Stat rows -->
  {stat_elements}

  <!-- Blinking cursor -->
  <rect x="450" y="{cursor_y + 4}" width="9" height="14" class="cursor"/>

  <!-- Footer -->
  <line x1="8" y1="{H - 28}" x2="{W - 8}" y2="{H - 28}" class="sep"/>
  <text x="20" y="{H - 12}" class="header">[ ACCESS GRANTED ] &#x2588; SECURE CONNECTION ESTABLISHED</text>
  <text x="{W - 20}" y="{H - 12}" class="header" text-anchor="end">AUTO-REFRESH: DAILY</text>
</svg>"""

    return svg


if __name__ == "__main__":
    print("Fetching GitHub stats...")
    stats = fetch_stats()
    print(f"Stats fetched: {stats}")

    print("Generating SVG...")
    svg = generate_svg(stats)

    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "profile-scan.svg")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Done! SVG saved to {output_path}")
