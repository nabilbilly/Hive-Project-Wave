# Generated by Django 5.1.4 on 2024-12-25 01:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Teamworkspace', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='No content')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Teamworkspace.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teamworkspace_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
