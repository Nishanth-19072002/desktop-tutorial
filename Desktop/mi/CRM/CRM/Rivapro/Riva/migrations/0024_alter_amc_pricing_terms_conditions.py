# Generated by Django 5.1.3 on 2025-01-02 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Riva', '0023_installationtable_keyvaluestore_outputtable_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amc_pricing',
            name='terms_conditions',
            field=models.TextField(null=True),
        ),
    ]
