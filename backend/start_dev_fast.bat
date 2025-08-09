@echo off
echo Starting Django with optimized reload settings...
cd /d "c:\Users\Hi\Desktop\suk-be\attendance-app\backend"

REM Start with watchdog for faster file change detection
python manage.py runserver 127.0.0.1:8000 --nothreading --watchdog

pause
