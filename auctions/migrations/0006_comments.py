# Generated by Django 4.0.1 on 2022-01-19 19:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_remove_bids_buyer_bids_buyer_remove_bids_listing_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(default='', max_length=5000)),
                ('listing', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='comments_from_listing', to='auctions.listings')),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='comments_from_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
