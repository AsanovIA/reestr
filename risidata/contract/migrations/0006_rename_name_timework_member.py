# Generated by Django 4.2.1 on 2023-10-15 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0005_contact_comment_alter_addagreement_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timework',
            old_name='name',
            new_name='member',
        ),
    ]
