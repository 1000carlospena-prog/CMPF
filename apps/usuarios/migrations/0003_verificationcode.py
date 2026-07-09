from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_profile_subscription_active_profile_subscription_end'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('code', models.CharField(max_length=6)),
                ('proposito', models.CharField(choices=[('register', 'Registro'), ('reset', 'Restablecer contraseña')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
