import os
import aiohttp

API_BASE = os.environ["API_BASE"].rstrip("/")
USER_ID = os.environ["USER_ID"]
API_TOKEN = os.environ["API_TOKEN"]

HEADERS = {"x-user-id": USER_ID, "x-api-token": API_TOKEN, "content-type": "application/json"}


class ApiClient:
    def __init__(self):
        self._session = None

    async def _s(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15))
        return self._session

    async def fetch_config(self):
        s = await self._s()
        async with s.get(f"{API_BASE}/api/public/userbot/config") as r:
            r.raise_for_status()
            return await r.json()

    async def heartbeat(self, status="running"):
        try:
            s = await self._s()
            async with s.post(f"{API_BASE}/api/public/userbot/heartbeat", json={"status": status}) as r:
                await r.read()
        except Exception:
            pass

    async def log(self, message, level="info"):
        try:
            s = await self._s()
            async with s.post(f"{API_BASE}/api/public/userbot/log", json={"level": level, "message": message[:1900]}) as r:
                await r.read()
        except Exception:
            pass

    async def report_plugin_error(self, plugin_name, error, disable=True):
        try:
            s = await self._s()
            async with s.post(
                f"{API_BASE}/api/public/userbot/plugin-error",
                json={"plugin_name": plugin_name, "error": str(error)[:1900], "disable": disable},
            ) as r:
                await r.read()
        except Exception:
            pass

    async def sync_local(self, plugins):
        try:
            s = await self._s()
            async with s.post(
                f"{API_BASE}/api/public/userbot/sync-local",
                json={"plugins": plugins},
            ) as r:
                await r.read()
        except Exception:
            pass

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


api = ApiClient()
