# Generated by Django 4.1 on 2023-03-22 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0003_routeplandata_routeplanhyperparameter'),
    ]

    operations = [
        migrations.CreateModel(
            name='NextLocData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='traffic')),
                ('type', models.CharField(default='route_plan_trajectory', max_length=50, verbose_name='Data Type')),
            ],
        ),
        migrations.CreateModel(
            name='NextLocHyperparameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epochs', models.IntegerField()),
                ('batch_size', models.IntegerField()),
                ('lr', models.FloatField()),
                ('dropout', models.FloatField()),
            ],
        ),
        migrations.AlterField(
            model_name='accidentdata',
            name='file',
            field=models.FileField(null=True, upload_to='traffic'),
        ),
        migrations.AlterField(
            model_name='representationdata',
            name='file',
            field=models.FileField(null=True, upload_to='traffic'),
        ),
        migrations.AlterField(
            model_name='routeplandata',
            name='file',
            field=models.FileField(null=True, upload_to='traffic'),
        ),
    ]