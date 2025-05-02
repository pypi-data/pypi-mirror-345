from macrokeyd.logger import logger
import pystray
from PIL import Image
import sys
import os

def create_tray_icon(stop_callback, pause_callback, resume_callback):
    icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'icon64x64.png')

    if not os.path.exists(icon_path):
        logger.error(f"Error: Icon file not found at {icon_path}.")
        sys.exit(1)

    image = Image.open(icon_path)

    menu = pystray.Menu(
        pystray.MenuItem("Pause", lambda _: pause_callback()),
        pystray.MenuItem("Resume", lambda _: resume_callback()),
        pystray.MenuItem("Exit", lambda icon, _: stop_callback(icon))
    )

    icon = pystray.Icon("macrokeyd", image, "MacroKeyD", menu)
    return icon

def run_tray_icon(stop_callback, pause_callback, resume_callback):
    icon = create_tray_icon(stop_callback, pause_callback, resume_callback)
    icon.run()