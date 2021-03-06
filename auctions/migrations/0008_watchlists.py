# Generated by Django 4.0.1 on 2022-01-20 00:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_listings_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Watchlists',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing_url', models.CharField(default='', max_length=2048)),
                ('listing', models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='URL_from_listing', to='auctions.listings')),
                ('user', models.ManyToManyField(blank=True, related_name='watchlist_from_watchlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
