# Generated by Django 5.1.3 on 2024-11-25 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_rename_date_waitlistemail_date_enrolled"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Note",
        ),
    ]
