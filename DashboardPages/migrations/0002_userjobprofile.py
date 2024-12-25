# Generated by Django 5.1.4 on 2024-12-23 11:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0008_category_community_country_educationlevel_and_more'),
        ('DashboardPages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserJobProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employment_type', models.CharField(choices=[('full-time', 'Full Time'), ('part-time', 'Part Time'), ('contract', 'Contract'), ('internship', 'Internship')], max_length=50)),
                ('english_level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('native', 'Native')], max_length=50)),
                ('expected_salary', models.IntegerField(blank=True, null=True)),
                ('interests', models.TextField(blank=True)),
                ('years_of_experience', models.IntegerField(default=0)),
                ('education_level', models.CharField(choices=[('high-school', 'High School'), ('bachelors', "Bachelor's Degree"), ('masters', "Master's Degree"), ('phd', 'PhD')], max_length=100)),
                ('preferred_location', models.CharField(blank=True, max_length=255)),
                ('work_schedule', models.CharField(choices=[('full-time', 'Full Time'), ('part-time', 'Part Time'), ('flexible', 'Flexible')], max_length=50)),
                ('email_notifications', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('skills', models.ManyToManyField(related_name='user_profiles', to='Accounts.skill')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]