# Generated by Django 3.2.15 on 2023-04-15 03:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_rename_name_user_username'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]