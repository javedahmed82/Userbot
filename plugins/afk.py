import time
from telethon import events
from ._helpers import register_cmd

_state = {"afk": False, "reason": "", "since": 0, "replied": set()}


def register(client, state):
    async def set_afk(event):
        m = event.pattern_match.group(1) or "no reason"
        _state.update(afk=True, reason=m, since=time.time(), replied=set())
        await event.edit(f"💤 **AFK:** {m}")

    async def auto_reply(event):
        if not _state["afk"]:
            return
        if not event.is_private and not event.mentioned:
            return
        sid = event.sender_id
        if sid in _state["replied"]:
            return
        _state["replied"].add(sid)
        elapsed = int(time.time() - _state["since"])
        await event.reply(f"💤 I'm AFK ({_state['reason']}) — away for {elapsed}s")

    async def back(event):
        if _state["afk"]:
            _state["afk"] = False
            await event.respond("✅ Back from AFK")

    register_cmd(client, state, "afk", set_afk)
    b1 = events.NewMessage(incoming=True)
    client.add_event_handler(auto_reply, b1)
    state["handlers"].append((b1, auto_reply))
    b2 = events.NewMessage(outgoing=True)
    client.add_event_handler(back, b2)
    state["handlers"].append((b2, back))
