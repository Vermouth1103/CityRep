# Generated by Django 3.2.15 on 2023-04-14 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0005_auto_20230413_1708'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SpeedPredictionHyperparameter',
        ),
    ]
