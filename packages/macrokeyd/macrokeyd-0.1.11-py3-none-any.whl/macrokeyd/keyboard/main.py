import asyncio
import subprocess
from evdev import InputDevice, categorize, ecodes, list_devices
from select import select
from ..common.config import ConfigLoader
import os
from ..common.env_utils import ensure_display_env
import click
from .. import __version__
from ..common.logger import get_logger
import threading
import pyudev
from time import sleep
from .actions import Action
logger = get_logger(__name__)

class MacroDaemon:
    def __init__(self, target_device_name, macros):
        if not ensure_display_env():
            raise EnvironmentError("Could not set DISPLAY environment variable.")

        import pyautogui
        import mouseinfo

        self.pyautogui = pyautogui
        self.mouseinfo = mouseinfo

        self.running = True
        self.paused = False
        self.target_device_name = target_device_name
        self.macros = macros

        self.keyboards = []
        self.udev_thread = threading.Thread(target=self.monitor_udev_events, daemon=True)
        self.udev_thread.start()
        self.loop = asyncio.get_event_loop()
        self.keyboard_lock = asyncio.Lock()

    def detect_keyboards(self, target_device_name):
        keyboards = []
        for path in list_devices():
            device = InputDevice(path)
            capabilities = device.capabilities()
            if ecodes.EV_KEY not in capabilities or ecodes.EV_REL in capabilities or device.name != target_device_name:
                continue
            try:
                device.grab()
                logger.info(f"[+] Exclusive grab: {device.name} ({device.path})")
                keyboards.append(device)
            except OSError as e:
                logger.warning(f"[!] Could not grab {device.name}: {e}")
        return keyboards

    async def update_keyboards(self, retries=5, delay=1):
        async with self.keyboard_lock:
            for kb in self.keyboards:
                try:
                    kb.ungrab()
                    logger.info(f"[−] Released keyboard: {kb.name} ({kb.path})")
                except Exception as e:
                    logger.warning(f"[!] Error releasing keyboard {kb.name}: {e}")

            for attempt in range(retries):
                self.keyboards = self.detect_keyboards(self.target_device_name)
                if self.keyboards:
                    logger.info(f"[+] Keyboard(s) successfully detected after {attempt + 1} attempt(s).")
                    break
                logger.debug(f"Keyboard not found, retrying ({attempt + 1}/{retries}) after {delay}s...")
                sleep(delay)

            if not self.keyboards:
                logger.warning(f"[!] Failed to detect keyboards after {retries} attempts.")

    def monitor_udev_events(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='input')
        logger.info("[udev] Monitoring udev events for keyboards.")

        for action, device in monitor:
            device_name = device.get('NAME', '').strip('"')
            logger.debug(f"[udev] Read device name: {device_name}")
            if device.get('ID_INPUT_KEYBOARD') != '1' or  device_name != self.target_device_name or not device_name:
                logger.debug(f"[udev] Ignoring device with properties {device}")
                continue
            logger.debug(f"[udev] Action: {action} on Device: {device_name}")
            if action == 'add':
                logger.info(f"[udev] Keyboard '{device_name}' connected.")
                asyncio.run_coroutine_threadsafe(self.update_keyboards(), self.loop)
            elif action == 'remove':
                logger.warning(f"[udev] Keyboard '{device_name}' disconnected.")
                asyncio.run_coroutine_threadsafe(self.update_keyboards(), self.loop)

    def execute_macro(self, keycode):
        macro = self.macros.get(keycode)
        if not macro:
            logger.warning(f"[!] Key {keycode} not assigned.")
            return

        action = Action(macro)
        action.run()

    async def run(self):
        logger.info(f"\nMacro Pad active for {self.target_device_name}... (Ctrl+C to exit)\n")
        await self.update_keyboards()

        while True:
            async with self.keyboard_lock:
                if not self.running or self.paused or not self.keyboards:
                    await asyncio.sleep(0.5)
                    continue

                readable_devices, _, _ = select(self.keyboards, [], [], 0.1)
                for dev in readable_devices:
                    try:
                        events = dev.read()
                    except OSError as e:
                        logger.warning(f"[!] Device disconnected: {dev.name} ({dev.path}), reason: {e}")
                        await self.update_keyboards()
                        continue

                    for event in events:
                        if event.type != ecodes.EV_KEY:
                            continue

                        keyevent = categorize(event)
                        if keyevent.keystate == 1:  # Key down
                            self.execute_macro(keyevent.keycode)

            await asyncio.sleep(0.5)


@click.command()
@click.option('--version', is_flag=True, help='Show the version and exit.')
def cli(version):
    if version:
        print(f"macrokeyd {__version__}")
    else:
        config_loader = ConfigLoader()
        target_device_name = config_loader.get_target_device_name()
        macros = config_loader.get_macros()

        daemon = MacroDaemon(target_device_name, macros)
        asyncio.run(daemon.run())


if __name__ == "__main__":
    cli()
