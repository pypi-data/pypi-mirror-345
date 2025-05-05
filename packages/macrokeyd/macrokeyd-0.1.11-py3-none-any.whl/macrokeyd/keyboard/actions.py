import subprocess
from macrokeyd.common.env_utils import ensure_display_env
import logging

logger = logging.getLogger(__name__)

class Action:
    def __init__(self, macro):
        self.type = macro.get('action')
        self.value = macro.get('value')

    def run(self):
        method_name = f"run_{self.type}"
        method = getattr(self, method_name, None)

        if not callable(method):
            logger.warning(f"[!] Action type '{self.type}' not implemented.")
            return

        logger.info(f"[ACTION] Executing '{self.type}': {self.value}")
        method()

    def run_command(self):
        try:
            subprocess.Popen(
                self.value, shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.debug(f"Executed command: {self.value}")
        except Exception as e:
            logger.error(f"Error executing command '{self.value}': {e}")

    def run_text(self):
        if not ensure_display_env():
            logger.error("Cannot execute text action: DISPLAY not set.")
            return
        import pyautogui
        try:
            pyautogui.typewrite(self.value)
            logger.debug(f"Typed text: {self.value}")
        except Exception as e:
            logger.error(f"Error typing text '{self.value}': {e}")