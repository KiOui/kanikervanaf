# Generated by Django 3.0.4 on 2020-03-15 16:42

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=1024)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("support_email", models.EmailField(max_length=254)),
                ("support_reply_number", models.IntegerField()),
                ("support_postal_code", models.CharField(max_length=6)),
                ("support_city", models.CharField(max_length=1024)),
                ("correspondence_address", models.CharField(max_length=1024)),
                ("correspondence_postal_code", models.CharField(max_length=6)),
                ("correspondence_city", models.CharField(max_length=1024)),
                (
                    "support_phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
                (
                    "cancellation_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
            ],
        ),
    ]
