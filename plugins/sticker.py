from ._helpers import register_cmd


def register(client, state):
    async def handler(event):
        if not event.is_reply:
            return await event.edit("Reply to a sticker to get info.")
        msg = await event.get_reply_message()
        if not msg.sticker:
            return await event.edit("Not a sticker.")
        attrs = msg.sticker.attributes
        emoji = next((a.alt for a in attrs if hasattr(a, "alt")), "?")
        await event.edit(
            f"🎨 **Sticker info**\n• Emoji: {emoji}\n• File ID: `{msg.sticker.id}`\n• Size: `{msg.sticker.size}` bytes"
        )
    register_cmd(client, state, "sticker", handler)
