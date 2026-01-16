import asyncio
import json
import logging
import math
import os
import sys
import datetime
import webbrowser
import collections
from typing import List, Dict, Any, Optional
import statistics

import aioping
from infi.systray import SysTrayIcon
from aiohttp import web

# Configure logging
# We defer file handler creation until we load config, but setup basic stream first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'
DASHBOARD_FILE = 'dashboard.html'

class PingHistory:
    def __init__(self, maxlen=3600):
        self.history = collections.deque(maxlen=maxlen)
        self.total_pings = 0
        self.failed_pings = 0

    def add(self, latency: Optional[float]):
        self.total_pings += 1
        if latency is None:
            self.failed_pings += 1
        self.history.append(latency)

    @property
    def packet_loss(self) -> float:
        if self.total_pings == 0:
            return 0.0
        return (self.failed_pings / self.total_pings) * 100.0

    @property
    def avg_latency(self) -> float:
        valid_pings = [x for x in self.history if x is not None]
        if not valid_pings:
            return 0.0
        return statistics.mean(valid_pings) * 1000  # convert to ms

    @property
    def last_latency(self) -> Optional[float]:
        if not self.history:
            return None
        val = self.history[-1]
        return val * 1000 if val is not None else None

class PingApp:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.targets: List[Dict[str, Any]] = []
        self.target_histories: Dict[str, PingHistory] = {}
        self.systray: Optional[SysTrayIcon] = None
        self.running = False
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.web_app = web.Application()
        self.web_runner = None

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "targets": [
                        {"name": "Google", "host": "8.8.8.8"},
                        {"name": "Cloudflare", "host": "1.1.1.1"},
                        {"name": "Localhost", "host": "127.0.0.1"}
                    ],
                    "ping_interval": 1,
                    "timeout": 1,
                    "dashboard_port": 8080,
                    "log_file": "ping_monitor.log"
                }

            # Setup file logging if specified
            log_file = self.config.get('log_file')
            if log_file:
                # Remove existing file handlers to avoid duplication on reload
                logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.FileHandler)]
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                logger.addHandler(file_handler)

            self.targets = self.config.get('targets', [])
            for target in self.targets:
                if target['name'] not in self.target_histories:
                    self.target_histories[target['name']] = PingHistory()

        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def get_menu_options(self):
        return (
            ("Open Dashboard", "green_icon.ico", self.open_dashboard),
            ("Reload Config", None, self.reload_config_callback)
        )

    def open_dashboard(self, systray):
        port = self.config.get('dashboard_port', 8080)
        url = f"http://localhost:{port}"
        webbrowser.open(url)

    def reload_config_callback(self, systray):
        logger.info("Reloading configuration...")
        self.load_config()

    def start_systray(self):
        # infi.systray runs in a separate thread if we call start()
        # but we need to ensure we don't block the asyncio loop.
        # However, SysTrayIcon doesn't expose a non-blocking run easily
        # except via start() which spawns a thread.
        menu_options = self.get_menu_options()
        self.systray = SysTrayIcon(
            "grey_icon.ico",
            "Ping Monitor",
            menu_options,
            on_quit=self.on_quit
        )
        self.systray.start()

    def on_quit(self, systray):
        self.running = False
        logger.info("Quitting application...")
        # Stop asyncio loop gracefully from the other thread is tricky
        # We set a flag and let the loop exit.

    async def ping_target(self, target):
        host = target['host']
        timeout = self.config.get('timeout', 1)
        name = target['name']

        try:
            delay = await aioping.ping(host, timeout=timeout)
            self.target_histories[name].add(delay)
            return True # Success
        except TimeoutError:
            self.target_histories[name].add(None)
            return False # Fail
        except Exception as e:
            logger.error(f"Error pinging {name}: {e}")
            self.target_histories[name].add(None)
            return False

    async def ping_loop(self):
        self.running = True
        logger.info("Starting concurrent ping loop...")

        while self.running:
            interval = self.config.get('ping_interval', 1)
            start_time = self.loop.time()

            # Ping all targets concurrently
            tasks = [self.ping_target(t) for t in self.targets]
            results = await asyncio.gather(*tasks)

            # Update Tray Icon based on results
            # Logic: If any critical target is down, show Red.
            # If all good, Green.
            # (Simple logic: if > 50% fail, Red, else if any fail, Orange, else Green)

            failures = results.count(False)
            total = len(results)

            if total > 0:
                if failures == 0:
                    icon = "green_icon.ico"
                    msg = "Online: All targets reachable"
                elif failures == total:
                    icon = "red_icon.ico"
                    msg = "Offline: All targets unreachable"
                else:
                    icon = "grey_icon.ico" # Or maybe a yellow icon if we had one
                    msg = f"Degraded: {failures}/{total} targets unreachable"

                if self.systray:
                    # systray.update might be blocking, but usually it's fast PostMessage
                    try:
                        self.systray.update(icon=icon, hover_text=msg)
                    except Exception as e:
                        logger.error(f"Failed to update tray: {e}")

            # Wait for remainder of interval
            elapsed = self.loop.time() - start_time
            sleep_time = max(0, interval - elapsed)
            await asyncio.sleep(sleep_time)

    # Web Server Handlers
    async def handle_dashboard(self, request):
        return web.FileResponse(DASHBOARD_FILE)

    async def handle_api_data(self, request):
        data = {
            "targets": []
        }
        for target in self.targets:
            name = target['name']
            history = self.target_histories.get(name)
            if history:
                data["targets"].append({
                    "name": name,
                    "host": target['host'],
                    "last_latency": history.last_latency,
                    "avg_latency": history.avg_latency,
                    "packet_loss": history.packet_loss
                })
        return web.json_response(data)

    async def start_web_server(self):
        port = self.config.get('dashboard_port', 8080)
        self.web_app.router.add_get('/', self.handle_dashboard)
        self.web_app.router.add_get('/api/data', self.handle_api_data)

        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        logger.info(f"Dashboard running at http://localhost:{port}")
        return runner

    def run(self):
        self.load_config()
        self.start_systray()

        try:
            # Start Web Server
            self.loop.run_until_complete(self.start_web_server())

            # Start Ping Loop
            self.loop.run_until_complete(self.ping_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.close()

if __name__ == "__main__":
    app = PingApp()
    app.run()
