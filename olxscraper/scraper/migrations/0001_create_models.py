# Generated by Django 4.1.7 on 2023-04-04 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OlxQuery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("search_keyword", models.TextField()),
                ("date_created", models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="OlxAdvertisement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.TextField()),
                ("price", models.FloatField()),
                ("location", models.TextField()),
                ("advertiser_name", models.TextField()),
                ("advertiser_phone_number", models.CharField(max_length=20)),
                ("olx_id", models.CharField(max_length=100)),
                (
                    "olx_query",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="scraper.olxquery",
                    ),
                ),
            ],
        ),
    ]
