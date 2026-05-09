import aiohttp
import urllib.parse
from ._helpers import register_cmd


def register(client, state):
    async def handler(event):
        arg = event.pattern_match.group(1) or ""
        parts = arg.split(" ", 1)
        if len(parts) < 2:
            target, text = "en", arg
        else:
            target, text = parts[0], parts[1]
        if not text:
            return await event.edit("Usage: `.tr <lang> <text>` or `.tr <text>`")
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target}&dt=t&q={urllib.parse.quote(text)}"
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as r:
                    data = await r.json(content_type=None)
            translated = "".join(seg[0] for seg in data[0])
            await event.edit(f"🌍 **[{target}]** {translated}")
        except Exception as e:
            await event.edit(f"❌ {e}")
    register_cmd(client, state, "tr", handler)
