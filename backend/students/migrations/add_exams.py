# add exams maually to students_exams table
from django.db import migrations, models
from django.utils import timezone
from datetime import timedelta
def add_exams(apps, schema_editor):
    Exam = apps.get_model('students', 'Exam')
    now = timezone.now()
    exams = [
        Exam(name='PWT 1'),
        Exam(name='PWT 2'),
        Exam(name='PWT 3'),
        Exam(name='PWT 4'),
        Exam(name='MID TERM'),
        Exam(name='FINAL EXAM'),
    ]
    Exam.objects.bulk_create(exams)
class Migration(migrations.Migration):
    dependencies = [
        ('students', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(add_exams),
    ]
