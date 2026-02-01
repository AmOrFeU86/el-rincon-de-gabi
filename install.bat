@echo off
title El Rincon de Gabi - Instalacion

echo ========================================
echo   El Rincon de Gabi - Instalando...
echo ========================================
echo.

:: Instalar dependencias del backend
echo [1/2] Instalando dependencias del backend...
cd /d %~dp0backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias de Python
    pause
    exit /b 1
)

echo.

:: Instalar dependencias del frontend
echo [2/2] Instalando dependencias del frontend...
cd /d %~dp0frontend
call npm install
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias de Node
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Instalacion completada!
echo   Ejecuta start.bat para iniciar
echo ========================================
pause
