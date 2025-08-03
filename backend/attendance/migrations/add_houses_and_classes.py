# Insert manually to attendance_houses tae
from django.db import migrations, models

class Migration(migrations.Migration):
    def add_houses(apps, schema_editor):
        Houses = apps.get_model('attendance', 'Houses')
        Houses.objects.bulk_create([
            Houses(id=1, name='ARAVALI_JR'),
            Houses(id=2, name='NILGIRI_JR'),
            Houses(id=3, name='SHIVALIK_JR'),
            Houses(id=4, name='UDAIGIRI_JR'),
            Houses(id=5, name='ARAVALI_SR'),
            Houses(id=6, name='NILGIRI_SR'),
            Houses(id=7, name='SHIVALIK_SR'),
            Houses(id=8, name='UDAIGIRI_SR'),
        ])

    def add_classes(apps, schema_editor):
        Classroom = apps.get_model('attendance', 'Classroom')
        Classroom.objects.bulk_create([
            Classroom(id=1, name='Class 6 A'),
            Classroom(id=2, name='Class 6 B'),
            Classroom(id=3, name='Class 7 A'),
            Classroom(id=4, name='Class 7 B'),
            Classroom(id=5, name='Class 8 A'),
            Classroom(id=6, name='Class 8 B'),
            Classroom(id=7, name='Class 9 A'),
            Classroom(id=8, name='Class 9 B'),
            Classroom(id=9, name='Class 10 A'),
            Classroom(id=10, name='Class 10 B'),
            Classroom(id=11, name='Class 11 A'),
            Classroom(id=12, name='Class 11 B'),
            Classroom(id=13, name='Class 12 A'),
            Classroom(id=14, name='Class 12 B'),
        ])

    dependencies = [
        ('attendance', '0011_alter_attendance_date_alter_student_roll_number'),
    ]
    operations = [
        migrations.RunPython(add_houses),
        migrations.RunPython(add_classes),
    ]
    