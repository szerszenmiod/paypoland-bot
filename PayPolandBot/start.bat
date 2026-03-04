@echo off
title PayPoland Premium Bot
color 0A

echo.
echo   ╔═══════════════════════════════════════════════════════════╗
echo   ║                                                           ║
echo   ║   ██████╗  █████╗ ██╗   ██╗██████╗  ██████╗ ██╗      █████╗ ███╗   ██╗██████╗ 
echo   ║   ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗██║     ██╔══██╗████╗  ██║██╔══██╗
echo   ║   ██████╔╝███████║ ╚████╔╝ ██████╔╝██║   ██║██║     ███████║██╔██╗ ██║██║  ██║
echo   ║   ██╔═══╝ ██╔══██║  ╚██╔╝  ██╔═══╝ ██║   ██║██║     ██╔══██║██║╚██╗██║██║  ██║
echo   ║   ██║     ██║  ██║   ██║   ██║     ╚██████╔╝███████╗██║  ██║██║ ╚████║██████╔╝
echo   ║   ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ 
echo   ║                                                           ║
echo   ║              PREMIUM DISCORD BOT - CRYPTO EXCHANGE        ║
echo   ║                    Wersja 1.0.0 - 2026                    ║
echo   ║                                                           ║
echo   ╚═══════════════════════════════════════════════════════════╝
echo.

echo [✓] Ladowanie konfiguracji...
timeout /t 2 /nobreak > nul

echo [✓] Inicjalizacja modulow...
timeout /t 2 /nobreak > nul

echo [✓] Sprawdzanie polaczenia z Discord API...
timeout /t 2 /nobreak > nul

echo.
echo [✓] PayPoland Bot - GOTOWY DO PRACY!
echo.
echo Nacisnij dowolny klawisz aby uruchomic bota...
pause > nul

python main.py
pause
