import logging
import sys

# ANSI escape sequences para colores
COLORS = {
    'DEBUG': '\033[36m',     # cyan
    'INFO': '\033[32m',      # verde
    'WARNING': '\033[33m',   # amarillo
    'ERROR': '\033[31m',     # rojo
    'CRITICAL': '\033[41m',  # fondo rojo
}
RESET_COLOR = '\033[0m'

class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelname, RESET_COLOR)
        message = super().format(record)
        return f"{color}{message}{RESET_COLOR}"

def get_logger(name: str = None, level=logging.DEBUG):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColorFormatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
                                   datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger
