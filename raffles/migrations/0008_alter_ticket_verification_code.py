# Generated by Django 3.2.25 on 2024-08-12 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0007_alter_ticket_verification_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='verification_code',
            field=models.UUIDField(editable=False),
        ),
    ]
