# Generated by Django 4.1.7 on 2023-04-03 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
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
                ("name", models.CharField(max_length=255)),
                ("details", models.TextField()),
                ("date_added", models.DateField(auto_now_add=True)),
            ],
        ),
    ]