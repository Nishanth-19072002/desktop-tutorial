# Generated by Django 5.1.3 on 2025-02-21 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Riva', '0045_alter_hidrec_wash_carwash_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hidrec_wash',
            name='price',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='hidrec_wash',
            name='priceoil_skimmer',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='hidrec_wash',
            name='total_price',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
