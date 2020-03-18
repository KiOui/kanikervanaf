# Generated by Django 3.0.4 on 2020-03-16 10:01

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0003_auto_20200316_0954"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="amount_used",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="cancellation_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, region=None
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="correspondence_address",
            field=models.CharField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="correspondence_city",
            field=models.CharField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="correspondence_postal_code",
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_city",
            field=models.CharField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, region=None
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_postal_code",
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_reply_number",
            field=models.IntegerField(blank=True),
        ),
    ]
