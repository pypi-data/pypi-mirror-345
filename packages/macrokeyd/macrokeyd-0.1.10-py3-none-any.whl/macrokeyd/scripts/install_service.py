import subprocess
import os
import sys
import platform
import click

def create_dbus_service():
    service_dir = os.path.expanduser("~/.local/share/dbus-1/services")
    if not os.path.exists(service_dir):
        os.makedirs(service_dir)
    service_file = os.path.join(service_dir, "org.macrokeyd.Service.service")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    macrokeyd_exec = os.path.normpath(os.path.join(current_dir, '..', 'macrokeyd'))

    service_content = f"""[D-BUS Service]
Name=org.macrokeyd.Service
Exec={macrokeyd_exec}
"""

    with open(service_file, "w") as f:
        f.write(service_content)

    click.echo(f"Archivo D-Bus creado en: {service_file}")

@click.command()
def cli():
    """Instala el servicio macrokeyd en systemd (Linux)."""
    if platform.system() != "Linux":
        click.echo("Error: macrokeyd solo puede instalarse como servicio en sistemas Linux.")
        sys.exit(1)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, '..', 'scripts', 'install_service.sh')
    script_path = os.path.normpath(script_path)

    if not os.path.exists(script_path):
        click.echo(f"Error: no se encuentra el script {script_path}")
        sys.exit(2)

    click.echo("Instalando servicio macrokeyd...")
    subprocess.run(['sudo', 'bash', script_path])

    create_dbus_service()

if __name__ == "__main__":
    cli()