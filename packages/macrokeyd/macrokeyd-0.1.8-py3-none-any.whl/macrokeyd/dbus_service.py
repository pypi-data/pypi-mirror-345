from .common.logger import get_logger
from dbus_next.service import ServiceInterface, method
from dbus_next.aio import MessageBus
import asyncio

logger = get_logger(__name__)

class MacrokeydService(ServiceInterface):
    def __init__(self, daemon):
        super().__init__('org.macrokeyd.Service')
        self.daemon = daemon

    @method()
    async def Pause(self):
        self.daemon.pause()

    @method()
    async def Resume(self):
        self.daemon.resume()

    @method()
    async def Stop(self):
        self.daemon.stop()

    @method()
    async def GetStatus(self) -> 's':
        return self.daemon.get_status()

async def main_loop(daemon):
    logger.info("[DBUS] Connecting to session bus...")
    bus = await MessageBus().connect()
    logger.info("[DBUS] Connected.")

    service = MacrokeydService(daemon)
    bus.export('/org/macrokeyd', service)
    logger.info("[DBUS] Exported object.")

    await bus.request_name('org.macrokeyd.Service')
    logger.info("[DBUS] Service name registered successfully.")

    while daemon.running:
        await asyncio.sleep(1)
