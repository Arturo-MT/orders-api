# Generated by Django 5.1.4 on 2025-01-15 22:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_store_order_store_product_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.store'),
        ),
    ]
