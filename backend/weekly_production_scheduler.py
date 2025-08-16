"""
JNV Attendance Weekly Backup Scheduler
Sends backup every Sunday at 9:00 AM to vinodrc3@gmail.com
"""
import os
import sys
import django
from datetime import datetime
import time
import schedule

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Email configuration
os.environ['EMAIL_HOST'] = 'smtp.gmail.com'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_USE_TLS'] = 'True'
os.environ['EMAIL_HOST_USER'] = 'vinodrc3@gmail.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'bjhu yxpm qhfh oxfd'
os.environ['DEFAULT_FROM_EMAIL'] = 'JNV Attendance System <vinodrc3@gmail.com>'

django.setup()

def send_weekly_backup():
    """Send weekly backup email"""
    try:
        from attendance.backup_utils import send_weekly_backup
        
        print(f"🚀 WEEKLY BACKUP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        success = send_weekly_backup('vinodrc3@gmail.com')
        
        if success:
            print("✅ Weekly backup sent successfully!")
        else:
            print("⚠️  No attendance data available")
            
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")

def run_scheduler():
    """Main weekly scheduler"""
    print("📅 JNV Attendance Weekly Backup Scheduler")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📅 Schedule: Every Sunday at 9:00 AM")
    print("📧 Email: vinodrc3@gmail.com")
    
    # Schedule weekly backup
    schedule.every().sunday.at("09:00").do(send_weekly_backup)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
        except KeyboardInterrupt:
            print(f"\n⏹️  Scheduler stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
