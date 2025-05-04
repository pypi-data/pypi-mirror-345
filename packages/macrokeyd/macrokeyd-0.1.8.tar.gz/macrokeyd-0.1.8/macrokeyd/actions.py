import subprocess
from .common.env_utils import ensure_display_env
import logging

logger = logging.getLogger(__name__)

def execute_command(command):
    subprocess.run(command, shell=True)

def write_text(text):
    if ensure_display_env():
        import pyautogui
        pyautogui.typewrite(text)
    else:
        logger.error("Cannot write text: DISPLAY environment variable not set.")