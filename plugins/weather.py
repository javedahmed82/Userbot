import aiohttp
from ._helpers import register_cmd


def register(client, state):
    async def handler(event):
        city = (event.pattern_match.group(1) or "").strip()
        if not city:
            return await event.edit("Usage: `.weather <city>`")
        await event.edit(f"⏳ Fetching weather for {city}...")
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"https://wttr.in/{city}?format=3") as r:
                    text = await r.text()
            await event.edit(f"🌤 {text.strip()}")
        except Exception as e:
            await event.edit(f"❌ {e}")
    register_cmd(client, state, "weather", handler)
