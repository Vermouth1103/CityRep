# Generated by Django 4.1 on 2023-03-22 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0002_accidentdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoutePlanData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='indtraffic')),
                ('type', models.CharField(default='route_plan_trajectory', max_length=50, verbose_name='Data Type')),
            ],
        ),
        migrations.CreateModel(
            name='RoutePlanHyperparameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epochs', models.IntegerField()),
                ('batch_size', models.IntegerField()),
                ('lr', models.FloatField()),
                ('dropout', models.FloatField()),
            ],
        ),
    ]