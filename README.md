# maptap leaderboard — daily-updating website

A public web page that shows daily and all-time rankings for the `#maptap`
Slack channel, refreshed automatically once a day. No server to run.

## How it works

```
#maptap (Slack)  ->  GitHub Action (daily)  ->  data.json  ->  GitHub Pages (your URL)
```

- `index.html` — the leaderboard page. Reads `data.json` and renders it.
- `data.json` — the parsed scores. Regenerated daily (a starter copy is included).
- `sync.py` — reads the Slack channel and rewrites `data.json`.
- `.github/workflows/sync.yml` — runs `sync.py` once a day and commits the result.

The page is fully static, so GitHub Pages can host it for free and give you a URL.

## What you need

1. A free GitHub account.
2. A Slack bot token that can read the channel. Creating a Slack app may need
   approval from a workspace admin in your Slack — that is the one real gate here.

## Setup

### 1. Create a Slack app and get a bot token
1. Go to https://api.slack.com/apps -> "Create New App" -> "From scratch".
2. Pick your workspace and name it (e.g. "maptap leaderboard").
3. Under "OAuth & Permissions" -> "Scopes" -> "Bot Token Scopes", add just one:
   - `channels:history`
4. Click "Install to Workspace" (an admin may need to approve this).
5. Copy the "Bot User OAuth Token" — it starts with `xoxb-`.
6. In Slack, open `#maptap` and type `/invite @your-app-name` so the bot can read it.

That single scope only lets the bot read message history of public channels it has
been invited to. Since you only invite it to `#maptap`, and `sync.py` only ever reads
the one channel ID, nothing else in the workspace is accessible.

### 2. Put these files in a GitHub repo
Create a new repository and upload everything in this folder, keeping the
`.github/workflows/` path intact.

### 3. Add the token as a secret
In the repo: Settings -> Secrets and variables -> Actions -> "New repository secret".
- Name: `SLACK_BOT_TOKEN`
- Value: the `xoxb-...` token from step 1.

The token lives only here, never in the page. The public site only ever shows the
parsed scores, not the token.

### 4. Turn on GitHub Pages
Settings -> Pages -> "Build and deployment" -> Source: "Deploy from a branch" ->
Branch: `main`, folder: `/ (root)` -> Save. After a minute you get a URL like
`https://YOURNAME.github.io/REPO/`. That's your link.

### 5. Run it once
Actions tab -> "Sync maptap leaderboard" -> "Run workflow". It pulls Slack, rewrites
`data.json`, and commits. After that it runs every day on its own.

## Adjusting things
- Logo: the Slant wordmark is embedded directly in `index.html` (a white version,
  sized for the dark header) so nothing loads over the network. A copy is also saved
  as `logo.png`. To change it, swap the image and rebuild, or replace the `brandlogo`
  data URI in `index.html`.
- Add a new player: open `sync.py` and add a line to the `MEMBERS` map
  (`"U012345": "Their Name",`). Get the ID in Slack: click the person's name ->
  "Copy member ID". Anyone not in the map shows up as their raw ID until you add them.
- Change the time of day: edit the `cron` line in `.github/workflows/sync.yml`
  (it's in UTC).
- Different channel: change `MAPTAP_CHANNEL_ID` in the workflow file. Find the ID in
  Slack via the channel's "Open channel details" -> bottom of the About tab.

## A note on access and privacy
The bot holds one read-only scope (`channels:history`) and is invited only to
`#maptap`, so it cannot reach other channels' content, and the script reads only the
one channel you configure. Names are resolved from the built-in `MEMBERS` list rather
than the Slack directory, so the workspace user list is never pulled either.

The published page itself is public — anyone with the link can see the leaderboard
(names and scores from #maptap only). If you later want it internal-only, host the
same files on a service with access control (e.g. Netlify or Vercel password
protection); the setup is otherwise identical.
