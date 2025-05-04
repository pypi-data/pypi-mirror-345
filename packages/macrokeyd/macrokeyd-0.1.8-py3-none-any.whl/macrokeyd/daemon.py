import asyncio
import subprocess
from macrokeyd.dbus_service import main_loop
from evdev import InputDevice, categorize, ecodes, list_devices
from select import select
from macrokeyd.common.config_loader import load_config
import os
from macrokeyd.common.env_utils import ensure_display_env
import click
from macrokeyd import __version__
from macrokeyd.common.logger import get_logger
import threading
import pyudev
from time import sleep
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
        self.update_keyboards()
        self.udev_thread = threading.Thread(target=self.monitor_udev_events, daemon=True)
        self.udev_thread.start()

    def pause(self):
        self.paused = True
        logger.info("[DBUS] Daemon paused.")

    def resume(self):
        self.paused = False
        logger.info("[DBUS] Daemon resumed.")

    def stop(self):
        self.running = False
        logger.info("[DBUS] Daemon stopped.")

    def get_status(self):
        return "paused" if self.paused else "running"

    def detect_keyboards(self, target_device_name):
        keyboards = []
        for path in list_devices():
            device = InputDevice(path)
            capabilities = device.capabilities()

            if ecodes.EV_KEY in capabilities and ecodes.EV_REL not in capabilities:
                if device.name == target_device_name:
                    try:
                        device.grab()
                        logger.info(f"[+] Exclusive grab: {device.name} ({device.path})")
                        keyboards.append(device)
                    except OSError as e:
                        logger.warning(f"[!] Could not grab {device.name}: {e}")

        if not keyboards:
            logger.warning(f"[!] No compatible keyboards found for {target_device_name}")

        return keyboards

    def update_keyboards(self, retries=5, delay=1):
        # Liberar los teclados previamente capturados
        for kb in self.keyboards:
            try:
                kb.ungrab()
                logger.info(f"[−] Released keyboard: {kb.name} ({kb.path})")
            except Exception as e:
                logger.warning(f"[!] Error releasing keyboard {kb.name}: {e}")

        # Intentos múltiples para detectar teclados
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
            if device.get('ID_INPUT_KEYBOARD') == '1':
                device_name = device.get('NAME')
                if not device_name:
                    logger.debug(f"[udev] Device with action '{action}' has no NAME property. Ignored.")
                    continue

                device_name = device_name.strip('"')
                logger.debug(f"[udev] Action: {action} on Device: {device_name}")

                if device_name == self.target_device_name:
                    if action == 'add':
                        logger.info(f"[udev] Keyboard '{device_name}' connected.")
                        self.update_keyboards()
                    elif action == 'remove':
                        logger.warning(f"[udev] Keyboard '{device_name}' disconnected.")
                        self.update_keyboards()

    def execute_macro(self, keycode):
        macro = self.macros.get(keycode)
        if not macro:
            logger.warning(f"[!] Key {keycode} not assigned.")
            return

        action_type = macro.get('action')
        value = macro.get('value')

        logger.info(f"[MACRO] Executing {action_type}: {value}")

        if action_type == 'command':
            try:
                logger.debug(f"Running command (non-blocking): {value} with environment: {os.environ}")
                subprocess.Popen(value, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=os.environ)
            except Exception as e:
                logger.error(f"Unexpected error running command '{value}': {e}")
        elif action_type == 'text':
            try:
                logger.debug(f"Typing text: {value}")
                self.pyautogui.typewrite(value)
            except Exception as e:
                logger.error(f"Error typing text '{value}': {e}")
        else:
            logger.warning(f"[!] Unknown action type: {action_type}")

    async def run(self):
        logger.info(f"\nMacro Pad active for {self.target_device_name}... (Ctrl+C to exit)\n")
        while self.running:
            if self.paused or not self.keyboards:
                await asyncio.sleep(0.5)
                continue

            r, _, _ = select(self.keyboards, [], [], 0.1)
            for dev in r:
                try:
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY:
                            keyevent = categorize(event)
                            if keyevent.keystate == 1:  # Key down
                                self.execute_macro(keyevent.keycode)
                except OSError as e:
                    logger.warning(f"[!] Device disconnected: {dev.name} ({dev.path}), reason: {e}")
                    self.update_keyboards()

async def main():
    CONFIG_PATH = get_config_path()
    ensure_config_exists(CONFIG_PATH)
    meta, macros = load_config(CONFIG_PATH)
    target_device_name = meta.get('target_device_name')

    if not target_device_name:
        logger.error("[!] 'target_device_name' not specified in configuration.")
        return

    daemon = MacroDaemon(target_device_name, macros)

    logger.debug("[DEBUG] Starting daemon run loop and DBus service loop...")
    await asyncio.gather(
        daemon.run(),
        main_loop(daemon)
    )
    logger.debug("[DEBUG] Daemon and DBus loops have exited.")

async def run_without_dbus():
    CONFIG_PATH = get_config_path()
    ensure_config_exists(CONFIG_PATH)
    meta, macros = load_config(CONFIG_PATH)
    target_device_name = meta.get('target_device_name')

    if not target_device_name:
        logger.error("[!] 'target_device_name' not specified in configuration.")
        return

    daemon = MacroDaemon(target_device_name, macros)
    await daemon.run()

@click.command()
@click.option('--run', is_flag=True, help='Run the macro daemon.')
@click.option('--with-dbus', is_flag=True, help='Run the macro daemon with DBus support.')
@click.option('--version', is_flag=True, help='Show the version and exit.')
def cli(run, with_dbus, version):
    if version:
        print(f"macrokeyd {__version__}")
        return

    if run:
        if with_dbus:
            asyncio.run(main())
        else:
            asyncio.run(run_without_dbus())
    else:
        click.echo("Use --run to start the daemon, --with-dbus for DBus support, or --help for more options.")

def get_config_path():
    xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    config_path = os.path.join(xdg_data_home, "macrokeyd", "default.json")
    return config_path

def ensure_config_exists(config_path):
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        default_path = os.path.join(os.path.dirname(__file__), 'macros', 'default.json')
        if os.path.exists(default_path):
            with open(default_path, 'r') as src, open(config_path, 'w') as dst:
                dst.write(src.read())
            logger.info(f"[+] Default configuration copied to {config_path}")
        else:
            logger.warning(f"[!] Default configuration file not found at {default_path}")

if __name__ == "__main__":
    cli()
