import requests
import json
import math
import os
from datetime import datetime, timedelta

LEETCODE_USERNAME = "zqU0CvVnA1"

def fetch_leetcode_calendar(username):
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            submissionCalendar
        }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }
    response = requests.post(
        url,
        json={"query": query, "variables": {"username": username}},
        headers=headers,
        timeout=15
    )
    data = response.json()
    calendar_str = data["data"]["matchedUser"]["submissionCalendar"]
    return json.loads(calendar_str)

def build_grid(calendar):
    today = datetime.now()
    start = today - timedelta(weeks=52)
    # Align to Monday
    start = start - timedelta(days=start.weekday())

    grid = []
    for week in range(53):
        week_data = []
        for day in range(7):
            date = start + timedelta(weeks=week, days=day)
            count = 0
            for ts_str, cnt in calendar.items():
                ts_date = datetime.fromtimestamp(int(ts_str))
                if ts_date.date() == date.date():
                    count += cnt
            week_data.append(count)
        grid.append(week_data)
    return grid

def get_color(count, theme):
    if theme == "dark":
        if count == 0:   return "#1a1a2e"
        elif count <= 2: return "#f7a941"
        elif count <= 5: return "#ff8c00"
        else:            return "#ffa116"
    else:
        if count == 0:   return "#ebedf0"
        elif count <= 2: return "#ffd280"
        elif count <= 5: return "#ffb347"
        else:            return "#ffa116"

def generate_svg(grid, theme):
    CELL  = 12
    PAD   = 2
    STEP  = CELL + PAD
    MARGIN = 20
    SNAKE_CELLS = 5

    weeks = len(grid)
    days  = 7
    W = weeks * STEP + MARGIN * 2
    H = days  * STEP + MARGIN * 2

    bg     = "#0d1117" if theme == "dark" else "#ffffff"
    snake  = "#00ff88"
    head   = "#00ffee"

    # --- build serpentine path through cell centres ---
    pts = []
    for col in range(weeks):
        rng = range(days) if col % 2 == 0 else range(days - 1, -1, -1)
        for row in rng:
            cx = MARGIN + col * STEP + CELL / 2
            cy = MARGIN + row * STEP + CELL / 2
            pts.append((cx, cy))

    # path length
    total_len = sum(
        math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)
    )
    snake_len = SNAKE_CELLS * STEP

    path_d = "M " + " L ".join(f"{x},{y}" for x, y in pts)

    # --- cell rectangles ---
    cells = ""
    for col, week in enumerate(grid):
        for row, count in enumerate(week):
            x = MARGIN + col * STEP
            y = MARGIN + row * STEP
            cells += f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{get_color(count, theme)}"/>\n    '

    dur = "10s"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    @keyframes move {{
      from {{ stroke-dashoffset: {snake_len:.1f}; }}
      to   {{ stroke-dashoffset: {-(total_len + snake_len):.1f}; }}
    }}
    .body {{ animation: move {dur} linear infinite; }}
    .head {{ animation: move {dur} linear infinite; }}
  </style>

  <rect width="{W}" height="{H}" fill="{bg}" rx="6"/>

  {cells}

  <!-- snake body -->
  <path d="{path_d}" fill="none" stroke="{snake}"
    stroke-width="{CELL - 2}" stroke-linecap="round" stroke-linejoin="round"
    stroke-dasharray="{snake_len:.1f} {total_len + snake_len * 2:.1f}"
    stroke-dashoffset="{snake_len:.1f}"
    class="body" opacity="0.85"/>

  <!-- snake head -->
  <path d="{path_d}" fill="none" stroke="{head}"
    stroke-width="{CELL - 6}" stroke-linecap="round" stroke-linejoin="round"
    stroke-dasharray="5 {total_len + snake_len * 2:.1f}"
    stroke-dashoffset="{snake_len - 2:.1f}"
    class="head" opacity="1"/>
</svg>'''

def main():
    print(f"Fetching LeetCode calendar for {LEETCODE_USERNAME} ...")
    calendar = fetch_leetcode_calendar(LEETCODE_USERNAME)
    print(f"  {len(calendar)} active days found")

    grid = build_grid(calendar)
    os.makedirs("dist", exist_ok=True)

    for theme in ("dark", "light"):
        suffix = "-dark" if theme == "dark" else ""
        fname  = f"dist/leetcode-contribution-grid-snake{suffix}.svg"
        with open(fname, "w") as f:
            f.write(generate_svg(grid, theme))
        print(f"  wrote {fname}")

    print("Done.")

if __name__ == "__main__":
    main()
