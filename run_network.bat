@echo off
setlocal
echo ==========================================
echo   College Voting System - Network Mode
echo ==========================================
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "10. 192. 172."') do (
    set IP=%%a
    goto :found
)

:found
set IP=%IP: =%
echo Detected Local IP: %IP%
echo.
echo 1. Search for this link on other devices:
echo    http://%IP%:8001/
echo.
echo 2. Make sure both devices are on the SAME WiFi.
echo.
echo Starting server...
echo.

python manage.py runserver 0.0.0.0:8001

pause
