import os
from .logger import get_logger
logger = get_logger(__name__)

def ensure_display_env():
    if "DISPLAY" in os.environ:
        return True

    x11_unix_dir = "/tmp/.X11-unix/"
    try:
        displays = [f.replace("X", ":") for f in os.listdir(x11_unix_dir) if f.startswith("X")]
    except FileNotFoundError:
        displays = []

    if not displays:
        logger.error("No available X11 displays detected in /tmp/.X11-unix/.")
        return False

    if len(displays) == 1:
        os.environ["DISPLAY"] = displays[0]
        logger.info(f"DISPLAY environment variable set automatically to {displays[0]}")
        return True
    else:
        logger.warning(f"Multiple X11 displays detected: {displays}. Please set DISPLAY manually.")
        return False
