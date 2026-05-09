from ._helpers import register_cmd

_notes = {}


def register(client, state):
    async def save(event):
        arg = event.pattern_match.group(1) or ""
        parts = arg.split(" ", 1)
        if len(parts) < 2:
            return await event.edit("Usage: `.save <name> <content>`")
        _notes[parts[0]] = parts[1]
        await event.edit(f"📌 Saved note `{parts[0]}`")

    async def get(event):
        name = (event.pattern_match.group(1) or "").strip()
        if name in _notes:
            await event.edit(_notes[name])
        else:
            await event.edit(f"❓ No note `{name}`")

    async def listn(event):
        if not _notes:
            return await event.edit("No notes saved.")
        await event.edit("📒 Notes:\n" + "\n".join(f"• `{k}`" for k in _notes))

    register_cmd(client, state, "save", save)
    register_cmd(client, state, "get", get)
    register_cmd(client, state, "notes", listn)
