# Generated by Django 5.1.3 on 2024-12-24 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Riva', '0020_products_gst'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='gst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]
