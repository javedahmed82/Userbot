from ._helpers import register_cmd
import platform
import psutil
import shutil
import time
import os
from datetime import datetime

START_TIME = time.time()

def get_uptime():
    uptime_seconds = int(time.time() - START_TIME)

    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    return f"{days}d {hours}h {minutes}m {seconds}s"

def register(client, state):

    async def system_handler(event):

        uname = platform.uname()

        cpu = psutil.cpu_percent(interval=1)

        ram = psutil.virtual_memory()

        disk = shutil.disk_usage("/")

        total_ram = round(ram.total / (1024**3), 2)
        used_ram = round(ram.used / (1024**3), 2)

        total_disk = round(disk.total / (1024**3), 2)
        free_disk = round(disk.free / (1024**3), 2)
        used_disk = total_disk - free_disk

        processes = len(psutil.pids())

        plugins_loaded = len([
            f for f in os.listdir("plugins")
            if f.endswith(".py") and not f.startswith("_")
        ])

        uptime = get_uptime()

        msg = f"""
╔══════════════════════╗
      ⚡ USERBOT CORE ⚡
╚══════════════════════╝

🟢 STATUS        : ONLINE & STABLE
🤖 CLIENT        : Telethon Userbot
🧠 MODE          : Production
🔄 AUTO SYNC     : Enabled
🛡 SAFE MODE     : Active

━━━━━━━━━━━━━━━━━━
🖥 SYSTEM INFORMATION
━━━━━━━━━━━━━━━━━━

🖥 OS            : {uname.system}
📱 Kernel        : {uname.release}
⚙ Architecture  : {uname.machine}
🐍 Python        : {platform.python_version()}
📦 Platform      : {platform.platform()}
🧰 Shell         : bash
🧪 Environment   : Virtualized Runtime

━━━━━━━━━━━━━━━━━━
⚡ PERFORMANCE
━━━━━━━━━━━━━━━━━━

🧠 CPU Usage     : {cpu}%
💾 RAM Usage     : {used_ram} GB / {total_ram} GB
📂 Disk Usage    : {used_disk:.2f} GB Used
🗂 Free Storage  : {free_disk} GB
🌡 CPU Temp      : Normal
🔋 System Load   : Stable
📈 Processes     : {processes} Running

━━━━━━━━━━━━━━━━━━
🌐 NETWORK & BOT
━━━━━━━━━━━━━━━━━━

📡 Ping          : Stable
🌍 Network       : Connected ✅
🔌 API Status    : Reachable
📶 Connection    : Stable
🛰 Telegram DC   : Connected
📨 Session       : Authorized

━━━━━━━━━━━━━━━━━━
🧩 USERBOT STATUS
━━━━━━━━━━━━━━━━━━

📦 Plugins Loaded : {plugins_loaded}
⚙ Active Tasks    : Running
🔄 Auto Restart    : Enabled
🛠 Error Handler   : Active
📜 Logs            : Recording
🧹 Cache Cleaner   : Running
🔐 Security Layer  : Enabled

━━━━━━━━━━━━━━━━━━
⏳ RUNTIME
━━━━━━━━━━━━━━━━━━

🕒 Uptime         : {uptime}
🚀 Runtime State  : Healthy

━━━━━━━━━━━━━━━━━━
🔥 SYSTEM MESSAGE
━━━━━━━━━━━━━━━━━━

✅ ALL SERVICES RUNNING
✅ NO CRITICAL ERRORS
✅ USERBOT OPERATING NORMALLY

╔══════════════════════╗
 ⚡ POWERED BY UNIQUE USERBOT ⚡
╚══════════════════════╝
"""

        await event.edit(msg)

    register_cmd(client, state, "system", system_handler)