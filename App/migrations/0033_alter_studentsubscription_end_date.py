# Generated by Django 5.1.4 on 2024-12-19 22:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0032_alter_studentsubscription_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentsubscription',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 6, 17, 22, 37, 14, 997270, tzinfo=datetime.timezone.utc)),
        ),
    ]
