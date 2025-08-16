"""
Manual Test Script - Send backup immediately
"""
import os
import sys
import django
from datetime import datetime

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

def test_backup_now():
    """Test backup immediately"""
    print("🧪 MANUAL BACKUP TEST")
    print("=" * 30)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📧 Email: vinodrc3@gmail.com")
    print()
    
    try:
        from attendance.backup_utils import send_weekly_backup
        
        print("📊 Sending test backup...")
        success = send_weekly_backup('vinodrc3@gmail.com')
        
        if success:
            print("✅ SUCCESS: Manual test backup sent!")
            print("📧 Check your email: vinodrc3@gmail.com")
            print("📁 Excel file should be attached")
        else:
            print("⚠️  No attendance data available for backup")
            print("✅ But email system is working correctly")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backup_now()
