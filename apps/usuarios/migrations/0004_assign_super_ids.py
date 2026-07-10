from django.db import migrations


def assign_super_ids(apps, schema_editor):
    Profile = apps.get_model('usuarios', 'Profile')
    v1_users = Profile.objects.filter(grado='v1', super_id__isnull=True).select_related('user').order_by('user__date_joined')
    next_id = 1
    existing = Profile.objects.filter(grado='v1', super_id__isnull=False).order_by('-super_id').first()
    if existing:
        next_id = existing.super_id + 1
    for profile in v1_users:
        profile.super_id = next_id
        profile.save(update_fields=['super_id'])
        next_id += 1


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0003_profile_super_id_alter_profile_grado'),
    ]
    operations = [
        migrations.RunPython(assign_super_ids),
    ]
