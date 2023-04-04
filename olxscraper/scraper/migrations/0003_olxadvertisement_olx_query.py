# Generated by Django 4.1.7 on 2023-04-04 02:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("scraper", "0002_olxquery_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="olxadvertisement",
            name="olx_query",
            field=models.ForeignKey(
                default=123,
                on_delete=django.db.models.deletion.PROTECT,
                to="scraper.olxquery",
            ),
            preserve_default=False,
        ),
    ]
