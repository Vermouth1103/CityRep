# Generated by Django 4.1 on 2023-03-21 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccidentData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='poptraffic')),
                ('type', models.CharField(default='route_plan_trajectory', max_length=50, verbose_name='Data Type')),
            ],
        ),
    ]
