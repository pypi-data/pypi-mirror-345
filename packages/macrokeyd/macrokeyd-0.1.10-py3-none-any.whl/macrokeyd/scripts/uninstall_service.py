import subprocess
import os
import sys
import platform
import click

@click.command()
def cli():
    """Desinstala el servicio macrokeyd de systemd (Linux)."""
    if platform.system() != "Linux":
        click.echo("Error: macrokeyd solo puede desinstalarse como servicio en sistemas Linux.")
        sys.exit(1)

    target_path = "/etc/systemd/system/macrokeyd.service"

    if os.path.exists(target_path):
        click.echo("Deteniendo servicio macrokeyd...")
        subprocess.run(["sudo", "systemctl", "stop", "macrokeyd"])

        click.echo("Deshabilitando servicio macrokeyd...")
        subprocess.run(["sudo", "systemctl", "disable", "macrokeyd"])

        click.echo("Eliminando archivo de servicio...")
        subprocess.run(["sudo", "rm", "-f", target_path])

        click.echo("Recargando systemd...")
        subprocess.run(["sudo", "systemctl", "daemon-reload"])

        click.echo("✅ Servicio macrokeyd desinstalado correctamente.")
    else:
        click.echo("ℹ️  El servicio macrokeyd no está instalado o ya fue eliminado.")

if __name__ == "__main__":
    cli()
    