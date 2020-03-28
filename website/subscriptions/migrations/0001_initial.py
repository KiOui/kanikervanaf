# Generated by Django 3.0.4 on 2020-03-27 19:49

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "__first__"),
    ]

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
                (
                    "price",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=10),
                ),
                ("support_email", models.EmailField(blank=True, max_length=254)),
                ("support_reply_number", models.CharField(blank=True, max_length=10)),
                ("support_postal_code", models.CharField(blank=True, max_length=6)),
                ("support_city", models.CharField(blank=True, max_length=1024)),
                (
                    "correspondence_address",
                    models.CharField(blank=True, max_length=1024),
                ),
                (
                    "correspondence_postal_code",
                    models.CharField(blank=True, max_length=6),
                ),
                ("correspondence_city", models.CharField(blank=True, max_length=1024)),
                (
                    "support_phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "cancellation_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                ("amount_used", models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="SubscriptionSearchTerm",
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
                (
                    "subscription",
                    models.ManyToManyField(to="subscriptions.Subscription"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubscriptionCategory",
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
                ("slug", models.SlugField()),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="subscriptions.SubscriptionCategory",
                    ),
                ),
            ],
            options={
                "verbose_name": "Subscription category",
                "verbose_name_plural": "Subscription categories",
                "unique_together": {("slug", "parent")},
            },
        ),
        migrations.AddField(
            model_name="subscription",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="subscriptions.SubscriptionCategory",
            ),
        ),
        migrations.CreateModel(
            name="QueuedMailList",
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
                ("token", models.CharField(max_length=64, unique=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("item_list", models.ManyToManyField(to="subscriptions.Subscription")),
                (
                    "user_information",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.UserInformation",
                    ),
                ),
            ],
        ),
    ]
