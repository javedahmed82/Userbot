import asyncio
from ._helpers import register_cmd


def register(client, state):
    async def handler(event):
        text = (event.pattern_match.group(1) or "").strip()
        if not text:
            return await event.edit("Usage: `.bc <message>`")
        await event.edit("📢 Broadcasting to all groups...")
        sent = 0
        async for d in client.iter_dialogs():
            if d.is_group:
                try:
                    await client.send_message(d.id, text)
                    sent += 1
                    await asyncio.sleep(0.5)
                except Exception:
                    continue
        await event.respond(f"✅ Sent to {sent} groups")
    register_cmd(client, state, "bc", handler)
