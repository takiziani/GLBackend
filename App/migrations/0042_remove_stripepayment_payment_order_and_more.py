# Generated by Django 5.1.4 on 2024-12-24 16:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0041_alter_studentsubscription_end_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripepayment',
            name='payment_order',
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='payment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='enrollment_pay', to='App.stripepayment'),
        ),
    ]
