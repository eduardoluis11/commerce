# Generated by Django 4.0.1 on 2022-01-19 12:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='category',
            field=models.CharField(default='None', max_length=64),
        ),
        migrations.AddField(
            model_name='listings',
            name='initial_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AddField(
            model_name='listings',
            name='picture_url',
            field=models.CharField(default='', max_length=2048),
        ),
        migrations.AddField(
            model_name='listings',
            name='product_name',
            field=models.CharField(default='Product Name', max_length=128),
        ),
        migrations.AddField(
            model_name='listings',
            name='seller_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='list_of_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='listings',
            name='description',
            field=models.CharField(default='', max_length=4500),
        ),
    ]
