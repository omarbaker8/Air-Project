# Generated by Django 4.2.14 on 2024-08-04 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_dailyconditionrating_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyconditionrating',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
