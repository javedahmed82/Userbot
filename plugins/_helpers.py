"""Shared helpers for plugins."""
import re
from telethon import events


def cmd(state, name):
    prefix = re.escape(state.get("prefix", "."))
    pattern = rf"^{prefix}{name}(?:\s+(.+))?$"
    return events.NewMessage(outgoing=True, pattern=pattern)


def register_cmd(client, state, name, handler):
    builder = cmd(state, name)
    client.add_event_handler(handler, builder)
    state["handlers"].append((builder, handler))
