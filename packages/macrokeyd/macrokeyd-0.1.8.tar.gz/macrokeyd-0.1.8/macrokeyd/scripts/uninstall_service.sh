#!/bin/bash
set -e

TARGET="/etc/systemd/system/macrokeyd.service"

echo "Desinstalando macrokeyd como servicio systemd..."

if [ "$(id -u)" -ne 0 ]; then
  echo "Este script debe ejecutarse como root (usa sudo)."
  exit 1
fi

# Verificar si systemd está presente
if ! pidof systemd > /dev/null; then
  echo "Error: systemd no está activo en este sistema."
  exit 2
fi

# Si el servicio está activo, detenerlo
if systemctl is-active --quiet macrokeyd; then
  echo "Deteniendo servicio macrokeyd..."
  systemctl stop macrokeyd
fi

# Si el servicio está habilitado, deshabilitarlo
if systemctl is-enabled --quiet macrokeyd; then
  echo "Deshabilitando servicio macrokeyd..."
  systemctl disable macrokeyd
fi

# Eliminar archivo de servicio
if [ -f "$TARGET" ]; then
  echo "Eliminando archivo de servicio..."
  rm -f "$TARGET"
fi

echo "Recargando systemd..."
systemctl daemon-reload

echo "✅ Servicio macrokeyd desinstalado correctamente."
