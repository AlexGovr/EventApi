# Generated by Django 3.2.4 on 2021-06-08 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_rename_transaction_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='cost',
            field=models.FloatField(default=1100),
            preserve_default=False,
        ),
    ]
