@echo off
title El Rincon de Gabi - Launcher

echo ========================================
echo   El Rincon de Gabi - Iniciando...
echo ========================================
echo.

:: Iniciar backend en nueva ventana
echo Iniciando backend...
start "Backend - FastAPI" cmd /k "cd /d %~dp0backend && python main.py"

:: Esperar un poco para que el backend arranque
timeout /t 2 /nobreak >nul

:: Iniciar frontend en nueva ventana
echo Iniciando frontend...
start "Frontend - Astro" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   Servidores iniciados!
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo ========================================
echo.
echo Cierra esta ventana o presiona una tecla para salir...
pause >nul
