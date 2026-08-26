#!/bin/bash
# Gera o executavel do Painel de Suporte (Mac)
# Desenvolvido por Wesley Walter

set -e
cd "$(dirname "$0")"

echo "Instalando o PyInstaller..."
pip3 install pyinstaller

echo "Gerando o executavel (pode demorar 1-2 minutos)..."
pyinstaller --onefile --windowed --name Suporte suporte_app.py

echo ""
echo "Pronto! O executavel esta em: dist/Suporte"
echo "Mande esse arquivo para quem for atender."
echo "(Na primeira vez, o macOS pode pedir para liberar em Preferencias > Privacidade e Seguranca)"
