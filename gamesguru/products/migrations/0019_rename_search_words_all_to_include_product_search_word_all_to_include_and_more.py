# Generated by Django 4.2.6 on 2024-01-29 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_alter_product_search_words_all_to_include_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='search_words_all_to_include',
            new_name='search_word_all_to_include',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='search_words_any_to_exclude',
            new_name='search_word_any_to_exclude',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='search_words_any_to_include',
            new_name='search_word_any_to_include',
        ),
    ]
