# Generated by Django 4.2.6 on 2024-01-28 19:12

import django.contrib.postgres.fields
from django.db import migrations, models


def propagate_lists(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        product.base_names = [product.base_name]
        product.search_names = [product.search_name]
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_alter_product_epi'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='product',
            name='unique_search_name',
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('epi',), name='unique_epi'),
        ),
        migrations.AddField(
            model_name='product',
            name='base_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default='<django.db.models.fields.CharField>', max_length=100), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='product',
            name='search_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default='<django.db.models.fields.CharField>', max_length=100), blank=True, default=list, size=None),
        ),
        migrations.RunPython(propagate_lists),
    ]
