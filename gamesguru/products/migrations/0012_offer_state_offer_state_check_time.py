# Generated by Django 4.2.6 on 2023-12-03 17:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_product_search_words_to_exclude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='state',
            field=models.CharField(choices=[('not checked', 'Not Checked'), ('outdated', 'Outdated'), ('valid', 'Valid')], default='not checked', max_length=16),
        ),
        migrations.AddField(
            model_name='offer',
            name='state_check_time',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='State check time'),
        ),
    ]
