import time
from ._helpers import register_cmd


def register(client, state):
    async def handler(event):
        t0 = time.time()
        msg = await event.edit("🏓 Pinging...")
        dt = (time.time() - t0) * 1000
        await msg.edit(f"🏓 **Pong!** `{dt:.0f} ms`")
    register_cmd(client, state, "ping", handler)
