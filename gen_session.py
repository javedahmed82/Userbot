"""Run once locally to generate a Telethon StringSession.
Paste the printed string into the dashboard's Session String field.
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("API ID: ").strip())
api_hash = input("API Hash: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n=== Your session string (keep secret!) ===")
    print(client.session.save())
