# Generated by Django 4.1 on 2023-03-07 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='pop_traffic')),
                ('type', models.CharField(max_length=50, verbose_name='Data Type')),
            ],
        ),
        migrations.CreateModel(
            name='Hyperparameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epochs', models.IntegerField()),
                ('batch_size', models.IntegerField()),
                ('lr', models.FloatField()),
                ('dropout', models.FloatField()),
                ('road_num', models.IntegerField()),
                ('road_dim', models.IntegerField()),
                ('region_num', models.IntegerField()),
                ('region_dim', models.IntegerField()),
                ('zone_num', models.IntegerField()),
                ('zone_dim', models.IntegerField()),
            ],
        ),
    ]
