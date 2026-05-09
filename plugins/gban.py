from ._helpers import register_cmd

_banned = set()


def register(client, state):
    async def gban(event):
        if not event.is_reply:
            return await event.edit("Reply to a user to gban.")
        msg = await event.get_reply_message()
        _banned.add(msg.sender_id)
        await event.edit(f"🔨 Globally banned `{msg.sender_id}`")

    async def ungban(event):
        if not event.is_reply:
            return await event.edit("Reply to a user to ungban.")
        msg = await event.get_reply_message()
        _banned.discard(msg.sender_id)
        await event.edit(f"✅ Unbanned `{msg.sender_id}`")

    register_cmd(client, state, "gban", gban)
    register_cmd(client, state, "ungban", ungban)
