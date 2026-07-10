from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_verificationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='verificationcode',
            name='intentos_fallidos',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('username', models.CharField(blank=True, max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('successful', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['ip_address', 'created_at'], name='usuarios_log_ip_addr_9ace5d_idx')],
            },
        ),
    ]
