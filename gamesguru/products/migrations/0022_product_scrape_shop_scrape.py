# Generated by Django 4.2.6 on 2024-01-29 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_remove_product_base_name_remove_product_search_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='scrape',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='shop',
            name='scrape',
            field=models.BooleanField(default=True),
        ),
    ]
