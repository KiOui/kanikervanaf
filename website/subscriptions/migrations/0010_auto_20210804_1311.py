# Generated by Django 3.2.6 on 2021-08-04 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0009_subscriptioncategory_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="queuedmaillist",
            name="address",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="queuedmaillist",
            name="email_address",
            field=models.EmailField(max_length=512),
        ),
        migrations.AlterField(
            model_name="queuedmaillist",
            name="firstname",
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name="queuedmaillist",
            name="lastname",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="queuedmaillist",
            name="residence",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="cancellation_number",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The cancellation number (possibly paid).",
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="correspondence_address",
            field=models.TextField(
                blank=True,
                default="",
                help_text="The correspondence address of the subscription provider.",
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="correspondence_city",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The city for the correspondence address of the subscription provider.",
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="correspondence_postal_code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The postal code for the correspondence address of the subscription provider.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="name",
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_city",
            field=models.TextField(
                blank=True,
                default="",
                help_text="The city for the support reply number.",
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_email",
            field=models.EmailField(
                blank=True,
                default="",
                help_text="The support email address for the subscription. If enabled in the website settings, this is also the email address where the deregister emails are sent to.",
                max_length=254,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_phone_number",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The support phone number (not paid).",
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_postal_code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The postal code for the support reply number.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="support_reply_number",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The reply number (Postbus) for the subscription provider (to send the customers letter to).",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="subscriptioncategory",
            name="name",
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name="subscriptionsearchterm",
            name="name",
            field=models.CharField(max_length=512),
        ),
    ]