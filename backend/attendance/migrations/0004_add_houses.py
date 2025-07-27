from django.db import migrations

def insert_houses(apps, schema_editor):
    Houses = apps.get_model('attendance', 'Houses')
    houses = [
        {'name': 'ARAVALI'},
        {'name': 'NILGIRI'},
        {'name': 'SHIVALIK'},
        {'name': 'UDAIGIRI'},
    ]
    for house in houses:
        Houses.objects.create(**house)

class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_houses'),  # Update with your previous migration name
    ]

    operations = [
        migrations.RunPython(insert_houses),
    ]