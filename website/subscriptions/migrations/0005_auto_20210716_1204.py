# Generated by Django 3.2 on 2021-07-16 10:04

from django.db import migrations, models
import django.db.models.deletion
import subscriptions.models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0004_auto_20210505_2048"),
    ]

    operations = [
        migrations.RenameField(
            model_name="subscriptioncategory",
            old_name="parent",
            new_name="category",
        ),
        migrations.AlterField(
            model_name="subscription",
            name="email_template_text",
            field=models.FileField(
                blank=True,
                help_text="The template of the email to generate (as text).",
                null=True,
                upload_to=subscriptions.models.email_template_filename,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="letter_template",
            field=models.FileField(
                blank=True,
                help_text="The template of the letter to generate.",
                null=True,
                upload_to=subscriptions.models.letter_template_filename,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="name",
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="slug",
            field=models.SlugField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="subscriptioncategory",
            name="email_template_text",
            field=models.FileField(
                blank=True,
                help_text="The template of the email to generate (as text).",
                null=True,
                upload_to=subscriptions.models.email_template_filename,
            ),
        ),
        migrations.AlterField(
            model_name="subscriptioncategory",
            name="letter_template",
            field=models.FileField(
                blank=True,
                help_text="The template of the letter to generate.",
                null=True,
                upload_to=subscriptions.models.letter_template_filename,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="subscriptioncategory",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="subscriptioncategory",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="subscriptions.subscriptioncategory",
            ),
        ),
    ]
