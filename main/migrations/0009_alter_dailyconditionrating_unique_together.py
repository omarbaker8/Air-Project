# Generated by Django 4.2.14 on 2024-08-04 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_dailyconditionrating_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dailyconditionrating',
            unique_together=set(),
        ),
    ]