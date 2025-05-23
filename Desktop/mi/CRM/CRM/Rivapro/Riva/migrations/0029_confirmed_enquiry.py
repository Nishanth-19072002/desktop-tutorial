# Generated by Django 5.1.3 on 2025-01-15 09:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Riva', '0028_remove_followup_entrydate_followup_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='confirmed_enquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation', models.CharField(max_length=40)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('enquiry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Riva.enquiry')),
            ],
        ),
    ]
