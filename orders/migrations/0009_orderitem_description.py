# Generated by Django 5.1.4 on 2025-01-06 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
