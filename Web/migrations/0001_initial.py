# Generated by Django 5.1.1 on 2024-09-14 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_id', models.IntegerField()),
                ('time_created', models.DateTimeField()),
                ('time_applied', models.DateTimeField()),
                ('time_ended', models.DateTimeField()),
                ('connection_code', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'appeals',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=300)),
                ('image', models.CharField(max_length=64)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'issues',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AppealIssues',
            fields=[
                ('appeal_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='Web.appeal')),
                ('count', models.IntegerField()),
            ],
            options={
                'db_table': 'appeal_issues',
                'managed': False,
            },
        ),
    ]
