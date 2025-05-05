from ..common.logger import get_logger
from dbus_next.service import ServiceInterface, method
from dbus_next.aio import MessageBus
import asyncio

logger = get_logger(__name__)

class MacrokeydService(ServiceInterface):
    def __init__(self):
        super().__init__('org.macrokeyd.Service')
        self.running = True

    @method()
    async def Pause(self):
        logger.info("[DBUS] Received 'Pause' command.")
        self.running = not self.running

    @method()
    async def Resume(self):
        logger.info("[DBUS] Received 'Resume' command.")
        self.running = True

    @method()
    async def Stop(self):
        logger.info("[DBUS] Received 'Stop' command.")

    @method()
    async def GetStatus(self) -> 's':
        logger.info("[DBUS] Received 'GetStatus' command.")
        running = str(self.running)
        logger.info(f"[DBUS] Current status: {running}")
        return running

async def main():
    logger.info("[DBUS] Connecting to session bus...")
    bus = await MessageBus().connect()
    logger.info(f"[DBUS] Connected {repr(bus)}.")

    service = MacrokeydService()
    bus.export('/org/macrokeyd', service)
    logger.info("[DBUS] Exported object.")

    await bus.request_name('org.macrokeyd.Service')
    logger.info("[DBUS] Service name registered successfully.")

    while True:
        await asyncio.sleep(1)

def entrypoint():
    asyncio.run(main())