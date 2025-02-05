# Generated by Django 4.2.14 on 2024-07-28 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_user_station',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='air_quality_data',
        ),
        migrations.AddField(
            model_name='favorite',
            name='station_uid',
            field=models.IntegerField(default=777),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'station_uid'), name='unique_user_station'),
        ),
    ]
