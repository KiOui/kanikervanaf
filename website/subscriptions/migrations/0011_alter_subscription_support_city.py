# Generated by Django 3.2.6 on 2021-08-04 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0010_auto_20210804_1344"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="support_city",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The city for the support reply number.",
                max_length=512,
            ),
        ),
    ]