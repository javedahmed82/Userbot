"""TeleBot - Telethon userbot driven by remote dashboard config + plugin store."""
import asyncio
import importlib
import importlib.util
import logging
import os
import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("userbot")

from api_client import api  # noqa: E402

PLUGINS_DIR = Path(__file__).parent / "plugins"
REMOTE_DIR = Path(__file__).parent / "plugins_remote"
REMOTE_DIR.mkdir(exist_ok=True)
(REMOTE_DIR / "__init__.py").touch(exist_ok=True)

STATE = {
    "prefix": ".",
    "client": None,
    "api": api,
    "handlers": [],            # list of (builder, callback)
    "loaded_versions": {},     # plugin_name -> version
    "loaded_modules": {},      # plugin_name -> module
    "last_reload_at": None,    # mirror of config.reload_requested_at
    "last_restart_at": None,   # mirror of config.restart_requested_at
    "local_fs_snapshot": {},   # plugin_name -> sha256(code)
}

import hashlib

IGNORED_PLUGIN_FILES = {"_helpers.py", "__init__.py"}


def _scan_local_plugins() -> dict[str, str]:
    """Return {plugin_name: code} for valid .py files under plugins/."""
    out: dict[str, str] = {}
    if not PLUGINS_DIR.exists():
        return out
    for f in sorted(PLUGINS_DIR.glob("*.py")):
        if f.name in IGNORED_PLUGIN_FILES or f.name.startswith("_"):
            continue
        try:
            out[f.stem] = f.read_text(encoding="utf-8")
        except Exception:
            continue
    return out


async def push_local_plugins():
    """Detect added/changed/removed local plugin files and push to dashboard."""
    current = _scan_local_plugins()
    snap = {n: hashlib.sha256(c.encode()).hexdigest() for n, c in current.items()}
    if snap == STATE["local_fs_snapshot"]:
        return
    STATE["local_fs_snapshot"] = snap
    payload = [{"plugin_name": n, "code": c, "category": "filesystem"} for n, c in current.items()]
    await api.sync_local(payload)
    await api.log(f"Synced {len(payload)} local plugin file(s) with dashboard")


def _unregister_all():
    client = STATE["client"]
    for builder, cb in STATE["handlers"]:
        try:
            client.remove_event_handler(cb, builder)
        except Exception:
            pass
    STATE["handlers"].clear()


def _builtin_code(name: str) -> str | None:
    f = PLUGINS_DIR / f"{name}.py"
    if f.exists():
        try:
            return f.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def _load_one(name: str, code: str) -> tuple[bool, str | None]:
    """Write code to plugins_remote/<name>.py and import. Returns (ok, error)."""
    try:
        path = REMOTE_DIR / f"{name}.py"
        path.write_text(code, encoding="utf-8")
        mod_name = f"plugins_remote.{name}"
        # remove any prior import
        sys.modules.pop(mod_name, None)
        spec = importlib.util.spec_from_file_location(mod_name, path)
        if spec is None or spec.loader is None:
            return False, "spec load failed"
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        # make `from ._helpers import ...` work by aliasing helpers
        spec.loader.exec_module(mod)  # type: ignore
        if hasattr(mod, "register"):
            mod.register(STATE["client"], STATE)
        STATE["loaded_modules"][name] = mod
        return True, None
    except Exception:
        return False, traceback.format_exc(limit=5)


async def sync_plugins(plugins: list[dict], bot_enabled: bool):
    """Reconcile local plugins with dashboard state."""
    if not bot_enabled:
        if STATE["handlers"]:
            _unregister_all()
            STATE["loaded_versions"].clear()
            await api.log("Bot paused via dashboard", "warn")
        return

    enabled = {p["plugin_name"]: p for p in plugins if p.get("enabled")}
    current = STATE["loaded_versions"]

    # changed or new?
    needs_reload = False
    for name, p in enabled.items():
        v = p.get("version") or 1
        if current.get(name) != v:
            needs_reload = True
            break
    # removed?
    if set(current.keys()) - set(enabled.keys()):
        needs_reload = True

    if not needs_reload:
        return

    _unregister_all()
    STATE["loaded_versions"].clear()

    # Pre-stage helpers from local plugins/ folder so `from ._helpers import ...` works for builtin code
    helpers_src = PLUGINS_DIR / "_helpers.py"
    if helpers_src.exists():
        (REMOTE_DIR / "_helpers.py").write_text(helpers_src.read_text(encoding="utf-8"), encoding="utf-8")

    loaded = []
    for name, p in enabled.items():
        code = p.get("code") or _builtin_code(name)
        if not code:
            await api.log(f"Plugin {name} has no code (builtin missing too)", "warn")
            continue
        ok, err = _load_one(name, code)
        if ok:
            STATE["loaded_versions"][name] = p.get("version") or 1
            loaded.append(name)
            log.info("Loaded plugin: %s v%s", name, p.get("version"))
        else:
            log.error("Plugin %s failed:\n%s", name, err)
            await api.report_plugin_error(name, err or "unknown error", disable=True)

    if loaded:
        await api.log(f"Reloaded plugins: {sorted(loaded)}")


async def sync_loop():
    while True:
        try:
            # 1) Push any local plugin file changes up to dashboard first
            await push_local_plugins()
            # 2) Pull current state
            data = await api.fetch_config()
            cfg = data.get("config") or {}
            plugins = data.get("plugins") or []
            STATE["prefix"] = cfg.get("prefix") or "."

            # 3) Honor restart request from dashboard
            restart_at = cfg.get("restart_requested_at")
            if restart_at and restart_at != STATE["last_restart_at"]:
                if STATE["last_restart_at"] is not None:
                    await api.log("Restart requested from dashboard — exiting", "warn")
                    await asyncio.sleep(0.5)
                    os._exit(0)  # supervisor (Koyeb/Docker) will respawn
                STATE["last_restart_at"] = restart_at

            # 4) Honor force-reload request (clear loaded_versions to force re-import)
            reload_at = cfg.get("reload_requested_at")
            if reload_at and reload_at != STATE["last_reload_at"]:
                if STATE["last_reload_at"] is not None:
                    STATE["loaded_versions"].clear()
                    await api.log("Force reload requested from dashboard", "warn")
                STATE["last_reload_at"] = reload_at

            await sync_plugins(plugins, bool(cfg.get("enabled")))
            await api.heartbeat("running" if cfg.get("enabled") else "stopped")
        except Exception as e:
            log.exception("sync error")
            await api.log(f"sync error: {e}", "error")
        await asyncio.sleep(10)


async def main():
    api_id_env = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    session = os.environ.get("TG_SESSION")
    api_id = int(api_id_env) if api_id_env else None

    if not (api_id and api_hash and session):
        data = await api.fetch_config()
        cfg = data.get("config") or {}
        try:
            api_id = int(cfg.get("api_id") or 0)
        except (TypeError, ValueError):
            api_id = 0
        api_hash = cfg.get("api_hash")
        session = cfg.get("session_string")
        if not (api_id and api_hash and session):
            await api.log("Missing api_id / api_hash / session_string in dashboard", "error")
            log.error("Configure your credentials in the dashboard first.")
            return

    client = TelegramClient(StringSession(session), api_id, api_hash)
    await client.start()
    STATE["client"] = client
    me = await client.get_me()
    await api.log(f"Connected as {me.first_name} (@{me.username or me.id})")
    log.info("Logged in as %s", me.username or me.id)

    asyncio.create_task(sync_loop())
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
