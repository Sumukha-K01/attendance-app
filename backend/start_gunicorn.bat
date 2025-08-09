@echo off
echo Starting Django with Gunicorn (zero-downtime reload)...
cd /d "c:\Users\Hi\Desktop\suk-be\attendance-app\backend"

REM Start gunicorn with auto-reload and graceful restart
gunicorn core.wsgi:application --bind 127.0.0.1:8000 --workers 2 --reload --timeout 60 --graceful-timeout 30

pause
