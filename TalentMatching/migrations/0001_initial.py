# Generated by Django 5.1.4 on 2024-12-23 07:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Accounts', '0008_category_community_country_educationlevel_and_more'),
        ('DashboardPages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateVector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_vector', models.JSONField()),
                ('experience_vector', models.JSONField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobVector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_vector', models.JSONField()),
                ('experience_vector', models.JSONField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='DashboardPages.joblisting')),
            ],
        ),
        migrations.CreateModel(
            name='MatchPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_salary', models.IntegerField(blank=True, null=True)),
                ('max_salary', models.IntegerField(blank=True, null=True)),
                ('preferred_locations', models.JSONField(default=list)),
                ('remote_only', models.BooleanField(default=False)),
                ('job_types', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SkillVector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vector', models.JSONField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Accounts.skill')),
            ],
        ),
        migrations.CreateModel(
            name='MatchScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('skill_match_score', models.FloatField()),
                ('experience_match_score', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DashboardPages.joblisting')),
            ],
            options={
                'indexes': [models.Index(fields=['candidate', '-score'], name='TalentMatch_candida_efce32_idx'), models.Index(fields=['job', '-score'], name='TalentMatch_job_id_57ed9c_idx')],
                'unique_together': {('candidate', 'job')},
            },
        ),
    ]
