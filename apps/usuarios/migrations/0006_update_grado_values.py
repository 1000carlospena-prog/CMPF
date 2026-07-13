from django.db import migrations


def update_grado(apps, schema_editor):
    Profile = apps.get_model('usuarios', 'Profile')
    Profile.objects.filter(grado='v00').update(grado='g0')


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_alter_profile_grado'),
    ]

    operations = [
        migrations.RunPython(update_grado, reverse_code=migrations.RunPython.noop),
    ]
