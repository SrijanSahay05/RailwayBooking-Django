# Generated by Django 5.1.3 on 2024-11-21 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('railways', '0004_journey_journey_seat_categories'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='seat_category',
            new_name='journey_seat_category',
        ),
    ]