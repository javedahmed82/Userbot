from telethon import events
from ._helpers import register_cmd

_filters = {}


def register(client, state):
    async def add(event):
        arg = event.pattern_match.group(1) or ""
        parts = arg.split(" ", 1)
        if len(parts) < 2:
            return await event.edit("Usage: `.filter <trigger> <reply>`")
        _filters[parts[0].lower()] = parts[1]
        await event.edit(f"✅ Filter for `{parts[0]}` added")

    async def rm(event):
        k = (event.pattern_match.group(1) or "").lower()
        _filters.pop(k, None)
        await event.edit(f"🗑 Removed `{k}`")

    async def listf(event):
        if not _filters:
            return await event.edit("No filters.")
        await event.edit("🔎 Filters:\n" + "\n".join(f"• `{k}`" for k in _filters))

    async def trigger(event):
        text = (event.raw_text or "").lower()
        for k, v in _filters.items():
            if k in text:
                await event.reply(v)
                break

    register_cmd(client, state, "filter", add)
    register_cmd(client, state, "stop", rm)
    register_cmd(client, state, "filters", listf)
    b = events.NewMessage(incoming=True)
    client.add_event_handler(trigger, b)
    state["handlers"].append((b, trigger))
