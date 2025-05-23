# Generated by Django 5.1.3 on 2024-12-17 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Riva', '0002_xpredict'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=255)),
                ('account_holder_name', models.CharField(max_length=255)),
                ('account_number', models.CharField(max_length=50)),
                ('ifsc_code', models.CharField(max_length=20)),
                ('branch_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
    ]
