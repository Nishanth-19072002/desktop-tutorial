# Generated by Django 5.1.3 on 2025-01-24 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Riva', '0041_enquiry_is_relegated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enquiry',
            name='companygst',
        ),
        migrations.RemoveField(
            model_name='enquiry',
            name='companypan',
        ),
    ]
