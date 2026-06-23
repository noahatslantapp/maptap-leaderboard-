#!/usr/bin/env python3
"""
Reads the #maptap Slack channel and writes data.json for the leaderboard site.

Minimal-access design: this script ONLY reads the one channel you point it at and
does NOT read the workspace user directory or any other channel. Player names are
resolved from the built-in MEMBERS map below (no users:read scope needed).

Environment variables (set as GitHub Actions secrets / env):
  SLACK_BOT_TOKEN      Bot User OAuth Token (starts with xoxb-)
  MAPTAP_CHANNEL_ID    The channel ID (default: the #maptap channel)

Required Slack bot scope: channels:history   (that's the only one)
The bot must be invited to the channel:  /invite @your-bot-name  in #maptap
Uses the Python standard library only — no packages to install.
"""
import os, re, json, time, urllib.request, urllib.parse, datetime

TOKEN = os.environ["SLACK_BOT_TOKEN"]
CHANNEL_ID = os.environ.get("MAPTAP_CHANNEL_ID", "C0B6XR5SKEZ")

# user_id -> display name, for everyone who posts in #maptap.
# Add a line here when a new person joins the game (find their ID by clicking
# their name in Slack -> "Copy member ID"). Unknown IDs fall back to the ID itself.
MEMBERS = {
    "U062ZL2MZKR": "Hayden Neal",
    "U083YMPDV7S": "Hannah Gaskill",
    "U0777UVE75Z": "Mckade Adams",
    "U0AGJN69AQN": "Emma Walton",
    "U04DFQXD04U": "Max Metcalf",
    "U0ADP5H1VD4": "Chris Arnold",
    "U0B433R2F61": "Mitch",
    "U0B1X34UCRJ": "Noah Hankin",
    "U0B9ZSVDMUZ": "Haley Brown",
    "U0B4K0M14KC": "Johnny Richards",
    "U09U4Q8DU9M": "Trevan Reese",
    "U04QX0HSSLC": "Thomas Clawson",
    "U0AU0G9QMQE": "Jeff Barton",
    "U0B440YRQ3H": "Russell Epling",
    "U0ATZ5ZQN4D": "Jonathan Farnsworth",
    "U0AN4E26WSX": "Jake Hope",
    "U0AC040ALQ7": "McKay Murphy",
    "U0B4M9V1JGH": "Nicole Priest",
    "U0A9HQN9B8D": "Seth Stones",
    "U09MLHRLFUZ": "McKay Court",
}

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}
MONTH_RE = re.compile(r"(" + "|".join(MONTHS) + r")\s+(\d{1,2})", re.I)
FINAL_RE = re.compile(r"Final score:\s*(\d+)", re.I)


def history():
    """Read messages from the one configured channel. Nothing else is touched."""
    msgs, cursor = [], ""
    while True:
        url = "https://slack.com/api/conversations.history?" + urllib.parse.urlencode(
            {"channel": CHANNEL_ID, "limit": 200, "cursor": cursor})
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + TOKEN})
        with urllib.request.urlopen(req) as r:
            d = json.load(r)
        if not d.get("ok"):
            raise RuntimeError(f"Slack API error: {d.get('error')}")
        msgs.extend(d["messages"])
        cursor = d.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            return msgs
        time.sleep(1)  # stay under rate limits


def parse(text):
    dm = MONTH_RE.search(text)
    fs = FINAL_RE.search(text)
    if not dm or not fs or fs.start() <= dm.end():
        return None
    month = MONTHS[dm.group(1).lower()]
    day = int(dm.group(2))
    rounds = []
    for tok in text[dm.end():fs.start()].split():
        m = re.match(r"(\d{1,3}):", tok)   # leading number of each "NN:emoji:" token
        if m:
            v = int(m.group(1))
            if 0 <= v <= 100:
                rounds.append(v)
    return {"month": month, "day": day, "label": f"{dm.group(1).title()} {day}",
            "final": int(fs.group(1)), "rounds": rounds}


def main():
    days = {}
    for m in history():
        if m.get("subtype"):          # skip joins / system messages
            continue
        p = parse(m.get("text", ""))
        if not p:
            continue
        uid = m.get("user", "")
        name = MEMBERS.get(uid, uid or "?")
        year = datetime.datetime.utcfromtimestamp(float(m["ts"])).year
        dk = f"{year}-{p['month']:02d}-{p['day']:02d}"
        day = days.setdefault(dk, {"label": p["label"], "results": []})
        if not any(r["name"].lower() == name.lower() for r in day["results"]):
            day["results"].append({"name": name, "finalScore": p["final"], "rounds": p["rounds"]})

    out = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "days": days}
    with open("data.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"Wrote data.json: {len(days)} days, "
          f"{sum(len(d['results']) for d in days.values())} entries")


if __name__ == "__main__":
    main()
