# Generated by Django 4.1 on 2023-03-08 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlowPredictionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='poptraffic')),
                ('type', models.CharField(default='route_plan_trajectory', max_length=50, verbose_name='Data Type')),
            ],
        ),
        migrations.CreateModel(
            name='FlowPredictionHyperparameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epochs', models.IntegerField()),
                ('batch_size', models.IntegerField()),
                ('lr', models.FloatField()),
                ('dropout', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SpeedPredictionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='poptraffic')),
                ('type', models.CharField(max_length=50, verbose_name='Data Type')),
            ],
        ),
        migrations.CreateModel(
            name='SpeedPredictionHyperparameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epochs', models.IntegerField()),
                ('batch_size', models.IntegerField()),
                ('lr', models.FloatField()),
                ('dropout', models.FloatField()),
            ],
        ),
    ]
