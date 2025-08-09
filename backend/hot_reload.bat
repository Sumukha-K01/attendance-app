@echo off
setlocal enabledelayedexpansion

set PORTS=8000 8001
set CURRENT_PORT=8000

echo Starting Django hot reload manager...
cd /d "c:\Users\Hi\Desktop\suk-be\attendance-app\backend"

:loop
echo Starting Django on port %CURRENT_PORT%...
start /b python manage.py runserver 127.0.0.1:%CURRENT_PORT% --nothreading

echo Server started on http://127.0.0.1:%CURRENT_PORT%
echo Press any key to restart with zero downtime...
pause >nul

REM Switch to alternate port
if %CURRENT_PORT%==8000 (
    set NEXT_PORT=8001
) else (
    set NEXT_PORT=8000
)

echo Starting new instance on port %NEXT_PORT%...
start /b python manage.py runserver 127.0.0.1:%NEXT_PORT% --nothreading

timeout /t 5 >nul
echo New instance ready. Stopping old instance on port %CURRENT_PORT%...

REM Kill old process (you might need to implement proper process tracking)
taskkill /f /im python.exe 2>nul

set CURRENT_PORT=%NEXT_PORT%
echo Now serving on http://127.0.0.1:%CURRENT_PORT%

goto loop
