# Generated by Django 4.2.6 on 2023-12-09 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_rename_search_words_to_exclude_product_search_words_any_to_exclude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='show_on_smartphones',
            field=models.BooleanField(default=True),
        ),
    ]
