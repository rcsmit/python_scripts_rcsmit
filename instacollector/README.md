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

## 4. Configure environment variables

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-your-bot-token"
export SPREADSHEET_ID="1VxN3uBwHLji9Eig8YA7DJs9cVBWN2QIV74no16lb8fY"
export WORKSHEET_NAME="Blad1"
export GOOGLE_SERVICE_ACCOUNT_FILE="/path/to/service_account.json"
export DEFAULT_COLLECTION="default"

# Optional: only allow specific Telegram user IDs to add links.
# Get your numeric ID by messaging @userinfobot on Telegram.
export ALLOWED_USER_IDS="111111111,222222222"
```

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
