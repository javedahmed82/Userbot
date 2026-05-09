# TeleBot — Telethon Userbot

Self-hosted Telethon userbot driven by your TeleBot Console dashboard.

## Setup

1. **Get credentials** from your dashboard (Config tab):
   - `USER_ID`, `API_TOKEN` (click Generate), `API_BASE` (your project URL)

2. **Get Telegram credentials** from https://my.telegram.org/apps: API ID + Hash

3. **Generate session string** locally once:
   ```bash
   pip install telethon
   python gen_session.py
   ```
   Paste the printed string into the dashboard's Session String field, then Save.

## Run

```bash
cp .env.example .env   # fill in USER_ID, API_TOKEN, API_BASE
pip install -r requirements.txt
python main.py
```

## Docker

```bash
docker build -t userbot .
docker run -d --restart=always --env-file .env userbot
```

## Free hosting

- **Koyeb** — free forever (1 service)
- **Fly.io** — generous free tier
- **Railway** — $5/mo free credit
- **Oracle Cloud** — free ARM VPS forever
- Your own VPS / Raspberry Pi

## Plugins (10 built-in)

| Command | Purpose |
|---------|---------|
| `.alive` | Bot status |
| `.ping` | Latency |
| `.afk <reason>` | Set AFK + auto-reply |
| `.gban` / `.ungban` (reply) | Global ban |
| `.save <name> <text>` `.get <name>` `.notes` | Notes |
| `.filter <trig> <reply>` `.stop <trig>` `.filters` | Auto-reply triggers |
| `.weather <city>` | Weather |
| `.tr <lang> <text>` | Translate |
| `.sticker` (reply) | Sticker info |
| `.bc <message>` | Broadcast to all groups |

Toggle plugins from dashboard — bot hot-reloads in ~10s.

## Add a custom plugin

Create `plugins/myplugin.py`:

```python
from ._helpers import register_cmd

def register(client, state):
    async def handler(event):
        await event.edit("Hello from my plugin!")
    register_cmd(client, state, "hello", handler)
```

Then insert a row in your `userbot_plugins` table with `plugin_name='myplugin'` and toggle on.
