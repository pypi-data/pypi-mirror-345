import os
import sys
import gi
from macrokeyd.common.env_utils import ensure_display_env
ensure_display_env()

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3
import asyncio
from dbus_next.aio import MessageBus
from dbus_next import Message, MessageType
from macrokeyd.common.logger import get_logger

# Updated import as requested
from macrokeyd.common.config import ConfigLoader

logger = get_logger(__name__)

indicator = None


async def send_dbus_message(command):
    bus = await MessageBus().connect()

    msg = Message(
        destination='org.macrokeyd.Service',
        path='/org/macrokeyd',
        interface='org.macrokeyd.Service',
        member=command
    )

    reply = await bus.call(msg)

    if reply.message_type == MessageType.ERROR:
        error_message = reply.body[0] if reply.body else "Unknown error"
        logger.error(f"Failed to send '{command}' command via D-Bus. "
                     f"Ensure 'macrokeyd' daemon is running. Details: {error_message}")

def on_pause(_):
    logger.info("Sending 'Pause' command via DBus.")
    asyncio.run(send_dbus_message('Pause'))

def on_resume(_):
    logger.info("Sending 'Resume' command via DBus.")
    asyncio.run(send_dbus_message('Resume'))

def on_exit(_):
    logger.info("Sending 'Exit' command via DBus and quitting.")
    asyncio.run(send_dbus_message('Exit'))
    # Gtk.main_quit()  @TODO; here we are... logic of pause and run.

def create_menu():
    menu = Gtk.Menu()

    pause_item = Gtk.MenuItem(label='Pause')
    pause_item.connect('activate', on_pause)
    menu.append(pause_item)

    resume_item = Gtk.MenuItem(label='Resume')
    resume_item.connect('activate', on_resume)
    menu.append(resume_item)

    exit_item = Gtk.MenuItem(label='Exit')
    exit_item.connect('activate', on_exit)
    menu.append(exit_item)

    menu.show_all()
    return menu

def create_tray_icon():
    global indicator  # Use the global variable
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon64x64.png')

    if not os.path.exists(icon_path):
        logger.error(f"Error: Icon file not found at {icon_path}.")
        sys.exit(1)

    indicator = AppIndicator3.Indicator.new(
        "macrokeyd-indicator",
        icon_path,
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS
    )

    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(create_menu())

    return indicator

def main():
    create_tray_icon()
    logger.info("Tray icon started successfully using AppIndicator.")
    Gtk.main()

if __name__ == "__main__":
    main()