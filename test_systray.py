import asyncio
import json
import logging
import math
import os
import sys
import datetime
from typing import List, Dict, Any, Optional

import aioping
from infi.systray import SysTrayIcon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'

class PingApp:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.targets: List[Dict[str, str]] = []
        self.current_target: Optional[Dict[str, str]] = None
        self.systray: Optional[SysTrayIcon] = None
        self.running = False
        self.loop = asyncio.get_event_loop()

        # Statistics
        self.total_pings = 0
        self.failed_pings = 0
        self.consecutive_disconnects = 0
        self.start_time = datetime.datetime.now()

        # State for pinging
        self.ping_task = None

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.warning(f"Config file {CONFIG_FILE} not found. Using defaults.")
                self.config = {
                    "targets": [{"name": "Google", "host": "8.8.8.8"}],
                    "default_target": "Google",
                    "ping_interval": 1,
                    "timeout": 1
                }

            self.targets = self.config.get('targets', [])
            
            # Set log file if specified
            log_file = self.config.get('log_file')
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                logger.addHandler(file_handler)

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)

    def get_menu_options(self):
        menu_options = []
        for target in self.targets:
            # We need to capture the target in the closure.
            # In Python loops, the variable is shared, so we use a default argument or functools.partial
            def make_callback(t):
                return lambda systray: self.set_target(t)

            menu_options.append((target['name'], None, make_callback(target)))

        menu_options.append(("Reload Config", None, self.reload_config_callback))
        return menu_options

    def set_target(self, target):
        logger.info(f"Switching target to {target['name']} ({target['host']})")
        self.current_target = target
        # Reset specific stats if needed, or keep cumulative
        self.consecutive_disconnects = 0

    def reload_config_callback(self, systray):
        logger.info("Reloading configuration...")
        self.load_config()
        # Note: We can't easily update the menu of the running systray with infi.systray
        # without restarting it. Restarting it from a callback (which is in the systray thread)
        # requires care. For now, we'll just reload targets. If the menu needs to change,
        # we might need to restart the app or accept that the menu is stale until restart.
        # But if we just updated the ping parameters, that takes effect immediately.
        # If the user wants to see new targets in the menu, they currently have to restart the app.
        logger.info("Configuration reloaded. Note: Restart application to update menu items if targets changed.")

    def start_systray(self):
        menu_options = self.get_menu_options()
        self.systray = SysTrayIcon(
            "grey_icon.ico",
            "Ping Monitor",
            tuple(menu_options),
            on_quit=self.on_quit
        )
        self.systray.start()

    def on_quit(self, systray):
        self.running = False
        # Stop the asyncio loop
        logger.info("Quitting application...")
        # We can't stop the loop directly from this thread easily if it's run_forever.
        # But we can set a flag that the coroutine checks.

    async def ping_loop(self):
        self.running = True

        # Select default target
        default_name = self.config.get('default_target')
        self.current_target = next((t for t in self.targets if t['name'] == default_name), self.targets[0])

        logger.info(f"Starting ping loop for {self.current_target['name']}")

        while self.running:
            if not self.current_target:
                await asyncio.sleep(1)
                continue

            host = self.current_target['host']
            timeout = self.config.get('timeout', 1)
            interval = self.config.get('ping_interval', 1)

            try:
                self.total_pings += 1
                delay = await aioping.ping(host, timeout=timeout)
                # Success
                ms = math.floor(delay * 1000)
                self.consecutive_disconnects = 0

                uptime = 100.0
                if self.total_pings > 0:
                    uptime = ((self.total_pings - self.failed_pings) / self.total_pings) * 100.0

                status_msg = f"Ping to {self.current_target['name']} ({host}): {ms}ms\nUptime: {uptime:.1f}%"

                # Update icon to green
                if self.systray:
                    self.systray.update(icon="green_icon.ico", hover_text=status_msg)

                logger.debug(status_msg.replace('\n', ' '))

            except TimeoutError:
                self.failed_pings += 1
                self.consecutive_disconnects += 1

                uptime = 100.0
                if self.total_pings > 0:
                    uptime = ((self.total_pings - self.failed_pings) / self.total_pings) * 100.0

                status_msg = f"TIMEOUT: {self.current_target['name']} ({host})\nDisconnected for {self.consecutive_disconnects * interval}s\nUptime: {uptime:.1f}%"

                # Update icon to red
                if self.systray:
                    self.systray.update(icon="red_icon.ico", hover_text=status_msg)

                logger.warning(status_msg.replace('\n', ' '))

            except Exception as e:
                logger.error(f"Ping error: {e}")
                if self.systray:
                    self.systray.update(icon="grey_icon.ico", hover_text=f"Error: {str(e)}")

            # Wait for next interval
            await asyncio.sleep(interval)

        # Cleanup
        if self.systray:
            self.systray.shutdown()

    def run(self):
        self.load_config()
        self.start_systray()
        try:
            self.loop.run_until_complete(self.ping_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.close()

if __name__ == "__main__":
    app = PingApp()
    app.run()
