# Generated by Django 4.2.1 on 2023-10-15 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0004_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='comment',
            field=models.TextField(blank=True, max_length=1000, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='addagreement',
            name='comment',
            field=models.TextField(blank=True, max_length=1000, verbose_name='Комментарий'),
        ),
    ]
