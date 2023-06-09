# Generated by Django 4.2 on 2023-06-02 13:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cashbook", "0006_category_is_active_alter_transaction_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="last_updated",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name="account",
            name="net_balance",
            field=models.FloatField(default=0),
        ),
    ]
