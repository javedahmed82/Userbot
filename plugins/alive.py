import platform
from ._helpers import register_cmd


def register(client, state):
    async def handler(event):
        text = (
            "**🤖 TeleBot is alive!**\n"
            f"• Prefix: `{state['prefix']}`\n"
            f"• Plugins: `{len(state['enabled_plugins'])}`\n"
            f"• Python: `{platform.python_version()}`\n"
            f"• Powered by Telethon"
        )
        await event.edit(text)
    register_cmd(client, state, "alive", handler)
