@echo off
REM Gerar executavel do Painel de Suporte
REM Desenvolvido por Wesley Walter

cd /d "%~dp0"
title Gerando executavel do Suporte
echo ============================================
echo   Gerando o executavel do Painel de Suporte...
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado neste computador.
    echo Instale em https://www.python.org/downloads/
    echo e marque "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

echo Python encontrado. Instalando o PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

if errorlevel 1 (
    echo.
    echo ERRO ao instalar o PyInstaller. Verifique sua internet e tente de novo.
    pause
    exit /b 1
)

echo.
echo Gerando o executavel agora (pode demorar 1-2 minutos)...
echo.
python -m PyInstaller --onefile --windowed --name Suporte suporte_app.py

if errorlevel 1 (
    echo.
    echo ERRO ao gerar o executavel. Veja as mensagens acima.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Pronto!
echo   O executavel esta em: dist\Suporte.exe
echo   Mande esse arquivo para quem for atender.
echo ============================================
echo.
pause
