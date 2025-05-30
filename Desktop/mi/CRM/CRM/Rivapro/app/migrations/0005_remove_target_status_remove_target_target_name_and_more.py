# Generated by Django 5.1.3 on 2024-12-30 06:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_target'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='target',
            name='status',
        ),
        migrations.RemoveField(
            model_name='target',
            name='target_name',
        ),
        migrations.RemoveField(
            model_name='target',
            name='target_value',
        ),
        migrations.RemoveField(
            model_name='target',
            name='user_profile',
        ),
        migrations.AddField(
            model_name='target',
            name='value',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.target'),
        ),
    ]
