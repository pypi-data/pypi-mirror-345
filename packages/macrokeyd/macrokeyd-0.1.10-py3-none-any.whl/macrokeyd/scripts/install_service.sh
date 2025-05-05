#!/bin/bash
set -e

SERVICE_FILE="systemd/macrokeyd.service"
TARGET="/etc/systemd/system/macrokeyd.service"

echo "Instalando macrokeyd como servicio systemd..."

if [ "$(id -u)" -ne 0 ]; then
  echo "Este script debe ejecutarse como root (usa sudo)."
  exit 1
fi

# Verificar si systemd está presente
if ! pidof systemd > /dev/null; then
  echo "Error: systemd no está activo en este sistema."
  exit 2
fi

if [ ! -f "$SERVICE_FILE" ]; then
  echo "No se encuentra el archivo $SERVICE_FILE."
  exit 3
fi

echo "Copiando servicio..."
cp "$SERVICE_FILE" "$TARGET"

echo "Recargando systemd..."
systemctl daemon-reload

echo "Habilitando servicio..."
systemctl enable macrokeyd

echo "Iniciando servicio..."
systemctl start macrokeyd

echo "✅ Servicio macrokeyd instalado y corriendo."
