import asyncio
import os
import subprocess
import threading
from pathlib import Path

import rumps
from dotenv import load_dotenv
from pylutron_caseta.smartbridge import Smartbridge

load_dotenv(Path(__file__).parent / ".env")

BRIDGE_HOST = os.environ["LUTRON_BRIDGE_HOST"]
CERTS_DIR = Path(__file__).parent / "certs"

BRIGHTNESS_LEVELS = [100, 75, 50, 25, 0]


def get_current_ssid():
    try:
        result = subprocess.run(
            [
                "/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport",
                "-I",
            ],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if " SSID:" in line:
                return line.split("SSID:")[1].strip()
    except Exception:
        pass
    return None


def is_bridge_reachable():
    try:
        result = subprocess.run(
            ["nc", "-z", "-w", "2", BRIDGE_HOST, "8081"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


class LutronMenubarApp(rumps.App):
    def __init__(self):
        super().__init__("💡", quit_button=None)
        self.bridge = None
        self.devices = {}
        self.loop = None
        self._thread = None
        self._needs_menu_rebuild = False
        self._state = "loading"
        self._build_loading_menu()
        self._start_bridge()

    @rumps.timer(1)
    def _check_rebuild(self, _):
        if self._needs_menu_rebuild:
            self._needs_menu_rebuild = False
            if self._state == "offline":
                self._build_offline_menu()
            elif self._state == "connected":
                self._build_device_menu()

    def _request_rebuild(self, state):
        self._state = state
        self._needs_menu_rebuild = True

    def _build_loading_menu(self):
        self.menu.clear()
        self.menu = [rumps.MenuItem("Connecting..."), None, rumps.MenuItem("Quit", callback=self._quit)]

    def _build_offline_menu(self):
        self.menu.clear()
        self.menu = [
            rumps.MenuItem("⚠️ Not on home network"),
            None,
            rumps.MenuItem("Retry", callback=self._retry),
            rumps.MenuItem("Quit", callback=self._quit),
        ]

    def _build_device_menu(self):
        self.menu.clear()
        rooms = {}
        for device_id, device in self.devices.items():
            if device["type"] == "SmartBridge":
                continue
            name = device["name"]
            room = name.split("_")[0] if "_" in name else "Other"
            light_name = name.split("_")[1] if "_" in name else name
            rooms.setdefault(room, []).append((device_id, light_name, device))

        for room, lights in sorted(rooms.items()):
            room_menu = rumps.MenuItem(room)
            for device_id, light_name, device in lights:
                state = device.get("current_state", 0)
                is_on = state > 0
                icon = "● " if is_on else "○ "
                level_str = f" ({state}%)" if is_on else ""
                light_menu = rumps.MenuItem(f"{icon}{light_name}{level_str}")

                toggle_label = "Turn Off" if is_on else "Turn On"
                toggle_item = rumps.MenuItem(
                    toggle_label,
                    callback=lambda sender, did=device_id, on=is_on: self._toggle(did, on),
                )
                light_menu.add(toggle_item)
                light_menu.add(None)

                for level in BRIGHTNESS_LEVELS:
                    if level == 0:
                        continue
                    marker = " ✓" if state == level else ""
                    item = rumps.MenuItem(
                        f"{level}%{marker}",
                        callback=lambda sender, did=device_id, lv=level: self._set_level(did, lv),
                    )
                    light_menu.add(item)

                room_menu.add(light_menu)
            self.menu.add(room_menu)

        self.menu.add(None)
        self.menu.add(rumps.MenuItem("Refresh", callback=self._retry))
        self.menu.add(rumps.MenuItem("Quit", callback=self._quit))

    def _start_bridge(self):
        self._thread = threading.Thread(target=self._connect, daemon=True)
        self._thread.start()

    def _connect(self):
        print("[DEBUG] Checking bridge reachability...")
        if not is_bridge_reachable():
            print("[DEBUG] Bridge not reachable")
            self._request_rebuild("offline")
            return

        print("[DEBUG] Bridge reachable, connecting...")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def connect():
            self.bridge = Smartbridge.create_tls(
                BRIDGE_HOST,
                str(CERTS_DIR / "caseta.key"),
                str(CERTS_DIR / "caseta.crt"),
                str(CERTS_DIR / "caseta-bridge.crt"),
            )
            await self.bridge.connect()
            self.devices = self.bridge.get_devices()

        self.loop.run_until_complete(connect())
        print(f"[DEBUG] Connected, found {len(self.devices)} devices")
        self._request_rebuild("connected")

    def _toggle(self, device_id, currently_on):
        def run():
            async def do():
                if currently_on:
                    await self.bridge.turn_off(device_id)
                else:
                    await self.bridge.turn_on(device_id)
                self.devices = self.bridge.get_devices()
            self.loop.run_until_complete(do())
            self._request_rebuild("connected")
        threading.Thread(target=run, daemon=True).start()

    def _set_level(self, device_id, level):
        def run():
            async def do():
                await self.bridge.set_value(device_id, level)
                self.devices = self.bridge.get_devices()
            self.loop.run_until_complete(do())
            self._request_rebuild("connected")
        threading.Thread(target=run, daemon=True).start()

    def _retry(self, _):
        self._build_loading_menu()
        self._start_bridge()

    def _quit(self, _):
        if self.bridge and self.loop:
            self.loop.run_until_complete(self.bridge.close())
        rumps.quit_application()


if __name__ == "__main__":
    LutronMenubarApp().run()
