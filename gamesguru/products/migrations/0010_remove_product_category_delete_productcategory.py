# Generated by Django 4.2.6 on 2023-11-29 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_product_unique_name_product_unique_search_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.DeleteModel(
            name='ProductCategory',
        ),
    ]
