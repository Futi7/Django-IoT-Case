# Generated by Django 3.0.7 on 2020-09-16 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20200915_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='time_stamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]