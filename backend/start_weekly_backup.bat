@echo off
echo Starting JNV Attendance Weekly Backup Scheduler...
cd /d "C:\Users\Hi\Desktop\vinod\attendance-app\backend"
python weekly_production_scheduler.py
pause
