# Generated by Django 3.0.7 on 2020-06-19 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
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
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "support_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "support_reply_number",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                (
                    "support_postal_code",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                (
                    "support_city",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "correspondence_address",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "correspondence_postal_code",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                (
                    "correspondence_city",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "support_phone_number",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "cancellation_number",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                ("amount_used", models.PositiveIntegerField(default=1)),
                ("slug", models.SlugField(max_length=100, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
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
                ("slug", models.SlugField(max_length=100, unique=True)),
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
