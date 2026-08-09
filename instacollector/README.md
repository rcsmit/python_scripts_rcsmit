# Instagram Collector Telegram Bot

Send Instagram links to this bot; it appends them as rows to your Google
Sheet (`InstaCollections`) so a JS page can read and display them.

## 1. Create the Telegram bot

1. Open Telegram, message **@BotFather**.
2. `/newbot`, follow the prompts, get your **bot token**.

## 2. Create a Google service account (so the bot can write to the sheet)

1. Go to https://console.cloud.google.com/ → create/select a project.
2. Enable the **Google Sheets API**.
3. Go to **IAM & Admin → Service Accounts → Create Service Account**.
4. Create a key for it (JSON) and download it as `service_account.json`.
5. Open your sheet, click **Share**, and share it with the service
   account's email (looks like `xxx@xxx.iam.gserviceaccount.com`) as
   **Editor**.

## 3. Install dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

## 4. Configure the bot

Run the setup script — it asks for each value and writes a `.env` file
next to the bot (the bot loads it automatically on startup):

```bash
python setup_env.py
```

It'll ask for:
- Telegram bot token (from @BotFather)
- Google Sheet ID (defaults to your InstaCollections sheet)
- Worksheet/tab name (defaults to `Blad1`)
- Path to your `service_account.json` key file
- Default collection name
- Allowed Telegram user IDs (optional — leave blank while testing; get
  your numeric ID by messaging @userinfobot on Telegram)

Re-run `python setup_env.py` any time to update a value; it shows your
current settings as defaults. The `.env` file is written with restricted
permissions (readable only by you) since it holds your bot token — never
commit it to a public repo.

## 5. Run it

```bash
python insta_collector_bot.py
```

Keep it running (screen/tmux, systemd, or a small always-on VPS/Fly.io/
Render worker — must be a long-running process, not serverless, since it
polls Telegram).

## How to use it in Telegram

- `/collection acro-italy` — new links you send now go into the
  "acro-italy" collection (so you can run several collections through one
  bot/sheet).
- `/whoami` — shows the active collection.
- `/list` — shows the last 5 links in the active collection.
- Just send or forward a message containing an Instagram post/reel/IGTV
  link. Any `#hashtags` in the same message become the `tags` column;
  the rest of the text becomes the `caption`.
- Multiple Instagram links in one message are all added.

Each row gets: `id, collection, url, date_added, added_by, caption, tags,
type, status` — matching your sheet's header exactly. `status` is always
set to `active` on add; you can flip it to `hidden` by hand in the sheet
to soft-delete something without your JS page showing it (have the page
filter on `status == "active"`).

## Notes

- Only Telegram users in `ALLOWED_USER_IDS` can add links, if you set
  that variable. Leave it unset while testing, then lock it down once
  you know who should be allowed to contribute.
- The bot doesn't download or re-host video — it only stores the link,
  which keeps you clear of Instagram's redistribution restrictions and
  is what your oEmbed-based JS page needs anyway.
- `chat_state.json` (which collection is "active" per chat) is created
  next to the script; back it up or set `STATE_FILE` to a persistent
  path if you're deploying somewhere with an ephemeral filesystem.

## Deploying to Railway (keep it running 24/7)

Railway runs this as a long-lived background worker, so it stays connected
to Telegram continuously rather than relying on your own laptop being on.

1. Push this folder to a GitHub repo. `.gitignore` already keeps `.env`
   and `service_account.json` out of it — don't remove those entries.
2. On [railway.com](https://railway.com), create a new project →
   **Deploy from GitHub repo** → select your repo. `railway.json` tells
   Railway to run `python insta_collector_bot.py` and always restart it
   if it stops (`restartPolicyType: ALWAYS`) — that matters here since a
   polling bot should never sit "stopped".
3. Open the deployed service → **Variables** tab → add:
   - `TELEGRAM_BOT_TOKEN`
   - `SPREADSHEET_ID`
   - `WORKSHEET_NAME`
   - `DEFAULT_COLLECTION`
   - `ALLOWED_USER_IDS` (optional)
   - `GOOGLE_SERVICE_ACCOUNT_JSON` — paste the **entire contents** of your
     `service_account.json` key file as one value (Railway has no file-secret
     mount, so the bot reads credentials straight from this variable when
     it's set — see `GOOGLE_SERVICE_ACCOUNT_JSON` in the script).
   - You do **not** need `GOOGLE_SERVICE_ACCOUNT_FILE` on Railway.
4. Railway deploys automatically on push. No domain/networking setup is
   needed — this service makes outbound calls to Telegram, it doesn't
   need to receive inbound HTTP traffic.
5. Check logs in the Railway dashboard to confirm "Bot starting
   (polling)..." appears and there are no auth errors.

Redeploy any time by pushing to the connected branch — Railway rebuilds
and restarts the worker automatically.

