# Generated by Django 4.2.18 on 2025-02-08 20:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_band_hashtag"),
    ]

    operations = [
        migrations.AddField(
            model_name="song",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
