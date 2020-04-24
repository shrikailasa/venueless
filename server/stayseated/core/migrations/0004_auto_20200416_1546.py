# Generated by Django 3.0.5 on 2020-04-16 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_auto_20200416_1143"),
    ]

    operations = [
        migrations.RenameField(
            model_name="chatevent", old_name="event_id", new_name="world_id",
        ),
        migrations.RenameField(
            model_name="user", old_name="event_id", new_name="world_id",
        ),
        migrations.AlterUniqueTogether(
            name="user",
            unique_together={("token_id", "world_id"), ("client_id", "world_id")},
        ),
    ]