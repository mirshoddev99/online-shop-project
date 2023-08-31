# Generated by Django 4.2.2 on 2023-08-26 13:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='auth_status',
            field=models.CharField(choices=[('new', 'new'), ('code_verified', 'code_verified')], default='new', max_length=31),
        ),
        migrations.CreateModel(
            name='UserConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4)),
                ('expiration_time', models.DateTimeField(null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verify_codes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]