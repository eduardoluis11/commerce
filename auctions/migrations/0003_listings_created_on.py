# Generated by Django 4.0.1 on 2022-01-19 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listings_category_listings_initial_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='created_on',
            field=models.DateTimeField(default='2022-01-01 1:00:00'),
        ),
    ]
